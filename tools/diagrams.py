"""diagrams.py — inline SVG for the `diagram` slides.

flow_svg() lays out boxes and arrows from a Screen line that contains
arrows. CUSTOM holds hand-drawn diagrams for slides where a flow chart
would not explain the idea (coordinates, curves, matrices, the U shape…).
No images, no network: every diagram is inline SVG styled by cv-deck.css.
"""
import html
import math


def esc(s):
    return html.escape(s, quote=False)


def wrap(text, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + ' ' + w).strip()
    if cur:
        lines.append(cur)
    return lines or ['']


def marker(mid):
    return (f'<defs><marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse"><path class="dg-arrowhead" d="M0,0 L10,5 L0,10 z"/>'
            f'</marker></defs>')


def text_block(x, y, lines, cls, lh, anchor='middle'):
    out = f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">'
    for k, l in enumerate(lines):
        out += f'<tspan x="{x:.1f}" dy="{0 if k == 0 else lh}">{esc(l)}</tspan>'
    return out + '</text>'


# ---------------------------------------------------------------- flow

W = 940
GAP = 46
T_FS, S_FS = 17, 14


def node_lines(node, bw, fmt):
    tw = max(6, int(bw / (T_FS * 0.56)))
    sw = max(6, int(bw / (S_FS * 0.52)))
    if 'stack' in node:
        parts = []
        for h, b in node['stack']:
            parts.append((wrap(fmt(h), tw), wrap(fmt(b), sw) if b else []))
        return parts
    return [(wrap(fmt(node['title']), tw), wrap(fmt(node['sub']), sw) if node.get('sub') else [])]


def part_h(tl, sl):
    return 16 + len(tl) * 21 + (len(sl) * 18 + 4 if sl else 0) + 10


def draw_node(x, y, bw, parts, dark=False, h=None):
    out = ''
    if len(parts) == 1:
        tl, sl = parts[0]
        hh = h or part_h(tl, sl)
        cls = 'dg-box dg-box--dark' if dark else 'dg-box'
        out += f'<rect class="{cls}" x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{hh:.1f}" rx="10"/>'
        inner = len(tl) * 21 + (len(sl) * 18 + 4 if sl else 0)
        ty = y + (hh - inner) / 2 + 16
        out += text_block(x + bw / 2, ty, tl, 'dg-t dg-t--light' if dark else 'dg-t', 21)
        if sl:
            out += text_block(x + bw / 2, ty + len(tl) * 21 + 2, sl, 'dg-s dg-s--light' if dark else 'dg-s', 18)
        return out, hh
    yy = y
    for k, (tl, sl) in enumerate(parts):
        ph = part_h(tl, sl)
        cls = 'dg-box' + (' dg-box--alt' if k % 2 else '')
        out += f'<rect class="{cls}" x="{x:.1f}" y="{yy:.1f}" width="{bw:.1f}" height="{ph:.1f}" rx="8"/>'
        out += text_block(x + bw / 2, yy + 24, tl, 'dg-t', 21)
        if sl:
            out += text_block(x + bw / 2, yy + 24 + len(tl) * 21 + 2, sl, 'dg-s', 18)
        yy += ph + 8
    return out, yy - y - 8


def parts_h(parts):
    if len(parts) == 1:
        return part_h(*parts[0])
    return sum(part_h(*p) for p in parts) + 8 * (len(parts) - 1)


