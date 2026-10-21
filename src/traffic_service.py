# Project provenance: local Codex-assisted maintenance/preview code.
# Scope and modifications: CONTRIBUTIONS.md and data/file-provenance.json.
# MIT applies only to rights held by project contributors; see LICENSE_SCOPE.md.
"""Read-only private subscription; independent of Xray and client routing.

Counts the primary interface, including both sides of proxy forwarding. These
are estimates, not AWS billing measurements. No AWS credentials are needed.
"""
import argparse
import base64
import datetime as dt
import hmac
import html
import json
import os
from pathlib import Path
import signal
import ssl
import threading
import time
import android_access
import adblock_access
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UTC = dt.timezone.utc


class BoundedServer(ThreadingHTTPServer):
    """Bound public connections; do TLS handshakes in timed worker threads."""
    daemon_threads = True
    request_queue_size = 16
    tls_context = None

    def __init__(self, *args, **kwargs):
        self.slots = threading.BoundedSemaphore(8)
        super().__init__(*args, **kwargs)

    def process_request(self, request, address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, address)
        except BaseException:
            self.slots.release()
            raise

    def process_request_thread(self, request, address):
        try:
            request.settimeout(8)
            if self.tls_context:
                request = self.tls_context.wrap_socket(request, server_side=True)
            super().process_request_thread(request, address)
        except (OSError, ssl.SSLError):
            self.shutdown_request(request)
        finally:
            self.slots.release()


def next_month(now):
    return dt.datetime(now.year + (now.month == 12), now.month % 12 + 1, 1, tzinfo=UTC)


def accumulate(state, boot, rx, tx, now):
    month = now.strftime('%Y-%m')
    if state is None:
        # Installation audit confirmed this is the instance's original boot,
        # within the current billing month. Seed ALL traffic since that boot.
        return {'month': month, 'boot': boot, 'last_rx': rx, 'last_tx': tx,
                'rx': rx, 'tx': tx, 'updated': now.isoformat(),
                'source': 'primary-interface-estimate',
                'seed': 'original-instance-boot'}
    same_boot = state['boot'] == boot
    dr = rx - state['last_rx'] if same_boot and rx >= state['last_rx'] else rx
    dw = tx - state['last_tx'] if same_boot and tx >= state['last_tx'] else tx
    if state['month'] != month:
        state['previous_month'] = {k: state[k] for k in ('month', 'rx', 'tx', 'updated')}
        state.update(month=month, rx=0, tx=0)
    state.update(boot=boot, last_rx=rx, last_tx=tx,
                 rx=state['rx'] + dr, tx=state['tx'] + dw,
                 updated=now.isoformat())
    return state


class Meter:
    def __init__(self, path, interface):
        self.path = Path(path)
        self.interface = interface
        self.lock = threading.Lock()
        self.state = json.loads(self.path.read_text()) if self.path.exists() else None
        self.boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()

    def sample(self, persist=False):
        with self.lock:
            folder = Path('/sys/class/net') / self.interface / 'statistics'
            rx = int((folder / 'rx_bytes').read_text())
            tx = int((folder / 'tx_bytes').read_text())
            self.state = accumulate(self.state, self.boot, rx, tx, dt.datetime.now(UTC))
            if persist:
                tmp = self.path.with_suffix('.tmp')
                with tmp.open('w') as f:
                    json.dump(self.state, f)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp, self.path)
            return dict(self.state)


