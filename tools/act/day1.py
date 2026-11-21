import json
from .pixelart import all_images

# ------------------------------------------------------------ Pixel Detective
PD_STYLE = '''
    .pd-wrap { display: grid; grid-template-columns: minmax(0, 1fr) 18rem; gap: var(--s4); align-items: start; }
    @media (max-width: 900px) { .pd-wrap { grid-template-columns: 1fr; } }
    .pd-grid { border-collapse: collapse; font-family: var(--font-mono); font-size: 0.56rem; line-height: 1; margin: 0 auto; }
    .pd-grid td { width: 1.55rem; height: 1.55rem; text-align: center; padding: 0; border: 1px solid rgba(0,0,0,.06); transition: background-color .4s; }
    body.projector .pd-grid { font-size: 0.62rem; }
    body.projector .pd-grid td { width: 2.1rem; height: 2.1rem; }
    .pd-steps { display: flex; gap: 6px; margin: var(--s2) 0 var(--s3); }
    .pd-steps span { flex: 1; height: 8px; border-radius: 4px; background: var(--border); }
    .pd-steps span.on { background: var(--coral); }
    .pd-side h2 { margin-bottom: var(--s2); }
'''

PD_BODY = '''        <div class="panel" id="play">
          <div class="pd-wrap">
            <div><table class="pd-grid" id="grid" aria-label="24 by 24 grid of pixel values"></table></div>
            <div class="pd-side">
              <h2 id="step-title">Step 1 of 5 · numbers only</h2>
              <div class="pd-steps" id="steps"><span></span><span></span><span></span><span></span><span></span></div>
              <p class="small muted" id="step-help">0 = black, 255 = white. This is all a computer receives. What is it?</p>
              <div class="choices" id="choices"></div>
              <p style="margin-top:var(--s3)"><button type="button" class="btn btn--ghost" id="reveal">Reveal more (−1 point)</button></p>
              <div class="verdict hidden" id="verdict"></div>
              <p><button type="button" class="btn hidden" id="next">Next image →</button></p>
            </div>
          </div>
        </div>
        <div class="panel finish hidden" id="finish">
          <h2 style="font-family:var(--font-display);font-size:1.6rem">Case closed</h2>
          <p class="finish__score" id="final">0 / 50</p>
          <p class="muted" id="final-note"></p>
          <div class="rowline"><button type="button" class="btn" id="again">Play again</button><a class="btn btn--ghost" href="./index.html">All activities</a></div>
        </div>
        <div class="panel">
          <h2>What this shows</h2>
          <p class="small muted">A computer never sees a cup: it receives 576 numbers. Each step blurs less: step 2 averages 4 × 4 blocks,
          step 3 averages 2 × 2 blocks, step 4 shows every pixel at low contrast and step 5 shows the real 24 × 24 image. Recognising the object
          from the numbers alone is the problem the whole course solves (slide 1.14, the semantic gap).</p>
        </div>'''

