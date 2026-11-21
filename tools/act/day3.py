import json

NS = 'xmlns="http://www.w3.org/2000/svg"'


def svg(body, bg='#f4f1ea'):
    return f'<svg {NS} viewBox="0 0 224 224" width="224" height="224"><rect width="224" height="224" fill="{bg}"/>{body}</svg>'


APPLE = '<circle cx="{x}" cy="{y}" r="22" fill="#d7263d"/><rect x="{sx}" y="{sy}" width="4" height="12" fill="#5b3a1a"/><ellipse cx="{lx}" cy="{ly}" rx="9" ry="5" fill="#3a9d23"/>'


def apple(x, y):
    return APPLE.format(x=x, y=y, sx=x - 2, sy=y - 32, lx=x + 9, ly=y - 28)


CUP = '<path d="M{a},120 L{b},120 L{c},175 L{d},175 Z" fill="#ffffff" stroke="#3b2f2f" stroke-width="4"/><path d="M{e},132 q18,0 14,18 q-3,14 -16,12" fill="none" stroke="#3b2f2f" stroke-width="4"/><rect x="{f}" y="114" width="{g}" height="8" fill="#6f4e37"/>'


def cup(x):
    return CUP.format(a=x, b=x + 50, c=x + 44, d=x + 6, e=x + 48, f=x + 2, g=46)