def flow_svg(spec, sid, fmt_plain=lambda x: x):
    mid = 'ah-' + sid.replace('.', '-')
    if spec['kind'] == 'branch':
        return branch_svg(spec, mid, fmt_plain)
    nodes = spec['nodes']
    n = len(nodes)
    longest = max(len(nd.get('title', '') + nd.get('sub', '')) if 'stack' not in nd else 60 for nd in nodes)
    per = 5 if longest < 34 else 4
    if n > per:
        rows_n = math.ceil(n / per)
        per = math.ceil(n / rows_n)
    rows = [nodes[i:i + per] for i in range(0, n, per)]
    cols = max(len(r) for r in rows)
    bw = (W - (cols - 1) * GAP) / cols
    out, y, prev_last = '', 0, None
    row_gap = 58
    for r_i, row in enumerate(rows):
        plist = [node_lines(nd, bw, fmt_plain) for nd in row]
        rh = max(parts_h(p) for p in plist)
        row_w = len(row) * bw + (len(row) - 1) * GAP
        x0 = (W - row_w) / 2
        for k, p in enumerate(plist):
            x = x0 + k * (bw + GAP)
            h = parts_h(p)
            dark = (r_i == 0 and k == 0) or (r_i == len(rows) - 1 and k == len(row) - 1)
            svg, _ = draw_node(x, y + (rh - h) / 2, bw, p, dark=dark and len(p) == 1, h=None)
            out += svg
            if k > 0:
                ax = x - GAP + 4
                out += (f'<line class="dg-line" x1="{ax:.1f}" y1="{y + rh / 2:.1f}" x2="{x - 4:.1f}" '
                        f'y2="{y + rh / 2:.1f}" marker-end="url(#{mid})"/>')
        if prev_last is not None:
            px, py = prev_last
            fx = x0 + bw / 2
            my = py + row_gap / 2
            out += (f'<path class="dg-line" d="M{px:.1f},{py + 2:.1f} L{px:.1f},{my:.1f} L{fx:.1f},{my:.1f} '
                    f'L{fx:.1f},{y - 4:.1f}" marker-end="url(#{mid})"/>')
        last_x = x0 + (len(row) - 1) * (bw + GAP) + bw / 2
        prev_last = (last_x, y + rh / 2 + parts_h(plist[-1]) / 2)
        y += rh + row_gap
    H = y - row_gap + 4
    return (f'<svg viewBox="-2 -2 {W + 4} {H + 4}" role="img" aria-label="Diagram">'
            f'{marker(mid)}{out}</svg>')


def branch_svg(spec, mid, fmt):
    branches = spec['branches']
    cols = max(len(b) for b in branches)
    rw = 230
    bw = (W - rw - GAP * (cols + 0.5)) / cols
    rowh, gap = 64, 18
    H = len(branches) * rowh + (len(branches) - 1) * gap
    out = ''
    rlines = wrap(fmt(spec['root']), 18)
    rh = 30 + len(rlines) * 21
    ry = (H - rh) / 2
    out += f'<rect class="dg-box dg-box--dark" x="0" y="{ry:.1f}" width="{rw}" height="{rh:.1f}" rx="10"/>'
    out += text_block(rw / 2, ry + 26, rlines, 'dg-t dg-t--light', 21)
    for b_i, br in enumerate(branches):
        y = b_i * (rowh + gap)
        cy = y + rowh / 2
        x = rw + GAP * 1.5
        out += (f'<path class="dg-line" d="M{rw:.1f},{H / 2:.1f} C{rw + 40:.1f},{H / 2:.1f} {x - 40:.1f},{cy:.1f} '
                f'{x - 4:.1f},{cy:.1f}" marker-end="url(#{mid})"/>')
        for k, nd in enumerate(br):
            xx = x + k * (bw + GAP)
            last = k == len(br) - 1
            cls = 'dg-box dg-box--alt' if last else 'dg-box'
            out += f'<rect class="{cls}" x="{xx:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{rowh}" rx="10"/>'
            lines = wrap(fmt(nd), int(bw / 9.5))
            out += text_block(xx + bw / 2, cy - (len(lines) - 1) * 10.5 + 6, lines, 'dg-t', 21)
            if k > 0:
                out += (f'<line class="dg-line" x1="{xx - GAP + 4:.1f}" y1="{cy:.1f}" x2="{xx - 4:.1f}" '
                        f'y2="{cy:.1f}" marker-end="url(#{mid})"/>')
    return f'<svg viewBox="-2 -2 {W + 4} {H + 4}" role="img" aria-label="Diagram">{marker(mid)}{out}</svg>'


# ---------------------------------------------------------------- custom