PD_JS = '''
(function () {
  'use strict';
  var IMAGES = __IMAGES__;
  var MAX = 50, STEP_NAMES = ['numbers only', 'coarse 6 × 6 blur', 'finer 12 × 12 blur', 'every pixel, faint', 'the full image'];
  var order, i, step, score, rand;
  var grid = document.getElementById('grid');

  function shuffle(a, r) { for (var k = a.length - 1; k > 0; k--) { var j = Math.floor(r() * (k + 1)); var t = a[k]; a[k] = a[j]; a[j] = t; } return a; }

  function blockAvg(px, b) {
    var out = [];
    for (var y = 0; y < 24; y++) { out.push([]); for (var x = 0; x < 24; x++) {
      var y0 = Math.floor(y / b) * b, x0 = Math.floor(x / b) * b, s = 0;
      for (var yy = y0; yy < y0 + b; yy++) for (var xx = x0; xx < x0 + b; xx++) s += px[yy][xx];
      out[y].push(Math.round(s / (b * b)));
    } }
    return out;
  }

  function render() {
    var img = IMAGES[order[i]], px = img.px, shade = null;
    if (step === 2) shade = blockAvg(px, 4);
    if (step === 3) shade = blockAvg(px, 2);
    if (step >= 4) shade = px;
    var html = '';
    for (var y = 0; y < 24; y++) {
      html += '<tr>';
      for (var x = 0; x < 24; x++) {
        var v = px[y][x], bg = '#ffffff', fg = '#14181f';
        if (shade) {
          var s = shade[y][x];
          if (step === 4) s = Math.round(255 - (255 - s) * 0.45);
          bg = 'rgb(' + s + ',' + s + ',' + s + ')';
          fg = s < 120 ? '#ffffff' : '#14181f';
        }
        html += '<td style="background:' + bg + ';color:' + fg + '">' + (step < 5 ? v : '') + '</td>';
      }
      html += '</tr>';
    }
    grid.innerHTML = html;
    document.getElementById('step-title').textContent = 'Step ' + step + ' of 5 · ' + STEP_NAMES[step - 1];
    Array.prototype.forEach.call(document.querySelectorAll('#steps span'), function (s, k) { s.className = k < step ? 'on' : ''; });
    document.getElementById('reveal').disabled = step >= 5;
  }

  function load() {
    step = 1;
    var img = IMAGES[order[i]];
    var others = shuffle(IMAGES.filter(function (o) { return o.name !== img.name; }).map(function (o) { return o.name; }), rand).slice(0, 3);
    var opts = shuffle(others.concat([img.name]), rand);
    var box = document.getElementById('choices'); box.innerHTML = '';
    opts.forEach(function (name) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'choice'; b.textContent = name;
      b.addEventListener('click', function () { guess(b, name === img.name); });
      box.appendChild(b);
    });
    document.getElementById('verdict').classList.add('hidden');
    document.getElementById('next').classList.add('hidden');
    document.getElementById('reveal').classList.remove('hidden');
    Act.setRound((i + 1) + ' / 10');
    render();
  }

  function guess(btn, right) {
    var pts = right ? 6 - step : 0, img = IMAGES[order[i]];
    score += pts; Act.setScore(score);
    Array.prototype.forEach.call(document.querySelectorAll('.choice'), function (c) {
      c.disabled = true; if (c.textContent === img.name) c.classList.add('is-right');
    });
    if (!right) btn.classList.add('is-wrong');
    var v = document.getElementById('verdict');
    v.className = 'verdict ' + (right ? 'verdict--good' : 'verdict--bad');
    v.innerHTML = '<h3>' + (right ? 'Correct at step ' + step + ': +' + pts : 'Not quite: it was ' + img.label + '. +0') + '</h3>';
    step = 5; render();
    document.getElementById('reveal').classList.add('hidden');
    var nb = document.getElementById('next'); nb.classList.remove('hidden'); nb.focus();
  }

  document.getElementById('reveal').addEventListener('click', function () { if (step < 5) { step++; render(); } });
  document.getElementById('next').addEventListener('click', function () { i++; if (i >= 10) finish(); else load(); });
  document.getElementById('again').addEventListener('click', start);

  function finish() {
    Act.finish(score);
    document.getElementById('play').classList.add('hidden');
    document.getElementById('finish').classList.remove('hidden');
    document.getElementById('final').textContent = score + ' / ' + MAX;
    document.getElementById('final-note').textContent = score >= 35 ? 'Sharp eyes: you read meaning out of raw numbers.' : 'Hard, right? That is exactly why vision took fifty years.';
  }

  function start() {
    rand = Act.rng(2211); order = shuffle(IMAGES.map(function (_, k) { return k; }), rand);
    i = 0; score = 0; Act.setScore(0);
    document.getElementById('play').classList.remove('hidden');
    document.getElementById('finish').classList.add('hidden');
    load();
  }

  Act.init({ id: 'pixel-detective', max: MAX });
  start();
})();
'''


def pixel_detective():
    return PD_STYLE, PD_BODY, PD_JS.replace('__IMAGES__', json.dumps(all_images(), separators=(',', ':'))), \
        'Ten mystery images arrive as raw pixel values — exactly what a computer receives. Reveal them step by step and name the object as early as you can. Correct at step 1 = 5 points, step 2 = 4 … step 5 = 1. A wrong guess scores 0.'


