import json
import random

# ------------------------------------------------------------ IoU Darts
ID_STYLE = '''
    .board { width: 100%; max-width: 760px; aspect-ratio: 3 / 2; display: block; background: #fff; border: 1px solid var(--border); border-radius: var(--radius-sm); touch-action: none; cursor: crosshair; user-select: none; }
    .target { font-family: var(--font-display); font-size: 2.6rem; color: var(--coral); line-height: 1; }
    body.projector .board { max-width: 1100px; }
'''

ID_BODY = '''        <div class="panel" id="play">
          <div class="rowline" style="justify-content:space-between;margin-bottom:var(--s3)">
            <div><span class="small muted">Target IoU</span><div class="target" id="target">0.50</div></div>
            <div class="rowline"><button type="button" class="btn btn--ghost" id="clear">Clear my box</button><button type="button" class="btn" id="throw" disabled>Throw!</button></div>
          </div>
          <svg class="board" id="board" viewBox="0 0 600 400" aria-label="Drag to draw a box">
            <rect id="gt" fill="rgba(11,116,87,.12)" stroke="#0b7457" stroke-width="3"/>
            <text id="gtlabel" font-size="14" font-weight="700" fill="#0b7457">ground truth</text>
            <rect id="inter" fill="rgba(240,160,60,.45)" stroke="none" visibility="hidden"/>
            <rect id="mine" fill="rgba(228,96,42,.12)" stroke="#e4602a" stroke-width="3" stroke-dasharray="8 5" visibility="hidden"/>
          </svg>
          <p class="small muted">Press and drag on the board to draw your box. Redraw as often as you like, then press <strong>Throw!</strong></p>
          <div class="verdict hidden" id="verdict"></div>
          <p><button type="button" class="btn hidden" id="next">Next target →</button></p>
        </div>
        <div class="panel finish hidden" id="finish">
          <h2 style="font-family:var(--font-display);font-size:1.6rem">Darts done</h2>
          <p class="finish__score" id="final">0 / 40</p>
          <div class="rowline"><button type="button" class="btn" id="again">Play again</button><a class="btn btn--ghost" href="./index.html">All activities</a></div>
        </div>
        <div class="panel"><h2>Scoring</h2><p class="small muted">Four throws at IoU 0.3, 0.5, 0.75 and 0.9. Hitting the target exactly scores 10; every 0.02 you are off costs 1 point (0.2 off or more scores 0). IoU = overlap area ÷ combined area (slide 2.20) — most people are surprised how much overlap 0.5 needs.</p></div>'''