SCENES = [
    {'id': 'apples', 'svg': svg('<rect y="170" width="224" height="54" fill="#a0703c"/>' + apple(60, 150) + apple(112, 150) + apple(164, 150)),
     'captions': ['three apples', 'a photo of three red apples on a table', 'a photo of five red apples on a table', 'a photo of a banana']},
    {'id': 'shapes', 'svg': svg('<circle cx="62" cy="112" r="38" fill="#e4302a"/><rect x="128" y="74" width="76" height="76" fill="#1f5fbf"/>', '#ffffff'),
     'captions': ['a red circle to the left of a blue square', 'a blue square to the left of a red circle', 'a red circle and a blue square', 'a green triangle']},
    {'id': 'ipod', 'svg': svg(apple(112, 120).replace('r="22"', 'r="62"').replace('height="12"', 'height="22"') +
                              '<rect x="66" y="104" width="92" height="34" fill="#ffffff" stroke="#999" stroke-width="2"/><text x="112" y="130" font-family="Arial" font-size="26" font-weight="700" text-anchor="middle" fill="#111">iPod</text>'),
     'captions': ['a photo of an apple', 'a photo of an iPod', 'a photo of a pear', 'a drawing of a fruit']},
    {'id': 'palm', 'svg': svg('<rect y="160" width="224" height="64" fill="#e8c27a"/><circle cx="182" cy="44" r="22" fill="#f6b21b"/>'
                              '<path d="M112,165 C108,130 104,100 110,70" stroke="#7a4b23" stroke-width="10" fill="none"/>'
                              '<path d="M110,70 C80,58 56,70 40,92 M110,70 C140,58 166,66 184,88 M110,70 C96,46 74,38 56,40 M110,70 C126,44 150,38 168,42 M110,70 C112,48 112,34 110,22" stroke="#2f8a2f" stroke-width="9" fill="none" stroke-linecap="round"/>', '#bfe3f5'),
     'captions': ['a palm tree in the desert', 'palm', 'a photo of a forest', 'a snowy mountain']},
    {'id': 'car', 'svg': svg('<rect y="150" width="224" height="74" fill="#555"/><rect y="182" width="224" height="5" fill="#f2f2f2"/>'
                             '<rect x="30" y="112" width="164" height="40" rx="12" fill="#d62828"/><path d="M62,112 L80,82 L146,82 L166,112 Z" fill="#d62828"/>'
                             '<path d="M84,108 L94,88 L120,88 L120,108 Z M126,108 L126,88 L144,88 L156,108 Z" fill="#cfe8ff"/>'
                             '<circle cx="68" cy="154" r="17" fill="#111"/><circle cx="158" cy="154" r="17" fill="#111"/>', '#bfe3f5'),
     'captions': ['a car', 'a drawing of a red car on a road', 'a photo of a bicycle', 'a red car parked in the snow']},
    {'id': 'stop', 'svg': svg('<rect x="106" y="140" width="12" height="84" fill="#888"/><polygon points="80,40 144,40 184,80 184,124 144,164 80,164 40,124 40,80" fill="#c1121f" stroke="#fff" stroke-width="5"/>'
                              '<text x="112" y="116" font-family="Arial" font-size="38" font-weight="700" text-anchor="middle" fill="#fff">STOP</text>', '#bfe3f5'),
     'captions': ['a stop sign', 'the word STOP', 'a red octagon', 'a traffic light']},
    {'id': 'cups', 'svg': svg('<rect y="175" width="224" height="49" fill="#a0703c"/>' + cup(40) + cup(124)),
     'captions': ['two cups of coffee', 'four cups of coffee', 'a drawing of two coffee cups', 'a teapot']},
    {'id': 'night', 'svg': svg('<circle cx="176" cy="46" r="20" fill="#f4f1c9"/><circle cx="168" cy="40" r="18" fill="#0d1b3e"/>'
                               '<circle cx="40" cy="30" r="2" fill="#fff"/><circle cx="90" cy="50" r="2" fill="#fff"/><circle cx="130" cy="24" r="2" fill="#fff"/>'
                               '<rect y="180" width="224" height="44" fill="#1e3d1e"/><polygon points="50,110 112,62 174,110" fill="#5a2a1a"/>'
                               '<rect x="62" y="108" width="100" height="74" fill="#6b6b80"/><rect x="78" y="124" width="24" height="22" fill="#ffd166"/><rect x="122" y="124" width="24" height="22" fill="#ffd166"/><rect x="102" y="152" width="20" height="30" fill="#2b1a10"/>', '#0d1b3e'),
     'captions': ['a house at night', 'a house during the day', 'a drawing of a house at night under a crescent moon', 'a castle']},
    {'id': 'mosque', 'svg': svg('<rect y="190" width="224" height="34" fill="#d9c6a0"/><rect x="48" y="130" width="128" height="62" fill="#f1ede2"/>'
                                '<path d="M60,132 A52,52 0 0 1 164,132 Z" fill="#2a9d8f"/><rect x="109" y="66" width="6" height="16" fill="#c9a227"/>'
                                '<circle cx="112" cy="60" r="8" fill="#c9a227"/><circle cx="116" cy="57" r="7" fill="#bfe3f5"/>'
                                '<rect x="182" y="70" width="18" height="122" fill="#f1ede2"/><polygon points="180,70 191,40 202,70" fill="#2a9d8f"/>'
                                '<path d="M100,192 L100,162 A12,12 0 0 1 124,162 L124,192 Z" fill="#7a5c3a"/>', '#bfe3f5'),
     'captions': ['a mosque', 'a drawing of a mosque with a green dome', 'a church', 'a dome']},
    {'id': 'clock', 'svg': svg('<circle cx="112" cy="112" r="84" fill="#ffffff" stroke="#222" stroke-width="8"/>' +
                               ''.join(f'<rect x="109" y="34" width="6" height="14" fill="#222" transform="rotate({a} 112 112)"/>' for a in range(0, 360, 30)) +
                               '<line x1="112" y1="112" x2="112" y2="52" stroke="#222" stroke-width="5" stroke-linecap="round"/>'
                               '<line x1="112" y1="112" x2="156" y2="112" stroke="#222" stroke-width="8" stroke-linecap="round"/><circle cx="112" cy="112" r="6" fill="#c1121f"/>', '#e9eef3'),
     'captions': ["a clock showing three o'clock", "a clock showing nine o'clock", 'a drawing of a clock', 'a wristwatch']},
]