# ------------------------------------------------------------ Be the Kernel
BK_STYLE = '''
    .bk-row { display: flex; gap: var(--s5); align-items: center; flex-wrap: wrap; margin-bottom: var(--s4); }
    .bk-op { font-family: var(--font-display); font-size: 2.4rem; color: var(--text-muted); }
    .bk-label { font-size: 0.72rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px; }
    body.projector .matrix td { width: 4.6rem; height: 4.6rem; font-size: 1.8rem; }
    .bk-work { font-family: var(--font-mono); font-size: 0.9rem; }
'''

BK_BODY = '''        <div class="panel" id="play">
          <p class="rowline"><span class="badge badge--plain" id="kname">kernel</span> <span class="timer muted" id="timer">0 s</span> <span class="muted small" id="streak">streak 0</span></p>
          <div class="bk-row">
            <div><p class="bk-label">Image patch</p><table class="matrix" id="patch"></table></div>
            <span class="bk-op">⊛</span>
            <div><p class="bk-label">Kernel</p><table class="matrix" id="kernel"></table></div>
            <span class="bk-op">=</span>
            <form id="form" class="field">
              <label for="answer">One output pixel</label>
              <input type="number" id="answer" step="any" required autocomplete="off">
              <button type="submit" class="btn">Check</button>
            </form>
          </div>
          <p class="small muted">Multiply each pair of numbers in the same position, then add all nine products. For the blur kernel, add the nine numbers and divide by 9.</p>
          <div class="verdict hidden" id="verdict"></div>
          <p><button type="button" class="btn hidden" id="next">Next round →</button></p>
        </div>
        <div class="panel finish hidden" id="finish">
          <h2 style="font-family:var(--font-display);font-size:1.6rem">Convolution complete</h2>
          <p class="finish__score" id="final">0 / 40</p>
          <div class="rowline"><button type="button" class="btn" id="again">Play again</button><a class="btn btn--ghost" href="./index.html">All activities</a></div>
        </div>
        <div class="panel"><h2>Scoring</h2><p class="small muted">Correct answer: 2 points. Answered within 20 seconds: +1. Three or more correct in a row (a streak): +1. Ten rounds, so 40 points at most. This multiply-and-add is exactly what every convolution layer does millions of times (slide 1.40).</p></div>'''

