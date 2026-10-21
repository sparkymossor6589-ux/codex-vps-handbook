# Project provenance: local Codex-assisted maintenance/preview code.
# Scope and modifications: CONTRIBUTIONS.md and data/file-provenance.json.
# MIT applies only to rights held by project contributors; see LICENSE_SCOPE.md.
"""Exercise authorization, per-friend isolation, revoke, and legacy compatibility."""
from pathlib import Path
from http.client import HTTPConnection
import json
import tempfile
import threading
import unittest
from test_online_entry import FakeMeter
from traffic_service import BoundedServer, make_handler


class AndroidAccessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'assets').mkdir()
        (self.root / 'assets/client.apk').write_bytes(b'APK' * 50000)
        for number in (1, 2):
            folder = self.root / f'friend{number:02d}'
            folder.mkdir()
            (folder / 'Tokyo-Android.yaml').write_text(f'friend: {number}\n')
        self.registry = {'origin': 'https://example.invalid', 'root': str(self.root),
                         'installer': 'client.apk', 'friends': [
                             {'id': 'friend01', 'label': 'Friend 1', 'token': 'token-one', 'enabled': True},
                             {'id': 'friend02', 'label': 'Friend 2', 'token': 'token-two', 'enabled': True}]}
        self.path = self.root / 'registry.json'
        self.save()
        config = {'android_registry': str(self.path), 'token': 'owner-token', 'total_bytes': 1024**4,
                  'node_uri': 'owner-secret-node', 'title': 'My VPS'}
        self.server = BoundedServer(('127.0.0.1', 0), make_handler(FakeMeter(), config))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def save(self):
        self.path.write_text(json.dumps(self.registry))

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.tmp.cleanup()

    def request(self, path, method='GET'):
        c = HTTPConnection(*self.server.server_address, timeout=3)
        c.request(method, path)
        r = c.getresponse()
        result = r.status, dict(r.getheaders()), r.read()
        c.close()
        return result

    def test_independent_profiles_and_private_page(self):
        self.assertEqual(self.request('/a/token-one/Tokyo-Android.yaml')[2], b'friend: 1\n')
        self.assertEqual(self.request('/a/token-two/Tokyo-Android.yaml')[2], b'friend: 2\n')
        status, headers, body = self.request('/a/token-one/setup')
        self.assertEqual(status, 200)
        self.assertIn(b'clashmeta://install-config?url=', body)
        for secret in (b'token-two', b'owner-token', b'owner-secret-node'):
            self.assertNotIn(secret, body)
        self.assertEqual(headers['Referrer-Policy'], 'no-referrer')
        self.assertIn("default-src 'none'", headers['Content-Security-Policy'])

    def test_bad_tokens_queries_and_traversal_never_return_data(self):
        for path in ['/a/wrong/setup', '/a/wrong?from=singlemessage', '/a/token-one/../registry.json',
                     '/a/token-one/%2e%2e/registry.json',
                     '/a/token-one/friend02/Tokyo-Android.yaml', '/a/token-one/config.json']:
            self.assertEqual(self.request(path)[0], 404, path)

    def test_revoke_is_dynamic_and_isolated(self):
        self.registry['friends'][0]['enabled'] = False
        self.save()
        for suffix in ('setup', 'Tokyo-Android.yaml', 'client.apk'):
            self.assertEqual(self.request('/a/token-one/' + suffix)[0], 404)
        self.assertEqual(self.request('/a/token-two/setup')[0], 200)
        self.assertEqual(self.request('/s/owner-token')[0], 200)

    def test_head_and_large_installer_and_missing_profile(self):
        status, headers, body = self.request('/a/token-one/client.apk')
        self.assertEqual(status, 200)
        self.assertEqual(body, b'APK' * 50000)
        self.assertEqual(headers['Content-Type'], 'application/vnd.android.package-archive')
        status, headers, body = self.request('/a/token-one/Tokyo-Android.yaml', 'HEAD')
        self.assertEqual((status, body), (200, b''))
        self.assertEqual(headers['profile-update-interval'], '12')
        (self.root / 'friend01/Tokyo-Android.yaml').unlink()
        self.assertEqual(self.request('/a/token-one/Tokyo-Android.yaml')[0], 503)

    def test_shared_aliases_deliver_one_profile_and_clean_page(self):
        self.registry['friends'] = [dict(self.registry['friends'][0], aliases=['old-token'])]
        self.save()
        self.assertEqual(self.request('/a/old-token/Tokyo-Android.yaml')[2], self.request('/a/token-one/Tokyo-Android.yaml')[2])
        status, headers, body = self.request('/a/old-token/setup')
        self.assertEqual(status, 200)
        text = body.decode()
        for irrelevant in ['朋友', '专属', '流量额度', '维护者', '未验证', 'Friend 1', 'old-token', '{{']:
            self.assertNotIn(irrelevant, text)
        self.assertIn('&amp;name=Tokyo-Android&amp;update-interval=720', text)
        nonce = text.split('<script nonce="', 1)[1].split('"', 1)[0]
        self.assertIn("script-src 'nonce-" + nonce + "'", headers['Content-Security-Policy'])
        self.assertIn('id="copy-url"', text)

    def test_browser_share_parameters_and_entry_path_variants(self):
        for path in ['/a/token-one', '/a/token-one/', '/a/token-one/setup/',
                     '/a/token-one/setup?from=singlemessage&isappinstalled=0',
                     '/a/token-one/setup/?utm_source=share', '/a/token-one?from=timeline']:
            with self.subTest(path=path):
                status, _, body = self.request(path)
                self.assertEqual(status, 200)
                self.assertIn('安卓接入'.encode(), body)
        self.assertEqual(self.request('/a/token-one/Tokyo-Android.yaml?download=1')[2], b'friend: 1\n')


if __name__ == '__main__':
    unittest.main()