ZS_STYLE = '''
    .zs { display: grid; grid-template-columns: 260px 1fr; gap: var(--s4); align-items: start; }
    @media (max-width: 760px) { .zs { grid-template-columns: 1fr; } }
    .zs svg { width: 100%; height: auto; border-radius: var(--radius-sm); border: 1px solid var(--border); }
    body.projector .zs { grid-template-columns: 420px 1fr; }
    .bar { height: 10px; border-radius: 5px; background: var(--teal-bright); margin-top: 4px; }
    .setup { border-left: 6px solid var(--amber); }
    .setup pre { background: var(--ink); color: #e8ecf5; padding: var(--s3); border-radius: var(--radius-sm); overflow-x: auto; }
'''

ZS_BODY = '''        <div class="panel setup hidden" id="setup">
          <h2>Teacher setup needed</h2>
          <p>This activity shows how a real CLIP model ranks the captions, so its scores must come from running CLIP — they are never made up. The scores file has not been generated yet.</p>
          <ol>
            <li>Open a new Colab notebook (a CPU runtime is enough).</li>
            <li>Run: <pre>!git clone https://github.com/mibnrashid/SDAIA_ComputerVision
%cd SDAIA_ComputerVision
!pip install -q cairosvg
!python tools/precompute_clip.py</pre></li>
            <li>Download the two files it writes, <code>activities/data/showdown.json</code> and <code>activities/data/showdown.js</code>, commit them to the repo (replacing the placeholder <code>showdown.js</code>), and reload this page.</li>
          </ol>
          <p class="small muted">The ten scenes are already on this page below the line; you can show them to the room while you set up.</p>
        </div>
        <div class="panel" id="play">
          <div class="zs">
            <div id="scene"></div>
            <div>
              <h2 id="qtitle">Which caption does CLIP rank highest?</h2>
              <div class="choices" id="choices" style="grid-template-columns:1fr"></div>
              <div class="verdict hidden" id="verdict"></div>
              <p><button type="button" class="btn hidden" id="next">Next scene →</button></p>
            </div>
          </div>
        </div>
        <div class="panel finish hidden" id="finish">
          <h2 style="font-family:var(--font-display);font-size:1.6rem">Showdown over</h2>
          <p class="finish__score" id="final">0 / 10</p>
          <p class="muted">CLIP likes caption-style wording, notices which words appear more than how they relate, struggles with counting and left/right, and can be hijacked by written text (slides 3.48–3.51).</p>
          <div class="rowline"><button type="button" class="btn" id="again">Play again</button><a class="btn btn--ghost" href="./index.html">All activities</a></div>
        </div>'''

ZS_JS = '''
(function () {
  'use strict';
  var SCENES = window.SHOWDOWN_SCENES || [], DATA = window.SHOWDOWN || null, MAX = 10, i, score;
  Act.init({ id: 'zero-shot-showdown', max: MAX });
  if (!DATA || !DATA.scenes) {
    document.getElementById('setup').classList.remove('hidden');
    document.getElementById('qtitle').textContent = 'Preview of the scenes (no scores yet)';
    i = 0;
    var show = function () {
      document.getElementById('scene').innerHTML = SCENES[i].svg;
      document.getElementById('choices').innerHTML = SCENES[i].captions.map(function (c) { return '<div class="choice">' + Act.esc(c) + '</div>'; }).join('');
      Act.setRound((i + 1) + ' / ' + SCENES.length);
    };
    var nb = document.getElementById('next'); nb.classList.remove('hidden'); nb.textContent = 'Next scene (preview) →';
    nb.addEventListener('click', function () { i = (i + 1) % SCENES.length; show(); });
    show();
    return;
  }
  var byId = {}; DATA.scenes.forEach(function (s) { byId[s.id] = s; });
  function load() {
    var S = SCENES[i], D = byId[S.id];
    document.getElementById('scene').innerHTML = S.svg;
    var box = document.getElementById('choices'); box.innerHTML = '';
    S.captions.forEach(function (c, k) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'choice'; b.textContent = c;
      b.addEventListener('click', function () { pick(k); });
      box.appendChild(b);
    });
    document.getElementById('verdict').classList.add('hidden');
    document.getElementById('next').classList.add('hidden');
    Act.setRound((i + 1) + ' / ' + SCENES.length);
  }
  function pick(k) {
    var S = SCENES[i], D = byId[S.id], best = D.best, right = k === best;
    if (right) { score++; Act.setScore(score); }
    Array.prototype.forEach.call(document.querySelectorAll('.choice'), function (c, j) {
      c.disabled = true;
      if (j === best) c.classList.add('is-right'); else if (j === k) c.classList.add('is-wrong');
      c.innerHTML = Act.esc(S.captions[j]) + ' <span class="small muted">' + (D.probs[j] * 100).toFixed(1) + '%</span><div class="bar" style="width:' + (D.probs[j] * 100).toFixed(1) + '%"></div>';
    });
    var v = document.getElementById('verdict');
    v.className = 'verdict ' + (right ? 'verdict--good' : 'verdict--bad');
    v.innerHTML = '<h3>' + (right ? 'You think like CLIP: +1' : 'CLIP preferred: “' + Act.esc(S.captions[best]) + '”') + '</h3><p>Probabilities from ' + Act.esc(DATA.model) + ' (softmax over these four captions).</p>';
    var nb = document.getElementById('next'); nb.classList.remove('hidden'); nb.focus();
  }
  document.getElementById('next').addEventListener('click', function () { i++; if (i >= SCENES.length) finish(); else load(); });
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
  start();
})();
'''