ID_JS = '''
(function () {
  'use strict';
  var TARGETS = [0.3, 0.5, 0.75, 0.9], GTS = [[180, 110, 380, 270], [240, 80, 400, 330], [120, 140, 420, 260], [210, 90, 390, 310]];
  var MAX = 40, round, score, box, drag;
  var svg = document.getElementById('board');
  function setRect(el, b) { el.setAttribute('x', b[0]); el.setAttribute('y', b[1]); el.setAttribute('width', Math.max(0, b[2] - b[0])); el.setAttribute('height', Math.max(0, b[3] - b[1])); }
  function iou(a, b) {
    var w = Math.max(0, Math.min(a[2], b[2]) - Math.max(a[0], b[0])), h = Math.max(0, Math.min(a[3], b[3]) - Math.max(a[1], b[1]));
    var inter = w * h, u = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter;
    return u > 0 ? inter / u : 0;
  }
  function pt(e) {
    var p = svg.createSVGPoint(), t = e.touches ? e.touches[0] : e;
    p.x = t.clientX; p.y = t.clientY;
    var q = p.matrixTransform(svg.getScreenCTM().inverse());
    return [Math.max(0, Math.min(600, q.x)), Math.max(0, Math.min(400, q.y))];
  }
  function down(e) { if (svg.dataset.locked) return; e.preventDefault(); drag = pt(e); move(e); }
  function move(e) {
    if (!drag) return; e.preventDefault();
    var p = pt(e);
    box = [Math.min(drag[0], p[0]), Math.min(drag[1], p[1]), Math.max(drag[0], p[0]), Math.max(drag[1], p[1])];
    var m = document.getElementById('mine'); setRect(m, box); m.setAttribute('visibility', 'visible');
    document.getElementById('throw').disabled = (box[2] - box[0]) < 4 || (box[3] - box[1]) < 4;
  }
  function up() { drag = null; }
  svg.addEventListener('mousedown', down); window.addEventListener('mousemove', move); window.addEventListener('mouseup', up);
  svg.addEventListener('touchstart', down, { passive: false }); svg.addEventListener('touchmove', move, { passive: false }); svg.addEventListener('touchend', up);

  function load() {
    var g = GTS[round]; box = null; delete svg.dataset.locked;
    setRect(document.getElementById('gt'), g);
    var lab = document.getElementById('gtlabel'); lab.setAttribute('x', g[0]); lab.setAttribute('y', g[1] - 8);
    ['mine', 'inter'].forEach(function (id) { document.getElementById(id).setAttribute('visibility', 'hidden'); });
    document.getElementById('target').textContent = TARGETS[round].toFixed(2);
    document.getElementById('throw').disabled = true;
    document.getElementById('verdict').classList.add('hidden');
    document.getElementById('next').classList.add('hidden');
    Act.setRound((round + 1) + ' / 4');
  }
  document.getElementById('clear').addEventListener('click', function () { if (!svg.dataset.locked) { box = null; document.getElementById('mine').setAttribute('visibility', 'hidden'); document.getElementById('throw').disabled = true; } });
  document.getElementById('throw').addEventListener('click', function () {
    if (!box || svg.dataset.locked) return;
    svg.dataset.locked = '1';
    var g = GTS[round], v = iou(box, g), d = Math.abs(v - TARGETS[round]);
    var pts = Math.max(0, Math.round(10 - d / 0.02));
    score += pts; Act.setScore(score);
    var ib = [Math.max(box[0], g[0]), Math.max(box[1], g[1]), Math.min(box[2], g[2]), Math.min(box[3], g[3])];
    var ie = document.getElementById('inter'); setRect(ie, ib); ie.setAttribute('visibility', ib[2] > ib[0] && ib[3] > ib[1] ? 'visible' : 'hidden');
    var el = document.getElementById('verdict');
    el.className = 'verdict ' + (pts >= 7 ? 'verdict--good' : pts >= 3 ? 'verdict--warn' : 'verdict--bad');
    el.innerHTML = '<h3>Your IoU: ' + v.toFixed(3) + ' (target ' + TARGETS[round] + ') · +' + pts + '</h3><p>Orange = intersection. IoU = intersection ÷ (your area + ground-truth area − intersection).</p>';
    document.getElementById('throw').disabled = true;
    var nb = document.getElementById('next'); nb.classList.remove('hidden'); nb.focus();
  });
  document.getElementById('next').addEventListener('click', function () { round++; if (round >= 4) finish(); else load(); });
  document.getElementById('again').addEventListener('click', start);
  function finish() {
    Act.finish(score);
    document.getElementById('play').classList.add('hidden');
    document.getElementById('finish').classList.remove('hidden');
    document.getElementById('final').textContent = score + ' / ' + MAX;
  }
  function start() {
    round = 0; score = 0; Act.setScore(0);
    document.getElementById('play').classList.remove('hidden');
    document.getElementById('finish').classList.add('hidden');
    load();
  }
  Act.init({ id: 'iou-darts', max: MAX });
  start();
})();
'''


def iou_darts():
    return ID_STYLE, ID_BODY, ID_JS, 'A green ground-truth box sits on the board. Drag your own box so that its IoU with the ground truth hits the target: 0.3, 0.5, 0.75, then 0.9. Up to 10 points per throw — closeness wins.'


# ------------------------------------------------------------ Be NMS
def _iou(a, b):
    w = max(0, min(a[2], b[2]) - max(a[0], b[0])); h = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    i = w * h
    return i / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - i)


def _nms(boxes, thr=0.5):
    order = sorted(range(len(boxes)), key=lambda k: -boxes[k]['s'])
    keep = []
    while order:
        b = order.pop(0); keep.append(b)
        order = [o for o in order if _iou(boxes[b]['b'], boxes[o]['b']) <= thr]
    return keep


