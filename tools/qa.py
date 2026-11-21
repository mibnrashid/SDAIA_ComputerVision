"""qa.py — static checks for the whole site. Run from the repo root:

    python tools/qa.py

Checks
  links     every relative href/src resolves to a file (and #fragment to an id)
  network   no http(s) in src=, href=, @import or url() except Colab/GitHub links
  leftover  no Applied-GenAI text left on student pages
  time      no "9:15" on any page
  arabic    no Arabic characters anywhere in the site
Exit code is non-zero if any check fails.
"""
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {'.git', 'content', 'tools', 'node_modules', '__pycache__'}
ALLOWED_HOSTS = ('colab.research.google.com', 'github.com', 'raw.githubusercontent.com')
# Library documentation links are allowed on the resources page only.
DOC_PAGES = {'resources/index.html'}


def site_files(exts):
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if f.lower().endswith(exts):
                yield os.path.join(dirpath, f)


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, '/')


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []      # (attr, value, line)
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k == 'id' and v:
                self.ids.add(v)
            if k == 'name' and tag == 'a' and v:
                self.ids.add(v)
            if k in ('href', 'src') and v is not None:
                self.refs.append((k, v, self.getpos()[0], tag))


_parsed = {}


def parse(path):
    if path not in _parsed:
        c = Collector()
        with open(path, encoding='utf-8') as fh:
            c.feed(fh.read())
        _parsed[path] = c
    return _parsed[path]


def check_links():
    errors = []
    for page in site_files(('.html',)):
        c = parse(page)
        for attr, val, line, tag in c.refs:
            if not val or val.startswith(('mailto:', 'javascript:', 'data:', 'tel:')):
                continue
            u = urlparse(val)
            if u.scheme in ('http', 'https'):
                continue                         # judged by check_network
            if '${' in val or "' +" in val:
                continue
            target = page if not u.path else os.path.normpath(
                os.path.join(os.path.dirname(page), unquote(u.path)))
            if u.path.endswith('/'):
                target = os.path.join(target, 'index.html')
            if not os.path.exists(target):
                errors.append(f'{rel(page)}:{line} broken {attr}="{val}"')
                continue
            if u.fragment and target.endswith('.html') and not u.fragment.isdigit():
                if u.fragment not in parse(target).ids:
                    errors.append(f'{rel(page)}:{line} missing #{u.fragment} in {rel(target)}')
    return errors


def check_network():
    errors = []
    pat_attr = re.compile(r'''\b(src|href)\s*=\s*["'](https?://[^"']+)''', re.I)
    pat_css = re.compile(r'''(@import\s+(?:url\()?["']?https?://[^"')\s]+|url\(\s*["']?https?://[^"')\s]+)''', re.I)
    for f in site_files(('.html', '.css', '.js')):
        text = open(f, encoding='utf-8').read()
        r = rel(f)
        for m in pat_attr.finditer(text):
            host = urlparse(m.group(2)).netloc
            tag_start = text.rfind('<', 0, m.start())
            tag = text[tag_start:tag_start + 8].lower()
            is_link = tag.startswith('<a ') or tag.startswith('<a\n')
            if m.group(1).lower() == 'src':
                errors.append(f'{r}: network src {m.group(2)}')
            elif not is_link:
                errors.append(f'{r}: network href on non-link {m.group(2)}')
            elif host.endswith(ALLOWED_HOSTS) or r in DOC_PAGES:
                pass
            else:
                errors.append(f'{r}: external link {m.group(2)} (only Colab/GitHub allowed here)')
        for m in pat_css.finditer(text):
            errors.append(f'{r}: network CSS {m.group(1)}')
    return errors


LEFTOVER = [r'Generative', r'\bRAG\b', r'Gemini', r'agai:', r'[Tt]okeniz']
# "token" is a real Day 3 term (ViT and VLM tokens), so it is only an error
# on pages that have nothing to do with Day 3 content.
TOKEN_OK = ('slides/day3.html', 'resources/', 'assessment/', 'notebooks/', 'activities/fool-the-model.html')


def check_leftover():
    errors = []
    for f in site_files(('.html', '.js', '.css')):
        r = rel(f)
        text = open(f, encoding='utf-8').read()
        for p in LEFTOVER:
            for m in re.finditer(p, text):
                line = text.count('\n', 0, m.start()) + 1
                errors.append(f'{r}:{line} leftover "{m.group(0)}"')
        if not r.startswith(TOKEN_OK):
            for m in re.finditer(r'\btokens?\b', text, re.I):
                line = text.count('\n', 0, m.start()) + 1
                errors.append(f'{r}:{line} leftover "{m.group(0)}"')
    return errors


def check_time():
    errors = []
    for f in site_files(('.html', '.js', '.json', '.ipynb')):
        text = open(f, encoding='utf-8').read()
        for m in re.finditer(r'(?<![\d.])9[:.]15(?!\d)', text):
            line = text.count('\n', 0, m.start()) + 1
            errors.append(f'{rel(f)}:{line} "9:15" on a student-facing file')
    return errors


def check_arabic():
    errors = []
    for f in site_files(('.html', '.js', '.css', '.json', '.ipynb', '.md', '.py')):
        text = open(f, encoding='utf-8').read()
        m = re.search(r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]', text)
        if m:
            line = text.count('\n', 0, m.start()) + 1
            errors.append(f'{rel(f)}:{line} Arabic character')
    return errors


CHECKS = {
    'links': check_links,
    'network': check_network,
    'leftover': check_leftover,
    'time': check_time,
    'arabic': check_arabic,
}


def main(argv):
    names = argv[1:] or list(CHECKS)
    failed = 0
    for n in names:
        errs = CHECKS[n]()
        status = 'PASS' if not errs else f'FAIL ({len(errs)})'
        print(f'[{status}] {n}')
        for e in errs[:60]:
            print('   ', e)
        failed += bool(errs)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