def svg(sid, body, vb='0 0 640 400', label='Diagram'):
    mid = 'ah-' + sid.replace('.', '-')
    return f'<svg viewBox="{vb}" role="img" aria-label="{esc(label)}">{marker(mid)}{body.replace("#AH", "#" + mid)}</svg>'


def t(x, y, s, cls='dg-t', anchor='middle'):
    return f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{esc(s)}</text>'


def d_channels(sid):  # 1.21
    b = ''
    for k, (name, cls) in enumerate([('Red', 'dg-fill-coral'), ('Green', 'dg-fill-teal'), ('Blue', 'dg-fill-ink')]):
        x, y = 30 + k * 26, 60 + k * 26
        b += f'<rect class="{cls}" x="{x}" y="{y}" width="200" height="200" rx="6" opacity="0.85"/>'
    b += t(130, 345, 'R · G · B channels', 'dg-s')
    for k, name in enumerate(['R', 'G', 'B']):
        b += t(48 + k * 26, 82 + k * 26, name, 'dg-t dg-t--light', 'start')
    b += '<line class="dg-line" x1="320" y1="200" x2="400" y2="200" marker-end="url(#AH)"/>'
    b += t(360, 188, 'stacked', 'dg-s')
    # colour image as a grid of coloured pixels
    cols = ['#e4602a', '#37cc95', '#0d1330', '#f0a03c', '#66ccff', '#ffffff', '#5a50a0', '#0b7457', '#fe833c']
    for i in range(6):
        for j in range(6):
            c = cols[(i * 2 + j) % len(cols)]
            b += f'<rect x="{420 + j * 33}" y="{100 + i * 33}" width="33" height="33" fill="{c}" stroke="#c9d1dc"/>'
    b += t(519, 345, 'one colour image · (H, W, 3)', 'dg-s')
    return svg(sid, b)


def d_coords(sid):  # 1.23
    b = ''
    x0, y0, c = 100, 70, 46
    for i in range(6):
        for j in range(9):
            hl = (i == 2 and j == 5)
            fill = 'dg-fill-teal' if hl else ''
            b += f'<rect class="{"dg-grid " + fill if hl else "dg-grid"}" x="{x0 + j * c}" y="{y0 + i * c}" width="{c}" height="{c}"/>'
    b += f'<circle class="dg-fill-coral" cx="{x0}" cy="{y0}" r="7"/>'
    b += t(x0 - 8, y0 - 14, '(0, 0)', 'dg-t', 'end')
    b += f'<line class="dg-line dg-line--teal" x1="{x0}" y1="{y0 - 34}" x2="{x0 + 9 * c}" y2="{y0 - 34}" marker-end="url(#AH)"/>'
    b += t(x0 + 9 * c - 4, y0 - 44, 'x (columns) →', 'dg-t', 'end')
    b += f'<line class="dg-line dg-line--coral" x1="{x0 - 34}" y1="{y0}" x2="{x0 - 34}" y2="{y0 + 6 * c}" marker-end="url(#AH)"/>'
    b += f'<text class="dg-t" x="{x0 - 46}" y="{y0 + 3 * c}" text-anchor="middle" transform="rotate(-90 {x0 - 46} {y0 + 3 * c})">y (rows) ↓</text>'
    b += t(x0 + 5.5 * c, y0 + 2.5 * c + 6, 'x=5', 'dg-s')
    b += t(x0 + 4.5 * c, y0 + 6 * c + 30, 'img[2, 5]  →  row y = 2, column x = 5', 'dg-t')
    return svg(sid, b)


