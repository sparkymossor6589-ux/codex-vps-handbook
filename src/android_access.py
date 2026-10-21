# Project provenance: local Codex-assisted maintenance/preview code.
# Scope and modifications: CONTRIBUTIONS.md and data/file-provenance.json.
# MIT applies only to rights held by project contributors; see LICENSE_SCOPE.md.
"""Private Android setup and streamed downloads; no access to owner credentials."""
from pathlib import Path
from urllib.parse import quote, urlsplit
import hmac
import html
import json
import secrets


def setup_page(registry, account, nonce=''):
    base = registry['origin'] + '/a/' + account['token']
    profile = base + '/Tokyo-Android.yaml'
    parameters = quote(profile, safe='') + '&name=Tokyo-Android&update-interval=720'
    values = {'BASE': base, 'PROFILE': profile,
              'IMPORT': 'clashmeta://install-config?url=' + parameters,
              'FALLBACK': 'clash://install-config?url=' + parameters,
              'NONCE': nonce}
    page = Path(__file__).with_name('android_setup.html').read_text()
    for name, value in values.items():
        page = page.replace('{{' + name + '}}', html.escape(value, quote=True))
    return page.encode('utf-8')


def serve(handler, config):
    """Return False for unrelated/unauthorized paths; never join request paths."""
    # Browsers and messaging apps may add sharing parameters or a trailing
    # slash. Neither changes which bearer-protected resource is requested.
    parts = urlsplit(handler.path)
    request_path = parts.path.rstrip('/')
    if parts.scheme or parts.netloc or not request_path.startswith('/a/'):
        return False
    registry_path = config.get('android_registry')
    if not registry_path:
        return False
    try:
        registry = json.loads(Path(registry_path).read_text())
    except (OSError, ValueError):
        return False
    matched = None
    for friend in registry['friends']:
        if not friend.get('enabled'):
            continue
        bases = ['/a/' + token for token in [friend['token'], *friend.get('aliases', [])]]
        for suffix, kind in [('', 'setup'), ('/setup', 'setup'), ('/Tokyo-Android.yaml', 'profile'), ('/client.apk', 'installer')]:
            if any(hmac.compare_digest(request_path.encode('utf-8'), (base + suffix).encode('utf-8')) for base in bases):
                matched = friend, kind
    if matched is None:
        return False
    friend, kind = matched
    stream = None
    if kind == 'setup':
        nonce = secrets.token_urlsafe(18)
        payload = setup_page(registry, friend, nonce)
        size = len(payload)
        content_type = 'text/html; charset=utf-8'
    else:
        root = Path(registry['root'])
        path = root / friend['id'] / 'Tokyo-Android.yaml' if kind == 'profile' else root / 'assets' / registry['installer']
        try:
            stream = path.open('rb')
            size = path.stat().st_size
        except OSError:
            if stream:
                stream.close()
            handler.send_response(503)
            handler.send_header('Content-Length', '0')
            handler.send_header('Connection', 'close')
            handler.end_headers()
            handler.close_connection = True
            return True
        content_type = 'application/yaml; charset=utf-8' if kind == 'profile' else 'application/vnd.android.package-archive'
    try:
        handler.send_response(200)
        handler.send_header('Content-Type', content_type)
        handler.send_header('Content-Length', str(size))
        handler.send_header('Cache-Control', 'no-store')
        handler.send_header('Referrer-Policy', 'no-referrer')
        handler.send_header('X-Content-Type-Options', 'nosniff')
        handler.send_header('Connection', 'close')
        if kind == 'setup':
            handler.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-" + nonce + "'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        elif kind == 'profile':
            handler.send_header('Content-Disposition', 'attachment; filename="Tokyo-Android.yaml"')
            handler.send_header('profile-update-interval', '12')
            handler.send_header('profile-web-page-url', registry['origin'] + '/a/' + friend['token'] + '/setup')
        else:
            handler.send_header('Content-Disposition', 'attachment; filename="' + registry['installer'] + '"')
        handler.end_headers()
        if handler.command != 'HEAD':
            if stream:
                while chunk := stream.read(64 * 1024):
                    handler.wfile.write(chunk)
            else:
                handler.wfile.write(payload)
    finally:
        if stream:
            stream.close()
        handler.close_connection = True
    return True
