# Slides — Day 2 · Where is it, what shape is it, where is it going?

Computer Vision for Developers · SDAIA Academy · Mon 23 Nov 2026

## How to read this file
Same format as `slides-day1.md`. One `###` = one slide. `Type`, `Screen`, `Notes`. `[STRETCH]` and `(cut first)` appear only in Notes. Footer: `SECTION LABEL · Day 2 · NN / TOTAL`.

---

## Opening

### 2.01 · Computer Vision for Developers — Day 2
Type: title
Screen: Day 2 — Where is it, what shape is it, where is it going? · Detection · Segmentation · Tracking
Notes: Yesterday the model said what is in the image. Today it says where, which pixels, and which one is which across a video.

### 2.02 · Warm-up: five questions from yesterday
Type: quiz
Screen: 1 · Shape of a 640 × 480 color photo in NumPy? · 2 · What does a kernel respond to? · 3 · Output size: W 32, K 3, P 0, S 1? · 4 · Why does an MLP fail on images (one reason)? · 5 · What does a skip connection add?
Notes: Answers: (480, 640, 3) · patterns that look like it · 30 · parameter explosion / no neighbourhood / not shift-tolerant · F(x) + x, learn only the change.

### 2.03 · From Day 1 to Day 2
Type: compare
Screen: Day 1 · one image → one label · "There is a cat" | Day 2 · one image → many objects, each with a location, a shape, and an identity over time · "Cat at (40, 60, 210, 300), these pixels, track #7"
Notes: The backbone you met yesterday is still inside every model today. We add heads that answer "where".

### 2.04 · Today's engineering question
Type: rule
Screen: How do we find every object in an image — quickly, at any size, without duplicates — and prove how good we are at it?
Notes: Every act today answers part of this sentence.

### 2.05 · Today, in eight acts
Type: list
Screen: 1 · The task ladder · 2 · Describing a box · 3 · Many objects: the two-stage story · 4 · Scale and duplicates · 5 · One look: YOLO and DETR · 6 · How good is the detector? · 7 · Pixel-level understanding · 8 · From frames to motion
Notes: Acts 3 to 5 are the history of detection told as fixes. Act 6 is where the exam is hardest.

### 2.06 · Goals for today
Type: cards
Screen: 01 · Name the right vision task for a business need · 02 · Convert between box formats and compute IoU · 03 · Explain how two-stage detectors work · 04 · Run NMS by hand · 05 · Explain YOLO's one-look idea and why DETR needs no NMS · 06 · Compute AP from a list of predictions · 07 · Explain U-Net's skip connections · 08 · Explain tracking by detection
Notes: Goals 4 and 6 are hand-calculation skills. You will do both today.

---

## Act 1 · The task ladder

### 2.07 · Act 1
Type: section
Screen: 01 · The task ladder · One image, many possible questions
Notes: Before choosing a model, choose the question.

### 2.08 · Eight questions about one image
Type: table
Screen: Classification · what is in it? | Classification + localisation · what, and where (one object)? | Object detection · where is every object? | Semantic segmentation · which class is every pixel? | Instance segmentation · which object does every pixel belong to? | Panoptic segmentation · every pixel: class + instance | Keypoints / pose · where are the joints? | Tracking · which object is which across frames?
Notes: Go down the ladder with one street photo. Each row gives a richer and more expensive answer.

### 2.09 · Classification vs detection
Type: compare
Screen: Classification · one label for the whole image · "street" | Detection · a box + class + confidence for each object · car 0.94 · person 0.88 · person 0.81
Notes: Detection answers "where" and "how many". Classification cannot count.

### 2.10 · Semantic vs instance segmentation
Type: compare
Screen: Semantic · every pixel gets a class · all people are one "person" blob | Instance · every object gets its own mask · person #1, person #2, person #3
Notes: If you need to count touching objects, you need instance segmentation.

### 2.11 · Things and stuff
Type: compare
Screen: Things · countable objects with clear shapes · car, person, bottle | Stuff · amorphous regions · road, sky, grass, water · Panoptic segmentation handles both
Notes: You count things, you measure stuff.

### 2.12 · Keypoints and pose
Type: definition
Screen: Keypoint detection — predicting the location of specific points on an object, such as 17 body joints for a person. Joined together they give a pose.
Notes: Used in sports analysis, physiotherapy, ergonomics, and fall detection.

### 2.13 · Which task does the business need?
Type: table
Screen: Count cars in a parking lot · detection | Check workers wear helmets · detection | Measure crack area on a wall · segmentation | Coach a squat · pose | Count people entering a mall · tracking | Sort a photo by scene type · classification
Notes: Ask the room before revealing each answer. The cheapest task that answers the question wins.