def nms_rounds():
    """Five fixed rounds: 2–3 objects, 6–10 overlapping scored boxes."""
    rnd = random.Random(23)
    rounds = []
    for r in range(5):
        n_obj = 2 + (r % 2) + (1 if r == 4 else 0)
        n_obj = min(n_obj, 3)
        objs = []
        while len(objs) < n_obj:
            w, h = rnd.randint(110, 170), rnd.randint(90, 150)
            x, y = rnd.randint(20, 600 - w - 20), rnd.randint(20, 400 - h - 20)
            o = [x, y, x + w, y + h]
            if all(_iou(o, p) < 0.05 for p in objs):
                objs.append(o)
        boxes = []
        target = rnd.randint(6, 10)
        while len(boxes) < target:
            o = objs[len(boxes) % n_obj]
            w, h = o[2] - o[0], o[3] - o[1]
            jx, jy, jw, jh = (rnd.uniform(-0.13, 0.13) for _ in range(4))
            b = [round(o[0] + jx * w), round(o[1] + jy * h), round(o[2] + (jx + jw * 0.5) * w), round(o[3] + (jy + jh * 0.5) * h)]
            b = [max(2, b[0]), max(2, b[1]), min(598, b[2]), min(398, b[3])]
            if b[2] - b[0] > 40 and b[3] - b[1] > 40:
                boxes.append({'b': b, 's': 0})
        scores = rnd.sample(range(52, 99), len(boxes))
        for bx, s in zip(boxes, scores):
            bx['s'] = s / 100
        letters = 'ABCDEFGHIJ'
        boxes.sort(key=lambda bx: -bx['s'])
        for k, bx in enumerate(boxes):
            bx['id'] = letters[k]
        keep = _nms(boxes)
        rounds.append({'boxes': boxes, 'keep': [boxes[k]['id'] for k in keep]})
    return rounds


NMS_STYLE = '''
    .board { width: 100%; max-width: 760px; aspect-ratio: 3 / 2; display: block; background: #fff; border: 1px solid var(--border); border-radius: var(--radius-sm); }
    .board .bx { fill: rgba(102,204,255,.06); stroke: #1a6fa0; stroke-width: 2.5; cursor: pointer; }
    .board .bx:hover { stroke-width: 4; }
    .board .bx.kept { stroke: #0b7457; stroke-width: 5; fill: rgba(55,204,149,.18); }
    .board .bx.gone { stroke: #c9d1dc; stroke-dasharray: 5 5; fill: none; }
    .board text { font: 700 15px var(--font-sans); fill: #14181f; pointer-events: none; }
    .nms-wrap { display: grid; grid-template-columns: minmax(0, 1fr) 9rem; gap: var(--s4); align-items: start; }
    .legend { list-style: none; padding: 0; margin: 0; display: grid; gap: 4px; font-family: var(--font-mono); }
    .legend li { padding: 4px 8px; border-radius: 6px; background: var(--card-2); }
    .legend li.kept { background: rgba(55,204,149,.3); }
    .legend li.gone { opacity: .45; text-decoration: line-through; }
    .seq { font-family: var(--font-mono); font-size: 1.1rem; }
    body.projector .board { max-width: 1100px; }
'''

NMS_BODY = '''        <div class="panel" id="play">
          <p>Click the boxes you would <strong>keep</strong>, in the order NMS keeps them (IoU threshold <strong>0.5</strong>). Then press Check.</p>
          <div class="nms-wrap">
            <svg class="board" id="board" viewBox="0 0 600 400" aria-label="Scored boxes"></svg>
            <div><p class="small muted" style="margin-bottom:6px">Box · confidence</p><ol class="legend" id="legend"></ol></div>
          </div>
          <p class="seq">Your order: <span id="mine">—</span></p>
          <div class="rowline"><button type="button" class="btn btn--ghost" id="undo">Undo</button><button type="button" class="btn" id="check">Check</button></div>
          <div class="verdict hidden" id="verdict"></div>
          <p><button type="button" class="btn hidden" id="next">Next round →</button></p>
        </div>
        <div class="panel finish hidden" id="finish">
          <h2 style="font-family:var(--font-display);font-size:1.6rem">Suppression complete</h2>
          <p class="finish__score" id="final">0 / 25</p>
          <div class="rowline"><button type="button" class="btn" id="again">Play again</button><a class="btn btn--ghost" href="./index.html">All activities</a></div>
        </div>
        <div class="panel"><h2>The rule</h2><p class="small muted">Keep the highest-confidence box, delete every remaining box that overlaps it by more than IoU 0.5, then repeat with the next highest box left (slide 2.47). Perfect order: 5 points. Each wrong, missing or out-of-order box costs 1.</p></div>'''

