"""build_decks.py — render content/slides-dayN.md into slides/dayN.html.

    python tools/build_decks.py          # all three days
    python tools/build_decks.py 2        # one day

One `###` heading = one <section class="slide">. The Type line picks the
layout; Screen is the visible text (split on " · " and " | "); Notes go to
the presenter-notes panel. [STRETCH] and (cut first) are stripped from
anything visible and kept in the notes. The output is plain static HTML on
the shared deck engine (assets/deck.js + deck.css + cv-deck.css).
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diagrams import CUSTOM, flow_svg  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TITLES = {1: 'From pixels to features',
          2: 'Where is it, what shape is it, where is it going?',
          3: 'Seeing beyond labels'}
DATES = {1: 'Sunday 22 November 2026', 2: 'Monday 23 November 2026', 3: 'Tuesday 24 November 2026'}

ACTIVITY_LINKS = {
    'This or That': ('../activities/index.html', 'Icebreaker'),
    'Pixel Detective': ('../activities/pixel-detective.html', 'Activity'),
    'Be the Kernel': ('../activities/be-the-kernel.html', 'Activity'),
    'Shape Race': ('../activities/shape-race.html', 'Activity'),
    'Spot the Bug': ('../activities/spot-the-bug.html', 'Activity'),
    'IoU Darts': ('../activities/iou-darts.html', 'Activity'),
    'Be NMS': ('../activities/be-nms.html', 'Activity'),
    'Threshold Tycoon': ('../activities/threshold-tycoon.html', 'Activity'),
    'Zero-Shot Showdown': ('../activities/zero-shot-showdown.html', 'Activity'),
    'Fool the Model': ('../activities/fool-the-model.html', 'Activity'),
    'pre-test': ('../assessment/pretest.html', 'Pre-test'),
    'Post-test': ('../assessment/posttest.html', 'Post-test'),
}

LABEL_RE = re.compile(r'^(Act|Day|Stage|Step|Lab|Layer|Position|Route) \d+$')


# ---------------------------------------------------------------- parsing

def parse(day):
    text = open(os.path.join(ROOT, 'content', f'slides-day{day}.md'), encoding='utf-8').read()
    slides, section = [], ''
    cur = None
    for line in text.splitlines():
        if line.startswith('## '):
            section = line[3:].strip()
            cur = None
        elif line.startswith('### '):
            m = re.match(r'### (\d+\.\d+) · (.+)', line)
            cur = {'id': m.group(1), 'title': m.group(2).strip(), 'section': section}
            slides.append(cur)
        elif cur is not None:
            for k in ('Type', 'Screen', 'Notes'):
                if line.startswith(k + ':'):
                    cur[k.lower()] = line[len(k) + 1:].strip()
    return slides


def visible(s):
    """Strip presenter-only tags from anything that appears on screen."""
    s = s.replace('[STRETCH]', '').replace('(cut first)', '')
    return re.sub(r'\s{2,}', ' ', s).strip()


def esc(s):
    return html.escape(s, quote=False)


def fmt(s):
    """Escape, then turn `code` into <code>."""
    s = esc(visible(s))
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', s)


NUM_RE = re.compile(r'(?<![\w.₀-₉/])([−-]?\d[\d,]*(?:\.\d+)?%?)(?![\w])')


def emph_numbers(s):
    out, pos = [], 0
    # do not touch numbers inside <code>…</code>
    for m in re.finditer(r'<code>.*?</code>', s):
        out.append(NUM_RE.sub(r'<b class="num">\1</b>', s[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(NUM_RE.sub(r'<b class="num">\1</b>', s[pos:]))
    return ''.join(out)


def dots(s):
    return [p.strip() for p in s.split(' · ') if p.strip()]


def bars(s):
    return [p.strip() for p in s.split(' | ') if p.strip()]


def starts_soft(s):
    return bool(s) and (s[0].islower() or s[0] in '"“(`[√⌊')


def group(segs):
    """Pair short heads with the lowercase descriptions that follow them."""
    items, i = [], 0
    while i < len(segs):
        s = segs[i]
        if (re.fullmatch(r'\d{1,2}', s) or LABEL_RE.match(s)) and i + 1 < len(segs):
            items.append({'num': s, 'head': segs[i + 1], 'body': []})
            i += 2
            continue
        if items:
            prev = items[-1]
            short = len(prev['head'].split()) <= 4 and not prev['head'].endswith('.')
            if starts_soft(s) and (short or prev['body']):
                prev['body'].append(s)
                i += 1
                continue
            if s[0].isdigit() and not prev['body'] and short and not re.fullmatch(r'[\d.,%]+', prev['head']) \
                    and prev['num'] is None:
                prev['body'].append(s)
                i += 1
                continue
        items.append({'num': None, 'head': s, 'body': []})
        i += 1
    for it in items:
        if not it['body'] and ' — ' in it['head']:
            h, b = it['head'].split(' — ', 1)
            it['head'], it['body'], it['dash'] = h, [b], True
    return items


def blist(segs, cls='blist'):
    return f'<ul class="{cls}">' + ''.join(f'<li>{fmt(s)}</li>' for s in segs) + '</ul>'


def joined(it):
    """Rebuild the original text of an item (head + body)."""
    return (' — ' if it.get('dash') else ' · ').join([it['head']] + it['body'])


def item_html(it):
    body = ' · '.join(it['body'])
    if body:
        return f'<b>{fmt(it["head"])}</b> — {fmt(body)}'
    return fmt(it['head'])


# ---------------------------------------------------------------- layouts

def head_block(s, eyebrow=None):
    eb = eyebrow if eyebrow is not None else visible(s['section_label'])
    return f'<p class="slide__eyebrow">{esc(eb)}</p><h2>{fmt(s["title"])}</h2>'


def lay_title(s, day):
    segs = dots(s['screen'])
    if segs[0].isupper():
        eyebrow, rest = segs[0].title().replace('Sdaia', 'SDAIA'), segs[1:]
    else:
        eyebrow = s['title'] if s['title'] != segs[0] else 'SDAIA Academy · Computer Vision for Developers'
        rest = segs
    h2, kick = rest[0], rest[1:]
    out = f'<p class="slide__eyebrow">{esc(visible(eyebrow))}</p><h2>{fmt(h2)}</h2>'
    if kick:
        out += f'<p class="slide__kicker">{" · ".join(fmt(k) for k in kick)}</p>'
    return out


def lay_section(s, day):
    segs = dots(s['screen'])
    badge = ''
    segs2 = []
    for x in segs:
        if x.lower().startswith('badge:'):
            badge = f'<span class="badge-home">{esc(x.split(":", 1)[1].strip())}</span>'
        else:
            segs2.append(x)
    out = ''
    if re.fullmatch(r'\d{1,2}', segs2[0]):
        out += f'<p class="sec-num">{segs2[0]}</p>'
        segs2 = segs2[1:]
    out += f'<h2>{fmt(segs2[0])}</h2>'
    if segs2[1:]:
        out += f'<p class="slide__kicker">{" · ".join(fmt(k) for k in segs2[1:])}</p>'
    return out + badge


def lay_definition(s, day):
    segs = dots(s['screen'])
    first = fmt(segs[0])
    if ' — ' in first:
        t, d = first.split(' — ', 1)
        first = f'<strong>{t}</strong> — {d}'
    out = head_block(s) + f'<div class="defbox">{first}</div>'
    if segs[1:]:
        items = group(segs[1:])
        out += '<ul class="blist">' + ''.join(f'<li>{item_html(it)}</li>' for it in items) + '</ul>'
    return out


def lay_compare(s, day):
    cols = bars(s['screen'])
    callout = []
    if len(cols) == 1:
        segs = dots(cols[0])
        cols_segs = [[segs[0]], [segs[1]]]
        callout = segs[2:]
    else:
        cols_segs = [dots(c) for c in cols]
        last = cols_segs[-1]
        seen_soft, cut = False, None
        for j, x in enumerate(last[1:], 1):
            if starts_soft(x) or x[0].isdigit() or x[0] in '(=':
                seen_soft = True
            elif seen_soft or j >= 2:
                cut = j
                break
        if cut:
            callout = last[cut:]
            cols_segs[-1] = last[:cut]
    n = len(cols_segs)
    out = head_block(s) + f'<div class="cmp cmp--{min(n, 3)}">'
    for c in cols_segs:
        out += f'<div class="cmp__col"><h3>{fmt(c[0])}</h3>'
        if c[1:]:
            out += blist(c[1:])
        out += '</div>'
    out += '</div>'
    if callout:
        out += f'<p class="callout">{" · ".join(fmt(x) for x in callout)}</p>'
    return out


def lay_cards(s, day):
    items = group(dots(s['screen']))
    n = len(items)
    avg = sum(len(it['head']) + len(' '.join(it['body'])) for it in items) / max(n, 1)
    if n <= 3:
        cols = n
    elif n == 4:
        cols = 4 if avg < 45 else 2
    elif n in (5, 6):
        cols = 3
    else:
        cols = 4
    out = head_block(s) + f'<div class="cards cards--{cols}">'
    for k, it in enumerate(items, 1):
        num = it['num'] or f'{k:02d}'
        out += (f'<div class="card-n"><span class="card-n__num">{esc(num)}</span>'
                f'<span class="card-n__head">{fmt(it["head"])}</span>')
        if it['body']:
            out += f'<span class="card-n__body">{" · ".join(fmt(b) for b in it["body"])}</span>'
        out += '</div>'
    return out + '</div>'


def lay_rule(s, day):
    segs = dots(s['screen'])
    out = f'<p class="slide__eyebrow">{esc(visible(s["section_label"]))} · {fmt(s["title"])}</p>'
    out += f'<p class="rule-text">{fmt(segs[0])}</p>'
    if segs[1:]:
        out += f'<p class="rule-sub">{" · ".join(fmt(x) for x in segs[1:])}</p>'
    return out


def lay_worked(s, day):
    segs = []
    for x in dots(s['screen']):
        # very short pieces ("B 0.90", "dog 1.0") belong on the line before them
        if segs and len(x) <= 10 and not segs[-1].endswith(('.', ':')):
            segs[-1] += ' · ' + x
        else:
            segs.append(x)
    out = head_block(s, 'Worked example') + '<ol class="steps-w">'
    out += ''.join(f'<li><span>{emph_numbers(fmt(x))}</span></li>' for x in segs)
    return out + '</ol>'


def parse_flow(screen):
    """Split a Screen line with arrows into flow nodes and loose notes."""
    if ' · → ' in screen:                     # one root, several branches
        parts = screen.split(' · → ')
        first = [p.strip() for p in parts[0].split(' → ')]
        branches = [first[1:]] + [[q.strip() for q in p.split(' → ')] for p in parts[1:]]
        return {'kind': 'branch', 'root': first[0], 'branches': branches}, []
    chunks = [dots(c) for c in screen.split(' → ')]
    nodes, notes = [], []
    pattern2 = all(len(c) == 2 for c in chunks[:-1]) and len(chunks) > 2
    for k, c in enumerate(chunks):
        last = k == len(chunks) - 1
        if last:
            take = 2 if (pattern2 and len(c) >= 2) else 1
            node, notes = c[:take], c[take:]
        else:
            node = c
        if len(node) == 2 and starts_soft(node[1]):
            nodes.append({'title': node[0], 'sub': node[1]})
        elif len(node) == 1:
            nodes.append({'title': node[0], 'sub': ''})
        else:
            items = group(node)
            nodes.append({'stack': [(it['head'], ' · '.join(it['body'])) for it in items]})
    return {'kind': 'flow', 'nodes': nodes}, notes


def lay_diagram(s, day):
    segs = dots(s['screen'])
    if s['id'] in CUSTOM:
        svg = CUSTOM[s['id']](s['id'])
        segs = [re.sub(r'^→\s*', '', x) for x in segs]
        return head_block(s) + f'<div class="dgm dgm--side">{svg}{blist(segs)}</div>'
    spec, notes = parse_flow(s['screen'])
    svg = flow_svg(spec, s['id'], fmt_plain=lambda x: esc(visible(x)))
    out = head_block(s) + f'<div class="dgm">{svg}'
    if notes:
        out += blist(notes)
    return out + '</div>'


def lay_table(s, day):
    rows = [dots(r) for r in bars(s['screen'])]
    out = head_block(s)
    if all(len(r) == 1 for r in rows) or (all(' vs ' in r[0] for r in rows)):
        out += '<div class="vs-grid">'
        for r in rows:
            if ' vs ' in r[0]:
                a, b = r[0].split(' vs ', 1)
                extra = f'<small>{fmt(" · ".join(r[1:]))}</small>' if r[1:] else ''
                out += (f'<div class="vs-row"><span>{fmt(a)}</span><span class="vs">vs</span>'
                        f'<span class="r">{fmt(b)}</span>{extra}</div>')
            else:
                out += f'<div class="vs-row"><span>{fmt(" · ".join(r))}</span></div>'
        return out + '</div>'
    width = max(len(r) for r in rows)
    out += '<table><tbody>'
    for r in rows:
        cells = r + [''] * (width - len(r))
        out += '<tr>' + ''.join(f'<td>{fmt(c)}</td>' for c in cells) + '</tr>'
    return out + '</tbody></table>'


PY_KW = r'\b(for|in|if|else|return|def|import|from|as|with|not|and|or|None|True|False|while|lambda)\b'


def highlight(code):
    code = esc(code)
    toks = []

    def keep(m, cls):
        toks.append(f'<span class="{cls}">{m.group(0)}</span>')
        return f'\x00{len(toks) - 1}\x00'
    code = re.sub(r'#.*$', lambda m: keep(m, 'c'), code)
    code = re.sub(r'(&quot;|"|\')[^"\']*\1', lambda m: keep(m, 's'), code)
    code = re.sub(PY_KW, lambda m: keep(m, 'k'), code)
    code = re.sub(r'\b[a-zA-Z_][\w.]*(?=\()', lambda m: keep(m, 'f'), code)
    code = re.sub(r'(?<![\w\x00])\d+(?:\.\d+)?', lambda m: keep(m, 'n'), code)
    return re.sub(r'\x00(\d+)\x00', lambda m: toks[int(m.group(1))], code)


def lay_code(s, day):
    segs = dots(s['screen'])
    lines, caption = [], []
    for x in segs:
        x = visible(x)
        m = re.match(r'^`([^`]+)`\s*(.*)$', x)
        if m:
            tail = m.group(2).strip()
            tail = re.sub(r'^[—-]\s*', '', tail)
            lines.append((m.group(1), tail))
        else:
            caption.append(x)
    width = max(len(c) for c, _ in lines) if lines else 0
    code = '\n'.join(highlight(c) + (' ' * (width - len(c) + 2) + f'<span class="c"># {esc(t)}</span>' if t else '')
                     for c, t in lines)
    out = head_block(s) + f'<pre><code>{code}</code></pre>'
    if caption:
        out += f'<p class="callout">{" · ".join(fmt(c) for c in caption)}</p>'
    return out


def lay_list(s, day):
    items = group(dots(s['screen']))
    cls = 'olist olist--cols' if len(items) > 7 else 'olist'
    out = head_block(s) + f'<ul class="{cls}">'
    for it in items:
        if it['num']:
            out += f'<li><b>{esc(it["num"])}</b><span>{fmt(joined(it))}</span></li>'
        elif it['body']:
            out += f'<li><b>{fmt(it["head"])}</b><span>{fmt(" · ".join(it["body"]))}</span></li>'
        else:
            out += f'<li><span></span><span>{fmt(it["head"])}</span></li>'
    return out + '</ul>'


def lay_activity(s, day):
    segs = dots(s['screen'])
    name, label = None, 'Activity'
    for key in ACTIVITY_LINKS:
        if key in s['title'] or key in s['screen']:
            name = key
            break
    href, label = ACTIVITY_LINKS.get(name, ('../activities/index.html', 'Activity'))
    rest = [x for x in segs if x not in ('Activity', name)]
    out = f'<p class="slide__eyebrow">{esc(visible(s["section_label"]))}</p><h2>{fmt(s["title"])}</h2>'
    out += f'<div class="act-card"><span class="act-label">{esc(label)}</span>'
    if name and name in segs:
        out += f'<h3>{esc(name)}</h3>'
    out += blist(rest, 'act-list') if rest else ''
    out += f'<a class="act-go" href="{href}">Open {esc(name or "activities")} →</a></div>'
    return out


def lay_quiz(s, day):
    items = group(dots(s['screen']))
    out = head_block(s, 'Quick check') + '<ol class="quiz">'
    out += ''.join(f'<li><span>{fmt(joined(it))}</span></li>' for it in items)
    return out + '</ol>'


LAYOUTS = {
    'title': lay_title, 'section': lay_section, 'definition': lay_definition,
    'compare': lay_compare, 'cards': lay_cards, 'rule': lay_rule, 'worked': lay_worked,
    'diagram': lay_diagram, 'table': lay_table, 'code': lay_code, 'list': lay_list,
    'activity': lay_activity, 'quiz': lay_quiz,
}
CLASS = {'title': 'slide--title', 'section': 'slide--section', 'rule': 'slide--rule'}


# ---------------------------------------------------------------- page

def section_label(sec):
    sec = visible(sec)
    return sec


def notes_html(s):
    meta = f'<p class="notes__meta">{esc(s["id"])} · {esc(s["type"])}</p>'
    return meta + f'<p>{esc(s.get("notes", ""))}</p>'


def build(day):
    slides = parse(day)
    total = len(slides)
    parts = []
    for n, s in enumerate(slides, 1):
        s['section_label'] = section_label(s['section'])
        body = LAYOUTS[s['type']](s, day)
        if '(Read at home)' in s['section'] and s['type'] != 'section':
            body = '<span class="badge-home">Read at home</span>' + body
        footer = (f'<div class="slide__footer"><span>{esc(s["section_label"])} · Day {day} · '
                  f'{n:02d} / {total}</span></div>')
        cls = ' '.join(filter(None, ['slide', CLASS.get(s['type']), f'slide--t-{s["type"]}']))
        parts.append(
            f'  <!-- {s["id"]} · {esc(s["title"])} -->\n'
            f'  <section class="{cls}" data-id="{s["id"]}">\n'
            f'    <div class="slide__body">{body}</div>\n'
            f'    {footer}\n'
            f'    <aside class="notes">{notes_html(s)}</aside>\n'
            f'  </section>\n')
    title = f'Day {day} — {TITLES[day]}'
    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} · Computer Vision for Developers</title>
  <link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../assets/theme.css">
  <link rel="stylesheet" href="../assets/site.css">
  <link rel="stylesheet" href="../assets/deck.css">
  <link rel="stylesheet" href="../assets/cv-deck.css">
</head>
<body>
<!-- Generated by tools/build_decks.py from content/slides-day{day}.md — edit the markdown, then rebuild. -->
<div class="deck" data-title="{esc(title)}" data-total="{total}">
{''.join(parts)}</div>
<script src="../assets/deck.js"></script>
</body>
</html>
'''
    out = os.path.join(ROOT, 'slides', f'day{day}.html')
    open(out, 'w', encoding='utf-8', newline='\n').write(page)
    print(f'slides/day{day}.html: {total} slides')
    return total


if __name__ == '__main__':
    days = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    for d in days:
        build(d)