def zero_shot_showdown():
    return ZS_STYLE, ZS_BODY, ZS_JS, 'Ten simple scenes, four captions each. Pick the caption a real CLIP model (openai/clip-vit-base-patch32) ranks highest. Think like the model, not like a person: 1 point per scene.'


# ------------------------------------------------------------ Fool the Model
TYPES = ['Out-of-distribution', 'Typographic attack', 'Counting / spatial', 'Bias / shortcut', 'Hallucination']


def icon(body):
    return f'<svg viewBox="0 0 120 80" width="120" height="80" aria-hidden="true"><rect width="120" height="80" rx="8" fill="#eef1f5"/>{body}</svg>'


CARDS = [
    {'text': 'A cat-vs-dog classifier is shown a photo of a car. It answers "dog, 97%".', 'type': 0,
     'icon': icon('<rect x="25" y="38" width="70" height="20" rx="6" fill="#d62828"/><circle cx="42" cy="60" r="7"/><circle cx="80" cy="60" r="7"/><path d="M40,38 L50,26 L74,26 L84,38 Z" fill="#d62828"/>'),
     'why': 'A car is unlike anything in its training data, and softmax must split 100% between "cat" and "dog". High confidence on an unknown input is the closed-set problem (slides 3.09–3.11).'},
    {'text': 'An apple with a paper label reading "iPod" stuck on it is classified by CLIP as an iPod.', 'type': 1,
     'icon': icon('<circle cx="60" cy="42" r="26" fill="#d7263d"/><rect x="38" y="34" width="44" height="16" fill="#fff"/><text x="60" y="46" font-size="11" font-weight="700" text-anchor="middle">iPod</text>'),
     'why': 'CLIP learned to read text from captions, and written words in the image can outweigh the object itself (slide 3.51).'},
    {'text': 'CLIP gives almost the same score to "a photo of three apples" and "a photo of five apples" for a picture of three apples.', 'type': 2,
     'icon': icon('<circle cx="35" cy="42" r="12" fill="#d7263d"/><circle cx="60" cy="42" r="12" fill="#d7263d"/><circle cx="85" cy="42" r="12" fill="#d7263d"/><text x="60" y="74" font-size="12" text-anchor="middle">3 or 5?</text>'),
     'why': 'CLIP matches which words appear, not precise quantities. Counting is a known blind spot (slide 3.50).'},
    {'text': 'A "husky vs wolf" classifier is 95% accurate — until you notice it calls any animal on snow a wolf.', 'type': 3,
     'icon': icon('<rect y="50" width="120" height="30" fill="#ffffff"/><polygon points="40,50 50,30 60,40 70,30 80,50" fill="#777"/><text x="60" y="20" font-size="11" text-anchor="middle">snow = wolf?</text>'),
     'why': 'The model learned a shortcut: the background (snow) correlated with the label in training, so it never learned the animal itself.'},
    {'text': 'A vision-language model is shown a green banana and asked "What colour is the banana?". It answers "Yellow".', 'type': 4,
     'icon': icon('<path d="M30,30 Q60,75 95,30 Q60,58 30,30 Z" fill="#7cb342"/><text x="60" y="74" font-size="11" text-anchor="middle">"yellow"</text>'),
     'why': 'Language prior: the model answered from what bananas usually are instead of looking at the image (slide 3.78).'},
    {'text': 'A factory defect detector trained in summer fails after the camera is moved and winter light changes the images.', 'type': 0,
     'icon': icon('<rect x="20" y="25" width="40" height="30" rx="4" fill="#555"/><polygon points="60,32 80,22 80,58 60,48" fill="#555"/><text x="95" y="45" font-size="18">❄</text>'),
     'why': 'The new images come from a different distribution (data drift). Accuracy drops silently with no error message (slide 3.96).'},
    {'text': 'A pneumonia model performs brilliantly in one hospital. It turns out it learned to spot the text marker that hospital\'s scanner prints in the corner.', 'type': 3,
     'icon': icon('<rect x="35" y="12" width="50" height="58" rx="4" fill="#222"/><ellipse cx="60" cy="42" rx="16" ry="20" fill="#888"/><text x="44" y="24" font-size="8" fill="#ff0">L ▲</text>'),
     'why': 'A shortcut again: the marker correlated with sick patients in the training data. It does not transfer to other hospitals.'},
    {'text': 'CLIP scores "a dog to the left of a cat" and "a cat to the left of a dog" almost identically.', 'type': 2,
     'icon': icon('<circle cx="35" cy="42" r="14" fill="#a0703c"/><circle cx="85" cy="42" r="14" fill="#777"/><text x="60" y="47" font-size="14" text-anchor="middle">⇄</text>'),
     'why': 'Spatial relations are weak in CLIP: it notices the words "dog" and "cat", not how they relate (bag of words, slide 3.50).'},
    {'text': 'Asked to describe a photo of an empty plate, a VLM writes: "A plate with a fork and a knife next to it." There is no cutlery.', 'type': 4,
     'icon': icon('<ellipse cx="60" cy="42" rx="34" ry="24" fill="#fff" stroke="#999" stroke-width="3"/><text x="60" y="47" font-size="10" text-anchor="middle">fork?</text>'),
     'why': 'Object hallucination: plates usually come with cutlery in captions, so the model mentions objects that are not there.'},
    {'text': 'A T-shirt with the word "dog" printed on it makes a zero-shot classifier label the person as a dog.', 'type': 1,
     'icon': icon('<path d="M35,20 L50,14 L70,14 L85,20 L95,34 L82,40 L80,70 L40,70 L38,40 L25,34 Z" fill="#2a9d8f"/><text x="60" y="48" font-size="13" font-weight="700" fill="#fff" text-anchor="middle">dog</text>'),
     'why': 'Text in the image hijacks the prediction — the same typographic attack as the iPod apple.'},
    {'text': 'A face-recognition system makes far more errors on darker-skinned women, because most training faces were lighter-skinned men.', 'type': 3,
     'icon': icon('<circle cx="40" cy="38" r="16" fill="#f1c27d"/><circle cx="80" cy="38" r="16" fill="#8d5524"/><text x="80" y="72" font-size="10" text-anchor="middle">more errors</text>'),
     'why': 'Bias from unbalanced training data: the model is accurate on the groups it saw most and worse on the rest.'},
    {'text': 'A vehicle detector trained only on sunny daytime video misses half the cars at night in the rain.', 'type': 0,
     'icon': icon('<rect width="120" height="80" rx="8" fill="#16213e"/><line x1="20" y1="10" x2="15" y2="25" stroke="#9cf"/><line x1="60" y1="8" x2="55" y2="23" stroke="#9cf"/><line x1="95" y1="12" x2="90" y2="27" stroke="#9cf"/><rect x="35" y="45" width="50" height="16" rx="5" fill="#444"/>'),
     'why': 'Night and rain are outside the training distribution. Include the hard conditions in your data (slide 2.113).'},
]