NMS_JS = '''
(function () {
  'use strict';
  var ROUNDS = __ROUNDS__, MAX = 25, r, score, picked, locked;
  var svg = document.getElementById('board');
  function draw() {
    var R = ROUNDS[r], html = '';
    R.boxes.slice().reverse().forEach(function (b) {
      var cls = 'bx' + (picked.indexOf(b.id) >= 0 ? ' kept' : '') + (locked && R.keep.indexOf(b.id) < 0 ? ' gone' : '');
      html += '<rect class="' + cls + '" data-id="' + b.id + '" x="' + b.b[0] + '" y="' + b.b[1] + '" width="' + (b.b[2] - b.b[0]) + '" height="' + (b.b[3] - b.b[1]) + '"/>';
    });
    R.boxes.forEach(function (b, k) {
      var c = k % 4, x = c % 2 ? b.b[2] - 16 : b.b[0] + 4, y = c < 2 ? b.b[1] + 17 : b.b[3] - 6;
      html += '<text x="' + x + '" y="' + y + '">' + b.id + '</text>';
    });
    svg.innerHTML = html;
    document.getElementById('legend').innerHTML = R.boxes.map(function (b) {
      return '<li class="' + (picked.indexOf(b.id) >= 0 ? 'kept' : '') + (locked && R.keep.indexOf(b.id) < 0 ? ' gone' : '') + '"><b>' + b.id + '</b> ' + b.s.toFixed(2) + '</li>';
    }).join('');
    document.getElementById('mine').textContent = picked.length ? picked.join(' → ') : '—';
  }
  svg.addEventListener('click', function (e) {
    var id = e.target.getAttribute && e.target.getAttribute('data-id');
    if (!id || locked) return;
    var k = picked.indexOf(id);
    if (k >= 0) picked.splice(k, 1); else picked.push(id);
    draw();
  });
  document.getElementById('undo').addEventListener('click', function () { if (!locked) { picked.pop(); draw(); } });
  document.getElementById('check').addEventListener('click', function () {
    if (locked) return; locked = true;
    var K = ROUNDS[r].keep, errors = 0;
    var n = Math.max(K.length, picked.length);
    for (var k = 0; k < n; k++) if (picked[k] !== K[k]) errors++;
    var pts = Math.max(0, 5 - errors);
    score += pts; Act.setScore(score);
    draw();
    var el = document.getElementById('verdict');
    el.className = 'verdict ' + (pts === 5 ? 'verdict--good' : pts >= 3 ? 'verdict--warn' : 'verdict--bad');
    el.innerHTML = '<h3>' + (pts === 5 ? 'Perfect NMS: +5' : '+' + pts) + '</h3><p class="seq">Correct sequence: ' + K.join(' → ') + '</p><p>Dashed boxes are the ones NMS suppresses: each overlaps a higher-scoring kept box by more than 0.5.</p>';
    var nb = document.getElementById('next'); nb.classList.remove('hidden'); nb.focus();
  });
  function load() {
    picked = []; locked = false; draw();
    document.getElementById('verdict').classList.add('hidden');
    document.getElementById('next').classList.add('hidden');
    Act.setRound((r + 1) + ' / ' + ROUNDS.length);
  }
  document.getElementById('next').addEventListener('click', function () { r++; if (r >= ROUNDS.length) finish(); else load(); });
  document.getElementById('again').addEventListener('click', start);
  function finish() {
    Act.finish(score);
    document.getElementById('play').classList.add('hidden');
    document.getElementById('finish').classList.remove('hidden');
    document.getElementById('final').textContent = score + ' / ' + MAX;
  }
  function start() {
    r = 0; score = 0; Act.setScore(0);
    document.getElementById('play').classList.remove('hidden');
    document.getElementById('finish').classList.add('hidden');
    load();
  }
  Act.init({ id: 'be-nms', max: MAX });
  start();
})();
'''


def be_nms():
    return NMS_STYLE, NMS_BODY, NMS_JS.replace('__ROUNDS__', json.dumps(nms_rounds())), 'A detector fired several overlapping, scored boxes on each object. You are Non-Maximum Suppression: click the boxes to keep, in the right order, at IoU 0.5. Five rounds; the correct sequence is shown after each one.'