def d_gradient(sid):  # 1.58
    b = '<path class="dg-line dg-line--teal" stroke-width="3" d="M40,70 C120,80 160,330 320,330 C470,330 520,120 610,90"/>'
    pts = [(75, 88), (125, 160), (170, 250), (225, 305), (290, 328)]
    for k in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[k], pts[k + 1]
        b += f'<line class="dg-line dg-line--coral" x1="{x1}" y1="{y1 - 14}" x2="{x2 - 6}" y2="{y2 - 18}" marker-end="url(#AH)"/>'
    for x, y in pts:
        b += f'<circle class="dg-fill-coral" cx="{x}" cy="{y - 10}" r="9"/>'
    b += f'<circle class="dg-fill-ink" cx="320" cy="320" r="7"/>'
    b += t(320, 362, 'minimum loss', 'dg-s')
    b += t(150, 60, 'start: random weights', 'dg-s', 'start')
    b += t(250, 220, 'small steps downhill', 'dg-t', 'start')
    b += '<line class="dg-line" x1="30" y1="380" x2="620" y2="380" marker-end="url(#AH)"/>'
    b += '<line class="dg-line" x1="30" y1="380" x2="30" y2="30" marker-end="url(#AH)"/>'
    b += t(600, 372, 'weights', 'dg-s', 'end')
    b += t(40, 40, 'loss', 'dg-s', 'start')
    return svg(sid, b)


def d_confusion(sid):  # 1.101
    cls = ['cat', 'dog', 'car']
    m = [[45, 9, 1], [7, 41, 2], [0, 3, 48]]
    x0, y0, c = 190, 80, 90
    b = ''
    for i in range(3):
        b += t(x0 - 14, y0 + i * c + c / 2 + 6, cls[i], 'dg-t', 'end')
        b += t(x0 + i * c + c / 2, y0 - 14, cls[i], 'dg-t')
        for j in range(3):
            v = m[i][j]
            box = 'dg-box dg-box--alt' if i == j else ('dg-box dg-box--warm' if v >= 5 else 'dg-box')
            b += f'<rect class="{box}" x="{x0 + j * c}" y="{y0 + i * c}" width="{c}" height="{c}"/>'
            b += t(x0 + j * c + c / 2, y0 + i * c + c / 2 + 8, str(v), 'dg-t')
    b += t(x0 + 1.5 * c, y0 - 46, 'predicted class →', 'dg-s')
    b += f'<text class="dg-s" x="{x0 - 92}" y="{y0 + 1.5 * c}" text-anchor="middle" transform="rotate(-90 {x0 - 92} {y0 + 1.5 * c})">true class →</text>'
    b += t(x0 + 1.5 * c, y0 + 3 * c + 36, 'diagonal = correct · orange = cat ↔ dog confusion', 'dg-s')
    return svg(sid, b)


def d_resnet(sid):  # 1.111
    b = ''
    b += t(80, 214, 'x', 'dg-t')
    b += '<line class="dg-line" x1="95" y1="208" x2="150" y2="208" marker-end="url(#AH)"/>'
    b += '<rect class="dg-box" x="155" y="180" width="130" height="56" rx="10"/>' + t(220, 214, 'conv + ReLU')
    b += '<line class="dg-line" x1="285" y1="208" x2="325" y2="208" marker-end="url(#AH)"/>'
    b += '<rect class="dg-box" x="330" y="180" width="110" height="56" rx="10"/>' + t(385, 214, 'conv')
    b += '<line class="dg-line" x1="440" y1="208" x2="478" y2="208" marker-end="url(#AH)"/>'
    b += '<circle class="dg-box dg-box--alt" cx="500" cy="208" r="20"/>' + t(500, 215, '+')
    b += '<line class="dg-line" x1="520" y1="208" x2="570" y2="208" marker-end="url(#AH)"/>'
    b += t(605, 214, 'F(x) + x', 'dg-t')
    b += '<path class="dg-line dg-line--coral" stroke-width="3" d="M110,208 C110,90 500,90 500,182" marker-end="url(#AH)"/>'
    b += t(305, 92, 'skip connection: x passes straight through', 'dg-t')
    b += t(298, 268, 'F(x): the block learns only the change', 'dg-s')
    return svg(sid, b)


