"""browser_check.py — open every page from disk in headless Chrome and fail
on any console output (errors, failed loads, uncaught exceptions).

    python tools/browser_check.py                 # every page
    python tools/browser_check.py index.html ...  # just these

The site's own code never calls console.log, so any CONSOLE line in
Chrome's log is treated as a failure.
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANDIDATES = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
]


def chrome():
    for c in CANDIDATES:
        if os.path.exists(c):
            return c
    return None


def file_url(path, query=''):
    p = os.path.abspath(path).replace(os.sep, '/')
    return 'file:///' + p.lstrip('/') + query


def run(path, query='', budget=4000, size='1280,800'):
    """Return (dom, console_lines) for one page."""
    exe = chrome()
    if not exe:
        raise SystemExit('No Chrome/Edge found for the browser check.')
    profile = tempfile.mkdtemp(prefix='cvd-chrome-')
    cmd = [exe, '--headless=new', '--disable-gpu', '--no-first-run',
           '--no-default-browser-check', '--disable-extensions',
           '--allow-file-access-from-files',
           f'--user-data-dir={profile}', '--enable-logging=stderr', '--v=0',
           f'--window-size={size}', f'--virtual-time-budget={budget}',
           '--dump-dom', file_url(path, query)]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
    lines = [l for l in p.stderr.splitlines() if ':CONSOLE' in l]
    return p.stdout, lines


def pages():
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in {'.git', 'content', 'tools', 'node_modules'}]
        for f in filenames:
            if f.endswith('.html'):
                out.append(os.path.join(dirpath, f))
    return sorted(out)


def main(argv):
    targets = [os.path.join(ROOT, a) for a in argv[1:]] or pages()
    bad = 0
    for t in targets:
        _, lines = run(t)
        r = os.path.relpath(t, ROOT).replace(os.sep, '/')
        if lines:
            bad += 1
            print(f'[FAIL] {r}')
            for l in lines:
                print('     ', re.sub(r'^\[[^\]]*\]\s*', '', l)[:300])
        else:
            print(f'[ ok ] {r}')
    print(f'{len(targets) - bad}/{len(targets)} pages with zero console output')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
