from .common import md, code, check, how_to_use, gpu_check

META = dict(id='2C', file='Lab_2C', title='Ultralytics for beginners', day=2, block='Day 2 · self-paced / tonight (optional)',
            goal='Do the Day 2 ideas in a few lines with YOLO26: predict, read the results, track a video, train on a tiny dataset and prompt YOLOE-26 with text — then see what the library hid from you.',
            libs='ultralytics (YOLO26, YOLOE-26)', gpu=True)

CELLS = [
    how_to_use('2C', META['title'], META['goal'], 'Day 2 · optional, self-paced', 30),
    code('''import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "ultralytics>=8.4.0", "supervision"], check=False)
import ultralytics
ultralytics.checks()''',
         'Installs Ultralytics (8.4+ is needed for YOLO26 and YOLOE-26)', 'A summary line like "Ultralytics 8.4.x Python-3.12 torch-2.x CUDA:0 (Tesla T4)"',
         'Old versions do not know yolo26n.pt → the pin >=8.4.0 fixes it', run=True),
    gpu_check('CPU (YOLO26n is small enough)'),
    md('''> **Licence first.** Ultralytics is **AGPL-3.0**. You may use it freely to learn. If you ship it inside a product, you must open-source your whole application or buy an enterprise licence (slide 2.66). torchvision (BSD), Transformers (Apache 2.0) and supervision (MIT) do not have this condition.'''),

    md('''## 5 · One look: predict in one line

`yolo26n.pt` is the nano YOLO26 model, trained on COCO's 80 classes. YOLO26 is **end-to-end**: it outputs one box per object with **no NMS step**, like DETR.'''),
    code('''from ultralytics import YOLO
import matplotlib.pyplot as plt
model = YOLO("yolo26n.pt")
results = model("https://ultralytics.com/images/bus.jpg")
r = results[0]
plt.figure(figsize=(6, 8)); plt.imshow(r.plot()[..., ::-1]); plt.axis("off"); plt.show()''',
         'Downloads YOLO26n and runs it on bus.jpg', 'A speed line (~10 ms on T4) and the bus photo with boxes for the bus and four people',
         'r.plot() returns BGR: without [..., ::-1] the colours are swapped (the Day 1 gotcha)', run=True),
    md('''### 5.1 · Read the results field by field
`r.boxes.xyxy` (pixels), `r.boxes.conf` (confidence), `r.boxes.cls` (class index), and `r.names` maps index → name.'''),
    code('''print("xyxy:", r.boxes.xyxy.shape, "| conf:", r.boxes.conf.shape, "| cls:", r.boxes.cls.shape)
@@ names = [r.names[int(c)] for c in r.boxes.cls] ||| names = []  # TODO: turn every class index in r.boxes.cls into its name with r.names
for n, c, b in zip(names, r.boxes.conf.tolist(), r.boxes.xyxy.tolist()):
    print(f"{n:<8} {c:.2f}  {[round(v) for v in b]}")
n_people = names.count("person")
print("people:", n_people)''',
         'TODO 1: map class indices to names and count the people', 'Lines like "bus 0.94 [..]" and "person 0.88 [..]"; people: 4',
         'r.boxes.cls holds floats: wrap with int() before indexing r.names'),
    check('len(names) == len(r.boxes) and n_people >= 3', 'Names read correctly and the people are counted.',
          'names = [r.names[int(c)] for c in r.boxes.cls]'),
    md('''### 5.2 · Box formats, again
The same boxes in three conventions — Ultralytics gives you all of them.'''),
    code('''print("xyxy  (pixels)    ", [round(v) for v in r.boxes.xyxy[0].tolist()])
print("xywh  (centre, px) ", [round(v) for v in r.boxes.xywh[0].tolist()])
print("xywhn (YOLO, 0–1)  ", [round(v, 3) for v in r.boxes.xywhn[0].tolist()])''',
         'Prints one box in xyxy, xywh and normalised xywh', 'Three lists; the last one has all values between 0 and 1',
         'Ultralytics xywh is centre-based (cx, cy, w, h), unlike COCO xywh (corner-based)'),

    md('''## 8 · Tracking in one argument
`model.track(..., tracker="bytetrack.yaml")` runs detection plus ByteTrack and returns IDs in `r.boxes.id`.'''),
    code('''import supervision as sv
from supervision.assets import download_assets, VideoAssets
video = download_assets(VideoAssets.VEHICLES)
ids = set()
N = 40 if FAST else 200
for k, res in enumerate(model.track(video, tracker="bytetrack.yaml", stream=True, verbose=False, imgsz=960)):
    if res.boxes.id is not None:
        ids.update(res.boxes.id.int().tolist())
    if k + 1 >= N:
        break
@@ n_tracks = len(ids) ||| n_tracks = 0  # TODO: how many different track IDs were seen? (the size of the set ids)
print(f"{n_tracks} different objects tracked in {N} frames")
plt.figure(figsize=(12, 7)); plt.imshow(res.plot()[..., ::-1]); plt.axis("off"); plt.show()''',
         'TODO 2: track the sample video and count unique IDs', 'Around 20–60 different objects in 200 frames and a frame with "id:" labels',
         'stream=True is essential: without it every frame\'s result is kept in memory', run=True),
    check('n_tracks == len(ids) and n_tracks > 0', 'Unique track IDs counted.', 'n_tracks = len(ids)'),

    md('''## Train on a tiny dataset (about 2 minutes)
`coco8.yaml` is a built-in dataset of 8 images — far too small to be useful, but perfect for seeing the training loop, curves and metrics end to end.'''),
    code('''train_model = YOLO("yolo26n.pt")
metrics = train_model.train(data="coco8.yaml", epochs=3 if FAST else 20, imgsz=640, batch=8, plots=True, verbose=False)
print("mAP@0.5:", round(metrics.box.map50, 3), "| mAP@0.5:0.95:", round(metrics.box.map, 3))
print("results saved in:", metrics.save_dir)''',
         'Fine-tunes YOLO26n on coco8 for 20 epochs', 'A training table per epoch and "mAP@0.5: ~0.7–0.9 | mAP@0.5:0.95: ~0.5–0.7" (8 easy images)',
         'Downloads coco8 (1 MB) automatically; on CPU set epochs lower', run=True),
    code('''# Escape hatch: skip training and evaluate the pretrained model instead
USE_PRETRAINED = False   # ← set to True and run this cell
if USE_PRETRAINED:
    metrics = YOLO("yolo26n.pt").val(data="coco8.yaml", imgsz=640, verbose=False)
    print("pretrained mAP@0.5:", round(metrics.box.map50, 3))''',
         'Escape: validate the pretrained model instead of training', 'Nothing unless USE_PRETRAINED = True', '—'),
    code('''from PIL import Image
import os
curves = os.path.join(str(metrics.save_dir), "results.png")
if os.path.exists(curves):
    plt.figure(figsize=(14, 7)); plt.imshow(Image.open(curves)); plt.axis("off"); plt.show()''',
         'Shows the training curves Ultralytics saved', 'A grid of loss and metric curves over the epochs', 'Missing file when the escape cell was used'),

    md('''## Open vocabulary: YOLOE-26 with text prompts
Type the classes you want; YOLOE-26 returns boxes **and masks** for them (Day 3, Act 5). The first `set_classes` call downloads a text encoder.'''),
    code('''from ultralytics import YOLOE
yoloe = YOLOE("yoloe-26s-seg.pt")
@@ prompts = ["person", "bus", "backpack"] ||| prompts = []  # TODO: a list of three things to look for, e.g. ["person", "bus", "backpack"]
yoloe.set_classes(prompts)
er = yoloe.predict("https://ultralytics.com/images/bus.jpg", verbose=False)[0]
print("found:", [er.names[int(c)] for c in er.boxes.cls])
plt.figure(figsize=(6, 8)); plt.imshow(er.plot()[..., ::-1]); plt.axis("off"); plt.show()''',
         'TODO 3: give YOLOE-26 a text vocabulary and run it', 'found: a list containing person and bus (backpack only if visible) and an image with coloured masks',
         'Calling set_classes on a *-seg-pf.pt (prompt-free) model raises an AssertionError — use yoloe-26s-seg.pt', run=True),
    check('len(prompts) >= 1 and all(isinstance(p, str) for p in prompts)', 'YOLOE ran with your own vocabulary.',
          'prompts = ["person", "bus", "backpack"]'),

    md('''## What Ultralytics hid from you

Every line above hides something you built by hand on Day 2:

| One line here | What it hid | Where you did it by hand |
|---|---|---|
| `model(img)` | resizing, normalising, box decoding, confidence filtering | Lab 2A, torchvision `weights.transforms()` |
| YOLO26 has no NMS | older YOLOs ran NMS with an IoU threshold you could get wrong | Lab 2A, `nms_numpy` |
| `metrics.box.map` | TP/FP matching at IoU ≥ 0.5, PR curve, interpolated AP, mean over classes | Lab 2A, `average_precision` |
| `model.track(...)` | ByteTrack: predict, match with IoU, keep low-confidence boxes | Lab 2B, `ByteTrackTracker` + `LineZone` |
| `train(data=...)` | data format (normalised cxcywh .txt files), augmentation, loss, schedule | Lab 2B, the RT-DETRv2 `Trainer` |

**Use the shortcut when you understand what it does.** And remember the AGPL licence before you put it in a product.'''),

    md('''## Extra tasks (optional)

1. **Sizes:** compare `yolo26n.pt` and `yolo26s.pt` on bus.jpg: number of boxes, confidences, and speed (`r.speed`).
2. **Confidence:** run `model(img, conf=0.1)` and `conf=0.7`. What changes?
3. **Export:** export YOLO26n to ONNX with `model.export(format="onnx")` and note the file size.''', extra=True),
    code('''# Extra 1
for w in ("yolo26n.pt", "yolo26s.pt"):
    rr = YOLO(w)("https://ultralytics.com/images/bus.jpg", verbose=False)[0]
    print(w, len(rr.boxes), "boxes |", {k: round(v, 1) for k, v in rr.speed.items()})''',
         'Extra 1 answer', 'Both find the bus and people; s is a little slower and a little more confident', '—',
         unsolved='# Extra 1 — your code here\n', extra=True),
    code('''# Extra 2
for c in (0.1, 0.7):
    print(c, len(model("https://ultralytics.com/images/bus.jpg", conf=c, verbose=False)[0].boxes), "boxes")''',
         'Extra 2 answer', 'More boxes at 0.1, fewer at 0.7', '—',
         unsolved='# Extra 2 — your code here\n', extra=True),
    code('''# Extra 3
path = YOLO("yolo26n.pt").export(format="onnx")
print(path, round(os.path.getsize(path) / 1e6, 1), "MB")''',
         'Extra 3 answer', 'yolo26n.onnx of a few MB', 'Needs the onnx package; Ultralytics installs it on first export',
         unsolved='# Extra 3 — your code here\n', extra=True),
]