def d_grid(sid):  # 2.56
    x0, y0, c = 40, 30, 46
    b = ''
    b += f'<ellipse class="dg-box dg-box--amber" cx="{x0 + 3.6 * c}" cy="{y0 + 4.2 * c}" rx="{1.9 * c}" ry="{1.4 * c}"/>'
    b += f'<rect class="dg-line dg-line--coral" stroke-width="3" x="{x0 + 1.7 * c}" y="{y0 + 2.8 * c}" width="{3.8 * c}" height="{2.8 * c}" fill="none"/>'
    b += f'<rect x="{x0 + 3 * c}" y="{y0 + 4 * c}" width="{c}" height="{c}" class="dg-fill-teal" opacity="0.55"/>'
    for i in range(8):
        b += f'<line class="dg-grid" x1="{x0}" y1="{y0 + i * c}" x2="{x0 + 7 * c}" y2="{y0 + i * c}"/>'
        b += f'<line class="dg-grid" x1="{x0 + i * c}" y1="{y0}" x2="{x0 + i * c}" y2="{y0 + 7 * c}"/>'
    b += f'<circle class="dg-fill-coral" cx="{x0 + 3.6 * c}" cy="{y0 + 4.2 * c}" r="6"/>'
    b += t(x0 + 3.5 * c, y0 + 7 * c + 28, '7 × 7 grid · object centre → one cell', 'dg-s')
    b += f'<line class="dg-line" x1="{x0 + 4 * c + 4}" y1="{y0 + 4.5 * c}" x2="440" y2="200" marker-end="url(#AH)"/>'
    b += '<rect class="dg-box" x="445" y="120" width="185" height="170" rx="10"/>'
    b += t(537, 150, 'this cell predicts', 'dg-t')
    for k, s in enumerate(['2 boxes (x, y, w, h)', 'a confidence each', '20 class scores']):
        b += t(537, 190 + k * 32, s, 'dg-s')
    return svg(sid, b)


def d_prcurve(sid):  # 2.73
    b = '<line class="dg-line" x1="70" y1="340" x2="610" y2="340" marker-end="url(#AH)"/>'
    b += '<line class="dg-line" x1="70" y1="340" x2="70" y2="30" marker-end="url(#AH)"/>'
    b += t(600, 372, 'recall', 'dg-t', 'end') + t(60, 24, 'precision', 'dg-t', 'start')
    good = 'M70,60 L190,60 L190,110 L300,110 L300,130 L420,130 L420,190 L520,190 L520,250'
    bad = 'M70,120 L150,120 L150,190 L260,190 L260,250 L360,250 L360,300'
    b += f'<path class="dg-line dg-line--teal" stroke-width="4" d="{good}"/>'
    b += f'<path class="dg-line dg-line--coral dg-line--dash" stroke-width="3" d="{bad}"/>'
    b += t(430, 120, 'good detector', 'dg-t', 'start')
    b += t(370, 296, 'weaker detector', 'dg-s', 'start')
    for k, v in enumerate(['0', '0.5', '1']):
        b += t(70 + k * 270, 362, v, 'dg-s')
    b += t(40, 64, '1', 'dg-s')
    return svg(sid, b)


def d_unet(sid):  # 2.93
    b = ''
    enc = [(40, 40, 120), (90, 120, 100), (140, 200, 80), (190, 280, 60)]
    for k, (x, y, w) in enumerate(enc):
        b += f'<rect class="dg-box" x="{x}" y="{y}" width="{w}" height="50" rx="8"/>'
        b += t(x + w / 2, y + 31, ['512', '256', '128', '64'][k], 'dg-t')
        xr = 640 - x - w
        b += f'<rect class="dg-box dg-box--alt" x="{xr}" y="{y}" width="{w}" height="50" rx="8"/>'
        b += t(xr + w / 2, y + 31, ['512', '256', '128', '64'][k], 'dg-t')
        if k < 3:
            b += f'<line class="dg-line dg-line--coral dg-line--dash" stroke-width="2.5" x1="{x + w + 4}" y1="{y + 25}" x2="{xr - 6}" y2="{y + 25}" marker-end="url(#AH)"/>'
        if k < 3:
            nx = enc[k + 1][0]
            b += f'<line class="dg-line" x1="{x + 30}" y1="{y + 52}" x2="{nx + 20}" y2="{y + 78}" marker-end="url(#AH)"/>'
            b += f'<line class="dg-line" x1="{640 - nx - 20}" y1="{y + 78}" x2="{640 - x - 30}" y2="{y + 52}" marker-end="url(#AH)"/>'
    b += '<rect class="dg-box dg-box--dark" x="260" y="345" width="120" height="44" rx="8"/>' + t(320, 373, 'bottleneck', 'dg-t dg-t--light')
    b += '<line class="dg-line" x1="230" y1="332" x2="262" y2="352" marker-end="url(#AH)"/>'
    b += '<line class="dg-line" x1="378" y1="352" x2="410" y2="332" marker-end="url(#AH)"/>'
    b += t(110, 22, 'encoder: what', 'dg-s') + t(530, 22, 'decoder: where', 'dg-s')
    b += t(320, 62, 'skip: copy across', 'dg-s')
    return svg(sid, b)