### 2.14 · Rule of thumb
Type: rule
Screen: Choose the simplest task that answers the business question. Each step down the ladder costs more labels, more compute, and more time.
Notes: Labelling a mask takes roughly ten times longer than drawing a box.

---

## Act 2 · Describing a box

### 2.15 · Act 2
Type: section
Screen: 02 · Describing a box · Four numbers, three conventions, many bugs
Notes: Floor content, but it causes real bugs in production.

### 2.16 · A bounding box
Type: definition
Screen: Bounding box — the smallest axis-aligned rectangle that contains an object, described by four numbers.
Notes: Axis-aligned means the sides are horizontal and vertical. Rotated boxes exist for aerial images; we skip them.

### 2.17 · Three box formats
Type: table
Screen: xyxy · (x_min, y_min, x_max, y_max) · torchvision, Pascal VOC | xywh · (x_min, y_min, width, height) · COCO | cxcywh · (x_centre, y_centre, width, height) · YOLO, DETR — often normalised to 0–1
Notes: Same box, three ways of writing it. Mixing them up is silent — the box just lands in the wrong place.

### 2.18 · Converting formats — worked
Type: worked
Screen: Image 640 × 480 · Box xyxy = (100, 120, 300, 360) · xywh = (100, 120, 200, 240) · cxcywh = (200, 240, 200, 240) · normalised cxcywh = (0.3125, 0.5, 0.3125, 0.5)
Notes: Width = 300 − 100, centre x = 100 + 200/2. Normalise by dividing x values by 640 and y values by 480.

### 2.19 · Gotcha: normalised vs pixel coordinates
Type: compare
Screen: Normalised · values 0–1 · independent of image size | Pixels · values up to width and height · A normalised box drawn as pixels is a tiny box in the top-left corner
Notes: If all your boxes are crammed into the top-left corner, you forgot to multiply by the image size.

### 2.20 · Comparing two boxes: IoU
Type: definition
Screen: IoU (Intersection over Union) — the area where two boxes overlap divided by the area they cover together. 0 = no overlap · 1 = identical.
Notes: IoU is how detection decides whether a prediction "hit" the real object.

### 2.21 · IoU — worked example 1
Type: worked
Screen: A = (0, 0, 4, 4) · area 16 · B = (2, 2, 6, 6) · area 16 · Intersection = (2, 2, 4, 4) · area 4 · Union = 16 + 16 − 4 = 28 · IoU = 4 / 28 ≈ 0.14
Notes: The boxes look like they overlap a fair bit, but IoU is only 0.14. Intuition underestimates how strict IoU is.

### 2.22 · IoU — worked example 2
Type: worked
Screen: A = (0, 0, 4, 4) · area 16 · B = (1, 0, 5, 4) · area 16 · Intersection = (1, 0, 4, 4) · area 12 · Union = 16 + 16 − 12 = 20 · IoU = 12 / 20 = 0.60
Notes: Shifted by one unit out of four, IoU is 0.6. Identical boxes give 1.0.

### 2.23 · What IoU values look like
Type: cards
Screen: 0.3 · loosely on the object · 0.5 · the classic "hit" threshold · 0.75 · tight · 0.9 · almost perfect
Notes: IoU Darts will train your eye for these numbers.

### 2.24 · IoU in code
Type: code
Screen: `ix1, iy1 = max(a.x1, b.x1), max(a.y1, b.y1)` · `ix2, iy2 = min(a.x2, b.x2), min(a.y2, b.y2)` · `inter = max(0, ix2 − ix1) * max(0, iy2 − iy1)` · `union = area(a) + area(b) − inter` · `iou = inter / union`
Notes: The max(0, …) handles boxes that do not overlap at all. Forgetting it gives negative areas.

### 2.25 · IoU Darts
Type: activity
Screen: Activity · IoU Darts · Drag a box to hit the target IoU · Closest team wins · Site → Activities → IoU Darts
Notes: Ten minutes.

### 2.26 · Localising one object
Type: diagram
Screen: Image → CNN backbone → features → two heads: class head (softmax over classes) + box head (4 numbers) · Loss = classification loss + box regression loss
Notes: For one object, this works. Predicting 4 numbers is a regression problem, like predicting a price.

### 2.27 · The problem
Type: rule
Screen: One head predicts one box. But a street photo has zero, three, or forty objects. How many box outputs should the network have?
Notes: The number of outputs must be fixed, but the number of objects is not. Acts 3 to 5 are three answers to this.

---

## Act 3 · Many objects — the two-stage story

### 2.28 · Act 3
Type: section
Screen: 03 · Many objects: the two-stage story · First find places that might contain an object, then classify each one
Notes: Each detector in this act fixes the slowness of the previous one.

