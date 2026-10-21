#!/usr/bin/env python3
# Project provenance: local Codex-assisted maintenance/preview code.
# Scope and modifications: CONTRIBUTIONS.md and data/file-provenance.json.
# MIT applies only to rights held by project contributors; see LICENSE_SCOPE.md.
"""Basic public-export check. Never prints matched secret values.

This is a conservative supplement to manual review, not a complete secret scanner.
"""
import argparse
import ast
import ipaddress
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

BLOCKED_SUFFIXES = {'.pem', '.key', '.p12', '.pfx', '.mobileconfig', '.db', '.sqlite', '.sqlite3', '.apk', '.zip', '.png', '.jpg', '.jpeg', '.webp', '.log', '.pyc'}
BLOCKED_DIRS = {'.git', 'private', 'secrets', 'backups', '__pycache__'}
PATTERNS = {
    'private-key-block': re.compile(r'-----BEGIN (?:OPENSSH |RSA |EC |ENCRYPTED )?PRIVATE KEY-----'),
    'aws-access-id': re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'github-access-token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b'),
    'personal-home-path': re.compile(r'/(?:Users|home)/[^/\s"\']+/'),
}

def check(root):
    findings = []
    files = sorted(p for p in root.rglob('*') if p.is_file() or p.is_symlink())
    for p in files:
        rel = p.relative_to(root)
        def add(kind):
            findings.append({'file': str(rel), 'kind': kind})
        if p.is_symlink():
            add('symlink-needs-review'); continue
        if any(x in BLOCKED_DIRS for x in rel.parts) or p.suffix.lower() in BLOCKED_SUFFIXES:
            add('non-public-file-type'); continue
        try:
            text = p.read_text(encoding='utf-8')
        except (UnicodeError, OSError):
            add('unreadable-or-binary'); continue
        for kind, pattern in PATTERNS.items():
            if pattern.search(text):
                # Historical server paths use the generic ubuntu account.
                if kind == 'personal-home-path' and not any(x != '/home/ubuntu/' for x in pattern.findall(text)):
                    continue
                add(kind)
        for value in re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text):
            try:
                address = ipaddress.ip_address(value)
            except ValueError:
                continue
            # Public resolvers can occur in source/docs; deployment IPs need review.
            if address.is_global and not address.is_multicast and not address.is_reserved and value not in {'1.1.1.1','8.8.8.8','8.8.4.4','223.5.5.5','119.29.29.29'}:
                add('public-ip-needs-review'); break
        if p.suffix == '.py':
            try:
                ast.parse(text, filename=str(rel))
            except SyntaxError:
                add('python-syntax')
        if p.suffix == '.md':
            for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', text):
                target = target.strip().split(' "', 1)[0]
                if urlsplit(target).scheme or target.startswith('#'):
                    continue
                local = unquote(target.split('#', 1)[0])
                candidate = (p.parent / local).resolve()
                if not candidate.is_relative_to(root.resolve()) or not candidate.exists():
                    add('broken-or-outside-local-link')
        if p.suffix == '.json' or p.name.endswith('.json.example'):
            try:
                json.loads(text)
            except ValueError:
                add('json-syntax')
    return {'files_checked': len(files), 'findings': findings,
            'limitations': 'Patterns only; no live-secret baseline, entropy scan, image inspection or history audit.'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', nargs='?', default='.')
    args = parser.parse_args()
    result = check(Path(args.directory).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(bool(result['findings']))
