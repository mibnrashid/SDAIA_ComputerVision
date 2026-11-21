"""build_resources.py — resources/index.html with docs links and the glossary.

    python tools/build_resources.py

The glossary is auto-extracted from every `definition` slide in
content/slides-day1/2/3.md: "Term — definition." becomes one entry; a
definition slide without " — " uses the slide title as the term.
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _page import page  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DOCS = [
    ('PyTorch', 'https://docs.pytorch.org/docs/stable/index.html', 'BSD', 'Tensors, nn.Module, training loops, DataLoader (Day 1).'),
    ('torchvision', 'https://docs.pytorch.org/vision/stable/index.html', 'BSD', 'Datasets, transforms, ResNet, Faster/Mask/Keypoint R-CNN, ops.nms and box_iou (Days 1–2).'),
    ('Hugging Face Transformers', 'https://huggingface.co/docs/transformers/index', 'Apache 2.0', 'RT-DETRv2, CLIP, SigLIP, Grounding DINO, SAM, Depth Anything (Days 2–3).'),
    ('Transformers · object detection guide', 'https://huggingface.co/docs/transformers/tasks/object_detection', 'Apache 2.0', 'The fine-tuning recipe Lab 2B adapts (CPPE-5).'),
    ('Hugging Face Datasets', 'https://huggingface.co/docs/datasets/index', 'Apache 2.0', 'load_dataset for CPPE-5 and Imagenette.'),
    ('supervision', 'https://supervision.roboflow.com/latest/', 'MIT', 'Detections, LineZone, annotators, sample videos (Lab 2B).'),
    ('trackers', 'https://github.com/roboflow/trackers', 'Apache 2.0', 'ByteTrackTracker — the replacement for sv.ByteTrack (Lab 2B).'),
    ('OpenCV', 'https://docs.opencv.org/4.x/', 'Apache 2.0', 'imread, cvtColor, filter2D, thresholding, Canny (Lab 1A).'),
    ('Ultralytics (YOLO26, YOLOE-26)', 'https://docs.ultralytics.com/', 'AGPL-3.0', 'Lab 2C only. <strong>AGPL note:</strong> free to learn with; if you ship it in a product you must open-source your whole application or buy an enterprise licence.'),
]

DATA = [
    ('CIFAR-10', 'https://www.cs.toronto.edu/~kriz/cifar.html', 'Lab 1B — 60,000 tiny images, 10 classes (downloaded by torchvision).'),
    ('CPPE-5', 'https://huggingface.co/datasets/rishitdagli/cppe-5', 'Lab 2B — medical PPE boxes, 5 classes.'),
    ('Imagenette', 'https://huggingface.co/datasets/frgfm/imagenette', 'Lab 3A — 10 easy ImageNet classes.'),
    ('COCO', 'https://cocodataset.org/', 'The 80-class benchmark behind every pretrained detector we use.'),
]


def glossary():
    entries = []
    for day in (1, 2, 3):
        text = open(os.path.join(ROOT, 'content', f'slides-day{day}.md'), encoding='utf-8').read()
        for m in re.finditer(r'### (\d+\.\d+) · (.+)\nType: definition\nScreen: (.+)', text):
            sid, title, screen = m.groups()
            first = screen.split(' · ')[0]
            if ' — ' in first:
                term, definition = first.split(' — ', 1)
            else:
                term, definition = title, screen
            entries.append({'term': term.strip(), 'def': definition.strip(), 'slide': sid, 'day': day})
    entries.sort(key=lambda e: e['term'].lower().lstrip('['))
    return entries


def fmt(s):
    s = html.escape(s, quote=False)
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', s)


STYLE = '''    .res-group { margin-bottom: var(--s6); }
    .res-group > h2 { margin-bottom: var(--s2); }
    .res-group > .note { color: var(--text-muted); max-width: 70ch; margin-bottom: var(--s4); }
    .res-grid { display: grid; gap: var(--s4); grid-template-columns: repeat(auto-fit, minmax(18rem, 1fr)); }
    .res { display: flex; flex-direction: column; padding: var(--s4); }
    .res h3 { font-size: 1.08rem; margin: 0 0 var(--s2); }
    .res h3 a { text-decoration: none; }
    .res h3 a:hover { text-decoration: underline; }
    .res p { color: var(--text-muted); font-size: var(--fs-small); margin: 0; }
    .lic { align-self: flex-start; margin-bottom: var(--s2); font-size: 0.7rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; padding: 0.2rem 0.6rem; border-radius: 999px; background: var(--card-2); color: var(--text-muted); }
    .lic--agpl { background: rgba(228,96,42,.15); color: var(--coral-ink); }
    .adv { display: inline-block; margin-left: var(--s2); font-size: 0.7rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; padding: 0.2rem 0.6rem; border-radius: 999px; background: var(--ink); color: var(--teal-bright); vertical-align: middle; }
    .gsearch { width: 100%; max-width: 28rem; font: inherit; padding: 0.7rem 0.9rem; border: 1px solid var(--border); border-radius: var(--radius-sm); margin-bottom: var(--s4); }
    .gloss { display: grid; gap: var(--s2); }
    .gloss div { padding: var(--s3) var(--s4); background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-sm); }
    .gloss dt { font-weight: 700; }
    .gloss dd { margin: var(--s1) 0 0; color: var(--text-muted); font-size: var(--fs-small); }
    .gloss .src { font-size: 0.72rem; color: var(--text-muted); font-family: var(--font-mono); }
    .quick { display: flex; flex-wrap: wrap; gap: var(--s2); }
    .quick a { text-decoration: none; font-weight: 600; font-size: var(--fs-small); padding: 0.4rem 0.9rem; border-radius: 999px; border: 1px solid var(--border); background: var(--card); }'''

SCRIPT = '''  <script>
    (function () {
      'use strict';
      var input = document.getElementById('gsearch'), items = document.querySelectorAll('#gloss > div'), count = document.getElementById('gcount');
      input.addEventListener('input', function () {
        var q = input.value.trim().toLowerCase(), n = 0;
        Array.prototype.forEach.call(items, function (it) { var hit = it.textContent.toLowerCase().indexOf(q) >= 0; it.hidden = !hit; if (hit) n++; });
        count.textContent = n + ' of ' + items.length + ' terms';
      });
    })();
  </script>'''


def main():
    g = glossary()
    docs = ''.join(
        f'<article class="card res"><span class="lic{" lic--agpl" if lic.startswith("AGPL") else ""}">{lic}</span>'
        f'<h3><a href="{url}" target="_blank" rel="noopener">{name} ↗</a></h3><p>{desc}</p></article>'
        for name, url, lic, desc in DOCS)
    data = ''.join(f'<article class="card res"><h3><a href="{url}" target="_blank" rel="noopener">{name} ↗</a></h3><p>{desc}</p></article>'
                   for name, url, desc in DATA)
    gl = ''.join(f'<div><dt>{fmt(e["term"])}</dt><dd>{fmt(e["def"])}</dd><span class="src">Day {e["day"]} · slide {e["slide"]}</span></div>' for e in g)
    body = f'''    <section class="section--tight">
      <div class="container">
        <div class="res-group">
          <h2>Course material</h2>
          <div class="quick">
            <a href="../slides/day1.html">Day 1 slides</a><a href="../slides/day2.html">Day 2 slides</a><a href="../slides/day3.html">Day 3 slides</a>
            <a href="../notebooks/index.html">Labs (Colab)</a><a href="../activities/index.html">Activities</a><a href="../project/index.html">Project brief</a>
          </div>
        </div>
        <div class="res-group" id="docs">
          <h2>Library documentation</h2>
          <p class="note">The official docs for every library in the labs, with its licence. Check the licence before you build a product on a library (slide 2.66).</p>
          <div class="res-grid">{docs}</div>
        </div>
        <div class="res-group" id="data">
          <h2>Datasets used in the labs</h2>
          <div class="res-grid">{data}</div>
        </div>
        <div class="res-group" id="deeper">
          <h2>Go deeper <span class="adv">Advanced</span></h2>
          <p class="note">For after the course, when you want the full theory: university-level lectures that go well beyond these three days.</p>
          <div class="res-grid">
            <article class="card res"><span class="lic">Advanced</span><h3><a href="https://github.com/KAUST-Academy/Artificial-Intelligence-Courses/tree/main/Lectures/Computer_Vision" target="_blank" rel="noopener">KAUST Academy · Computer Vision lectures ↗</a></h3>
              <p>The KAUST Academy computer vision lecture series (slides and notebooks). Expect more maths than in this course — a good next step once the labs feel easy.</p></article>
          </div>
        </div>
        <div class="res-group" id="glossary">
          <h2>Glossary</h2>
          <p class="note">Every term defined on a slide in the three decks, extracted automatically from the definition slides. <span id="gcount">{len(g)} terms</span></p>
          <input type="search" id="gsearch" class="gsearch" placeholder="Filter terms, e.g. IoU, anchor, CLIP" aria-label="Filter the glossary">
          <dl class="gloss" id="gloss">{gl}</dl>
        </div>
      </div>
    </section>
'''
    out = page('../', 'Resources', 'Resources',
               'Library documentation with licences, the datasets behind the labs, where to go deeper, and a glossary of every term defined in the slides.',
               body, style=STYLE, scripts=SCRIPT)
    with open(os.path.join(ROOT, 'resources', 'index.html'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(out)
    print(f'wrote resources/index.html with {len(g)} glossary terms')


if __name__ == '__main__':
    main()
