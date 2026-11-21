"""snap.py — screenshot deck slides into a contact sheet for visual review.

    python tools/snap.py <day> <n> [<n> ...] --out sheet.png
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_check import chrome, file_url  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def shot(page, frag, out, size='1280,800'):
    profile = tempfile.mkdtemp(prefix='cvd-snap-')
    subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--user-data-dir={profile}',
                    f'--window-size={size}', '--virtual-time-budget=3000', f'--screenshot={out}',
                    file_url(page) + frag], capture_output=True, timeout=120)


def main(argv):
    from PIL import Image
    out = argv[argv.index('--out') + 1]
    args = [a for a in argv[1:argv.index('--out')]]
    day, nums = args[0], args[1:]
    tmp = tempfile.mkdtemp(prefix='cvd-shots-')
    imgs = []
    for n in nums:
        p = os.path.join(tmp, f'{n}.png')
        shot(os.path.join(ROOT, 'slides', f'day{day}.html'), f'#{n}', p)
        imgs.append(Image.open(p).convert('RGB'))
    cols = 2
    w, h = 640, 400
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * w, rows * h), 'white')
    for k, im in enumerate(imgs):
        sheet.paste(im.resize((w, h)), ((k % cols) * w, (k // cols) * h))
    sheet.save(out)
    print(out)


if __name__ == '__main__':
    main(sys.argv)
