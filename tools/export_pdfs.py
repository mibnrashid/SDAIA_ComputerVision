"""export_pdfs.py — print the three decks to slides_pdf/ (one slide per page, no notes).

    python tools/export_pdfs.py          # all three days
    python tools/export_pdfs.py 2        # one day

Uses headless Chrome, the same print path as the deck's "Print to PDF" button.
Re-run after rebuilding the decks so the PDFs match the HTML.
"""
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_check import chrome, file_url  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'slides_pdf')
NAMES = {
    1: 'Day1_From_pixels_to_features.pdf',
    2: 'Day2_Detection_segmentation_tracking.pdf',
    3: 'Day3_Seeing_beyond_labels.pdf',
}


def export(day):
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, NAMES[day])
    profile = tempfile.mkdtemp(prefix='cvd-pdf-')
    subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--no-first-run', f'--user-data-dir={profile}',
                    '--no-pdf-header-footer', '--virtual-time-budget=8000', f'--print-to-pdf={out}',
                    file_url(os.path.join(ROOT, 'slides', f'day{day}.html'))], capture_output=True, timeout=300)
    data = open(out, 'rb').read()
    pages = len(re.findall(rb'/Type\s*/Page[^s]', data))
    slides = len(re.findall(r'<section class="slide[ "]',
                            open(os.path.join(ROOT, 'slides', f'day{day}.html'), encoding='utf-8').read()))
    status = 'OK' if pages == slides else 'MISMATCH'
    print(f'slides_pdf/{NAMES[day]}: {pages} pages for {slides} slides · {len(data) / 1e6:.1f} MB · {status}')
    return pages == slides


if __name__ == '__main__':
    days = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    sys.exit(0 if all([export(d) for d in days]) else 1)
