from .common import md, code, check, how_to_use, gpu_check

META = dict(id='2B', file='Lab_2B', title='Fine-tune and track', day=2, block='Day 2 · B5 (finish tonight)',
            goal='Fine-tune RT-DETRv2 on the CPPE-5 protective-equipment dataset for a few minutes, measure validation mAP, look at a failure gallery, then track and count vehicles in a video with ByteTrack and a counting line.',
            libs='transformers (RT-DETRv2), datasets, torchmetrics, supervision, trackers', gpu=True)

CELLS = [
    how_to_use('2B', META['title'], META['goal'], 'Day 2 · Block 5 · Acts 6 and 8', 50),
    code('''# Install the libraries Colab does not have (about 30 s)
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "supervision", "trackers", "torchmetrics", "pycocotools", "accelerate>=1.1.0"], check=False)
print("installed")''',
         'Installs supervision, trackers, torchmetrics, pycocotools and accelerate (needed by Trainer)', 'installed', 'pip resolver warnings are harmless; a real failure prints an error line', run=True),
    gpu_check('a tiny training run (a few steps) — the numbers will be poor, but every cell runs'),
    code('''import numpy as np, matplotlib.pyplot as plt, time
import transformers, datasets
from transformers import AutoImageProcessor, AutoModelForObjectDetection, TrainingArguments, Trainer
from datasets import load_dataset
print("transformers", transformers.__version__, "| datasets", datasets.__version__)''',
         'Imports', 'transformers 5.x and datasets 4.x versions', 'transformers 4.x also works for this lab'),

    md('''## 6 · The data: CPPE-5

1,000 training photos of medical protective equipment with boxes for five classes: Coverall, Face_Shield, Gloves, Goggles, Mask. Boxes are in **COCO xywh** pixels. (The Hub id is `rishitdagli/cppe-5`; the old `cppe-5` id used a loading script that `datasets` 4 no longer runs.)'''),
    code('''ds = load_dataset("rishitdagli/cppe-5")
split = ds["train"].train_test_split(test_size=0.1, seed=0)
train_ds, val_ds = split["train"], split["test"]
if FAST:
    train_ds, val_ds = train_ds.select(range(64)), val_ds.select(range(16))
CATEGORIES = ds["train"].features["objects"]["category"].feature.names
id2label = dict(enumerate(CATEGORIES)); label2id = {v: k for k, v in id2label.items()}
print(ds)
print("classes:", CATEGORIES, "| train", len(train_ds), "| val", len(val_ds))
print("first example objects:", train_ds[0]["objects"])''',
         'Loads CPPE-5 from the Hub and makes a 90/10 train/val split', 'DatasetDict with train 1000 / test 29 · classes [\'Coverall\', \'Face_Shield\', \'Gloves\', \'Goggles\', \'Mask\'] · train 900 · val 100',
         'If the Hub layout changed, the feature path for category names may differ → print ds["train"].features', run=True),
    code('''def draw_boxes(ax, image, boxes_xyxy, labels, color, scores=None):
    ax.imshow(image); ax.axis("off")
    for k, (b, l) in enumerate(zip(boxes_xyxy, labels)):
        x1, y1, x2, y2 = b
        ax.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, color=color, lw=2))
        txt = id2label[int(l)] + (f" {scores[k]:.2f}" if scores is not None else "")
        ax.text(x1, y1, txt, color="white", fontsize=7, bbox=dict(facecolor=color, alpha=0.7, pad=1))

def xywh_to_xyxy(b): return [b[0], b[1], b[0] + b[2], b[1] + b[3]]

fig, axes = plt.subplots(1, 3, figsize=(14, 5))
for ax, ex in zip(axes, train_ds.select(range(3))):
    draw_boxes(ax, ex["image"], [xywh_to_xyxy(b) for b in ex["objects"]["bbox"]], ex["objects"]["category"], "lime")
plt.show()''',
         'Draws three training images with their ground-truth boxes', 'Three photos of people in masks, gloves and coveralls with green labelled boxes',
         'Boxes landing in the wrong place = you treated xywh as xyxy'),

    md('''### 6.1 · Clean "runaway" boxes
A few CPPE-5 boxes stick out of the image. The model's processor rejects them, so clip every box to the image and drop boxes with no area.'''),
    code('''def clean_boxes(bboxes, categories, W, H):
    out_b, out_c = [], []
    for (x, y, w, h), c in zip(bboxes, categories):
        x, y = max(0.0, x), max(0.0, y)
        @@ w, h = min(w, W - x), min(h, H - y) ||| w, h = w, h  # TODO: shrink w and h so the box ends inside the image (min with W - x and H - y)
        if w > 1 and h > 1:
            out_b.append([x, y, w, h]); out_c.append(c)
    return out_b, out_c

print(clean_boxes([[600, 10, 100, 50], [5, 5, 0.5, 9]], [0, 1], W=640, H=480))''',
         'TODO 1: clip boxes to the image', '([[600, 10, 40, 50]], [0]) — the first box is cut at the right edge, the second is dropped',
         'Forgetting this raises "bounding box outside image" errors during training'),
    check('clean_boxes([[600, 10, 100, 50], [5, 5, 0.5, 9]], [0, 1], 640, 480) == ([[600, 10, 40, 50]], [0])',
          'Runaway boxes are clipped and empty boxes dropped.', 'w, h = min(w, W - x), min(h, H - y)'),

    md('''## 5 → 6 · The model: RT-DETRv2

`PekingU/rtdetr_v2_r18vd` is RT-DETRv2 with a ResNet-18 backbone, pretrained on COCO. We replace its 80-class head with our 5 classes (`ignore_mismatched_sizes=True`). The processor resizes to 480 × 480 to keep training under five minutes.'''),
    code('''CKPT = "PekingU/rtdetr_v2_r18vd"
SIZE = 480
processor = AutoImageProcessor.from_pretrained(CKPT, do_resize=True, size={"height": SIZE, "width": SIZE})

def transform(batch):
    images, annotations = [], []
    for image_id, image, objs in zip(batch["image_id"], batch["image"], batch["objects"]):
        image = image.convert("RGB")
        boxes, cats = clean_boxes(objs["bbox"], objs["category"], image.width, image.height)
        images.append(image)
        annotations.append({"image_id": image_id, "annotations": [
            {"bbox": b, "category_id": c, "area": b[2] * b[3], "iscrowd": 0} for b, c in zip(boxes, cats)]})
    enc = processor(images=images, annotations=annotations, return_tensors="pt")
    return {"pixel_values": enc["pixel_values"], "labels": enc["labels"]}

train_t = train_ds.with_transform(transform)
val_t = val_ds.with_transform(transform)
sample = train_t[0]
print("pixel_values", tuple(sample["pixel_values"].shape), "| label keys", list(sample["labels"].keys()))
print("boxes (normalised cx, cy, w, h):", sample["labels"]["boxes"][:2])

def collate_fn(batch):
    return {"pixel_values": torch.stack([x["pixel_values"] for x in batch]), "labels": [x["labels"] for x in batch]}''',
         'Builds the processor, the on-the-fly transform and the collate function',
         'pixel_values (3, 480, 480) · label keys include class_labels and boxes · boxes are normalised cxcywh between 0 and 1',
         'KeyError on "image_id" → check the column names with print(train_ds)', run=True),
    code('''model = AutoModelForObjectDetection.from_pretrained(
    CKPT, id2label=id2label, label2id=label2id, ignore_mismatched_sizes=True).to(DEVICE)
print(f"{sum(p.numel() for p in model.parameters()) / 1e6:.1f} M parameters")''',
         'Loads RT-DETRv2 with a new 5-class head', 'A warning that some head weights were newly initialised (expected) and about 20 M parameters',
         'The "newly initialized" warning is normal here — it is the new head', run=True),

    md('''### 6.2 · Start training now (≈ 5 minutes on a T4)
Run this cell, then go back to the slides: Act 8 (tracking) is taught while your GPU trains.'''),
    code('''EPOCHS = 8
args = TrainingArguments(
    output_dir="rtdetr-cppe5",
    num_train_epochs=EPOCHS,
    max_steps=4 if FAST else -1,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    learning_rate=1e-4,
    weight_decay=1e-4,
    max_grad_norm=0.1,
    warmup_steps=30,
    lr_scheduler_type="cosine",
    fp16=(DEVICE == "cuda"),
    eval_strategy="epoch" if not FAST else "no",
    save_strategy="no",
    logging_steps=10,
    remove_unused_columns=False,
    dataloader_num_workers=0 if os.name == "nt" else 2,   # Windows cannot pickle notebook functions into workers
    report_to="none",
)
trainer = Trainer(model=model, args=args, train_dataset=train_t, eval_dataset=val_t, data_collator=collate_fn)
t0 = time.time()
trainer.train()
print(f"training took {(time.time() - t0) / 60:.1f} min")''',
         'Fine-tunes RT-DETRv2 on 900 images for 8 epochs', 'A progress bar to ~900 steps, loss falling from ~20+ to ~8–10, eval_loss each epoch, "training took ~4–6 min"',
         'CUDA out of memory → lower per_device_train_batch_size to 4; too slow → use the escape cell below', run=True),
    code('''# Escape hatch: use an RT-DETR that someone already fine-tuned on CPPE-5
# Use this if training failed or did not finish. It is RT-DETR (v1, ResNet-50) trained for 3,000 steps.
USE_PRETRAINED = False   # ← set to True and run this cell
if USE_PRETRAINED:
    ESCAPE = "qubvel-hf/rt-detr-finetuned-cppe-5-3k-steps"
    processor = AutoImageProcessor.from_pretrained(ESCAPE)
    model = AutoModelForObjectDetection.from_pretrained(ESCAPE).to(DEVICE)
    id2label = {int(k): v for k, v in model.config.id2label.items()}
    print("loaded", ESCAPE, id2label)''',
         'Escape: load a public CPPE-5 fine-tuned RT-DETR instead', 'Nothing unless USE_PRETRAINED = True; then "loaded … {0: \'Coverall\', …}"',
         'If the label order differs from CATEGORIES, the printed id2label shows the mapping actually used', run=True),

    md('''## 6 · Read the training results

### 6.3 · Curves: is the loss still falling?'''),
    code('''logs = trainer.state.log_history if not globals().get("USE_PRETRAINED") else []
tr = [(l["step"], l["loss"]) for l in logs if "loss" in l]
ev = [(l["step"], l["eval_loss"]) for l in logs if "eval_loss" in l]
if tr:
    plt.figure(figsize=(6, 3.5))
    plt.plot(*zip(*tr), label="train loss")
    if ev: plt.plot(*zip(*ev), "o-", label="val loss")
    plt.xlabel("step"); plt.legend(); plt.title("RT-DETRv2 on CPPE-5"); plt.show()
else:
    print("No training log (escape model in use).")''',
         'Plots train and validation loss from the Trainer log', 'Train loss falling steeply then flattening; val loss falling — still going down at the end means more epochs would help',
         'Empty plot in FAST mode: only 4 steps were run'),
    md('''### 6.4 · Validation mAP
Run the model on every validation image, keep **all** boxes (threshold 0) — mAP sweeps the threshold itself — and compute COCO mAP with torchmetrics.'''),
    code('''from torchmetrics.detection import MeanAveragePrecision

@torch.no_grad()
def predict(images, threshold=0.0):
    model.eval()
    inputs = processor(images=images, return_tensors="pt").to(DEVICE)
    outputs = model(**inputs)
    sizes = [(im.height, im.width) for im in images]
    @@ return processor.post_process_object_detection(outputs, threshold=threshold, target_sizes=sizes) ||| return None  # TODO: post_process_object_detection(outputs, threshold=threshold, target_sizes=sizes)

metric = MeanAveragePrecision(box_format="xyxy", class_metrics=True)
all_preds = []
for i in range(0, len(val_ds), 8):
    batch = [val_ds[j] for j in range(i, min(i + 8, len(val_ds)))]
    images = [ex["image"].convert("RGB") for ex in batch]
    results = predict(images)
    for ex, r in zip(batch, results):
        boxes, cats = clean_boxes(ex["objects"]["bbox"], ex["objects"]["category"], ex["width"], ex["height"])
        target = {"boxes": torch.tensor([xywh_to_xyxy(b) for b in boxes], dtype=torch.float32).reshape(-1, 4),
                  "labels": torch.tensor(cats, dtype=torch.int64)}
        pred = {k: r[k].cpu() for k in ("boxes", "scores", "labels")}
        metric.update([pred], [target]); all_preds.append((ex, pred, target))
res = metric.compute()
print(f"val mAP@0.5:0.95 = {res['map']:.3f} | mAP@0.5 = {res['map_50']:.3f}")
for name, ap in zip(CATEGORIES, res["map_per_class"].tolist()):
    print(f"   {name:<12} AP {ap:.3f}")''',
         'TODO 2: post-processing with target_sizes; then COCO mAP on the validation set',
         'val mAP@0.5:0.95 around 0.15–0.30 and mAP@0.5 around 0.30–0.55 after 8 epochs; Coverall and Mask highest, Goggles lowest',
         'Without target_sizes the boxes stay normalised (0–1) and mAP is ~0', run=True),
    check('isinstance(predict([val_ds[0]["image"].convert("RGB")]), list) and float(res["map"]) >= 0',
          'Post-processing returns one result per image and mAP was computed.', 'return processor.post_process_object_detection(outputs, threshold=threshold, target_sizes=sizes)'),
    md('''Write your validation mAP here — it is part of tonight's deliverable: **val mAP@0.5:0.95 = ____**'''),

    md('''### 6.5 · Failure gallery: what did it miss?
For each image, recall at IoU ≥ 0.5 with boxes above 0.5 confidence. The six worst images are shown: green = ground truth, red = prediction.'''),
    code('''from torchvision.ops import box_iou
def image_recall(pred, target, conf=0.5):
    if len(target["boxes"]) == 0: return 1.0
    p = pred["boxes"][pred["scores"] > conf]
    if len(p) == 0: return 0.0
    return float((box_iou(target["boxes"], p).max(1).values >= 0.5).float().mean())

worst = sorted(all_preds, key=lambda t: image_recall(t[1], t[2]))[:6]
fig, axes = plt.subplots(2, 3, figsize=(15, 9))
for ax, (ex, pred, target) in zip(axes.ravel(), worst):
    m = pred["scores"] > 0.5
    draw_boxes(ax, ex["image"].convert("RGB"), target["boxes"].tolist(), target["labels"].tolist(), "green")
    draw_boxes(ax, ex["image"].convert("RGB"), pred["boxes"][m].tolist(), pred["labels"][m].tolist(), "red", pred["scores"][m].tolist())
    ax.set_title(f"recall {image_recall(pred, target):.2f}")
plt.tight_layout(); plt.show()''',
         'Shows the six validation images with the lowest recall', 'Six photos; typical misses: small gloves, goggles on faces, crowded scenes, unusual colours',
         '—'),
    md('''Pick **two** failures and write a cause and a fix for each (this is exactly what the project's failure analysis asks for):

1. *Failure:* … *Cause:* … *Fix to try:* …
2. *Failure:* … *Cause:* … *Fix to try:* …'''),

    md('''## 8 · From frames to motion: tracking and counting

Our CPPE-5 model does not know cars, so for tracking we load the **COCO-pretrained** RT-DETRv2 again. Each frame: detect → track (ByteTrack gives every object a `tracker_id`) → count with a line (supervision `LineZone`).

`sv.ByteTrack` is deprecated in recent supervision releases in favour of the separate `trackers` package; the cell below uses `trackers` and falls back to `sv.ByteTrack` on older installs.'''),
    code('''import supervision as sv
from supervision.assets import download_assets, VideoAssets
video_path = download_assets(VideoAssets.VEHICLES)
info = sv.VideoInfo.from_video_path(video_path)
print(video_path, "|", info.width, "x", info.height, "|", info.fps, "fps |", info.total_frames, "frames")

coco_processor = AutoImageProcessor.from_pretrained(CKPT)
coco_model = AutoModelForObjectDetection.from_pretrained(CKPT).to(DEVICE).eval()
VEHICLES = {"car", "truck", "bus", "motorcycle", "motorbike"}
vehicle_ids = [i for i, n in coco_model.config.id2label.items() if n in VEHICLES]
print("vehicle class ids:", vehicle_ids)''',
         'Downloads the supervision sample video and the COCO detector', 'vehicles.mp4 | 3840 x 2160 | 25 fps | 538 frames · vehicle class ids: [2, 3, 5, 7] (the exact ids depend on the label map)',
         'Video download is ~35 MB; if it fails, rerun the cell', run=True),
    code('''try:
    from trackers import ByteTrackTracker
    tracker = ByteTrackTracker()
    track = tracker.update
    print("using trackers.ByteTrackTracker")
except ImportError:
    tracker = sv.ByteTrack()
    track = tracker.update_with_detections
    print("using sv.ByteTrack (older supervision)")

def detect(frame_bgr, threshold=0.4):
    rgb = np.ascontiguousarray(frame_bgr[..., ::-1])     # BGR → RGB, as a normal (positive-stride) array
    inputs = coco_processor(images=rgb, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        outputs = coco_model(**inputs)
    r = coco_processor.post_process_object_detection(outputs, threshold=threshold, target_sizes=[rgb.shape[:2]])[0]
    det = sv.Detections.from_transformers(r, id2label=coco_model.config.id2label)
    return det[np.isin(det.class_id, vehicle_ids)]

frame0 = next(sv.get_video_frames_generator(video_path))
d0 = detect(frame0)
print(len(d0), "vehicles in the first frame")''',
         'Creates the tracker and a detect() function returning supervision Detections', 'using trackers.ByteTrackTracker · around 10–20 vehicles in the first frame',
         'from_transformers needs the post-processed dict (boxes, scores, labels), not the raw model output'),
    code('''import cv2
SCALE = 1280 / info.width
W, H = int(info.width * SCALE), int(info.height * SCALE)
line_zone = sv.LineZone(start=sv.Point(0, int(H * 0.55)), end=sv.Point(W, int(H * 0.55)))
box_ann, label_ann = sv.BoxAnnotator(thickness=2), sv.LabelAnnotator(text_scale=0.5)
line_ann = sv.LineZoneAnnotator(thickness=2, text_scale=0.8)
N_FRAMES = 40 if FAST else 300
out_info = sv.VideoInfo(width=W, height=H, fps=info.fps, total_frames=N_FRAMES)

t0 = time.time()
with sv.VideoSink("counted_raw.mp4", out_info) as sink:
    for k, frame in enumerate(sv.get_video_frames_generator(video_path, end=N_FRAMES)):
        frame = cv2.resize(frame, (W, H))
        detections = detect(frame)
        @@ detections = track(detections) ||| pass  # TODO: give every detection a tracker_id: detections = track(detections)
        @@ crossed_in, crossed_out = line_zone.trigger(detections) ||| pass  # TODO: count line crossings: crossed_in, crossed_out = line_zone.trigger(detections)
        labels = [f"#{t}" for t in detections.tracker_id] if detections.tracker_id is not None else []
        frame = box_ann.annotate(frame.copy(), detections)
        frame = label_ann.annotate(frame, detections, labels)
        frame = line_ann.annotate(frame, line_zone)
        sink.write_frame(frame)
print(f"{N_FRAMES} frames in {time.time() - t0:.0f}s | IN {line_zone.in_count} | OUT {line_zone.out_count}")
plt.figure(figsize=(12, 7)); plt.imshow(frame[..., ::-1]); plt.axis("off"); plt.title("last frame"); plt.show()''',
         'TODO 3 and 4: track, then count with the line, writing an annotated video',
         '"300 frames in ~60 s | IN n | OUT m" (both counts in the tens or below) and a frame with boxes, #IDs and the counting line',
         'LineZone without tracker IDs raises or counts nothing → TODO 3 must come before TODO 4', run=True),
    check('detections.tracker_id is not None and (line_zone.in_count + line_zone.out_count) >= 0 and len(set(detections.tracker_id)) == len(detections)',
          'Every detection has a unique tracker_id, and the line is counting.', 'detections = track(detections), then line_zone.trigger(detections)'),
    code('''# Re-encode to H.264 so the browser can play it, then show it
from IPython.display import Video, display
try:
    ok = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "counted_raw.mp4", "-vcodec", "libx264",
                         "-pix_fmt", "yuv420p", "counted.mp4"]).returncode == 0
except FileNotFoundError:
    ok = False
if ok:
    display(Video("counted.mp4", embed=True, width=720))
else:
    print("ffmpeg not available here — download counted_raw.mp4 from the Files panel to watch it.")''',
         'Re-encodes the video with ffmpeg and plays it inline', 'An embedded video: cars with boxes and IDs crossing the line, counters going up',
         'Colab has ffmpeg; locally you may need to install it'),

    md('''## Extra tasks (optional)

1. **Threshold choice:** compute precision and recall on the validation set at confidence 0.3, 0.5 and 0.7. Which would you ship for a hospital PPE check, and why?
2. **ID switches:** set the detection threshold in `detect()` to 0.7 and rerun tracking on 150 frames. Do IDs change more often? Why?
3. **Per-lane counting:** add a second `LineZone` covering only the left half of the road and compare the counts.
4. **Train longer:** set `EPOCHS = 20` (≈ 12 min on a T4) and compare the mAP with your 8-epoch run.''', extra=True),
    code('''# Extra 1
for conf in (0.3, 0.5, 0.7):
    tp = fp = fn = 0
    for ex, pred, target in all_preds:
        m = pred["scores"] > conf; p = pred["boxes"][m]; pl = pred["labels"][m]
        matched = set()
        for b, l in zip(p, pl):
            ious = box_iou(b[None], target["boxes"])[0] if len(target["boxes"]) else torch.zeros(0)
            j = int(ious.argmax()) if len(ious) else -1
            if j >= 0 and ious[j] >= 0.5 and target["labels"][j] == l and j not in matched:
                tp += 1; matched.add(j)
            else:
                fp += 1
        fn += len(target["boxes"]) - len(matched)
    print(f"conf {conf}: precision {tp / max(tp + fp, 1):.2f} recall {tp / max(tp + fn, 1):.2f}")''',
         'Extra 1 answer', 'Precision rises and recall falls as the threshold goes up', '—',
         unsolved='# Extra 1 — your code here (hint: reuse all_preds and box_iou; a TP needs IoU >= 0.5 and the same class)\n', extra=True),
    code('''# Extra 2 — rerun the tracking cell with detect(frame, threshold=0.7) and N_FRAMES = 150, then compare the IDs''',
         'Extra 2 answer (instructions)', '—', '—',
         unsolved='# Extra 2 — your code here\n', extra=True),
    code('''# Extra 3
left = sv.LineZone(start=sv.Point(0, int(H * 0.55)), end=sv.Point(W // 2, int(H * 0.55)))
try:
    from trackers import ByteTrackTracker
    tracker2 = ByteTrackTracker(); track2 = tracker2.update
except ImportError:
    tracker2 = sv.ByteTrack(); track2 = tracker2.update_with_detections
for frame in sv.get_video_frames_generator(video_path, end=N_FRAMES):
    d = track2(detect(cv2.resize(frame, (W, H))))
    left.trigger(d)
print("left half: IN", left.in_count, "OUT", left.out_count)''',
         'Extra 3 answer', 'Counts for the left half only, smaller than the full-line counts', '—',
         unsolved='# Extra 3 — your code here\n', extra=True),
    code('''# Extra 4 — set EPOCHS = 20 in the training cell, rerun from there, and compare res["map"]''',
         'Extra 4 answer (instructions)', '—', '—',
         unsolved='# Extra 4 — your code here\n', extra=True),
]