BK_JS = '''
(function () {
  'use strict';
  var KERNELS = [
    { name: 'Sobel-x (vertical edges)', k: [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], div: 1 },
    { name: 'Box blur (÷ 9)', k: [[1, 1, 1], [1, 1, 1], [1, 1, 1]], div: 9 },
    { name: 'Sharpen', k: [[0, -1, 0], [-1, 5, -1], [0, -1, 0]], div: 1 }
  ];
  var MAX = 40, ROUNDS = 10, round, score, streak, rand, cur, t0, timerId;

  function table(id, m, cls) {
    document.getElementById(id).innerHTML = m.map(function (r) {
      return '<tr>' + r.map(function (v) { return '<td' + (cls ? ' class="' + cls + '"' : '') + '>' + v + '</td>'; }).join('') + '</tr>';
    }).join('');
  }

  function load() {
    var K = KERNELS[round % 3];
    var p = [0, 1, 2].map(function () { return [0, 1, 2].map(function () { return Math.floor(rand() * 10); }); });
    if (K.div === 9) {                      // make the blur answer a whole number
      var s = 0; p.forEach(function (r, y) { r.forEach(function (v, x) { if (y !== 1 || x !== 1) s += v; }); });
      p[1][1] = (9 - s % 9) % 9;
    }
    var sum = 0, work = [];
    for (var y = 0; y < 3; y++) for (var x = 0; x < 3; x++) { sum += p[y][x] * K.k[y][x]; if (K.k[y][x] !== 0) work.push(p[y][x] + '·' + K.k[y][x]); }
    cur = { K: K, p: p, ans: sum / K.div, work: work.join(' + ').replace(/\\+ -/g, '− ').replace(/·-/g, '·−') };
    table('patch', p); table('kernel', K.k, 'k');
    document.getElementById('kname').textContent = K.name;
    document.getElementById('verdict').classList.add('hidden');
    document.getElementById('next').classList.add('hidden');
    document.getElementById('form').classList.remove('hidden');
    var a = document.getElementById('answer'); a.value = ''; a.focus();
    Act.setRound((round + 1) + ' / ' + ROUNDS);
    t0 = Date.now(); clearInterval(timerId);
    timerId = setInterval(function () { document.getElementById('timer').textContent = Math.floor((Date.now() - t0) / 1000) + ' s'; }, 250);
  }

  document.getElementById('form').addEventListener('submit', function (e) {
    e.preventDefault();
    clearInterval(timerId);
    var v = parseFloat(document.getElementById('answer').value), secs = (Date.now() - t0) / 1000;
    var right = Math.abs(v - cur.ans) < 0.01, pts = 0;
    if (right) { streak++; pts = 2 + (secs <= 20 ? 1 : 0) + (streak >= 3 ? 1 : 0); } else streak = 0;
    score += pts; Act.setScore(score);
    document.getElementById('streak').textContent = 'streak ' + streak;
    var el = document.getElementById('verdict');
    el.className = 'verdict ' + (right ? 'verdict--good' : 'verdict--bad');
    el.innerHTML = '<h3>' + (right ? 'Correct: +' + pts + (secs <= 20 ? ' (fast)' : '') + (streak >= 3 ? ' (streak)' : '') : 'The answer is ' + cur.ans + '. +0') + '</h3>' +
      '<p class="bk-work">' + cur.work + (cur.K.div === 9 ? ' = ' + (cur.ans * 9) + ', ÷ 9 = ' + cur.ans : ' = ' + cur.ans) + '</p>';
    document.getElementById('form').classList.add('hidden');
    var nb = document.getElementById('next'); nb.classList.remove('hidden'); nb.focus();
  });
  document.getElementById('next').addEventListener('click', function () { round++; if (round >= ROUNDS) finish(); else load(); });
  document.getElementById('again').addEventListener('click', start);

  function finish() {
    Act.finish(score);
    document.getElementById('play').classList.add('hidden');
    document.getElementById('finish').classList.remove('hidden');
    document.getElementById('final').textContent = score + ' / ' + MAX;
  }
  function start() {
    rand = Act.rng(4013); round = 0; score = 0; streak = 0; Act.setScore(0);
    document.getElementById('play').classList.remove('hidden');
    document.getElementById('finish').classList.add('hidden');
    load();
  }
  Act.init({ id: 'be-the-kernel', max: MAX });
  start();
})();
'''


def be_the_kernel():
    return BK_STYLE, BK_BODY, BK_JS, 'You are the convolution. Each round shows a 3 × 3 image patch and a kernel (Sobel-x, blur or sharpen). Multiply, add, and type the one output pixel. Ten rounds, with a timer and streak bonuses.'


# ------------------------------------------------------------ Shape Race
SR_STYLE = '''
    .sr-stack { list-style: none; padding: 0; margin: 0 0 var(--s4); display: grid; gap: 6px; max-width: 38rem; }
    .sr-stack li { display: grid; grid-template-columns: 2rem 1fr auto; gap: var(--s3); align-items: center; padding: 0.55rem 0.9rem; border-radius: var(--radius-sm); border: 1px solid var(--border); background: var(--card); font-family: var(--font-mono); }
    .sr-stack li b { font-family: var(--font-display); color: var(--teal); }
    .sr-stack li .out { color: var(--text-muted); }
    .formula { font-family: var(--font-mono); font-size: 1.2rem; padding: var(--s3); background: #fdf3e2; border-radius: var(--radius-sm); border-left: 5px solid var(--amber); }
    .sr-inputs { display: flex; gap: var(--s3); align-items: flex-end; flex-wrap: wrap; }
'''

SR_BODY = '''        <div class="panel" id="play">
          <h2>What shape comes out?</h2>
          <ol class="sr-stack" id="stack"></ol>
          <form id="form" class="sr-inputs">
            <div class="field"><label for="c">Channels C</label><input type="number" id="c" required min="1"></div>
            <div class="field"><label for="w">Height = width</label><input type="number" id="w" required min="1"></div>
            <button type="submit" class="btn">Check</button>
            <button type="button" class="btn btn--ghost" id="show-formula">Show the formula (−1)</button>
          </form>
          <p class="formula hidden" id="formula">Output = ⌊(W − K + 2P) / S⌋ + 1 &nbsp;·&nbsp; channels = number of kernels (C_out); pooling keeps the channels</p>
          <div class="verdict hidden" id="verdict"></div>
          <p><button type="button" class="btn hidden" id="next">Next stack →</button></p>
        </div>
        <div class="panel finish hidden" id="finish">
          <h2 style="font-family:var(--font-display);font-size:1.6rem">Race over</h2>
          <p class="finish__score" id="final">0 / 24</p>
          <div class="rowline"><button type="button" class="btn" id="again">Play again</button><a class="btn btn--ghost" href="./index.html">All activities</a></div>
        </div>'''