### 2.29 · Idea 1: the sliding window
Type: diagram
Screen: Slide a window across the image → classify each crop → "object" or "background" · Repeat at many window sizes and shapes
Notes: It works in principle. Let's count the cost.

### 2.30 · Why sliding windows explode
Type: worked
Screen: 640 × 480 image · a window every 8 pixels → about 4,800 positions · × 10 sizes × 3 shapes → about 144,000 crops · each needs a CNN pass · and most of them are background
Notes: Far too slow. We need to look only where objects probably are.

### 2.31 · Idea 2: region proposals
Type: definition
Screen: Region proposal — a candidate box that might contain an object, found by a fast method that groups similar pixels (e.g. selective search). About 2,000 per image instead of 100,000+.
Notes: Proposals do not know what the object is. They only say "something might be here".

### 2.32 · R-CNN (2014)
Type: diagram
Screen: Image → ~2,000 region proposals → warp each to a fixed size → CNN on each → classify (SVM) + refine the box
Notes: R stands for regions. It was a big accuracy jump over hand-crafted features.

### 2.33 · R-CNN's problem
Type: cards
Screen: 2,000 CNN passes per image · about 47 seconds per image · Overlapping regions recompute the same features again and again · Three separate training stages
Notes: Forty-seven seconds per image is not usable for video. Where is the waste?

### 2.34 · Fast R-CNN: compute features once
Type: diagram
Screen: Image → CNN once → one feature map → crop each proposal's region from the feature map (RoI pooling) → fixed-size features → classify + refine box
Notes: Crop the features, not the pixels. One CNN pass instead of two thousand.

### 2.35 · RoI pooling
Type: definition
Screen: RoI pooling — take a region of the feature map of any size and pool it into a fixed grid (e.g. 7 × 7), so every proposal gives the same-sized input to the head.
Notes: The head needs fixed-size input, but proposals come in all sizes. RoI pooling solves that.

### 2.36 · Fast R-CNN's new bottleneck
Type: rule
Screen: The CNN now takes a fraction of a second. The slow part is the proposal method — selective search runs on the CPU and takes about 2 seconds.
Notes: Fix one bottleneck and another appears. That is engineering.

### 2.37 · Faster R-CNN: the network proposes
Type: diagram
Screen: Image → CNN → feature map → Region Proposal Network (RPN) suggests boxes → RoI pooling → classify + refine · Everything is one network, trained together
Notes: Let the network learn where objects are likely to be. This removed the last hand-designed step.

### 2.38 · Anchors
Type: definition
Screen: Anchor — a pre-defined template box placed at every feature-map position. The RPN predicts, for each anchor, "is there an object?" and how to nudge the anchor to fit it.
Notes: Instead of predicting boxes from nothing, the network adjusts templates. Much easier to learn.

### 2.39 · Anchors — worked
Type: worked
Screen: 3 scales (small, medium, large) × 3 aspect ratios (1:2, 1:1, 2:1) = 9 anchors per position · Feature map 40 × 30 → 1,200 positions × 9 ≈ 10,800 anchors · The RPN keeps the best few hundred
Notes: Many anchors, few objects. That imbalance matters in training.

### 2.40 · The two-stage pattern
Type: diagram
Screen: Stage 1 · propose: "where might something be?" → Stage 2 · classify and refine: "what is it, exactly where?" · Accurate, especially for small objects · slower than one-stage
Notes: Faster R-CNN is still a strong, accurate baseline. Lab 2A runs it from torchvision.

### 2.41 · The two-stage family
Type: table
Screen: R-CNN · CNN per proposal · ~47 s / image | Fast R-CNN · CNN once, RoI pooling · ~2 s (proposals are slow) | Faster R-CNN · learned proposals (RPN) · about 5–7 images / s on a 2015 GPU | Mask R-CNN · + a mask head (Act 7)
Notes: Read the middle column. Each row fixed the slow part of the row above it.

---

## Act 4 · Scale and duplicates

### 2.42 · Act 4
Type: section
Screen: 04 · Scale and duplicates · Two problems every detector must solve
Notes: Small objects and duplicate boxes. Both cause most real-world failures.

### 2.43 · The scale problem
Type: rule
Screen: A person close to the camera is 400 pixels tall. A person far away is 20 pixels tall. Same class, 20× size difference.
Notes: Deep layers have a big receptive field — good for big objects, terrible for tiny ones.

### 2.44 · Fix 1: the image pyramid
Type: compare
Screen: Idea · run the detector on the image at several sizes (100%, 50%, 25%) | Cost · several full passes · accurate but slow
Notes: Works, but multiplies the cost.

### 2.45 · Fix 2: the Feature Pyramid Network
Type: diagram
Screen: Early layers · high resolution, weak meaning · Deep layers · low resolution, strong meaning · FPN · pass deep meaning back up to the high-resolution layers → detect small objects on fine maps, large objects on coarse maps
Notes: One pass, many scales. FPN is inside almost every modern detector, including the torchvision models we use.

