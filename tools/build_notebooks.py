"""build_notebooks.py — generate the 14 lab notebooks and content/notebooks-spec.md.

    python tools/build_notebooks.py

Each lab in tools/nb/ is one list of cells. From it we write
notebooks/Lab_XX_solved.ipynb and Lab_XX_unsolved.ipynb (identical except
the TODO lines and the extra-task answers) and the cell-by-cell spec, so
the spec and the notebooks can never disagree on order.
"""
import os
import sys

import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nb import lab1a, lab1b, lab2a, lab2b, lab2c, lab3a, lab3b  # noqa: E402
from nb.common import REPO  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABS = [lab1a, lab1b, lab2a, lab2b, lab2c, lab3a, lab3b]
COLAB = f'https://colab.research.google.com/github/{REPO}/blob/main/notebooks/'


def build_nb(lab, solved):
    nb = new_notebook()
    nb.metadata = {
        'kernelspec': {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'},
        'language_info': {'name': 'python'},
        'colab': {'provenance': [], 'gpuType': 'T4'} if lab.META['gpu'] else {'provenance': []},
        'accelerator': 'GPU' if lab.META['gpu'] else 'None',
    }
    for c in lab.CELLS:
        src = c.source(solved)
        nb.cells.append(new_markdown_cell(src) if c.kind == 'md' else new_code_cell(src))
    return nb


def write_notebooks():
    os.makedirs(os.path.join(ROOT, 'notebooks'), exist_ok=True)
    for lab in LABS:
        for solved in (True, False):
            name = f"{lab.META['file']}_{'solved' if solved else 'unsolved'}.ipynb"
            nb = build_nb(lab, solved)
            nbformat.validate(nb)
            with open(os.path.join(ROOT, 'notebooks', name), 'w', encoding='utf-8', newline='\n') as fh:
                nbformat.write(nb, fh)
            print('wrote notebooks/' + name, len(nb.cells), 'cells')


def cell_md(s):
    return s.replace('|', '\\|').replace('\n', ' ')


API_NOTES = '''## API check against current docs (21 Nov 2026)

Checked on the web and by running the code locally on CPU with torch 2.15, torchvision 0.29,
transformers 5.23, datasets 5.2, supervision 0.32 and trackers. Differences from what `01-plan.md` assumes:

| Topic | What the plan says | What is true now | What the notebooks do |
|---|---|---|---|
| CPPE-5 dataset id | `cppe-5` (verify) | The canonical id is **`rishitdagli/cppe-5`**, converted to Parquet (the old loading script was removed; `datasets` 4+ no longer runs scripts). 1,000 train / 29 test images, 5 classes, COCO `xywh` boxes. | `load_dataset("rishitdagli/cppe-5")`, 90/10 train/val split of `train`. |
| supervision ByteTrack | `sv.ByteTrack` + `update_with_detections()` | **`sv.ByteTrack` was removed in supervision 0.31** (deprecated since 0.28). Its replacement is `ByteTrackTracker` from the separate `trackers` package, method `update(detections)`. `LineZone.trigger()` is unchanged and still needs `tracker_id`. | `pip install trackers`; `ByteTrackTracker().update(...)`, with a fallback to `sv.ByteTrack` on old installs. |
| CLIP features in Transformers v5 | `get_image_features` returns a tensor | In v5, `get_image_features` / `get_text_features` return a `BaseModelOutputWithPooling`; the embedding is `.pooler_output`. v4 returned a tensor. | A two-line `as_tensor()` helper handles both. |
| Grounding DINO post-processing | `post_process_grounded_object_detection` | Same method, but the box cutoff is now **`threshold`** (was `box_threshold`), and v5 returns phrases in **`text_labels`** (`labels` in older versions). Prompt format unchanged: lowercase, `"a cat. a dog."`. | `threshold=0.35, text_threshold=0.25`; reads `text_labels` with a fallback to `labels`. |
| RT-DETRv2 | in Transformers since Feb 2025 | Confirmed (`PekingU/rtdetr_v2_r18vd`, `AutoModelForObjectDetection`). The official fine-tuning guide still uses DETR on CPPE-5; we adapt it to RT-DETRv2. Post-processing needs `target_sizes` or boxes stay normalised. | Guide pattern adapted; 480 × 480 inputs; 8 epochs ≈ 5 min on a T4 (to be confirmed — see "Run before class"). |
| SAM | `facebook/sam-vit-base` | Unchanged: `SamProcessor` + `image_processor.post_process_masks(pred_masks, original_sizes, reshaped_input_sizes)`. `input_boxes` is nested per image. | As documented. |
| Depth Anything V2 | `pipeline("depth-estimation")` | Unchanged; model `depth-anything/Depth-Anything-V2-Small-hf`. Output is relative inverse depth (larger = nearer). | As documented. |
| Ultralytics | YOLO26 (`yolo26n.pt`), YOLOE-26 | Confirmed. YOLO26 and YOLOE-26 need **ultralytics ≥ 8.4.0**. `YOLOE("yoloe-26s-seg.pt").set_classes([...])` works (the first call downloads a text encoder); calling it on a `-pf` checkpoint raises an error. Tracking: `model.track(..., tracker="bytetrack.yaml")`. | `pip install "ultralytics>=8.4.0"`. |
| torchvision detection | `fasterrcnn_resnet50_fpn_v2`, `maskrcnn_resnet50_fpn_v2`, `keypointrcnn_resnet50_fpn`, `ops.nms` / `box_iou` | Unchanged. Use the `*_Weights.DEFAULT` enums and `weights.transforms()`. | As documented. |
| Imagenette for Lab 3A | "a 300-image Imagenette slice (verify)" | `frgfm/imagenette` on the Hub has Parquet files under `160px/`; the repo still contains an old loading script, so we read the Parquet files directly. torchvision also ships `datasets.Imagenette`. | Lists the repo's `160px` validation Parquet files and loads them with the `parquet` builder; falls back to torchvision. 30 images per class = 300. |
'''


def write_spec():
    run_first = []
    out = ['# Notebooks spec — Labs 1A to 3B', '',
           'Generated by `tools/build_notebooks.py` from the same source as the notebooks, so cell order here always',
           'matches the `.ipynb` files. Solved and unsolved notebooks are identical except the TODO lines and the',
           'extra-task answer cells. Colab links use',
           f'`{COLAB}<file>`.', '']
    for lab in LABS:
        for i, c in enumerate(lab.CELLS, 1):
            if c.run:
                run_first.append((lab.META['id'], i, c.what))
    out += ['## Run before class', '',
            'These cells need a GPU, a large download or the live Hub, so they could not be fully verified here',
            '(no GPU on the build machine). Ice runs each solved notebook top to bottom on a Colab T4 and checks the',
            'expected output in the tables below. Highest priority first: 1B (Sunday), then 2A, 2B, 2C, 3A, 3B.', '',
            '| Lab | Cell | What to check |', '|---|---|---|']
    out += [f'| {l} | {n} | {cell_md(w)} |' for l, n, w in run_first]
    out += ['', API_NOTES, '']
    out += ['## Rules every notebook follows', '',
            '- A "How to use this notebook" cell first, then a GPU check with a CPU fallback (`FAST` mode).',
            '- Sections are numbered to match the deck acts of that day.',
            '- 3–5 one-line TODOs, each followed by a check cell that prints ✅ or a hint (never a traceback).',
            '- An "Extra tasks" section with 3–4 tasks; answers only in the solved version.',
            '- Every training step is capped at about 5 minutes on a T4 and followed by an escape cell (pretrained weights or a faster option).',
            '- All data downloads automatically inside Colab.', '']
    for lab in LABS:
        m = lab.META
        todos = sum(1 for c in lab.CELLS if c.is_todo)
        out += [f"## Lab {m['id']} · {m['title']}", '',
                f"- **Files:** `{m['file']}_unsolved.ipynb`, `{m['file']}_solved.ipynb`",
                f"- **When:** {m['block']}",
                f"- **Goal:** {m['goal']}",
                f"- **Libraries:** {m['libs']}",
                f"- **Cells:** {len(lab.CELLS)} · **TODOs:** {todos} · **GPU:** {'T4 recommended' if m['gpu'] else 'not needed'}", '',
                '| # | Type | What it does | PRE-WRITTEN / TODO | Expected output | What will break → fix |',
                '|---|---|---|---|---|---|']
        for i, c in enumerate(lab.CELLS, 1):
            kind = 'markdown' if c.kind == 'md' else 'code'
            if c.is_todo:
                tag = 'TODO: `' + cell_md(' / '.join(c.todo_lines())) + '`'
            elif c.extra and c.unsolved is not None:
                tag = 'EXTRA (answer in solved only)'
            else:
                tag = 'PRE-WRITTEN'
            flag = ' **[Run before class]**' if c.run else ''
            out.append(f'| {i} | {kind} | {cell_md(c.what)}{flag} | {tag} | {cell_md(c.expect)} | {cell_md(c.breaks)} |')
        out.append('')
    with open(os.path.join(ROOT, 'content', 'notebooks-spec.md'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(out))
    print('wrote content/notebooks-spec.md')


INDEX_STYLE = """    .daygroup { margin-bottom: var(--s5); }
    .daygroup > h2 { margin-bottom: var(--s3); }
    .labgrid { display: grid; gap: var(--s4); grid-template-columns: repeat(auto-fit, minmax(19rem, 1fr)); }
    .lab { display: flex; flex-direction: column; overflow: hidden; }
    .lab__head { display: flex; align-items: baseline; justify-content: space-between; gap: var(--s3); padding: var(--s3) var(--s4); color: #fff; background: var(--teal); }
    .lab--d2 .lab__head { background: var(--ink); }
    .lab--d3 .lab__head { background: var(--teal-bright); color: var(--ink); }
    .lab__id { font-family: var(--font-display); font-size: 2.2rem; font-weight: 700; line-height: 1; }
    .lab__when { font-size: 0.72rem; font-weight: 700; letter-spacing: var(--tracking-eyebrow); text-transform: uppercase; }
    .lab__body { padding: var(--s4); flex: 1 1 auto; }
    .lab__body h3 { font-family: var(--font-display); font-size: 1.3rem; margin: 0 0 var(--s2); }
    .lab__body p { color: var(--text-muted); font-size: var(--fs-small); margin: 0 0 var(--s2); }
    .lab__libs { font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-muted); }
    .lab__foot { display: grid; gap: var(--s2); padding: var(--s3) var(--s4); border-top: 1px solid var(--border); background: var(--card-2); }
    .lab__btns { display: flex; flex-wrap: wrap; gap: var(--s2); }
    .colab { display: inline-flex; align-items: center; border-radius: 6px; overflow: hidden; text-decoration: none; font-size: 0.8rem; font-weight: 700; border: 1px solid #b98600; white-space: nowrap; }
    .colab span:first-child { background: #4a4d52; color: #fff; padding: 5px 8px; }
    .colab span:last-child { background: #f9ab00; color: #1a1c1f; padding: 5px 9px; }
    .colab:hover span:last-child { background: #ffbe1a; }
    .lab__dl { font-size: 0.8rem; }
    .note { border-left: 5px solid var(--amber); background: rgba(240,160,60,.12); padding: var(--s4); border-radius: var(--radius-sm); margin-bottom: var(--s5); }"""

DAY_TITLES = {1: 'Day 1 · From pixels to features', 2: 'Day 2 · Where is it, what shape is it, where is it going?', 3: 'Day 3 · Seeing beyond labels'}


def write_index():
    from _page import page
    import html as _h
    groups = []
    for d in (1, 2, 3):
        cards = []
        for lab in LABS:
            m = lab.META
            if m['day'] != d:
                continue
            u, s_ = f"{m['file']}_unsolved.ipynb", f"{m['file']}_solved.ipynb"
            cards.append(f"""          <article class="card lab lab--d{d}">
            <div class="lab__head"><span class="lab__id">{m['id']}</span><span class="lab__when">{_h.escape(m['block'])}</span></div>
            <div class="lab__body">
              <h3>{_h.escape(m['title'])}</h3>
              <p>{_h.escape(m['goal'])}</p>
              <p class="lab__libs">{_h.escape(m['libs'])}</p>
            </div>
            <div class="lab__foot">
              <div class="lab__btns">
                <a class="colab" href="{COLAB}{u}" target="_blank" rel="noopener"><span>Open unsolved in</span><span>Colab</span></a>
                <a class="colab" href="{COLAB}{s_}" target="_blank" rel="noopener"><span>Open solved in</span><span>Colab</span></a>
              </div>
              <span class="lab__dl">Download: <a href="./{u}" download>unsolved .ipynb</a> · <a href="./{s_}" download>solved .ipynb</a></span>
            </div>
          </article>""")
        groups.append(f"""        <div class="daygroup" id="day{d}">
          <h2>{DAY_TITLES[d]}</h2>
          <div class="labgrid">
{chr(10).join(cards)}
          </div>
        </div>""")
    body = f"""    <section class="section--tight">
      <div class="container">
        <div class="note"><strong>How to start a lab:</strong> click <em>Open unsolved in Colab</em>, then <em>Runtime → Change runtime type → T4 GPU</em>, then run the cells top to bottom. Every TODO is one line and is checked by the cell below it (✅ or a hint). Stuck for five minutes? Open the solved version and compare. Colab forgets files between sessions, so re-run from the top when you come back.</div>
{chr(10).join(groups)}
      </div>
    </section>
"""
    html_ = page('../', 'Labs', 'The labs',
                 'Seven Colab labs, each in an <em>unsolved</em> version (one-line TODOs with checks) and a <em>solved</em> version. Labs 1A, 1B, 2A and 2B are done in class and finished at night; 2C is optional; 3A and 3B are your portfolio pieces after the course.',
                 body, style=INDEX_STYLE)
    with open(os.path.join(ROOT, 'notebooks', 'index.html'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(html_)
    print('wrote notebooks/index.html')


if __name__ == '__main__':
    write_notebooks()
    write_spec()
    write_index()
