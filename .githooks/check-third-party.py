#!/usr/bin/env python3
"""Policy check: no vendored third-party libraries and no third-party requests from the built site.

usage: check-third-party.py <built-site-dir> [--source-only | --site-only]

1. Source tree: fails on vendored libraries (assets/plugins, vendor/, node_modules/, *.min.js, *.min.css).
2. Built site: fails on any script, stylesheet, font, image, media, frame or form target that is not same-origin
   (relative URLs, the site's own host, data: URIs); mailto:, tel: and plain <a href> links are allowed.
Works offline; it only reads files.
"""
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
LOADING_RELS = {'stylesheet', 'preload', 'prefetch', 'modulepreload', 'icon', 'shortcut', 'apple-touch-icon',
                'manifest', 'mask-icon', 'preconnect', 'dns-prefetch'}
VENDORED = re.compile(r'(^|/)(assets/plugins|vendor|node_modules)(/|$)|\.min\.(js|css)$')
URL_IN_CSS = re.compile(r'url\(\s*[\'"]?([^\'")\s]+)|@import\s+[\'"]([^\'"]+)')


def own_hosts():
    hosts = set()
    config = ROOT / '_config.yml'
    if config.exists():
        for line in config.read_text().splitlines():
            m = re.match(r'^url:\s*[\'"]?(\S+?)[\'"]?\s*$', line)
            if m:
                hosts.add(urlparse(m.group(1)).hostname)
    return hosts


def is_external(url, hosts):
    url = url.strip()
    if not url or url.startswith(('#', 'data:', 'mailto:', 'tel:', 'about:')):
        return False
    parsed = urlparse(url if '://' in url or url.startswith('//') else 'x:' + url)
    if '://' not in url and not url.startswith('//'):
        return False  # relative URL
    return parsed.hostname not in hosts


class Finder(HTMLParser):
    def __init__(self, hosts):
        super().__init__()
        self.hosts, self.found = hosts, []

    def add(self, tag, attr, url):
        if is_external(url, self.hosts):
            self.found.append(f'<{tag} {attr}="{url}">')

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script', 'iframe', 'embed', 'img', 'source', 'video', 'audio', 'track', 'frame', 'input'):
            self.add(tag, 'src', a.get('src') or '')
        if tag == 'object':
            self.add(tag, 'data', a.get('data') or '')
        if tag in ('img', 'source'):
            for part in (a.get('srcset') or '').split(','):
                self.add(tag, 'srcset', part.strip().split(' ')[0])
        if tag == 'video':
            self.add(tag, 'poster', a.get('poster') or '')
        if tag == 'form':
            self.add(tag, 'action', a.get('action') or '')
        if tag == 'link' and LOADING_RELS & set((a.get('rel') or '').lower().split()):
            self.add(tag, 'href', a.get('href') or '')


def check_source():
    files = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout.splitlines()
    return [f'vendored third-party file in the source tree: {f}' for f in files if VENDORED.search(f)]


def check_site(site):
    hosts, problems = own_hosts(), []
    for path in sorted(site.rglob('*')):
        rel = path.relative_to(site)
        if path.suffix == '.html':
            finder = Finder(hosts)
            finder.feed(path.read_text(errors='replace'))
            problems += [f'{rel}: external {item}' for item in finder.found]
        elif path.suffix == '.css':
            for m in URL_IN_CSS.finditer(path.read_text(errors='replace')):
                url = m.group(1) or m.group(2)
                if is_external(url, hosts):
                    problems.append(f'{rel}: external url({url})')
        elif path.suffix == '.js' and re.search(r'https?://', path.read_text(errors='replace')):
            problems.append(f'{rel}: script mentions an absolute URL; check that it is not loaded')
    return problems


def main(argv):
    mode = next((a for a in argv if a.startswith('--')), '')
    dirs = [a for a in argv if not a.startswith('--')]
    problems = []
    if mode != '--site-only':
        problems += check_source()
    if mode != '--source-only':
        if not dirs:
            sys.exit('usage: check-third-party.py <built-site-dir> [--source-only | --site-only]')
        problems += check_site(Path(dirs[0]))
    for p in problems:
        print(f'third-party policy: {p}', file=sys.stderr)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