### 2.46 · The duplicate problem
Type: rule
Screen: A detector usually fires several overlapping boxes on the same object — all with high confidence. We want one box per object.
Notes: Show a photo with five boxes stacked on one car.

### 2.47 · Non-Maximum Suppression (NMS)
Type: definition
Screen: NMS — keep the highest-confidence box, delete every other box that overlaps it by more than an IoU threshold, then repeat with the next highest remaining box.
Notes: Keep the best, remove its copies, repeat.

### 2.48 · NMS step by step
Type: worked
Screen: Boxes (score): A 0.95 · B 0.90 · C 0.80 · D 0.75 · E 0.60 · F 0.55 · IoU threshold 0.5 · Keep A → remove B (IoU 0.7 with A) and D (0.6) · Next highest left: C → keep → remove E (0.65 with C) · Next: F → keep (overlaps nothing above 0.5) · Result: A, C, F
Notes: Walk through it slowly. Be NMS lets them do exactly this.

### 2.49 · The NMS threshold
Type: compare
Screen: Too high (0.9) · almost nothing is removed · duplicates survive | Too low (0.2) · real neighbouring objects get deleted · Typical: 0.45–0.7
Notes: The threshold is a trade-off between duplicates and missed neighbours.

### 2.50 · Two knobs people confuse
Type: compare
Screen: Confidence threshold · "how sure must a box be to show at all?" · removes weak boxes | NMS IoU threshold · "how much overlap counts as a duplicate?" · removes copies
Notes: They do completely different jobs. Many bug reports are someone changing the wrong one.

### 2.51 · Where NMS fails: crowds
Type: cards
Screen: Two people standing close have high-IoU boxes · NMS keeps one, deletes the other · Crowd counting undercounts · Fixes: Soft-NMS (lower the score instead of deleting) · or detectors with no NMS at all (Act 5)
Notes: This failure is why NMS-free detectors are such a big deal.

### 2.52 · Be NMS
Type: activity
Screen: Activity · Be NMS · Keep and remove boxes in the right order · Site → Activities → Be NMS
Notes: Eight minutes. Then launch Lab 2A: IoU and NMS by hand.

### 2.53 · Lab 2A — part 1
Type: list
Screen: Write IoU · test it on the worked examples · Write NMS in NumPy · compare with `torchvision.ops.nms` · Check: same boxes kept
Notes: The asserts print a green tick when your function matches the library.

---

## Act 5 · One look — YOLO and DETR

### 2.54 · Act 5
Type: section
Screen: 05 · One look · What if we skip proposals and predict every box in one pass?
Notes: One-stage detectors trade a little accuracy for a lot of speed.

### 2.55 · YOLO — You Only Look Once (2016)
Type: definition
Screen: YOLO — a one-stage detector: one forward pass of one network predicts all boxes and classes at once, with no separate proposal step.
Notes: The name says it: one look, not two thousand.

### 2.56 · The grid idea
Type: diagram
Screen: Split the image into a 7 × 7 grid · The cell containing an object's centre is responsible for it · Each cell predicts boxes, a confidence for each, and class probabilities
Notes: Every cell is a tiny detector for its own region.

### 2.57 · YOLOv1's output — worked
Type: worked
Screen: 7 × 7 grid · 2 boxes per cell × (x, y, w, h, confidence) = 10 numbers · + 20 class probabilities · = 30 numbers per cell · output tensor = 7 × 7 × 30
Notes: The whole detection result is one tensor. That is why it is fast.

### 2.58 · YOLO's loss in plain words
Type: cards
Screen: Box error · how far off are the box positions and sizes? · Objectness error · was "there is an object here" right? · Class error · was the class right? · Total = weighted sum of the three
Notes: Same multi-task idea as localising one object, but for every cell at once.

### 2.59 · YOLOv1's limits
Type: cards
Screen: Each cell predicts only 2 boxes → flocks of birds fail · One class per cell · Small objects get lost in coarse cells · Boxes less precise than Faster R-CNN
Notes: Every later YOLO version fixes one of these.

### 2.60 · The YOLO evolution
Type: table
Screen: v2 · anchors, batch norm | v3 · predictions at 3 scales (like FPN) | v4 / v5 · training tricks, heavy augmentation, easy tooling | v8 · anchor-free | YOLO26 (Jan 2026) · end-to-end, no NMS step
Notes: (cut first) Don't memorise versions. Notice the direction: anchors in, then anchors out, then NMS out.

### 2.61 · Anchor-based vs anchor-free
Type: compare
Screen: Anchor-based · adjust pre-defined template boxes · many hand-tuned settings | Anchor-free · predict the object centre and its distances to the box edges directly · simpler, fewer settings
Notes: Modern detectors are mostly anchor-free.