SR_JS = '''
(function () {
  'use strict';
  var MAX = 24, ROUNDS = 8, round, score, rand, cur, peeked;
  function pick(a) { return a[Math.floor(rand() * a.length)]; }
  function out(W, K, P, S) { return Math.floor((W - K + 2 * P) / S) + 1; }

  function makeStack() {
    var W = pick([32, 64, 96, 128, 224]), C = 3, layers = [], n = 3 + Math.floor(rand() * 2);
    var start = { C: C, W: W };
    for (var k = 0; k < n; k++) {
      var L;
      if (rand() < 0.35 && W >= 4) L = { type: 'MaxPool', K: 2, P: 0, S: 2 };
      else {
        var K = pick([1, 3, 3, 5, 7]), P = pick([0, Math.floor(K / 2)]), S = pick([1, 1, 2]);
        L = { type: 'Conv', K: K, P: P, S: S, Cout: pick([16, 32, 64, 128]) };
      }
      var W2 = out(W, L.K, L.P, L.S);
      if (W2 < 1) { k--; continue; }
      L.Win = W; W = W2; L.Wout = W; if (L.type === 'Conv') C = L.Cout; L.Cout = C;
      layers.push(L);
    }
    return { start: start, layers: layers, C: C, W: W };
  }

  function load() {
    cur = makeStack(); peeked = false;
    var html = '<li><b>in</b><span>input image</span><span class="out">' + cur.start.C + ' × ' + cur.start.W + ' × ' + cur.start.W + '</span></li>';
    cur.layers.forEach(function (L, k) {
      html += '<li><b>' + (k + 1) + '</b><span>' + (L.type === 'Conv' ? 'Conv ' + L.Cout + ' kernels, K=' + L.K + ', P=' + L.P + ', S=' + L.S : 'MaxPool K=2, S=2') +
              '</span><span class="out">?</span></li>';
    });
    document.getElementById('stack').innerHTML = html;
    ['c', 'w'].forEach(function (id) { document.getElementById(id).value = ''; });
    document.getElementById('formula').classList.add('hidden');
    document.getElementById('verdict').classList.add('hidden');
    document.getElementById('next').classList.add('hidden');
    document.getElementById('form').classList.remove('hidden');
    document.getElementById('c').focus();
    Act.setRound((round + 1) + ' / ' + ROUNDS);
  }

  document.getElementById('show-formula').addEventListener('click', function () { peeked = true; document.getElementById('formula').classList.remove('hidden'); });
  document.getElementById('form').addEventListener('submit', function (e) {
    e.preventDefault();
    var c = parseInt(document.getElementById('c').value, 10), w = parseInt(document.getElementById('w').value, 10);
    var right = c === cur.C && w === cur.W, pts = right ? (peeked ? 2 : 3) : 0;
    score += pts; Act.setScore(score);
    var lines = cur.layers.map(function (L, k) {
      return (k + 1) + '. ⌊(' + L.Win + ' − ' + L.K + ' + 2·' + L.P + ') / ' + L.S + '⌋ + 1 = ' + L.Wout + ' → ' + L.Cout + ' × ' + L.Wout + ' × ' + L.Wout;
    });
    Array.prototype.forEach.call(document.querySelectorAll('#stack .out'), function (o, k) {
      if (k > 0) { var L = cur.layers[k - 1]; o.textContent = L.Cout + ' × ' + L.Wout + ' × ' + L.Wout; }
    });
    var v = document.getElementById('verdict');
    v.className = 'verdict ' + (right ? 'verdict--good' : 'verdict--bad');
    v.innerHTML = '<h3>' + (right ? 'Correct: +' + pts : 'Answer: ' + cur.C + ' × ' + cur.W + ' × ' + cur.W + '. +0') + '</h3><p style="font-family:var(--font-mono)">' + lines.join('<br>') + '</p>';
    document.getElementById('form').classList.add('hidden');
    var nb = document.getElementById('next'); nb.classList.remove('hidden'); nb.focus();
  });
  document.getElementById('next').addEventListener('click', function () { round++; if (round >= ROUNDS) finish(); else load(); });
  document.getElementById('again').addEventListener('click', start);
  function finish() {
    Act.finish(score);
    document.getElementById('play').classList.add('hidden');
    document.getElementById('finish').classList.remove('hidden');
    document.getElementById('final').textContent = score + ' / ' + MAX;
  }
  function start() {
    rand = Act.rng(7519); round = 0; score = 0; Act.setScore(0);
    document.getElementById('play').classList.remove('hidden');
    document.getElementById('finish').classList.add('hidden');
    load();
  }
  Act.init({ id: 'shape-race', max: MAX });
  start();
})();
'''


