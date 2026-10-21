# Project provenance: local Codex-assisted maintenance/preview code.
# Scope and modifications: CONTRIBUTIONS.md and data/file-provenance.json.
# MIT applies only to rights held by project contributors; see LICENSE_SCOPE.md.
"""Serve owner-only, versioned enhancement files using the existing bearer URL."""
from pathlib import Path
from urllib.parse import quote
import hashlib, hmac, html, json, re

DEFAULT_ROOT = Path('/etc/vps-access/enhance')

def payload(config, path):
    token_path = '/s/' + config['token']
    prefix = token_path + '/enhance'
    if not (hmac.compare_digest(path, prefix) or path.startswith(prefix + '/')):
        return None
    root = Path(config.get('enhance_root', DEFAULT_ROOT))
    suffix = path[len(prefix):]
    if suffix == '':
        if not (root / 'current/manifest.json').is_file():
            return (503, 'text/plain', b'Not available')
        origin = config['public_origin'].rstrip('/')
        module_url = origin + prefix + '/ChineseApps.srmodule'
        install = 'shadowrocket://install?module=' + quote(module_url, safe='')
        e = html.escape
        content = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer">
<title>中文应用增强</title><style>body{{font:17px/1.7 -apple-system,sans-serif;background:#f2f5fa;color:#182234;margin:0;padding:24px 18px}}main{{max-width:620px;margin:auto}}section{{background:white;border:1px solid #dce3ed;border-radius:18px;padding:22px;margin:18px 0}}h1{{font-size:28px}}h2{{font-size:21px;margin-top:0}}a.button{{display:block;background:#1767da;color:white;padding:14px;border-radius:12px;text-align:center;text-decoration:none;font-weight:600}}input{{box-sizing:border-box;width:100%;font-size:14px;padding:10px}}small{{color:#536178}}li{{margin:10px 0}}</style></head>
<body><main><h1>中文应用增强</h1><p>保留现有节点、国内外分流和 DNS，另外添加应用增强模块。</p>
<section><h2>1 · 导入模块</h2><p>包含知乎、小红书、哔哩哔哩、贴吧、微博、Keep、高德、菜鸟、闲鱼、网易云、什么值得买、喜马拉雅、12306和起点。</p>
<p>按已同意的范围整合去广告、界面精简及各来源提供的下载、图标、皮肤等功能。来源未提供的功能不会凭空增加，当前版本效果仍需逐项测试。</p>
<a class="button" href="{e(install,quote=True)}">导入中文应用增强</a>
<details><summary>手动导入</summary><p>小火箭 → 配置 → 模块 → 添加，将下方地址粘贴到 URL。</p><input readonly aria-label="增强模块地址" value="{e(module_url,quote=True)}"></details></section>
<section><h2>2 · 在本机完成证书设置</h2><ol><li>先保持模块关闭，打开小火箭的 HTTPS 解密设置。</li><li>在当前设备生成自己的 CA 证书，按提示安装。不要使用他人的证书，也不要发送证书私钥。</li><li>iPhone 按提示在“设置 → 通用 → VPN与设备管理”安装描述文件，再到“关于本机 → 证书信任设置”核对对应证书并启用完全信任。</li><li>回到小火箭，开启 HTTPS 解密，再启用增强模块。</li></ol>
<small>手动安装证书不会自动获得 SSL 信任。解密按列出的主机工作，同主机普通请求也可能被解密。模块不包含证书或私钥。</small></section>
<section><h2>3 · 测试与停用</h2><p>先测试一两款常用 App，再检查搜索、评论、播放、消息等正常功能，并分别在 Wi-Fi 和蜂窝观察。模块已导入不等于广告已经拦截成功。</p>
<p>需要回退时，在“配置 → 模块”关闭或移除“中文应用增强”；原节点和在线分流配置继续保留。若此前没有使用 HTTPS 解密，也可关闭其总开关。</p>
<details><summary>只启用单个 App</summary><p>不要同时启用总模块和同一 App 的独立模块。独立模块地址和测试状态保存在本次交付说明中。</p></details></section>
<small>私人入口，请勿转发。请在自己的设备上完成实际效果与正常功能检查。</small></main></body></html>'''.encode()
        return 200, 'text/html; charset=utf-8', content
    # No percent decoding, queries, fragments, traversal, arbitrary file serving.
    pieces = suffix.strip('/').split('/')
    if len(pieces) == 1:
        folder = root / 'current'; name = pieces[0]
    elif len(pieces) == 2 and re.fullmatch(r'\d{8}-r\d+', pieces[0]):
        folder = root / pieces[0]; name = pieces[1]
    else:
        return 404, 'text/plain', b''
    if not re.fullmatch(r'[A-Za-z0-9_.-]+\.(?:srmodule|js|json|list|txt)', name):
        return 404, 'text/plain', b''
    try:
        manifest = json.loads((folder / 'manifest.json').read_text())
        if name not in manifest['allowed_files']:
            return 404, 'text/plain', b''
        p = folder / name
        if p.is_symlink():
            return 404, 'text/plain', b''
        data = p.read_bytes()
        expected = manifest.get('hashes', {}).get(name)
        if expected is None or hashlib.sha256(data).hexdigest() != expected:
            return 503, 'text/plain', b''
        return 200, 'text/plain; charset=utf-8', data
    except (OSError, ValueError, KeyError):
        return 503, 'text/plain', b''

def serve(handler, config):
    result = payload(config, handler.path)
    if result is None:
        return False
    status, kind, data = result
    handler.send_response(status)
    handler.send_header('Content-Type', kind)
    handler.send_header('Content-Length', str(len(data)))
    handler.send_header('Cache-Control', 'no-store')
    handler.send_header('Referrer-Policy', 'no-referrer')
    handler.send_header('X-Content-Type-Options', 'nosniff')
    handler.send_header('Connection', 'close')
    if kind.startswith('text/html'):
        handler.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
    handler.end_headers()
    if handler.command != 'HEAD':
        handler.wfile.write(data)
    handler.close_connection = True
    return True