def d_maskrcnn(sid):  # 2.95
    b = '<rect class="dg-box" x="20" y="80" width="200" height="200" rx="8"/>'
    b += '<path class="dg-fill-teal" opacity="0.6" d="M80,250 C60,180 90,130 120,120 C160,110 175,170 170,250 Z"/>'
    b += '<rect class="dg-line dg-line--coral" stroke-width="3" fill="none" x="62" y="112" width="122" height="146"/>'
    b += t(120, 306, 'box + mask inside it', 'dg-s')
    b += '<line class="dg-line" x1="228" y1="180" x2="270" y2="180" marker-end="url(#AH)"/>'
    b += '<rect class="dg-box dg-box--dark" x="275" y="140" width="130" height="80" rx="10"/>'
    b += t(340, 175, 'Faster R-CNN', 'dg-t dg-t--light') + t(340, 199, '+ RoIAlign', 'dg-s dg-s--light')
    for k, (name, cls) in enumerate([('class', 'dg-box'), ('box', 'dg-box'), ('mask head', 'dg-box dg-box--warm')]):
        y = 70 + k * 95
        b += f'<path class="dg-line" d="M405,180 C430,180 430,{y + 28} 455,{y + 28}" marker-end="url(#AH)"/>'
        b += f'<rect class="{cls}" x="460" y="{y}" width="150" height="56" rx="10"/>' + t(535, y + 34, name)
    return svg(sid, b)


def d_fpn(sid):  # 2.45
    b = ''
    left = [(60, 290, 200), (85, 200, 150), (110, 120, 100), (135, 50, 50)]
    for k, (x, y, w) in enumerate(left):
        b += f'<rect class="dg-box" x="{x}" y="{y}" width="{w}" height="50" rx="6"/>'
        xr = 380 + (200 - w) / 2
        b += f'<rect class="dg-box dg-box--alt" x="{xr}" y="{y}" width="{w}" height="50" rx="6"/>'
        b += f'<line class="dg-line" x1="{x + w + 6}" y1="{y + 25}" x2="{xr - 6}" y2="{y + 25}" marker-end="url(#AH)"/>'
        if k < 3:
            ny, nw = left[k + 1][1], left[k + 1][2]
            b += f'<line class="dg-line dg-line--coral" stroke-width="2.5" x1="{480}" y1="{ny + 52}" x2="{480}" y2="{y - 4}" marker-end="url(#AH)"/>'
    b += t(160, 372, 'backbone: fine → coarse', 'dg-s')
    b += t(480, 372, 'FPN: meaning flows back down', 'dg-s')
    b += t(160, 30, 'deep: strong meaning', 'dg-s')
    b += t(480, 30, 'large objects ↑ · small objects ↓', 'dg-s')
    return svg(sid, b)