def shape_race():
    return SR_STYLE, SR_BODY, SR_JS, 'Each round gives a stack of conv and pool layers with W, K, P and S. Predict the final output shape: channels and height × width. 3 points per correct stack; peeking at the formula ⌊(W − K + 2P)/S⌋ + 1 costs 1 point.'


# ------------------------------------------------------------ Spot the Bug
BUGS = [
    {'title': 'Colours look wrong', 'lines': ['import cv2', 'import matplotlib.pyplot as plt', 'img = cv2.imread("palm.jpg")', 'plt.imshow(img)', 'plt.title("Palm tree")', 'plt.show()'],
     'bug': 3, 'fix': 'plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))',
     'why': 'OpenCV loads images as B, G, R. Matplotlib expects R, G, B, so blue and red swap: green palms, orange sky. Convert before showing (slide 1.27).'},
    {'title': 'Brightening makes it darker', 'lines': ['import numpy as np', 'img = cv2.imread("x_ray.png", 0)   # uint8', 'brighter = img + 100', 'brighter = np.clip(brighter, 0, 255)', 'cv2.imwrite("brighter.png", brighter)'],
     'bug': 2, 'fix': 'brighter = img.astype(np.int16) + 100',
     'why': 'uint8 wraps around at 256: 200 + 100 becomes 44, so bright pixels turn dark. Clipping afterwards is too late — convert to a larger type first, add, then clip (slide 1.26).'},
    {'title': 'The crop is in the wrong place', 'lines': ['# box from a detector: x1, y1, x2, y2 = 200, 50, 400, 150', 'x1, y1, x2, y2 = box', 'crop = img[x1:x2, y1:y2]', 'cv2.imwrite("crop.png", crop)'],
     'bug': 2, 'fix': 'crop = img[y1:y2, x1:x2]',
     'why': 'NumPy indexes rows first: img[y, x]. Swapping them crops a different region and raises no error (slide 1.24).'},
    {'title': 'Predictions change every run', 'lines': ['model = SmallCNN()', 'model.load_state_dict(torch.load("best.pt"))', 'with torch.no_grad():', '    logits = model(images)', 'preds = logits.argmax(dim=1)'],
     'bug': 1, 'fix': 'model.load_state_dict(torch.load("best.pt")); model.eval()',
     'why': 'A new model starts in training mode: dropout stays on and BatchNorm uses batch statistics, so the same image gets different predictions. Call model.eval() before inference (slide 1.98).'},
    {'title': 'A suspiciously great test score', 'lines': ['best_lr, best_acc = None, 0', 'for lr in [1e-2, 1e-3, 1e-4]:', '    model = train(train_set, lr)', '    acc = evaluate(model, test_set)', '    if acc > best_acc: best_lr, best_acc = lr, acc', 'print("final test accuracy:", best_acc)'],
     'bug': 3, 'fix': 'acc = evaluate(model, val_set)   # tune on validation; test once at the end',
     'why': 'Choosing the learning rate by the test score leaks the test set into your decisions, so the final number is optimistic — a lie. Tune on the validation set, keep the test set sealed (slide 1.56).'},
]