### 2.62 · DETR: detection as a set
Type: diagram
Screen: Image → CNN backbone → transformer → a fixed set of N "object queries" → each query outputs one box + class (or "no object") · Matched one-to-one to the ground truth during training
Notes: Each query learns to claim one object. Because training forbids two queries claiming the same object, duplicates never form.

### 2.63 · Why DETR needs no NMS
Type: rule
Screen: NMS cleans up duplicates after the fact. DETR is trained so duplicates are never produced — no anchors, no NMS, one clean set of boxes.
Notes: Day 3 explains the transformer inside. For today: one prediction per object, by design.

### 2.64 · RT-DETR: DETR made fast
Type: cards
Screen: Original DETR · slow to train, slow to run · RT-DETR · real-time transformer detector · RT-DETRv2 · improved version, available in Hugging Face Transformers · We fine-tune RT-DETRv2 in Lab 2B
Notes: This is the model in your afternoon lab.

### 2.65 · One-stage vs two-stage
Type: table
Screen: Two-stage (Faster R-CNN) · higher accuracy on small objects · slower · good when accuracy matters most | One-stage (YOLO, RT-DETR) · real-time · simpler to deploy · the default for video and edge devices
Notes: The gap has nearly closed. Speed requirements usually decide.

### 2.66 · Know your licences
Type: table
Screen: torchvision · BSD · use freely in products | Hugging Face Transformers · Apache 2.0 · use freely | supervision · MIT · use freely | Ultralytics YOLO · AGPL-3.0 · ship it in a product → you must open-source your code or buy a licence
Notes: As a developer, check the licence before you build a product on a library. Lab 2C uses Ultralytics for learning only.

---

## Act 6 · How good is the detector?

### 2.67 · Act 6
Type: section
Screen: 06 · How good is the detector? · "It looks good on my photos" is not evaluation
Notes: This act is the most heavily tested on the exam. Go slowly.

### 2.68 · When is a prediction correct?
Type: cards
Screen: A prediction is a True Positive (TP) if · its IoU with a ground-truth box ≥ threshold (e.g. 0.5) · AND its class is correct · AND that ground truth was not already matched
Notes: All three conditions. The third one stops two predictions both counting for the same object.

### 2.69 · TP, FP, FN for detection
Type: table
Screen: True Positive · a correct box on a real object | False Positive · a box on nothing, wrong class, or a duplicate | False Negative · a real object with no matching box | (True negatives are not counted — there are infinite empty boxes)
Notes: Detection has no true negatives. That is why we use precision and recall, not accuracy.

### 2.70 · Precision and recall for detection
Type: compare
Screen: Precision = TP / (TP + FP) · "of the boxes I drew, how many were right?" | Recall = TP / (TP + FN) · "of the real objects, how many did I find?"
Notes: Same definitions as Day 1, applied to boxes.

### 2.71 · Which one matters more?
Type: compare
Screen: Airport weapon screening · missing one is a disaster → prioritise recall | Spam-like alerts to a busy operator · false alarms get ignored → prioritise precision
Notes: The business decides which error is worse. Threshold Tycoon is exactly this.

### 2.72 · Confidence changes everything
Type: rule
Screen: Raise the confidence threshold → fewer boxes → precision up, recall down. Lower it → more boxes → recall up, precision down.
Notes: There is no single precision or recall for a detector, only one per threshold.

### 2.73 · The precision–recall curve
Type: diagram
Screen: Sort predictions by confidence · go down the list one by one · after each, compute precision and recall · plot recall on x, precision on y · A good detector stays high and to the right
Notes: The curve summarises every possible threshold at once.

### 2.74 · AP by hand — the setup
Type: worked
Screen: 5 ground-truth objects · 8 predictions sorted by confidence · TP · TP · FP · TP · FP · TP · FP · FP
Notes: We already decided which are TP and which are FP using IoU ≥ 0.5. Now we build the curve.

### 2.75 · AP by hand — the table
Type: table
Screen: 1 TP · P 1/1 = 1.00 · R 1/5 = 0.2 | 2 TP · 2/2 = 1.00 · 0.4 | 3 FP · 2/3 = 0.67 · 0.4 | 4 TP · 3/4 = 0.75 · 0.6 | 5 FP · 3/5 = 0.60 · 0.6 | 6 TP · 4/6 = 0.67 · 0.8 | 7 FP · 4/7 = 0.57 · 0.8 | 8 FP · 4/8 = 0.50 · 0.8
Notes: Precision counts TPs so far divided by predictions so far. Recall counts TPs so far divided by 5. Recall never goes down.