def make_handler(meter, config):
    total = int(config['total_bytes'])
    token_path = '/s/' + config['token']

    def setup_page(status):
        origin = config['public_origin'].rstrip('/')
        subscription_url = origin + token_path
        profile_url = origin + token_path + '/AWS-Tokyo-Online.conf'
        sub_link = 'sub://' + base64.b64encode(subscription_url.encode()).decode() + '#AWS%20Tokyo'
        profile_link = 'shadowrocket://config/add/' + profile_url
        escape = html.escape
        return f'''<!doctype html><html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="referrer" content="no-referrer"><title>My VPS · iPhone 接入</title>
<style>body{{font:17px/1.7 -apple-system,BlinkMacSystemFont,sans-serif;background:#f2f5fa;color:#182234;margin:0;padding:24px 18px}}main{{max-width:560px;margin:auto}}section{{background:white;border:1px solid #dce3ed;border-radius:18px;padding:22px;margin:18px 0}}h1{{font-size:28px;line-height:1.3}}h2{{font-size:20px;margin-top:0}}.button{{display:block;background:#1767da;color:white;padding:13px 18px;border-radius:12px;text-align:center;text-decoration:none;font-weight:600;margin:16px 0}}small{{color:#536178}}code{{font-size:15px}}summary{{cursor:pointer}}input{{box-sizing:border-box;width:100%;font-size:14px;padding:10px;border:1px solid #cad4e2;border-radius:8px}}li{{margin:9px 0}}</style>
</head><body><main><h1>My VPS<br>iPhone 在线接入</h1>
<p>一次扫码进入此页，按顺序完成两次导入。以后在线更新，无需再传文件。</p>
<section><h2>1 · 添加节点与流量订阅</h2><p>返回此页前，先在小火箭完成订阅添加与刷新。已有同一订阅时刷新即可。</p>
<a class="button" href="{escape(sub_link, quote=True)}">导入节点与流量订阅</a>
<small>{escape(status)}。这是整台服务器的流量估算，所有设备共用。</small>
<details><summary>按钮没有打开小火箭？</summary><p>复制下方地址，在小火箭首页＋ → 类型 Subscribe → URL 中粘贴并保存。</p><input readonly aria-label="节点订阅地址" value="{escape(subscription_url, quote=True)}"></details></section>
<section><h2>2 · 添加在线分流配置</h2><p>使用你为自己的设备准备的分流规则与 DNS 设置，并绑定此在线更新地址。</p>
<a class="button" href="{escape(profile_link, quote=True)}">导入在线分流配置</a>
<p>导入后选“使用配置”，首页“全局路由”选“配置”，TOKYO 分组选择 My VPS。</p>
<details><summary>手动添加在线配置地址</summary><p>配置页＋ → 粘贴下方地址 → 下载 → 使用配置。</p><input readonly aria-label="在线分流配置地址" value="{escape(profile_url, quote=True)}"></details></section>
<section><h2>3 · 开启自动更新</h2><p>小火箭 → 设置 → 自动更新：分别开启“配置”和“订阅”的自动后台更新；iPhone 系统中允许小火箭后台 App 刷新。按需选择更新间隔。</p>
<p>配置在服务器发布新版本后，客户端拉取即可更新；订阅更新负责节点与流量显示。iOS 后台调度不保证准点，需要立即生效时手动更新即可。</p>
<p>首次连接的 VPN 授权由本人确认。最后分别用 Wi-Fi 与蜂窝网络测试国内应用、Google、ChatGPT 对话与上传。</p></section>
<small>此链接仅供本人使用。请用 Safari 打开本页；不要把本页地址填入节点订阅栏。若提示重复订阅，返回并更新已有订阅，不要反复添加。</small>
<section><h2>4 · 中文应用增强</h2><p>保留现有节点与分流，单独添加应用增强模块。首次需要在设备本地完成证书设置。</p><a class="button" href="{escape(origin + token_path + '/enhance', quote=True)}">设置中文应用增强</a></section></main></body></html>'''.encode('utf-8')

    class Handler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'

        def log_message(self, *args):
            # Never put the subscription's bearer token in access logs.
            pass

        def do_HEAD(self):
            self.do_GET()

        def do_GET(self):
            self.connection.settimeout(10)
            if adblock_access.serve(self, config):
                return
            if android_access.serve(self, config):
                return
            routes = {token_path: 'subscription'}
            if config.get('public_origin') and config.get('routing_profile'):
                routes[token_path + '/setup'] = 'setup'
                routes[token_path + '/AWS-Tokyo-Online.conf'] = 'profile'
            route = next((kind for path, kind in routes.items()
                          if hmac.compare_digest(self.path, path)), None)
            if route is None:
                self.send_response(404)
                self.send_header('Content-Length', '0')
                self.send_header('Connection', 'close')
                self.end_headers()
                self.close_connection = True
                return
            state = meter.sample()
            used = state['rx'] + state['tx']
            remaining = max(0, total - used)
            now = dt.datetime.now(UTC)
            reset = next_month(now)
            cn = dt.timezone(dt.timedelta(hours=8))
            title = config.get('title', 'My VPS')
            status = (f'剩余约 {remaining / 1024**3:.2f} GB / {total / 1024**3:.0f} GB'
                      f' · {reset.astimezone(cn):%m/%d %H:%M} 重置'
                      f' · 更新 {now.astimezone(cn):%m/%d %H:%M}')
            # Serve the user's existing node together with the traffic metadata.
            # The private HTTPS bearer URL now also protects the proxy details.
            node_uri = config['node_uri']
            content = f'STATUS={status}\nREMARKS={title}\n{node_uri}\n'
            payload = base64.b64encode(content.encode('utf-8'))
            content_type = 'text/plain; charset=utf-8'
            if route == 'setup':
                payload = setup_page(status)
                content_type = 'text/html; charset=utf-8'
            elif route == 'profile':
                try:
                    payload = Path(config['routing_profile']).read_bytes()
                except OSError:
                    self.send_response(503)
                    self.send_header('Content-Length', '0')
                    self.send_header('Connection', 'close')
                    self.end_headers()
                    self.close_connection = True
                    return
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('X-Content-Type-Options', 'nosniff')
            if route == 'setup':
                self.send_header('Content-Security-Policy',
                                 "default-src 'none'; style-src 'unsafe-inline'; "
                                 "base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
            # Shadowrocket prioritizes this header over STATUS and otherwise
            # shows only RX/TX/total, not remaining/reset. Use its native
            # STATUS/REMARKS content fields for a directly readable estimate.
            # Monthly reset is informational, NOT a subscription expiry.
            self.send_header('profile-title', 'base64:' + base64.b64encode(title.encode()).decode())
            self.send_header('profile-update-interval', '1')
            self.send_header('X-Traffic-Source', 'interface-estimate-not-AWS-invoice')
            self.send_header('X-Traffic-Updated', state['updated'])
            self.send_header('X-Traffic-Reset', reset.isoformat())
            self.send_header('Connection', 'close')
            self.end_headers()
            print('Authenticated', route, 'refresh', now.isoformat(), flush=True)
            if self.command != 'HEAD':
                self.wfile.write(payload)
            self.close_connection = True

    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='/etc/vps-access/config.json')
    parser.add_argument('--state', default='/var/lib/vps-access/meter.json')
    parser.add_argument('--bind', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=18444)
    parser.add_argument('--cert')
    parser.add_argument('--key')
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    meter = Meter(args.state, config['interface'])
    meter.sample(persist=True)
    stopped = threading.Event()
    server = BoundedServer((args.bind, args.port), make_handler(meter, config))
    if args.cert:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.load_cert_chain(args.cert, args.key)
        server.tls_context = context
    elif args.bind not in ('127.0.0.1', '::1'):
        raise SystemExit('Refusing public HTTP listener; TLS is required.')

    def shutdown(*_):
        stopped.set()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        tick = 0
        while not stopped.wait(1):
            tick += 1
            meter.sample(persist=tick % 5 == 0)
    finally:
        server.shutdown()
        server.server_close()
        meter.sample(persist=True)


if __name__ == '__main__':
    main()
