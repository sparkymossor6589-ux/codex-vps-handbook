# Project provenance: local Codex-assisted maintenance/preview code.
# Scope and modifications: CONTRIBUTIONS.md and data/file-provenance.json.
# MIT applies only to rights held by project contributors; see LICENSE_SCOPE.md.
from pathlib import Path
from http.client import HTTPConnection
import datetime as dt
import hashlib,json,tempfile,threading,unittest

from traffic_service import BoundedServer,make_handler

class Meter:
    def sample(self):
        return {'rx':1,'tx':2,'updated':dt.datetime.now(dt.timezone.utc).isoformat()}

class EnhancementTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.folder=self.root/'20261022-r1';self.folder.mkdir()
        (self.root/'current').symlink_to(self.folder.name)
        self.body=b'#!name=Test\n[Rule]\nDOMAIN,ads.example.invalid,REJECT\n'
        (self.folder/'ChineseApps.srmodule').write_bytes(self.body)
        (self.folder/'manifest.json').write_text(json.dumps({'version':'20261022-r1','allowed_files':['ChineseApps.srmodule'],'hashes':{'ChineseApps.srmodule':hashlib.sha256(self.body).hexdigest()}}))
        self.config={'token':'test-token','total_bytes':1024**4,'title':'My VPS','node_uri':'vless://test@example.invalid:443#AWS%20Tokyo','public_origin':'https://example.invalid','routing_profile':str(self.root/'profile.conf'),'enhance_root':str(self.root)}
        (self.root/'profile.conf').write_text('[Rule]\nFINAL,TOKYO\n')
        self.server=BoundedServer(('127.0.0.1',0),make_handler(Meter(),self.config))
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()

    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.temp.cleanup()

    def req(self,path,method='GET'):
        c=HTTPConnection(*self.server.server_address,timeout=3);c.request(method,path);r=c.getresponse();out=(r.status,dict(r.getheaders()),r.read());c.close();return out

    def test_module_stable_and_pinned_assets_and_head(self):
        for p in ['/s/test-token/enhance/ChineseApps.srmodule','/s/test-token/enhance/20261022-r1/ChineseApps.srmodule']:
            self.assertEqual(self.req(p)[::2],(200,self.body))
            status,headers,body=self.req(p,'HEAD');self.assertEqual(status,200);self.assertEqual(body,b'');self.assertEqual(int(headers['Content-Length']),len(self.body))

    def test_wrong_bearer_traversal_queries_and_manifest_denied(self):
        for p in ['/s/wrong/enhance','/s/wrong/enhance/ChineseApps.srmodule','/s/test-token/enhance/../config.json','/s/test-token/enhance/%2e%2e/config.json','/s/test-token/enhance/20261022-r1/../../config.json','/s/test-token/enhance/ChineseApps.srmodule?x=1','/s/test-token/enhance/manifest.json']:
            with self.subTest(p=p):self.assertEqual(self.req(p)[0],404)

    def test_corrupt_asset_never_delivered_as_success(self):
        (self.folder/'ChineseApps.srmodule').write_text('corrupt')
        self.assertEqual(self.req('/s/test-token/enhance/ChineseApps.srmodule')[0],503)

    def test_page_has_local_install_link_and_certificate_gate(self):
        status,headers,body=self.req('/s/test-token/enhance');text=body.decode()
        self.assertEqual(status,200);self.assertIn('shadowrocket://install?module=',text);self.assertIn('先保持模块关闭',text);self.assertNotIn(self.config['node_uri'],text);self.assertNotIn('<script',text);self.assertEqual(headers['Referrer-Policy'],'no-referrer')

    def test_original_profile_bytes_are_untouched(self):
        path='/s/test-token/AWS-Tokyo-Online.conf'
        before=self.req(path)[2];self.req('/s/test-token/enhance');self.req('/s/test-token/enhance/ChineseApps.srmodule')
        self.assertEqual(before,self.req(path)[2]);self.assertEqual(before,(self.root/'profile.conf').read_bytes())

if __name__=='__main__':unittest.main()