### 2.76 · AP by hand — the area
Type: worked
Screen: Interpolated precision at each recall = the best precision at that recall or higher · R 0 → 0.4: 1.00 · R 0.4 → 0.6: 0.75 · R 0.6 → 0.8: 0.67 · R 0.8 → 1.0: 0 (one object never found) · AP = 0.4×1.00 + 0.2×0.75 + 0.2×0.67 + 0.2×0 ≈ 0.68
Notes: AP is the area under the cleaned-up curve. The last term is zero because recall never reached 1: one object was missed entirely.

### 2.77 · From AP to mAP
Type: definition
Screen: mAP (mean Average Precision) — compute AP separately for each class, then take the mean. One number for the whole detector.
Notes: A detector great at cars and terrible at bicycles can still have a decent mAP. Always look per class.

### 2.78 · mAP@0.5 vs mAP@0.5:0.95
Type: compare
Screen: mAP@0.5 · a hit needs IoU ≥ 0.5 · forgiving | mAP@0.5:0.95 · average of mAP at IoU 0.5, 0.55, … 0.95 · rewards tight boxes · the COCO standard · always lower
Notes: When comparing models, make sure both use the same definition.

### 2.79 · Speed is a metric too
Type: cards
Screen: Latency · milliseconds per image · FPS · images per second · Measure on the target hardware, not your laptop · Accuracy nobody waits for is worthless
Notes: A 30 FPS camera needs under 33 milliseconds per frame, including drawing and tracking.

### 2.80 · Choosing the operating threshold
Type: rule
Screen: The default threshold (often 0.25 or 0.5) is not a decision. Pick the threshold from the cost of a false positive vs the cost of a false negative for your user.
Notes: In your project, state your threshold and why. That is worth rubric marks.

### 2.81 · What a high mAP still hides
Type: cards
Screen: Per-class weakness · Small objects · Night, rain, glare · Rare classes · Unseen camera angles · Look at failure images, not only the number
Notes: Every project must include five failure images with causes. This is why.

### 2.82 · Threshold Tycoon
Type: activity
Screen: Activity · Threshold Tycoon · Choose the confidence threshold for three businesses · Hidden costs decide the winner · Site → Activities → Threshold Tycoon
Notes: Ten minutes. Reveal the best thresholds at the end and why they differ.

### 2.83 · Lab 2A — part 2
Type: list
Screen: Compute precision, recall and AP for a list of predictions · Check against the worked example (≈ 0.68) · Run Faster R-CNN, Mask R-CNN and Keypoint R-CNN from torchvision · Read the output fields: boxes, labels, scores, masks, keypoints
Notes: Students who finish early do the NMS threshold sweep extra task.

---

## Act 7 · Pixel-level understanding: segmentation

### 2.84 · Act 7
Type: section
Screen: 07 · Pixel-level understanding · Boxes are rough. Some problems need the exact shape.
Notes: Measuring a crack, a tumour, or a field needs pixels, not boxes.

### 2.85 · Semantic segmentation
Type: definition
Screen: Semantic segmentation — assigning a class label to every pixel in the image. The output is a label map the same size as the input.
Notes: A 512 by 512 image gives 262,144 classification decisions.

### 2.86 · The obvious attempt: a sliding window per pixel
Type: compare
Screen: Idea · crop a patch around each pixel, classify the centre pixel | Problem · 262,144 crops per image, overlapping crops recompute the same features · absurdly slow
Notes: The same waste we saw with R-CNN.

### 2.87 · Fully convolutional networks
Type: diagram
Screen: Use only conv layers (no fully connected head) → output a class score map instead of one label · But pooling shrinks the map: 512 → 16
Notes: Without fully connected layers, the network outputs a map. But the map is tiny and blurry.

### 2.88 · The tension
Type: compare
Screen: Downsampling · grows the receptive field · understands what | Full resolution · keeps fine detail · knows where · Segmentation needs both
Notes: Go down to understand, come back up to locate.

### 2.89 · Encoder–decoder
Type: diagram
Screen: Encoder · conv + pool: 512 → 256 → 128 → 64 → 32 (more meaning, less detail) → Decoder · upsample: 32 → 64 → 128 → 256 → 512 (back to full size) → per-pixel classes
Notes: The decoder must learn how to grow the map back.

### 2.90 · Upsampling options
Type: cards
Screen: Nearest / bilinear · copy or average · no learning · Unpooling · put values back in place · Max unpooling · remember where the max came from · Transposed convolution · learned upsampling
Notes: Transposed convolution lets the network learn how to upsample.

