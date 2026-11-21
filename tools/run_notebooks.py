"""run_notebooks.py — execute notebooks headless (CPU, FAST mode) and report.

    <python-with-torch> tools/run_notebooks.py Lab_1A_solved [Lab_2A_solved ...] [--skip-extra]

Runs each notebook in a scratch folder with CVD_FAST=1, continues past errors,
and prints: cells that raised, check cells that printed ❌ (a failure in a
solved notebook), and how long it took. Exit code 1 if anything failed.
"""
import os
import sys
import tempfile
import time

import nbformat
from nbclient import NotebookClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(name, skip_extra=False):
    path = os.path.join(ROOT, 'notebooks', name + '.ipynb')
    nb = nbformat.read(path, as_version=4)
    if skip_extra:
        cut = next((i for i, c in enumerate(nb.cells) if c.cell_type == 'markdown' and c.source.startswith('## Extra tasks')), None)
        if cut is not None:
            nb.cells = nb.cells[:cut]
    work = tempfile.mkdtemp(prefix='cvd-nb-')
    os.environ['CVD_FAST'] = '1'
    os.environ.setdefault('MPLBACKEND', 'Agg')
    client = NotebookClient(nb, timeout=1800, kernel_name='python3', allow_errors=True,
                            resources={'metadata': {'path': work}})
    t0 = time.time()
    client.execute()
    errors, fails = [], []
    for i, c in enumerate(nb.cells, 1):
        if c.cell_type != 'code':
            continue
        for o in c.get('outputs', []):
            if o.output_type == 'error':
                errors.append((i, o.ename, o.evalue[:300]))
            text = o.get('text', '') if o.output_type == 'stream' else ''
            if '❌' in text:
                fails.append((i, text.strip()[:200]))
    print(f'== {name}: {time.time() - t0:.0f}s · {len(errors)} errors · {len(fails)} failed checks')
    for e in errors:
        print('   ERROR cell', e)
    for f in fails:
        print('   CHECK cell', f)
    out = os.path.join(tempfile.gettempdir(), f'executed-{name}.ipynb')
    nbformat.write(nb, out)
    return not errors and not fails


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    names = [a for a in sys.argv[1:] if not a.startswith('--')]
    ok = all([run(n, '--skip-extra' in sys.argv) for n in names])
    sys.exit(0 if ok else 1)
