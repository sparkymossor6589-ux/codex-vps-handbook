# Project provenance: local Codex-assisted maintenance/preview code.
# Scope and modifications: CONTRIBUTIONS.md and data/file-provenance.json.
# MIT applies only to rights held by project contributors; see LICENSE_SCOPE.md.
"""Historical Ubuntu/Linux x86_64 bootstrap, parameterized for a reader-reviewed upstream release.

Without --apply, only show an explanation. See src/README.md before using.
"""
import argparse
import os
import platform
import re
import textwrap

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Install on a new server; requires root')
    parser.add_argument('--server', help='Your own server address, stored only in the private client file')
    parser.add_argument('--version', help='Reviewed upstream Xray release version, without v prefix')
    parser.add_argument('--sha256', help='SHA-256 of the official Linux x86_64 release archive')
    parser.add_argument('--target', help='Your validated REALITY TLS target host:port')
    parser.add_argument('--server-name', help='A validated server name corresponding to the target')
    args = parser.parse_args()
    if not args.apply:
        print('Preview only: no downloads, files, users or services changed.')
        print('Supply your own reviewed version, checksum and REALITY target before --apply. Read src/README.md.')
        return
    if os.geteuid() != 0 or platform.system() != 'Linux' or platform.machine() != 'x86_64':
        raise SystemExit('Requires root on Linux x86_64; inspect this script before installation.')
    if not args.server or args.server.startswith('REPLACE_WITH_') or args.server.endswith('.invalid'):
        raise SystemExit('--server must be your own server address when applying.')
    if not args.version or not re.fullmatch(r'[0-9]+(?:\.[0-9]+){1,3}', args.version):
        raise SystemExit('--version must identify your reviewed official release.')
    if not args.sha256 or not re.fullmatch(r'[0-9a-fA-F]{64}', args.sha256):
        raise SystemExit('--sha256 must be the official archive checksum.')
    if not args.target or not args.server_name or ':' not in args.target:
        raise SystemExit('--target and --server-name must match your validated deployment.')
    import hashlib
    import json
    from pathlib import Path
    import pwd
    import secrets
    import subprocess
    import urllib.request
    import uuid
    import zipfile

    VERSION = args.version
    EXPECTED_SHA256 = args.sha256.lower()
    ROOT = Path('/opt/xray-' + VERSION)
    CONFIG_DIR = Path('/etc/xray-personal')
    CONFIG = CONFIG_DIR / 'config.json'
    UNIT = Path('/etc/systemd/system/xray-personal.service')
    CLIENT = Path('/home/ubuntu/vps-client.json')

    def run(args, **kwargs):
        return subprocess.run(args, check=True, text=True, capture_output=True, **kwargs)

    if CONFIG.exists() or UNIT.exists() or CLIENT.exists():
        raise SystemExit('Existing deployment found; no files overwritten.')

    archive = Path('/var/tmp/xray-' + VERSION + '-linux-64.zip')
    url = 'https://github.com/XTLS/Xray-core/releases/download/v' + VERSION + '/Xray-linux-64.zip'
    if not archive.exists() or hashlib.sha256(archive.read_bytes()).hexdigest() != EXPECTED_SHA256:
        urllib.request.urlretrieve(url, archive)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != EXPECTED_SHA256:
        raise SystemExit('Release checksum mismatch; installation stopped.')
    ROOT.mkdir(mode=0o755, exist_ok=True)
    with zipfile.ZipFile(archive) as bundle:
        (ROOT / 'xray').write_bytes(bundle.read('xray'))
    os.chmod(ROOT / 'xray', 0o755)
    print('Release archive SHA-256 verified.', flush=True)

    try:
        pwd.getpwnam('xray-personal')
    except KeyError:
        run(['useradd', '--system', '--user-group', '--home-dir', '/var/lib/xray-personal', '--shell', '/usr/sbin/nologin', 'xray-personal'])
    account = pwd.getpwnam('xray-personal')
    keylines = run([str(ROOT / 'xray'), 'x25519']).stdout.splitlines()
    keys = {line.split(':', 1)[0].replace(' ', '').lower(): line.split(':', 1)[1].strip() for line in keylines if ':' in line}
    private = keys.get('privatekey')
    public = keys.get('publickey') or keys.get('password(publickey)') or keys.get('password')
    if not private or not public:
        raise SystemExit('Unexpected key generator format; no configuration written.')
    client_id = str(uuid.uuid4())
    short_id = secrets.token_hex(8)
    config = {
        'log': {'loglevel': 'warning'},
        'inbounds': [{
            'tag': 'self-use-reality', 'listen': '0.0.0.0', 'port': 443,
            'protocol': 'vless',
            'settings': {'clients': [{'id': client_id, 'flow': 'xtls-rprx-vision'}], 'decryption': 'none'},
            'streamSettings': {
                'network': 'raw', 'security': 'reality',
                'realitySettings': {
                    'show': False, 'target': args.target, 'xver': 0,
                    'serverNames': [args.server_name], 'privateKey': private,
                    'shortIds': [short_id],
                    'limitFallbackUpload': {'afterBytes': 1048576, 'bytesPerSec': 65536, 'burstBytesPerSec': 131072},
                    'limitFallbackDownload': {'afterBytes': 1048576, 'bytesPerSec': 65536, 'burstBytesPerSec': 131072}
                }
            }
        }],
        'outbounds': [{'tag': 'direct', 'protocol': 'freedom'}, {'tag': 'block', 'protocol': 'blackhole'}],
        'routing': {'rules': [{
            'type': 'field',
            'ip': ['0.0.0.0/8', '10.0.0.0/8', '100.64.0.0/10', '127.0.0.0/8', '169.254.0.0/16', '172.16.0.0/12', '192.168.0.0/16', '224.0.0.0/4', '240.0.0.0/4', '::/128', '::1/128', 'fc00::/7', 'fe80::/10', 'ff00::/8'],
            'outboundTag': 'block'
        }]}
    }
    CONFIG_DIR.mkdir(mode=0o750, exist_ok=True)
    os.chown(CONFIG_DIR, 0, account.pw_gid)
    CONFIG.write_text(json.dumps(config, indent=2) + '\n')
    os.chmod(CONFIG, 0o640)
    os.chown(CONFIG, 0, account.pw_gid)
    try:
        run([str(ROOT / 'xray'), 'run', '-test', '-config', str(CONFIG)])
    except subprocess.CalledProcessError:
        raise SystemExit('Configuration validation failed; service was not installed.')

    unit = textwrap.dedent('''
    [Unit]
    Description=Personal VPS encrypted connection
    After=network-online.target
    Wants=network-online.target

    [Service]
    Type=simple
    User=xray-personal
    Group=xray-personal
    StateDirectory=xray-personal
    WorkingDirectory=/var/lib/xray-personal
    ExecStart=/opt/xray-__REVIEWED_VERSION__/xray run -config /etc/xray-personal/config.json
    Restart=on-failure
    RestartSec=5
    AmbientCapabilities=CAP_NET_BIND_SERVICE
    CapabilityBoundingSet=CAP_NET_BIND_SERVICE
    NoNewPrivileges=true
    PrivateTmp=true
    ProtectHome=true
    ProtectSystem=strict
    ProtectKernelTunables=true
    ProtectKernelModules=true
    ProtectControlGroups=true
    RestrictSUIDSGID=true
    LockPersonality=true
    LimitNOFILE=65535

    [Install]
    WantedBy=multi-user.target
    ''').replace('__REVIEWED_VERSION__', VERSION)
    UNIT.write_text(unit)
    os.chmod(UNIT, 0o644)
    run(['systemctl', 'daemon-reload'])
    run(['systemctl', 'enable', '--now', 'xray-personal.service'])
    client = {'server': args.server, 'port': 443, 'uuid': client_id,
              'public_key': public, 'short_id': short_id,
              'server_name': args.server_name, 'flow': 'xtls-rprx-vision',
              'fingerprint': 'chrome', 'version': VERSION}
    CLIENT.write_text(json.dumps(client, indent=2) + '\n')
    os.chmod(CLIENT, 0o600)
    owner = pwd.getpwnam('ubuntu')
    os.chown(CLIENT, owner.pw_uid, owner.pw_gid)
    print(run(['systemctl', 'is-active', 'xray-personal.service']).stdout.strip(), flush=True)
    print(run(['systemctl', 'show', 'xray-personal.service', '--property=MemoryCurrent', '--property=ActiveState', '--property=SubState']).stdout, flush=True)
    print('Client credentials saved privately; server private key stays on server.', flush=True)


if __name__ == '__main__':
    main()