### 2.91 · Transposed convolution — worked
Type: worked
Screen: Input [1, 2] · kernel [1, 1, 1] · stride 2 · Each input value stamps a scaled copy of the kernel, 2 steps apart · 1 × [1, 1, 1] at positions 0–2 · 2 × [1, 1, 1] at positions 2–4 · overlaps add → output [1, 1, 3, 2, 2] · length = (2 − 1)·2 + 3 = 5
Notes: (cut first) Formula: out = (in − 1)·S − 2P + K. Overlaps add up, which can create checkerboard artifacts.

### 2.92 · The problem with plain encoder–decoders
Type: rule
Screen: By the bottom of the encoder, the exact edges are gone. The decoder can guess the shape, but boundaries come out blurry.
Notes: Information destroyed by pooling cannot be recovered by upsampling alone.

### 2.93 · U-Net: skip connections across
Type: diagram
Screen: Encoder levels are copied directly across to the matching decoder levels · The decoder gets both "what" (from below) and "where" (from the skip) · U-shaped diagram
Notes: The encoder knows what, the decoder needs where, and skip connections deliver it. Different from ResNet's skips: these concatenate across the U.

### 2.94 · Why U-Net is everywhere
Type: cards
Screen: Works with few training images · Precise boundaries · Medical imaging standard · The core inside Stable Diffusion's denoiser (Day 3)
Notes: Created in 2015 for cell images. You will meet it again tomorrow inside image generators.

### 2.95 · Instance segmentation: Mask R-CNN
Type: diagram
Screen: Faster R-CNN (box + class per object) + a small mask head that predicts a mask inside each box · RoIAlign: precise feature cropping without rounding
Notes: Detect first, then segment inside each box. Lab 2A runs it.

### 2.96 · Panoptic and keypoints
Type: cards
Screen: Panoptic · every pixel gets a class and, for things, an instance ID · Keypoint R-CNN · Mask R-CNN's idea, predicting joints instead of masks · Pose = keypoints + their connections
Notes: Same backbone, different heads. That is the pattern of modern vision.

### 2.97 · Segmentation metrics
Type: compare
Screen: Pixel accuracy · misleading — 95% background gives 95% for doing nothing | Mask IoU · overlap of predicted and true masks | Dice = 2|A ∩ B| / (|A| + |B|) · common in medical imaging
Notes: Accuracy lies again, for the same imbalance reason as Day 1.

### 2.98 · Choosing boxes or masks
Type: table
Screen: Counting · boxes are enough | Measuring area or length · masks | Touching objects · instance masks | Background regions (road, sky) · semantic masks | Labelling budget is tight · boxes
Notes: Masks cost far more to label. Use them only when shape matters.

---

## Act 8 · From frames to motion: tracking

### 2.99 · Act 8
Type: section
Screen: 08 · From frames to motion · Detection sees each frame alone. Tracking connects them.
Notes: Ceiling block. Start the Lab 2B training before teaching this act, so it trains while you talk.

### 2.100 · Lab 2B — start training now
Type: list
Screen: Open Lab 2B · run up to "Start training" · RT-DETRv2 fine-tunes for a few minutes on a small dataset · We read the results after this act
Notes: Get every student's training cell running, then teach Act 8 while the GPUs work.

### 2.101 · Video is a stack of frames
Type: cards
Screen: Frame rate · 25–30 frames per second is typical · Each frame is an image · Motion blur · fast objects smear · Neighbouring frames are almost identical
Notes: A one-minute video at 30 FPS is 1,800 images.

### 2.102 · Why detection alone is not enough
Type: rule
Screen: A detector says "3 people" in every frame. It cannot say whether they are the same 3 people, or count how many entered the shop today.
Notes: Counting entries needs identity over time.

### 2.103 · Tracking by detection
Type: diagram
Screen: Each frame: detect → predict where existing tracks should be now → match new detections to tracks → update matched tracks · start new tracks · retire lost tracks
Notes: Detect, predict, match, update. Four verbs.

### 2.104 · Predict: a motion model
Type: definition
Screen: Motion model — a guess of where each tracked object will be in the next frame, based on its recent speed and direction. The Kalman filter is the classic way to do this.
Notes: If a car moved 10 pixels right each frame, expect it 10 pixels further right now.

### 2.105 · Match: who is who?
Type: cards
Screen: Compute IoU between predicted track boxes and new detections · High IoU = probably the same object · Assign pairs so the total overlap is best (Hungarian algorithm) · Optionally compare appearance too
Notes: IoU comes back. Matching is just IoU plus a fair assignment.

### 2.106 · Tracking failures
Type: cards
Screen: ID switch · two people cross and swap IDs · Lost track · object hidden behind a pillar, comes back with a new ID · Fragmentation · one object, many short tracks
Notes: ID switches ruin counts. They are the main thing tracking metrics punish.