def d_linecount(sid):  # 2.108
    b = '<rect class="dg-fill-muted" x="0" y="120" width="640" height="160" opacity="0.5"/>'
    b += '<line class="dg-line dg-line--dash" x1="0" y1="200" x2="640" y2="200"/>'
    b += '<line class="dg-line dg-line--coral" stroke-width="5" x1="330" y1="100" x2="330" y2="300"/>'
    b += t(330, 90, 'virtual line', 'dg-t')
    for k, (x, y, idn) in enumerate([(160, 140, '#7'), (260, 220, '#8'), (440, 140, '#5')]):
        b += f'<rect class="dg-box dg-box--dark" x="{x}" y="{y}" width="80" height="44" rx="8"/>'
        b += t(x + 40, y + 28, idn, 'dg-t dg-t--light')
        b += f'<line class="dg-line dg-line--teal" stroke-width="2.5" x1="{x - 70}" y1="{y + 22}" x2="{x - 4}" y2="{y + 22}" marker-end="url(#AH)"/>'
    b += t(480, 330, 'IN: 1 (#5 crossed)', 'dg-t')
    b += t(160, 330, 'same ID never counted twice', 'dg-s')
    return svg(sid, b)


def d_attention(sid):  # 3.18
    b = ''
    x0, y0, c = 40, 40, 56
    for i in range(6):
        for j in range(10):
            b += f'<rect class="dg-grid" x="{x0 + j * c}" y="{y0 + i * c}" width="{c}" height="{c}"/>'
    b += f'<rect class="dg-fill-coral" opacity="0.8" x="{x0 + 2 * c}" y="{y0 + 2.6 * c}" width="{5.6 * c}" height="{1.6 * c}" rx="20"/>'
    b += f'<rect class="dg-fill-coral" opacity="0.8" x="{x0 + 3 * c}" y="{y0 + 1.8 * c}" width="{3 * c}" height="{1 * c}" rx="14"/>'
    for cx in (3, 6.6):
        b += f'<circle class="dg-fill-ink" cx="{x0 + cx * c}" cy="{y0 + 4.3 * c}" r="{0.55 * c}"/>'
    src = (x0 + 3 * c, y0 + 4.3 * c)
    b += f'<circle cx="{src[0]}" cy="{src[1]}" r="{0.75 * c}" fill="none" stroke="#37cc95" stroke-width="5"/>'
    for (tx, ty, w) in [(6.6, 4.3, 6), (4.5, 2.3, 5), (6.5, 3.2, 4), (8.5, 0.5, 1)]:
        b += (f'<line class="dg-line dg-line--teal" stroke-width="{w}" opacity="{0.35 + w / 10}" '
              f'x1="{src[0]}" y1="{src[1]}" x2="{x0 + tx * c}" y2="{y0 + ty * c}"/>')
    b += t(x0 + 8.5 * c, y0 + 0.5 * c - 10, 'sky: weak', 'dg-s')
    b += t(320, 385, 'thick line = high attention weight', 'dg-s')
    return svg(sid, b)


def d_backbone(sid):  # 3.38
    b = '<rect class="dg-box dg-box--dark" x="10" y="150" width="170" height="90" rx="10"/>'
    b += t(95, 190, 'DINOv2', 'dg-t dg-t--light') + t(95, 214, 'frozen backbone', 'dg-s dg-s--light')
    tasks = [('small head', 'classification'), ('small head', 'segmentation'),
             ('small head', 'depth'), ('nearest neighbours', 'image retrieval')]
    for k, (h, task) in enumerate(tasks):
        y = 20 + k * 92
        b += f'<path class="dg-line" d="M180,195 C220,195 230,{y + 30} 262,{y + 30}" marker-end="url(#AH)"/>'
        b += f'<rect class="dg-box" x="266" y="{y}" width="170" height="60" rx="10"/>' + t(351, y + 36, h, 'dg-s')
        b += f'<line class="dg-line" x1="436" y1="{y + 30}" x2="466" y2="{y + 30}" marker-end="url(#AH)"/>'
        b += f'<rect class="dg-box dg-box--alt" x="470" y="{y}" width="160" height="60" rx="10"/>' + t(550, y + 36, task)
    return svg(sid, b)


