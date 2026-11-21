from .common import md, code, check, how_to_use, gpu_check

META = dict(id='2A', file='Lab_2A', title='Detection by hand', day=2, block='Day 2 · B2 + B4',
            goal='Write IoU and NMS yourself and match torchvision.ops, compute precision, recall and AP by hand (≈ 0.68 on the slide example), then run Faster R-CNN, Mask R-CNN and Keypoint R-CNN and read their outputs field by field.',
            libs='NumPy, torchvision.ops, torchvision detection models', gpu=True)

CELLS = [
    how_to_use('2A', META['title'], META['goal'], 'Day 2 · Blocks 2 and 4 · Acts 2, 4, 6 and 7', 40),
    gpu_check('the same settings (inference only, a little slower)'),
    code('''import numpy as np, matplotlib.pyplot as plt, urllib.request
import torchvision
from torchvision.ops import box_iou, nms
from torchvision.io import decode_image
from torchvision.utils import draw_bounding_boxes, draw_segmentation_masks, draw_keypoints
print("torchvision", torchvision.__version__)''',
         'Imports', 'torchvision version, e.g. 0.2x', '—'),

    md('''## 2 · Describing a box

torchvision uses **xyxy** in pixels: `(x_min, y_min, x_max, y_max)`. COCO uses **xywh**, YOLO uses normalised **cxcywh**. Same box, three ways of writing it (slide 2.18).'''),
    code('''def xyxy_to_xywh(b):  x1, y1, x2, y2 = b; return (x1, y1, x2 - x1, y2 - y1)
def xyxy_to_cxcywh(b): x1, y1, x2, y2 = b; return ((x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1)
box, W, H = (100, 120, 300, 360), 640, 480
cx, cy, w, h = xyxy_to_cxcywh(box)
print("xywh       ", xyxy_to_xywh(box))
print("cxcywh     ", (cx, cy, w, h))
print("normalised ", (cx / W, cy / H, w / W, h / H))''',
         'Converts the slide-2.18 box between formats', 'xywh (100, 120, 200, 240) · cxcywh (200.0, 240.0, 200, 240) · normalised (0.3125, 0.5, 0.3125, 0.5)', '—'),
    md('''### 2.1 · IoU by hand
Intersection over Union = overlap area ÷ combined area. Fill in the intersection line — remember `max(0, …)` for boxes that do not overlap.'''),
    code('''def iou(a, b):
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    @@ inter = max(0, ix2 - ix1) * max(0, iy2 - iy1) ||| inter = 0  # TODO: intersection area = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    area = lambda r: (r[2] - r[0]) * (r[3] - r[1])
    union = area(a) + area(b) - inter
    return inter / union

print("example 1:", round(iou((0, 0, 4, 4), (2, 2, 6, 6)), 3))   # slide 2.21
print("example 2:", round(iou((0, 0, 4, 4), (1, 0, 5, 4)), 3))   # slide 2.22
print("no overlap:", iou((0, 0, 1, 1), (5, 5, 6, 6)))''',
         'TODO 1: the intersection line of IoU', 'example 1: 0.143 · example 2: 0.6 · no overlap: 0.0',
         'Without max(0, …) two far-apart boxes give a positive "intersection" (negative × negative)'),
    check('abs(iou((0,0,4,4),(2,2,6,6)) - 4/28) < 1e-9 and abs(iou((0,0,4,4),(1,0,5,4)) - 0.6) < 1e-9 and iou((0,0,1,1),(5,5,6,6)) == 0',
          'IoU matches both worked examples and handles no overlap.', 'inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)'),
    code('''rng = np.random.default_rng(0)
xy = rng.uniform(0, 400, (20, 2)); wh = rng.uniform(20, 150, (20, 2))
boxes = np.hstack([xy, xy + wh]).astype(np.float32)
mine = np.array([[iou(a, b) for b in boxes] for a in boxes])
lib = box_iou(torch.tensor(boxes), torch.tensor(boxes)).numpy()
print("max difference vs torchvision.ops.box_iou:", float(np.abs(mine - lib).max()))''',
         'Compares your IoU with torchvision.ops.box_iou on 20 random boxes', 'max difference vs torchvision.ops.box_iou: ~1e-7 (tiny float error)', '—'),

    md('''## 4 · Scale and duplicates: NMS

**NMS**: keep the highest-confidence box, delete every other box that overlaps it by more than an IoU threshold, then repeat with the next highest remaining box. These six boxes reproduce slide 2.48.'''),
    code('''names = list("ABCDEF")
det_boxes = np.array([[100, 100, 200, 200], [110, 105, 210, 205], [300, 100, 400, 200],
                      [90, 120, 190, 215], [310, 110, 405, 210], [500, 300, 600, 400]], dtype=np.float32)
det_scores = np.array([0.95, 0.90, 0.80, 0.75, 0.60, 0.55], dtype=np.float32)
print("IoU(A,B) =", round(iou(det_boxes[0], det_boxes[1]), 2), "| IoU(A,D) =", round(iou(det_boxes[0], det_boxes[3]), 2),
      "| IoU(C,E) =", round(iou(det_boxes[2], det_boxes[4]), 2))

def nms_numpy(boxes, scores, iou_thr=0.5):
    order = np.argsort(-scores)          # highest score first
    keep = []
    while len(order) > 0:
        best = order[0]
        keep.append(int(best))
        ious = np.array([iou(boxes[best], boxes[o]) for o in order[1:]])
        @@ order = order[1:][ious <= iou_thr] ||| order = order[1:]  # TODO: keep only the remaining boxes whose IoU with best is <= iou_thr
    return keep

kept = nms_numpy(det_boxes, det_scores)
print("kept:", [names[k] for k in kept])''',
         'TODO 2: the suppression line of NMS, on the slide example', 'IoU(A,B) = 0.75 | IoU(A,D) = 0.59 | IoU(C,E) = 0.71 · kept: [\'A\', \'C\', \'F\']',
         'Using > instead of <= keeps the duplicates and removes everything else'),
    check('kept == [0, 2, 5]', 'NMS keeps A, C and F, like slide 2.48.', 'order = order[1:][ious <= iou_thr]'),
    code('''scores_r = rng.uniform(0.3, 1.0, len(boxes)).astype(np.float32)
mine = nms_numpy(boxes, scores_r, 0.5)
lib = nms(torch.tensor(boxes), torch.tensor(scores_r), 0.5).tolist()
print("yours:      ", mine)
print("torchvision:", lib)
print("same boxes kept:", mine == lib)''',
         'Compares your NMS with torchvision.ops.nms on random boxes', 'Two identical index lists and "same boxes kept: True"', 'Different order → you are not sorting by score first'),

    md('''## 6 · How good is the detector? AP by hand

Five ground-truth objects, eight predictions sorted by confidence, already marked TP/FP with IoU ≥ 0.5 (slides 2.74–2.76).'''),
    code('''tps = np.array([1, 1, 0, 1, 0, 1, 0, 0])     # TP TP FP TP FP TP FP FP
n_gt = 5
tp_cum = np.cumsum(tps)
@@ precision = tp_cum / np.arange(1, len(tps) + 1) ||| precision = np.zeros(len(tps))  # TODO: TPs so far ÷ predictions so far (np.arange(1, len(tps) + 1))
recall = tp_cum / n_gt
for k in range(len(tps)):
    print(f"{k+1}  {'TP' if tps[k] else 'FP'}  P {precision[k]:.2f}  R {recall[k]:.1f}")''',
         'TODO 3: the precision column of the AP table', 'The table from slide 2.75: P 1.00 1.00 0.67 0.75 0.60 0.67 0.57 0.50, R 0.2 0.4 0.4 0.6 0.6 0.8 0.8 0.8',
         'Dividing by n_gt gives recall, not precision'),
    check('np.allclose(precision, [1, 1, 2/3, 3/4, 3/5, 4/6, 4/7, 4/8])', 'Precision column matches slide 2.75.',
          'precision = tp_cum / np.arange(1, len(tps) + 1)'),
    code('''def average_precision(precision, recall):
    """Area under the interpolated PR curve (slide 2.76)."""
    ap, prev_r = 0.0, 0.0
    for k in range(len(recall)):
        if recall[k] > prev_r:                      # recall went up at this prediction
            ap += (recall[k] - prev_r) * precision[k:].max()
            prev_r = recall[k]
    return ap

ap = average_precision(precision, recall)
print(f"AP = {ap:.3f}")
plt.figure(figsize=(4.5, 3.4))
plt.step(np.r_[0, recall], np.r_[1, precision], where="post", marker="o")
plt.xlabel("recall"); plt.ylabel("precision"); plt.xlim(0, 1.02); plt.ylim(0, 1.05); plt.title(f"PR curve · AP = {ap:.2f}")
plt.show()''',
         'Computes AP from the PR points and plots the curve', 'AP = 0.683 and a stepped PR curve that never reaches recall 1.0',
         'Taking precision[k] instead of the max to the right gives 0.65 — not the interpolated AP'),
    code('''# mAP = mean of per-class AP. A second class "bicycle" with 3 objects:
ap_car = ap
tps_b = np.array([1, 0, 0, 1, 0]); cum = np.cumsum(tps_b)
ap_bike = average_precision(cum / np.arange(1, 6), cum / 3)
print(f"AP car {ap_car:.2f} | AP bicycle {ap_bike:.2f} | mAP {(ap_car + ap_bike) / 2:.2f}")''',
         'Shows mAP as the mean of per-class AP', 'AP car 0.68 | AP bicycle 0.50 | mAP 0.59', '—'),

    md('''## 3 & 7 · Real detectors from torchvision

All three models share a ResNet-50 + FPN backbone (Day 1) and differ only in their heads. We use the Ultralytics sample photo `bus.jpg`; if the download fails we fall back to a built-in image.'''),
    code('''try:
    urllib.request.urlretrieve("https://ultralytics.com/images/bus.jpg", "bus.jpg")
    img = decode_image("bus.jpg")
except Exception as e:
    print("Download failed, using a built-in image instead:", e)
    from skimage import data
    img = torch.from_numpy(data.astronaut()).permute(2, 0, 1)
print("image tensor:", tuple(img.shape), img.dtype)   # (C, H, W) uint8
plt.imshow(img.permute(1, 2, 0)); plt.axis("off"); plt.show()''',
         'Downloads bus.jpg and loads it as a (C, H, W) uint8 tensor', 'image tensor: (3, 1080, 810) torch.uint8 and the photo of a bus with people',
         'No internet → the built-in astronaut image is used; detections change accordingly', run=True),
    code('''from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2, FasterRCNN_ResNet50_FPN_V2_Weights
weights = FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT
frcnn = fasterrcnn_resnet50_fpn_v2(weights=weights, box_score_thresh=0.05).to(DEVICE).eval()   # eval()!
CATS = weights.meta["categories"]
preprocess = weights.transforms()
with torch.no_grad():
    out = frcnn([preprocess(img).to(DEVICE)])[0]
print("fields:", list(out.keys()))
print("boxes", tuple(out["boxes"].shape), "| labels", tuple(out["labels"].shape), "| scores", tuple(out["scores"].shape))
for b, l, s in list(zip(out["boxes"], out["labels"], out["scores"]))[:5]:
    print(f"{CATS[l]:<10} {s:.2f}  xyxy {[round(v) for v in b.tolist()]}")''',
         'Runs Faster R-CNN v2 and prints the raw output fields', 'fields: [\'boxes\', \'labels\', \'scores\'] · dozens of boxes · top lines: person 0.99…, bus 0.99…',
         'Weights download is 167 MB; forgetting .eval() raises "targets should be passed" in training mode', run=True),
    code('''CONF = 0.5
@@ keep = out["scores"] > CONF ||| keep = torch.ones_like(out["scores"], dtype=torch.bool)  # TODO: keep only boxes whose score is above CONF
labels = [f"{CATS[l]} {s:.2f}" for l, s in zip(out["labels"][keep], out["scores"][keep])]
drawn = draw_bounding_boxes(img, out["boxes"][keep].cpu(), labels, width=4, colors="lime", font_size=24)
print(int(keep.sum()), "boxes above", CONF)
plt.figure(figsize=(6, 8)); plt.imshow(drawn.permute(1, 2, 0)); plt.axis("off"); plt.show()''',
         'TODO 4: the confidence threshold, then draw the boxes', 'About 5–6 boxes above 0.5 (4 people, 1 bus, maybe a stop sign) drawn on the photo',
         'This is the confidence threshold, not the NMS threshold — the model already ran NMS internally'),
    check('keep.dtype == torch.bool and int(keep.sum()) == int((out["scores"] > CONF).sum())', 'Confidence filter is correct.',
          'keep = out["scores"] > CONF'),
    code('''from torchvision.models.detection import maskrcnn_resnet50_fpn_v2, MaskRCNN_ResNet50_FPN_V2_Weights
mweights = MaskRCNN_ResNet50_FPN_V2_Weights.DEFAULT
mrcnn = maskrcnn_resnet50_fpn_v2(weights=mweights).to(DEVICE).eval()
with torch.no_grad():
    mout = mrcnn([mweights.transforms()(img).to(DEVICE)])[0]
print("fields:", list(mout.keys()), "| masks", tuple(mout["masks"].shape), "(N, 1, H, W) probabilities")
mk = mout["scores"] > 0.5
masks = (mout["masks"][mk, 0] > 0.5).cpu()
seg = draw_segmentation_masks(img, masks, alpha=0.55)
plt.figure(figsize=(6, 8)); plt.imshow(seg.permute(1, 2, 0)); plt.axis("off"); plt.show()''',
         'Runs Mask R-CNN v2 and draws instance masks', 'fields include \'masks\' with shape (N, 1, 1080, 810); each person and the bus gets its own colour',
         'Masks are probabilities: forgetting > 0.5 makes draw_segmentation_masks fail (it needs bool)', run=True),
    code('''from torchvision.models.detection import keypointrcnn_resnet50_fpn, KeypointRCNN_ResNet50_FPN_Weights
kweights = KeypointRCNN_ResNet50_FPN_Weights.DEFAULT
krcnn = keypointrcnn_resnet50_fpn(weights=kweights).to(DEVICE).eval()
with torch.no_grad():
    kout = krcnn([kweights.transforms()(img).to(DEVICE)])[0]
print("keypoints", tuple(kout["keypoints"].shape), "→ (N people, 17 joints, [x, y, visibility])")
print("joint names:", kweights.meta["keypoint_names"][:5], "…")
kk = kout["scores"] > 0.8
SKELETON = [(0, 1), (0, 2), (1, 3), (2, 4), (5, 6), (5, 7), (7, 9), (6, 8), (8, 10), (5, 11), (6, 12), (11, 12), (11, 13), (13, 15), (12, 14), (14, 16)]
pose = draw_keypoints(img, kout["keypoints"][kk, :, :2].cpu(), connectivity=SKELETON, colors="yellow", radius=5, width=3)
plt.figure(figsize=(6, 8)); plt.imshow(pose.permute(1, 2, 0)); plt.axis("off"); plt.show()''',
         'Runs Keypoint R-CNN and draws skeletons', 'keypoints (N, 17, 3); yellow stick figures on each person',
         '—', run=True),

    md('''## Extra tasks (optional)

1. **NMS threshold sweep:** run torchvision's NMS on Faster R-CNN's raw boxes (scores > 0.05) with thresholds 0.3, 0.5, 0.7, 0.9 and count the boxes left.
2. **Confidence sweep:** count the kept boxes for confidence 0.1, 0.3, 0.5, 0.7, 0.9. Which knob removes duplicates, which removes weak boxes?
3. **Formats:** convert the kept Faster R-CNN boxes to COCO xywh and to YOLO normalised cxcywh.
4. **Soft-NMS:** instead of deleting overlapping boxes, multiply their score by (1 − IoU). Run it on the six slide boxes.''', extra=True),
    code('''# Extra 1
b, s = out["boxes"].cpu(), out["scores"].cpu()
for t in (0.3, 0.5, 0.7, 0.9):
    print(f"NMS IoU {t}: {len(nms(b, s, t))} boxes")''',
         'Extra 1 answer', 'Box count grows as the NMS threshold rises (fewer duplicates removed)', '—',
         unsolved='# Extra 1 — your code here (hint: nms(out["boxes"].cpu(), out["scores"].cpu(), t))\n', extra=True),
    code('''# Extra 2
for c in (0.1, 0.3, 0.5, 0.7, 0.9):
    print(f"confidence > {c}: {int((out['scores'] > c).sum())} boxes")''',
         'Extra 2 answer', 'Box count falls as confidence rises', '—',
         unsolved='# Extra 2 — your code here\n', extra=True),
    code('''# Extra 3
Hh, Ww = img.shape[1:]
for x1, y1, x2, y2 in out["boxes"][keep].cpu().tolist():
    print("coco", [round(v) for v in (x1, y1, x2 - x1, y2 - y1)],
          "| yolo", [round(v, 3) for v in ((x1 + x2) / 2 / Ww, (y1 + y2) / 2 / Hh, (x2 - x1) / Ww, (y2 - y1) / Hh)])''',
         'Extra 3 answer', 'One line per kept box in both formats', '—',
         unsolved='# Extra 3 — your code here\n', extra=True),
    code('''# Extra 4
def soft_nms(boxes, scores, thr=0.3):
    scores = scores.copy(); idx = list(range(len(scores))); out_ = []
    while idx:
        best = max(idx, key=lambda i: scores[i]); out_.append((names[best], round(float(scores[best]), 2))); idx.remove(best)
        for i in idx: scores[i] *= (1 - iou(boxes[best], boxes[i]))
        idx = [i for i in idx if scores[i] > thr]
    return out_
print(soft_nms(det_boxes, det_scores))''',
         'Extra 4 answer', 'A, C, F keep their scores; B, D, E survive only with much lower scores or drop out', '—',
         unsolved='# Extra 4 — your code here\n', extra=True),
]