FM_STYLE = '''
    .fm { display: grid; grid-template-columns: 150px 1fr; gap: var(--s4); align-items: start; }
    .fm svg { width: 100%; height: auto; }
    .fm p.case { font-size: 1.2rem; }
    body.projector .fm { grid-template-columns: 240px 1fr; }
    body.projector .fm p.case { font-size: 1.7rem; }
'''

FM_BODY = '''        <div class="panel" id="play">
          <div class="fm">
            <div id="icon"></div>
            <div>
              <p class="case" id="case"></p>
              <div class="choices" id="choices"></div>
              <div class="verdict hidden" id="verdict"></div>
              <p><button type="button" class="btn hidden" id="next">Next case →</button></p>
            </div>
          </div>
        </div>
        <div class="panel finish hidden" id="finish">
          <h2 style="font-family:var(--font-display);font-size:1.6rem">Case files closed</h2>
          <p class="finish__score" id="final">0 / 12</p>
          <div class="rowline"><button type="button" class="btn" id="again">Play again</button><a class="btn btn--ghost" href="./index.html">All activities</a></div>
        </div>
        <div class="panel"><h2>The five failure types</h2><ul class="small muted">
          <li><strong>Out-of-distribution</strong> — the input is unlike the training data (new object, camera, season, weather).</li>
          <li><strong>Typographic attack</strong> — written text in the image hijacks the prediction.</li>
          <li><strong>Counting / spatial</strong> — the model ignores how many, or where things are relative to each other.</li>
          <li><strong>Bias / shortcut</strong> — the model learned a spurious cue or reflects unbalanced data.</li>
          <li><strong>Hallucination</strong> — a vision-language model states things that are not in the image.</li></ul></div>'''