def d_matrix(sid):  # 3.44
    x0, y0, c = 170, 70, 70
    b = ''
    for i in range(4):
        b += f'<rect class="dg-box dg-box--dark" x="{x0 - 90}" y="{y0 + i * c + 8}" width="74" height="{c - 16}" rx="6"/>'
        b += t(x0 - 53, y0 + i * c + c / 2 + 6, f'img {i + 1}', 'dg-s dg-s--light')
        b += f'<rect class="dg-box dg-box--amber" x="{x0 + i * c + 6}" y="{y0 - 54}" width="{c - 12}" height="40" rx="6"/>'
        b += t(x0 + i * c + c / 2, y0 - 28, f'text {i + 1}', 'dg-s')
        for j in range(4):
            cls = 'dg-box dg-box--alt' if i == j else 'dg-box'
            b += f'<rect class="{cls}" x="{x0 + j * c}" y="{y0 + i * c}" width="{c}" height="{c}"/>'
            b += t(x0 + j * c + c / 2, y0 + i * c + c / 2 + 7, '↑' if i == j else '↓', 'dg-t')
    b += t(x0 + 2 * c, y0 + 4 * c + 36, 'diagonal: matching pairs (push up) · rest: push down', 'dg-s')
    return svg(sid, b)


def d_space(sid):  # 3.45
    b = '<rect class="dg-box" x="10" y="10" width="620" height="380" rx="14"/>'
    pairs = [(120, 110, 'dog photo', '"a photo of a dog"'), (420, 120, 'palm photo', '"a palm tree in the desert"'),
             (260, 290, 'car photo', '"a red car on a street"')]
    for x, y, img, txt in pairs:
        b += f'<rect class="dg-box dg-box--dark" x="{x - 50}" y="{y - 30}" width="100" height="60" rx="6"/>'
        b += t(x, y + 6, img, 'dg-s dg-s--light')
        b += f'<rect class="dg-box dg-box--amber" x="{x - 30}" y="{y + 44}" width="{len(txt) * 7.6 + 20}" height="34" rx="17"/>'
        b += t(x - 20, y + 66, txt, 'dg-s', 'start')
        b += f'<line class="dg-line dg-line--teal dg-line--dash" x1="{x}" y1="{y + 30}" x2="{x}" y2="{y + 44}"/>'
    b += t(320, 380, 'close together = good match', 'dg-s')
    return svg(sid, b)


def d_diffusion(sid):  # 3.85
    b = ''
    import random
    rnd = random.Random(7)
    for k in range(5):
        x = 20 + k * 124
        b += f'<rect class="dg-box" x="{x}" y="120" width="100" height="100" rx="8"/>'
        if k < 4:
            op = 1 - k * 0.28
            b += f'<circle class="dg-fill-teal" cx="{x + 50}" cy="170" r="30" opacity="{op:.2f}"/>'
        for _ in range(k * 22):
            b += f'<rect class="dg-fill-ink" x="{x + 4 + rnd.random() * 90:.0f}" y="{124 + rnd.random() * 90:.0f}" width="4" height="4" opacity="0.7"/>'
    b += '<line class="dg-line dg-line--coral" stroke-width="3" x1="40" y1="90" x2="600" y2="90" marker-end="url(#AH)"/>'
    b += t(320, 76, 'forward: add a little noise each step (easy)', 'dg-t')
    b += '<line class="dg-line dg-line--teal" stroke-width="3" x1="600" y1="250" x2="40" y2="250" marker-end="url(#AH)"/>'
    b += t(320, 282, 'reverse: a network removes a little noise each step (learned)', 'dg-t')
    b += t(70, 320, 'image', 'dg-s') + t(570, 320, 'pure noise', 'dg-s')
    return svg(sid, b)


CUSTOM = {
    '1.21': d_channels, '1.23': d_coords, '1.58': d_gradient, '1.101': d_confusion,
    '1.111': d_resnet, '2.45': d_fpn, '2.56': d_grid, '2.73': d_prcurve, '2.93': d_unet,
    '2.95': d_maskrcnn, '2.108': d_linecount, '3.18': d_attention, '3.38': d_backbone,
    '3.44': d_matrix, '3.45': d_space, '3.85': d_diffusion,
}