# ------------------------------------------------------------ Threshold Tycoon
def tycoon_data():
    rnd = random.Random(9)
    biz = [
        {'name': 'Airport security', 'story': 'Your detector flags weapons in X-ray bag scans. A flagged bag gets a 30-second manual check. A missed weapon is a disaster.',
         'fp': 1, 'fn': 50, 'unit': 'cost points'},
        {'name': 'Shop people-counting', 'story': 'A camera counts customers walking in, for a footfall report. A phantom person and a missed person are equally wrong.',
         'fp': 1, 'fn': 1, 'unit': 'cost points'},
        {'name': 'Clinic screening', 'story': 'A model flags chest X-rays for a doctor to review. A false alarm costs a doctor\'s time; a missed finding delays treatment badly.',
         'fp': 3, 'fn': 15, 'unit': 'cost points'},
    ]
    for b in biz:
        preds = []
        for _ in range(18):          # real objects: scores lean high
            preds.append({'s': round(min(0.99, max(0.05, rnd.gauss(0.68, 0.18))), 2), 'y': 1})
        for _ in range(22):          # false detections: scores lean low
            preds.append({'s': round(min(0.97, max(0.02, rnd.gauss(0.35, 0.18))), 2), 'y': 0})
        preds.sort(key=lambda p: -p['s'])
        b['preds'] = preds
        best = None
        for t in [k / 100 for k in range(0, 101)]:
            fp = sum(1 for p in preds if p['s'] >= t and not p['y'])
            fn = sum(1 for p in preds if p['s'] < t and p['y'])
            c = fp * b['fp'] + fn * b['fn']
            if best is None or c < best[1]:
                best = (t, c)
        b['best_t'], b['best_cost'] = best
    return biz


TT_STYLE = '''
    .tt-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--s4); }
    @media (max-width: 800px) { .tt-grid { grid-template-columns: 1fr; } }
    .slider { width: 100%; accent-color: var(--teal); }
    .thr { font-family: var(--font-display); font-size: 3rem; color: var(--teal); line-height: 1; }
    .dots { display: flex; flex-wrap: wrap; gap: 4px; }
    .dot { width: 2.5rem; padding: 3px 0; text-align: center; border-radius: 6px; font: 600 0.75rem var(--font-mono); border: 2px solid transparent; }
    .dot.pos { background: rgba(11,116,87,.16); }
    .dot.neg { background: rgba(228,96,42,.14); }
    .dot.on { border-color: var(--ink); }
    .dot.off { opacity: .35; }
'''

TT_BODY = '''        <div class="panel" id="play">
          <h2 id="bname">Business</h2>
          <p id="story"></p>
          <div class="tt-grid">
            <div>
              <label for="slider" class="small muted">Confidence threshold</label>
              <div class="thr" id="thr">0.50</div>
              <input type="range" class="slider" id="slider" min="0" max="1" step="0.01" value="0.5">
              <div class="statgrid" style="margin-top:var(--s3)">
                <div class="stat"><b id="tp">0</b><span>True positives</span></div>
                <div class="stat"><b id="fp">0</b><span>False positives</span></div>
                <div class="stat"><b id="fn">0</b><span>False negatives</span></div>
                <div class="stat"><b id="prec">0</b><span>Precision</span></div>
                <div class="stat"><b id="rec">0</b><span>Recall</span></div>
              </div>
              <p style="margin-top:var(--s3)"><button type="button" class="btn" id="lock">Lock in this threshold</button></p>
            </div>
            <div>
              <p class="small muted">The 40 detections, sorted by confidence. Green = a real object, orange = a false detection. Boxes with a dark border pass the threshold.</p>
              <div class="dots" id="dots"></div>
            </div>
          </div>
          <div class="verdict hidden" id="verdict"></div>
          <p><button type="button" class="btn hidden" id="next">Next business →</button></p>
        </div>
        <div class="panel finish hidden" id="finish">
          <h2 style="font-family:var(--font-display);font-size:1.6rem">Quarter closed</h2>
          <p class="finish__score" id="final">0 / 30</p>
          <p class="muted">Same detector quality, three different best thresholds — because the cost of each error is different (slide 2.80).</p>
          <div class="rowline"><button type="button" class="btn" id="again">Play again</button><a class="btn btn--ghost" href="./index.html">All activities</a></div>
        </div>
        <div class="panel"><h2>Scoring</h2><p class="small muted">Each business hides a cost for a false positive and a cost for a false negative. When you lock in, your total cost is compared with the best possible threshold: matching the optimum scores 10, and the score falls in proportion as your cost rises above it.</p></div>'''

