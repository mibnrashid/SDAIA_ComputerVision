"""check_notebooks.py — acceptance checks for the 14 lab notebooks.

    python tools/check_notebooks.py

  * exactly 14 notebooks, each readable and valid with nbformat
  * every unsolved notebook contains "# TODO"; no solved notebook does
  * solved and unsolved have the same number of cells and differ only in
    TODO cells and extra-task answer cells
  * 3–5 TODO cells per lab, an "Extra tasks" section with 3–4 tasks,
    a "How to use" cell first and a GPU check second
  * cell order matches content/notebooks-spec.md (cell count and type per row)
"""
import os
import re
import sys

import nbformat

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nb import lab1a, lab1b, lab2a, lab2b, lab2c, lab3a, lab3b  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABS = [lab1a, lab1b, lab2a, lab2b, lab2c, lab3a, lab3b]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    errors = []
    files = sorted(f for f in os.listdir(os.path.join(ROOT, 'notebooks')) if f.endswith('.ipynb'))
    if len(files) != 14:
        errors.append(f'{len(files)} notebooks, expected 14')
    spec = open(os.path.join(ROOT, 'content', 'notebooks-spec.md'), encoding='utf-8').read()
    for lab in LABS:
        m = lab.META
        nbs = {}
        for kind in ('solved', 'unsolved'):
            path = os.path.join(ROOT, 'notebooks', f"{m['file']}_{kind}.ipynb")
            nb = nbformat.read(path, as_version=4)
            nbformat.validate(nb)
            nbs[kind] = nb
        text = {k: '\n'.join(c.source for c in nb.cells) for k, nb in nbs.items()}
        if '# TODO' not in text['unsolved']:
            errors.append(f"Lab {m['id']}: unsolved has no # TODO")
        if '# TODO' in text['solved']:
            errors.append(f"Lab {m['id']}: solved still contains # TODO")
        s, u = nbs['solved'].cells, nbs['unsolved'].cells
        if len(s) != len(u):
            errors.append(f"Lab {m['id']}: {len(s)} vs {len(u)} cells")
        for i, (a, b, c) in enumerate(zip(s, u, lab.CELLS), 1):
            if a.source != b.source and not (c.is_todo or c.extra):
                errors.append(f"Lab {m['id']} cell {i}: solved and unsolved differ outside a TODO/extra cell")
        todos = sum(c.is_todo for c in lab.CELLS)
        n_todo_lines = text['unsolved'].count('# TODO')
        if not 3 <= n_todo_lines <= 5:
            errors.append(f"Lab {m['id']}: {n_todo_lines} TODO lines (want 3–5)")
        extra_md = [c for c in lab.CELLS if c.kind == 'md' and c.src.startswith('## Extra tasks')]
        n_extra = len(re.findall(r'^\d\. ', extra_md[0].src, re.M)) if extra_md else 0
        if not 3 <= n_extra <= 4:
            errors.append(f"Lab {m['id']}: {n_extra} extra tasks (want 3–4)")
        if 'How to use this notebook' not in s[0].source or not any('GPU check' in c.source for c in s[1:3]):
            errors.append(f"Lab {m['id']}: How-to-use is not first or the GPU check is not in the first three cells")
        sec = spec.split(f"## Lab {m['id']} ·")[1].split('\n## ')[0]
        rows = re.findall(r'^\| (\d+) \| (markdown|code) \|', sec, re.M)
        kinds = [('markdown' if c.cell_type == 'markdown' else 'code') for c in s]
        if [r[1] for r in rows] != kinds or [int(r[0]) for r in rows] != list(range(1, len(s) + 1)):
            errors.append(f"Lab {m['id']}: spec rows do not match notebook cell order")
        print(f"Lab {m['id']}: {len(s)} cells · {todos} TODO cells ({n_todo_lines} TODO lines) · {n_extra} extra tasks · valid JSON")
    if errors:
        print('PROBLEMS:'); [print('  -', e) for e in errors]
        return 1
    print('ALL NOTEBOOK CHECKS PASS (14 notebooks)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