FM_JS = '''
(function () {
  'use strict';
  var CARDS = __CARDS__, TYPES = __TYPES__, MAX = 12, i, score;
  function load() {
    var C = CARDS[i];
    document.getElementById('icon').innerHTML = C.icon;
    document.getElementById('case').textContent = C.text;
    var box = document.getElementById('choices'); box.innerHTML = '';
    TYPES.forEach(function (t, k) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'choice'; b.textContent = t;
      b.addEventListener('click', function () { pick(k, b); });
      box.appendChild(b);
    });
    document.getElementById('verdict').classList.add('hidden');
    document.getElementById('next').classList.add('hidden');
    Act.setRound((i + 1) + ' / ' + CARDS.length);
  }
  function pick(k, btn) {
    var C = CARDS[i], right = k === C.type;
    if (right) { score++; Act.setScore(score); }
    Array.prototype.forEach.call(document.querySelectorAll('.choice'), function (c, j) { c.disabled = true; if (j === C.type) c.classList.add('is-right'); });
    if (!right) btn.classList.add('is-wrong');
    var v = document.getElementById('verdict');
    v.className = 'verdict ' + (right ? 'verdict--good' : 'verdict--bad');
    v.innerHTML = '<h3>' + (right ? 'Correct: +1' : 'It is: ' + TYPES[C.type]) + '</h3><p>' + Act.esc(C.why) + '</p>';
    var nb = document.getElementById('next'); nb.classList.remove('hidden'); nb.focus();
  }
  document.getElementById('next').addEventListener('click', function () { i++; if (i >= CARDS.length) finish(); else load(); });
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
  Act.init({ id: 'fool-the-model', max: MAX });
  start();
})();
'''


def fool_the_model():
    return FM_STYLE, FM_BODY, FM_JS.replace('__CARDS__', json.dumps(CARDS)).replace('__TYPES__', json.dumps(TYPES)), \
        'Twelve real ways vision models fail. For each case, label the failure type: out-of-distribution, typographic attack, counting/spatial, bias/shortcut, or hallucination. An explanation appears after every answer.'