### 2.107 · ByteTrack's idea
Type: compare
Screen: Old trackers · throw away low-confidence boxes before matching | ByteTrack · match high-confidence boxes first, then try the low-confidence ones against unmatched tracks · a half-hidden person keeps their ID
Notes: A low score often means partly hidden, not "not a person". ByteTrack keeps those boxes useful.

### 2.108 · Counting with a line
Type: diagram
Screen: Draw a virtual line across the road · When a tracked object's centre crosses it → count in or out · Needs tracker IDs, otherwise one car is counted many times
Notes: Lab 2B does exactly this with supervision's LineZone.

### 2.109 · Worked case: traffic analytics
Type: cards
Screen: Detect vehicles · track with ByteTrack · count per lane with lines · speed = pixels moved × metres per pixel × FPS · flag stopped vehicles
Notes: This is a real product type. Many project teams pick it.

### 2.110 · Lab 2B — read the results
Type: list
Screen: Training curves: is loss still falling? · Validation mAP · Precision–recall curve · Failure gallery: what did it miss? · Then: ByteTrack + line counting on the video
Notes: Read one student's results on the projector and diagnose it together.

### 2.111 · Lab 2C — Ultralytics for beginners
Type: cards
Screen: Optional, self-paced · Predict, track and train in about 5 lines with YOLO26 · Try text prompts with YOLOE-26 · Ends with "what the library hid from you" · Learning only — remember the AGPL licence
Notes: Good for anyone who struggled with 2B. It shows the same ideas with less code.

---

## [STRETCH] Your own data

### 2.112 · Your own data
Type: section
Screen: Your own data · Labelling, formats, and the traps
Notes: [STRETCH] Twenty-five minutes. Very useful for the project; skip if behind.

### 2.113 · How many images do you need?
Type: cards
Screen: Fine-tuning a pretrained detector · a few hundred labelled images per class is a usable start · More variety beats more copies · Include the hard cases: night, glare, occlusion
Notes: [STRETCH] Variety in conditions matters more than raw count.

### 2.114 · Label formats
Type: compare
Screen: YOLO · one .txt per image · class cx cy w h, normalised | COCO · one JSON for the dataset · xywh in pixels · plus image and category lists
Notes: [STRETCH] Converting between them is where boxes silently shift. Check by drawing labels on images first.

### 2.115 · Data traps
Type: cards
Screen: Leakage · near-identical frames from one video in both train and test · Class imbalance · 5,000 cars, 40 bicycles · Label noise · boxes drawn loosely or inconsistently · Split by video or location, not by frame
Notes: [STRETCH] Frame leakage gives beautiful test scores that collapse in the real world.

### 2.116 · No defect examples? Anomaly detection
Type: cards
Screen: Factories have thousands of good parts and few defects · Learn what "normal" looks like · Flag anything far from normal · PatchCore idea: store normal patch features, compare new patches to the memory
Notes: [STRETCH] A completely different framing: learn normal instead of learning defects.

---

## Close of Day 2

### 2.117 · Ten distinctions to remember
Type: table
Screen: Classification vs detection | Semantic vs instance segmentation | xyxy vs xywh vs cxcywh | Confidence threshold vs NMS threshold | Two-stage vs one-stage | Anchor-based vs anchor-free | NMS vs NMS-free (DETR) | Precision vs recall | mAP@0.5 vs mAP@0.5:0.95 | Detection vs tracking
Notes: Read them aloud. These are tomorrow's exam.

### 2.118 · Day 2 recap
Type: list
Screen: Choose the simplest task that answers the question · IoU measures box overlap · Two-stage: propose then classify · FPN handles scale, NMS removes duplicates · YOLO looks once; DETR avoids duplicates by design · mAP summarises precision across recall and classes · U-Net brings "where" back with skip connections · Tracking = detect, predict, match, update
Notes: Eight lines, the whole day.

### 2.119 · Exit ticket
Type: quiz
Screen: 1 · IoU of (0, 0, 2, 2) and (1, 0, 3, 2)? · 2 · Duplicates survive — which threshold do you lower? · 3 · Why does detection not use accuracy? · 4 · What does a U-Net skip connection carry? · 5 · What causes an ID switch?
Notes: Answers: intersection 2, union 6 → 0.33 · the NMS IoU threshold · no true negatives (infinite empty boxes) · fine "where" detail from the encoder · two tracks swapping when objects cross or overlap.

### 2.120 · Tonight
Type: list
Screen: Finish Lab 2A and Lab 2B · Try Lab 2C if you want · Project: README with your use case and data source · Revise Days 1–2 for the exam
Notes: The exam covers Days 1 and 2 only.

### 2.121 · Tomorrow — Day 3
Type: title
Screen: Theory exam at 9:00 · Seeing beyond labels · Transformers · CLIP · Segment Anything · Project presentations
Notes: Exam first thing, then models that understand words, then your presentations.

---
Total slides: 121