SB_STYLE = '''
    .code { font-family: var(--font-mono); font-size: 0.95rem; background: var(--ink); border-radius: var(--radius-sm); padding: var(--s2); }
    .code button { display: grid; grid-template-columns: 2rem 1fr; width: 100%; text-align: left; font: inherit; color: #e8ecf5; background: none; border: 0; border-radius: 6px; padding: 0.4rem 0.6rem; cursor: pointer; white-space: pre; }
    .code button:hover { background: rgba(255,255,255,.08); }
    .code button span:first-child { color: #93a4c4; }
    .code button.is-wrong { background: rgba(228,96,42,.35); }
    .code button.is-right { background: rgba(55,204,149,.35); }
    body.projector .code { font-size: 1.3rem; }
'''

SB_BODY = '''        <div class="panel" id="play">
          <h2 id="title">Bug</h2>
          <p class="small muted">Click the line that contains the bug.</p>
          <div class="code" id="code"></div>
          <div class="verdict hidden" id="verdict"></div>
          <p><button type="button" class="btn hidden" id="next">Next snippet →</button></p>
        </div>
        <div class="panel finish hidden" id="finish">
          <h2 style="font-family:var(--font-display);font-size:1.6rem">All bugs found</h2>
          <p class="finish__score" id="final">0 / 10</p>
          <div class="rowline"><button type="button" class="btn" id="again">Play again</button><a class="btn btn--ghost" href="./index.html">All activities</a></div>
        </div>'''

SB_JS = '''
(function () {
  'use strict';
  var BUGS = __BUGS__, MAX = 10, i, score, tries, done;
  function load() {
    var b = BUGS[i]; tries = 0; done = false;
    document.getElementById('title').textContent = (i + 1) + ' · ' + b.title;
    var box = document.getElementById('code'); box.innerHTML = '';
    b.lines.forEach(function (line, k) {
      var btn = document.createElement('button'); btn.type = 'button';
      btn.innerHTML = '<span>' + (k + 1) + '</span><span>' + Act.esc(line) + '</span>';
      btn.addEventListener('click', function () { click(btn, k); });
      box.appendChild(btn);
    });
    document.getElementById('verdict').classList.add('hidden');
    document.getElementById('next').classList.add('hidden');
    Act.setRound((i + 1) + ' / ' + BUGS.length);
  }
  function click(btn, k) {
    if (done) return;
    var b = BUGS[i]; tries++;
    if (k !== b.bug && tries < 2) { btn.classList.add('is-wrong'); return; }
    done = true;
    var pts = k === b.bug ? (tries === 1 ? 2 : 1) : 0;
    score += pts; Act.setScore(score);
    if (k !== b.bug) btn.classList.add('is-wrong');
    document.querySelectorAll('#code button')[b.bug].classList.add('is-right');
    var v = document.getElementById('verdict');
    v.className = 'verdict ' + (pts ? 'verdict--good' : 'verdict--bad');
    v.innerHTML = '<h3>' + (pts ? 'Found it: +' + pts : 'The bug is on line ' + (b.bug + 1) + '. +0') + '</h3><p><strong>Fix:</strong> <code>' + Act.esc(b.fix) + '</code></p><p>' + Act.esc(b.why) + '</p>';
    var nb = document.getElementById('next'); nb.classList.remove('hidden'); nb.focus();
  }
  document.getElementById('next').addEventListener('click', function () { i++; if (i >= BUGS.length) finish(); else load(); });
  document.getElementById('again').addEventListener('click', start);
  function finish() {
    Act.finish(score);
    document.getElementById('play').classList.add('hidden');
    document.getElementById('finish').classList.remove('hidden');
    document.getElementById('final').textContent = score + ' / ' + MAX;
  }
  function start() {
    i = 0; score = 0; Act.setScore(0);
    document.getElementById('play').classList.remove('hidden');
    document.getElementById('finish').classList.add('hidden');
    load();
  }
  Act.init({ id: 'spot-the-bug', max: MAX });
  start();
})();
'''


def spot_the_bug():
    return SB_STYLE, SB_BODY, SB_JS.replace('__BUGS__', json.dumps(BUGS)), 'Five short pieces of vision code, each with one real bug that does not crash — it just gives wrong results. Click the buggy line: right first time = 2 points, second try = 1. Then read the fix.'
