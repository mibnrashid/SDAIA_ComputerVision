"""check_slides.py — validate content/slides-day{1,2,3}.md without changing them.

Checks, per file:
  * every `###` heading looks like `### D.NN · Title`
  * numbering is continuous from D.01 and the day prefix matches the file
  * every slide has exactly one Type, Screen and Notes line, in that order
  * Type is one of the known layouts
  * the "Total slides: N" line equals the real number of `###` headings

Prints the counts and exits non-zero on any problem.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPES = {'title', 'section', 'definition', 'compare', 'cards', 'rule', 'worked',
         'diagram', 'table', 'code', 'list', 'activity', 'quiz'}
EXPECTED = {1: 128, 2: 121, 3: 105}
HEAD = re.compile(r'^### (\d)\.(\d{2,3}) · (.+)$')


def check(day):
    path = os.path.join(ROOT, 'content', f'slides-day{day}.md')
    lines = open(path, encoding='utf-8').read().splitlines()
    problems = []
    slides = []
    cur = None
    total_line = None
    for i, line in enumerate(lines, 1):
        if line.startswith('### '):
            m = HEAD.match(line)
            if not m:
                problems.append(f'line {i}: malformed heading: {line}')
            cur = {'line': i, 'head': line, 'm': m, 'fields': []}
            slides.append(cur)
        elif line.startswith('## ') or line.strip() == '---':
            cur = None
        elif cur is not None:
            for key in ('Type', 'Screen', 'Notes'):
                if line.startswith(key + ':'):
                    cur['fields'].append((key, line[len(key) + 1:].strip()))
        if line.startswith('Total slides:'):
            total_line = int(re.findall(r'\d+', line)[0])

    for n, s in enumerate(slides, 1):
        keys = [k for k, _ in s['fields']]
        if keys != ['Type', 'Screen', 'Notes']:
            problems.append(f"line {s['line']}: fields {keys}, expected Type, Screen, Notes")
        if s['m']:
            d, num = int(s['m'].group(1)), int(s['m'].group(2))
            if d != day:
                problems.append(f"line {s['line']}: day prefix {d}, expected {day}")
            if num != n:
                problems.append(f"line {s['line']}: numbered {d}.{num:02d}, expected {day}.{n:02d}")
        t = dict(s['fields']).get('Type')
        if t and t not in TYPES:
            problems.append(f"line {s['line']}: unknown Type '{t}'")
        for k, v in s['fields']:
            if not v:
                problems.append(f"line {s['line']}: empty {k}")
        screen = dict(s['fields']).get('Screen', '')
        if '[STRETCH]' in screen or '(cut first)' in screen:
            problems.append(f"line {s['line']}: [STRETCH]/(cut first) on Screen")

    if total_line is None:
        problems.append('no "Total slides:" line')
    elif total_line != len(slides):
        problems.append(f'Total line says {total_line}, real count is {len(slides)}')
    return len(slides), total_line, problems


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    bad = False
    counts = []
    for day in (1, 2, 3):
        n, total, problems = check(day)
        counts.append(n)
        ok = not problems and n == total == EXPECTED[day]
        print(f'Day {day}: {n} slides · Total line {total} · expected {EXPECTED[day]} · {"OK" if ok else "PROBLEMS"}')
        for p in problems:
            print('   ', p)
        bad |= not ok
    print(' / '.join(map(str, counts)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
