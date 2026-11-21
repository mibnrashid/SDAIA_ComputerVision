from .common import md, code, check, how_to_use, gpu_check

META = dict(id='3B', file='Lab_3B', title='Open-vocabulary toolbox', day=3, block='Day 3 · take-home (portfolio)',
            goal='Detect anything you can name with Grounding DINO, turn the boxes into exact masks with SAM and measure their area, estimate depth from one photo with Depth Anything V2, then find three prompts that break it.',
            libs='transformers (Grounding DINO, SAM, Depth Anything V2)', gpu=True)

CELLS = [
    how_to_use('3B', META['title'], META['goal'], 'Day 3 · take-home · Act 5', 40),
    gpu_check('CPU (each model runs in a few seconds per image)'),
    code('''import numpy as np, matplotlib.pyplot as plt, urllib.request
from PIL import Image
import transformers
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection, SamModel, SamProcessor, pipeline
print("transformers", transformers.__version__)

try:
    urllib.request.urlretrieve("https://ultralytics.com/images/bus.jpg", "bus.jpg")
    image = Image.open("bus.jpg").convert("RGB")
except Exception as e:
    print("Download failed, using a built-in image:", e)
    from skimage import data
    image = Image.fromarray(data.astronaut())
print("image size (W, H):", image.size)
plt.figure(figsize=(5, 6.5)); plt.imshow(image); plt.axis("off"); plt.show()''',
         'Imports and loads the bus photo', 'image size (W, H): (810, 1080) and the bus photo', 'No internet → the astronaut image is used; adapt the prompts', run=True),

    md('''## 5 · Open-vocabulary detection: Grounding DINO

Give the model **text**; it returns boxes for whatever the text describes. The prompt format matters: **lowercase, with a full stop after each class** — `"a bus. a person."`'''),
    code('''classes = ["Bus", "Person", "Backpack", "Traffic light"]
@@ text = " ".join(c.lower() + "." for c in classes) ||| text = ""  # TODO: lowercase every class and end each with a full stop, joined by spaces → "bus. person. backpack. traffic light."
print(repr(text))''',
         'TODO 1: build the Grounding DINO prompt string', "'bus. person. backpack. traffic light.'", 'Commas or capital letters make the model merge or miss classes'),
    check('text == "bus. person. backpack. traffic light."', 'Prompt format is right: lowercase, a full stop after each class.',
          '" ".join(c.lower() + "." for c in classes)'),
    code('''GD = "IDEA-Research/grounding-dino-tiny"
gd_processor = AutoProcessor.from_pretrained(GD)
gd_model = AutoModelForZeroShotObjectDetection.from_pretrained(GD).to(DEVICE).eval()
inputs = gd_processor(images=image, text=text, return_tensors="pt").to(DEVICE)
with torch.no_grad():
    outputs = gd_model(**inputs)
det = gd_processor.post_process_grounded_object_detection(
    outputs, inputs.input_ids, threshold=0.35, text_threshold=0.25, target_sizes=[image.size[::-1]])[0]
phrases = det.get("text_labels", det["labels"])          # v5 returns text_labels; older versions put text in labels
boxes = det["boxes"].cpu()
for p, s, b in zip(phrases, det["scores"].tolist(), boxes.tolist()):
    print(f"{p:<15} {s:.2f}  {[round(v) for v in b]}")''',
         'Runs Grounding DINO tiny and post-processes with target_sizes', 'Lines for bus (~0.8), several persons (~0.5–0.7), maybe a backpack; boxes in pixels',
         'Older transformers call the argument box_threshold instead of threshold → upgrade transformers', run=True),
    code('''def draw(ax, image, boxes, labels, color="lime"):
    ax.imshow(image); ax.axis("off")
    for (x1, y1, x2, y2), l in zip(boxes, labels):
        ax.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False, color=color, lw=2))
        ax.text(x1, y1, l, color="black", fontsize=8, bbox=dict(facecolor=color, alpha=0.8, pad=1))
fig, ax = plt.subplots(figsize=(5, 6.5)); draw(ax, image, boxes.tolist(), phrases); plt.show()''',
         'Draws the text-prompted boxes', 'The bus and the people boxed and labelled with their phrases', '—'),

    md('''## 5.1 · Promptable segmentation: SAM

SAM does not know *what* things are — it returns the exact pixels of whatever you point at. Here we point with the Grounding DINO boxes: **text → box → mask** ("Grounded SAM").'''),
    code('''SAM = "facebook/sam-vit-base"
sam_processor = SamProcessor.from_pretrained(SAM)
sam_model = SamModel.from_pretrained(SAM).to(DEVICE).eval()
sam_inputs = sam_processor(images=image, input_boxes=[boxes.tolist()], return_tensors="pt").to(DEVICE)
with torch.no_grad():
    sam_out = sam_model(**sam_inputs, multimask_output=False)
masks = sam_processor.image_processor.post_process_masks(
    sam_out.pred_masks.cpu(), sam_inputs["original_sizes"].cpu(), sam_inputs["reshaped_input_sizes"].cpu())[0][:, 0]
masks = masks.numpy().astype(bool)
print("masks:", masks.shape, "→ (boxes, H, W)", "| IoU scores:", sam_out.iou_scores.squeeze().cpu().numpy().round(2))''',
         'Runs SAM with the boxes as prompts and resizes masks back to the photo', 'masks: (N, 1080, 810) → (boxes, H, W) and quality scores around 0.9',
         'input_boxes must be nested per image: [[box1, box2, …]]; a flat list gives a shape error', run=True),
    code('''overlay = np.array(image).astype(float) / 255
rng = np.random.default_rng(1)
for m in masks:
    overlay[m] = overlay[m] * 0.45 + rng.uniform(0.2, 1, 3) * 0.55
plt.figure(figsize=(5, 6.5)); plt.imshow(overlay); plt.axis("off"); plt.title("text → box → mask"); plt.show()''',
         'Overlays each mask in its own colour', 'Each detected object filled with a different colour, edges following the real outlines', '—'),
    md('''### 5.2 · Measure: mask area
Boxes can count; masks can **measure**. Report every object's area in pixels and as a share of the photo.'''),
    code('''areas = []
for p, m in zip(phrases, masks):
    @@ area_pct = 100 * m.sum() / m.size ||| area_pct = 0.0  # TODO: percentage of the image covered by mask m (pixels in the mask ÷ all pixels × 100)
    areas.append(area_pct)
    print(f"{p:<15} {int(m.sum()):>8} px   {area_pct:5.1f}% of the image")''',
         'TODO 2: mask area as a percentage of the image', 'The bus covers roughly 30–45% of the image, each person roughly 2–6%',
         'Using the box area instead of the mask over-estimates people a lot'),
    check('len(areas) == len(masks) and all(abs(a - 100 * m.mean()) < 1e-6 for a, m in zip(areas, masks))',
          'Areas are correct.', 'area_pct = 100 * m.sum() / m.size'),

    md('''## 5.3 · Depth from one photo: Depth Anything V2

A relative depth map from a single image, with no training. Depth Anything predicts **relative inverse depth**: larger values = **closer** to the camera.'''),
    code('''depth_pipe = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device=0 if DEVICE == "cuda" else -1)
dres = depth_pipe(image)
depth = dres["predicted_depth"].squeeze().cpu().numpy()
depth = np.array(Image.fromarray(depth).resize(image.size, Image.BILINEAR))
fig, axes = plt.subplots(1, 2, figsize=(10, 6.5))
axes[0].imshow(image); axes[0].axis("off")
axes[1].imshow(dres["depth"], cmap="inferno"); axes[1].axis("off"); axes[1].set_title("bright = near")
plt.show()''',
         'Runs Depth Anything V2 Small and shows the depth map', 'A depth image where the people in front are bright and the far street is dark', 'First run downloads ~100 MB', run=True),
    code('''mean_depth = [float(depth[m].mean()) for m in masks]
@@ nearest = int(np.argmax(mean_depth)) ||| nearest = 0  # TODO: index of the object with the LARGEST mean depth value (= nearest), np.argmax
for p, d in zip(phrases, mean_depth):
    print(f"{p:<15} mean depth {d:6.2f}")
print("nearest object:", phrases[nearest])''',
         'TODO 3: combine masks and depth to find the nearest object', 'One line per object; the nearest object is a person in the foreground',
         'np.argmin picks the farthest object — remember: larger = closer for this model'),
    check('nearest == int(np.argmax(mean_depth))', 'Nearest object found by combining mask and depth.', 'nearest = int(np.argmax(mean_depth))'),

    md('''## 5.4 · Break it: three prompts that fail

Foundation models fail in ways you can predict from the slides (counting, spatial words, negation, rare words, things that are not there). Try your own prompts in the cell below, then fill in the table.'''),
    code('''def ground(prompt, thr=0.35):
    inp = gd_processor(images=image, text=prompt, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        o = gd_model(**inp)
    r = gd_processor.post_process_grounded_object_detection(o, inp.input_ids, threshold=thr, text_threshold=0.25,
                                                            target_sizes=[image.size[::-1]])[0]
    labs = r.get("text_labels", r["labels"])
    fig, ax = plt.subplots(figsize=(4, 5.2)); draw(ax, image, r["boxes"].cpu().tolist(), labs, "orange"); ax.set_title(prompt, fontsize=9); plt.show()

for prompt in ["the person on the far left.", "a person not wearing a jacket.", "a giraffe."]:
    ground(prompt)''',
         'A helper to try any prompt; three example prompts that often fail', 'Usually: "far left" boxes several people; "not wearing" still boxes everyone; "giraffe" may box something wrong or nothing',
         'Results vary by image; write down what you see'),
    md('''| Prompt | What happened | Why (which failure type?) |
|---|---|---|
| 1. | | |
| 2. | | |
| 3. | | |'''),

    md('''## Extra tasks (optional)

1. **Your own photo:** upload a photo (Files panel), and run the whole text → box → mask → area pipeline on it.
2. **Point prompts:** give SAM a single click (`input_points=[[[x, y]]]`) on the bus instead of a box.
3. **Thresholds:** run Grounding DINO with `threshold=0.2` and `0.5`. What appears and disappears?
4. **CLIP check:** crop each detected box and ask CLIP (Lab 3A) whether the crop matches its phrase — a cheap way to filter false positives.''', extra=True),
    code('''# Extra 1
# img = Image.open("my_photo.jpg").convert("RGB"); image = img   # then re-run the cells from section 5''',
         'Extra 1 answer (instructions)', '—', '—', unsolved='# Extra 1 — your code here\n', extra=True),
    code('''# Extra 2
pt_inputs = sam_processor(images=image, input_points=[[[400, 500]]], return_tensors="pt").to(DEVICE)
with torch.no_grad():
    po = sam_model(**pt_inputs)
pm = sam_processor.image_processor.post_process_masks(po.pred_masks.cpu(), pt_inputs["original_sizes"].cpu(),
                                                      pt_inputs["reshaped_input_sizes"].cpu())[0][0]
print("3 candidate masks, scores:", po.iou_scores.squeeze().cpu().numpy().round(2))
fig, axes = plt.subplots(1, 3, figsize=(12, 5))
for ax, m in zip(axes, pm): ax.imshow(image); ax.imshow(m.numpy(), alpha=0.5); ax.axis("off")
plt.show()''',
         'Extra 2 answer', 'Three candidate masks (part, object, larger region) with quality scores', '—',
         unsolved='# Extra 2 — your code here (hint: sam_processor(images=image, input_points=[[[x, y]]], ...))\n', extra=True),
    code('''# Extra 3
for thr in (0.2, 0.5):
    ground("bus. person. backpack. traffic light.", thr)''',
         'Extra 3 answer', 'More (and wronger) boxes at 0.2, fewer at 0.5', '—', unsolved='# Extra 3 — your code here\n', extra=True),
    code('''# Extra 4
from transformers import CLIPModel, CLIPProcessor
import torch.nn.functional as F
cm = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(DEVICE).eval(); cp = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
feat = lambda o: o if torch.is_tensor(o) else o.pooler_output
crops = [image.crop(tuple(int(v) for v in b)) for b in boxes.tolist()]
with torch.no_grad():
    ie = F.normalize(feat(cm.get_image_features(**cp(images=crops, return_tensors="pt").to(DEVICE))), dim=-1)
    te = F.normalize(feat(cm.get_text_features(**cp(text=[f"a photo of a {p}" for p in phrases], return_tensors="pt", padding=True).to(DEVICE))), dim=-1)
for p, s in zip(phrases, (ie * te).sum(-1).tolist()):
    print(f"{p:<15} CLIP agreement {s:.3f}")''',
         'Extra 4 answer', 'One agreement score per box; low scores flag doubtful detections', '—',
         unsolved='# Extra 4 — your code here\n', extra=True),
]