TT_JS = '''
(function () {
  'use strict';
  var BIZ = __BIZ__, MAX = 30, b, score, locked;
  var slider = document.getElementById('slider');
  function stats(t) {
    var P = BIZ[b].preds, tp = 0, fp = 0, fn = 0;
    P.forEach(function (p) { if (p.s >= t) { if (p.y) tp++; else fp++; } else if (p.y) fn++; });
    return { tp: tp, fp: fp, fn: fn, prec: tp + fp ? tp / (tp + fp) : 1, rec: tp / (tp + fn) };
  }
  function update() {
    var t = parseFloat(slider.value), s = stats(t);
    document.getElementById('thr').textContent = t.toFixed(2);
    ['tp', 'fp', 'fn'].forEach(function (k) { document.getElementById(k).textContent = s[k]; });
    document.getElementById('prec').textContent = s.prec.toFixed(2);
    document.getElementById('rec').textContent = s.rec.toFixed(2);
    document.getElementById('dots').innerHTML = BIZ[b].preds.map(function (p) {
      return '<span class="dot ' + (p.y ? 'pos' : 'neg') + ' ' + (p.s >= t ? 'on' : 'off') + '">' + p.s.toFixed(2) + '</span>';
    }).join('');
  }
  slider.addEventListener('input', function () { if (!locked) update(); });
  document.getElementById('lock').addEventListener('click', function () {
    if (locked) return; locked = true; slider.disabled = true;
    var B = BIZ[b], t = parseFloat(slider.value), s = stats(t);
    var cost = s.fp * B.fp + s.fn * B.fn;
    var pts = cost === 0 ? 10 : Math.round(10 * B.best_cost / cost);
    if (B.best_cost === 0 && cost > 0) pts = Math.max(0, 10 - cost);
    score += pts; Act.setScore(score);
    var el = document.getElementById('verdict');
    el.className = 'verdict ' + (pts >= 8 ? 'verdict--good' : pts >= 5 ? 'verdict--warn' : 'verdict--bad');
    el.innerHTML = '<h3>Your cost: ' + cost + ' · best possible: ' + B.best_cost + ' at threshold ' + B.best_t.toFixed(2) + ' · +' + pts + '</h3>' +
      '<p>Hidden costs: a false positive cost <strong>' + B.fp + '</strong>, a false negative cost <strong>' + B.fn + '</strong>. ' +
      (B.fn > B.fp * 5 ? 'Misses are far worse here, so the best threshold is low: accept false alarms to catch almost everything.' :
       B.fn === B.fp ? 'Both errors cost the same, so the best threshold balances them.' : 'Misses cost more than false alarms, so the best threshold sits below the middle.') + '</p>';
    var nb = document.getElementById('next'); nb.classList.remove('hidden'); nb.focus();
  });
  function load() {
    locked = false; slider.disabled = false; slider.value = 0.5;
    document.getElementById('bname').textContent = (b + 1) + ' · ' + BIZ[b].name;
    document.getElementById('story').textContent = BIZ[b].story;
    document.getElementById('verdict').classList.add('hidden');
    document.getElementById('next').classList.add('hidden');
    Act.setRound((b + 1) + ' / 3');
    update();
  }
  document.getElementById('next').addEventListener('click', function () { b++; if (b >= BIZ.length) finish(); else load(); });
  document.getElementById('again').addEventListener('click', start);
  function finish() {
    Act.finish(score);
    document.getElementById('play').classList.add('hidden');
    document.getElementById('finish').classList.remove('hidden');
    document.getElementById('final').textContent = score + ' / ' + MAX;
  }
  function start() {
    b = 0; score = 0; Act.setScore(0);
    document.getElementById('play').classList.remove('hidden');
    document.getElementById('finish').classList.add('hidden');
    load();
  }
  Act.init({ id: 'threshold-tycoon', max: MAX });
  start();
})();
'''


def threshold_tycoon():
    return TT_STYLE, TT_BODY, TT_JS.replace('__BIZ__', json.dumps(tycoon_data())), 'You run detection for three businesses: airport security, a shop counting people, and a clinic screening X-rays. For each, slide the confidence threshold over 40 labelled detections and watch precision and recall. Each business hides different costs for false alarms and misses — lock in the threshold you think is cheapest.'
