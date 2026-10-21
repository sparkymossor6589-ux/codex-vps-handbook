# Project provenance: local Codex-assisted maintenance/preview code.
# Scope and modifications: CONTRIBUTIONS.md and data/file-provenance.json.
# MIT applies only to rights held by project contributors; see LICENSE_SCOPE.md.
"""Check private online entry, profile delivery, and legacy subscription."""
import base64
import datetime as dt
from http.client import HTTPConnection
from pathlib import Path
import tempfile
import threading
import unittest

from traffic_service import BoundedServer, make_handler


class FakeMeter:
    def sample(self):
        return {'rx': 100, 'tx': 200, 'updated': dt.datetime.now(dt.timezone.utc).isoformat()}


class OnlineEntryTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.profile = Path(self.folder.name) / 'profile.conf'
        self.profile.write_text('[General]\nupdate-url = https://example.invalid/s/test-token/AWS-Tokyo-Online.conf\n[Rule]\nFINAL,TOKYO\n')
        self.config = {'token': 'test-token', 'total_bytes': 1024**4,
                       'title': 'My VPS', 'node_uri': 'vless://test@example.invalid:443#AWS%20Tokyo',
                       'public_origin': 'https://example.invalid', 'routing_profile': str(self.profile)}
        self.server = BoundedServer(('127.0.0.1', 0), make_handler(FakeMeter(), self.config))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.folder.cleanup()

    def request(self, path, method='GET'):
        connection = HTTPConnection(*self.server.server_address, timeout=3)
        connection.request(method, path)
        response = connection.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return result

    def test_existing_subscription_keeps_node_and_estimate(self):
        status, headers, body = self.request('/s/test-token')
        decoded = base64.b64decode(body).decode()
        self.assertEqual(status, 200)
        self.assertIn('STATUS=', decoded)
        self.assertIn('REMARKS=My VPS', decoded)
        self.assertEqual(decoded.splitlines()[-1], self.config['node_uri'])
        self.assertNotIn('subscription-userinfo', {key.lower() for key in headers})

    def test_setup_has_both_native_imports_and_no_external_resources(self):
        status, headers, body = self.request('/s/test-token/setup')
        text = body.decode()
        self.assertEqual(status, 200)
        self.assertIn('sub://', text)
        self.assertIn('shadowrocket://config/add/https://example.invalid/s/test-token/AWS-Tokyo-Online.conf', text)
        self.assertNotIn('<script', text)
        self.assertNotIn('<img', text)
        self.assertNotIn(self.config['node_uri'], text)
        self.assertEqual(headers['Referrer-Policy'], 'no-referrer')
        self.assertIn("default-src 'none'", headers['Content-Security-Policy'])

    def test_profile_is_live_and_head_has_no_body(self):
        path = '/s/test-token/AWS-Tokyo-Online.conf'
        self.assertEqual(self.request(path)[2], self.profile.read_bytes())
        self.profile.write_text('[General]\n[Rule]\nFINAL,DIRECT\n')
        self.assertEqual(self.request(path)[2], self.profile.read_bytes())
        status, headers, body = self.request(path, 'HEAD')
        self.assertEqual(status, 200)
        self.assertEqual(int(headers['Content-Length']), self.profile.stat().st_size)
        self.assertEqual(body, b'')

    def test_wrong_tokens_and_path_traversal_are_rejected(self):
        for path in ['/', '/setup', '/s/wrong', '/s/wrong/setup',
                     '/s/test-token/../config.json', '/s/test-token/%2e%2e/config.json',
                     '/s/test-token/setup?next=https://bad.invalid',
                     '/s/test-token/AWS-Tokyo-Online.conf/extra']:
            with self.subTest(path=path):
                status, _, body = self.request(path)
                self.assertEqual((status, body), (404, b''))

    def test_missing_profile_is_not_a_successful_empty_update(self):
        self.profile.unlink()
        self.assertEqual(self.request('/s/test-token/AWS-Tokyo-Online.conf')[0], 503)


if __name__ == '__main__':
    unittest.main()
