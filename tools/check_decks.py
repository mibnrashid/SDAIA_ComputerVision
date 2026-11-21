"""check_decks.py — acceptance checks for the three HTML decks.

    python tools/check_decks.py [day ...] [--no-pdf]

For each day:
  1. counts `###` headings in content/slides-dayN.md and the Total line
  2. counts <section class="slide …"> in slides/dayN.html — fails on mismatch
  3. opens the deck headless with ?measure and reads the self-test report:
     slides still overflowing 1280x720 after auto-shrink, arrow keys,
     Home/End, notes toggle, print button
  4. prints the deck to PDF with Chrome and checks one page per slide
"""
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_check import chrome, file_url, run  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def md_counts(day):
    text = open(os.path.join(ROOT, 'content', f'slides-day{day}.md'), encoding='utf-8').read()
    heads = len(re.findall(r'^### ', text, re.M))
    total = int(re.search(r'^Total slides:\s*(\d+)', text, re.M).group(1))
    return heads, total


def html_count(day):
    text = open(os.path.join(ROOT, 'slides', f'day{day}.html'), encoding='utf-8').read()
    return len(re.findall(r'<section class="slide[ "]', text))


def pdf_pages(day):
    out = os.path.join(tempfile.mkdtemp(prefix='cvd-pdf-'), f'day{day}.pdf')
    profile = tempfile.mkdtemp(prefix='cvd-chrome-')
    cmd = [chrome(), '--headless=new', '--disable-gpu', '--no-first-run', f'--user-data-dir={profile}',
           '--no-pdf-header-footer', '--virtual-time-budget=6000', f'--print-to-pdf={out}',
           file_url(os.path.join(ROOT, 'slides', f'day{day}.html'))]
    subprocess.run(cmd, capture_output=True, timeout=300)
    data = open(out, 'rb').read()
    return len(re.findall(rb'/Type\s*/Page[^s]', data))


def main(argv):
    sys.stdout.reconfigure(encoding='utf-8')
    do_pdf = '--no-pdf' not in argv
    days = [int(a) for a in argv[1:] if a.isdigit()] or [1, 2, 3]
    bad = False
    for d in days:
        heads, total = md_counts(d)
        n = html_count(d)
        ok_count = heads == total == n
        print(f'Day {d}: md headings {heads} · Total line {total} · HTML .slide {n} · {"OK" if ok_count else "MISMATCH"}')
        bad |= not ok_count
        dom, console = run(os.path.join(ROOT, 'slides', f'day{d}.html'), '?measure', budget=8000)
        m = re.search(r'<pre id="measure-report">(.*?)</pre>', dom, re.S)
        if not m:
            print('   no measure report (deck.js failed?)', console[:3])
            bad = True
            continue
        rep = json.loads(m.group(1).replace('&quot;', '"').replace('&amp;', '&'))
        print(f'   live .slide elements {rep["slides"]} · overflowing {len(rep["overflow"])} {rep["overflow"]}')
        print(f'   auto-shrunk {len(rep["shrunk"])} slides')
        print(f'   keys {rep["keys"]} · notes {rep["notes"]} · print {rep["print"]}')
        if console:
            print('   console:', console[:3])
        checks = [rep['slides'] == total, not rep['overflow'], all(rep['keys'].values()),
                  all(rep['notes'].values()), rep['print']['button'], not console]
        if do_pdf:
            pages = pdf_pages(d)
            print(f'   PDF pages {pages} (one per slide: {"OK" if pages == total else "NO"})')
            checks.append(pages == total)
        bad |= not all(checks)
    print('ALL DECK CHECKS PASS' if not bad else 'DECK CHECKS FAILED')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
