# Computer Vision for Developers: topic proposal

SDAIA Academy · 22–24 Nov 2026 · 3 days · about 20 students (year 2–5 undergrads)
Status: proposal for Musa to approve. Once approved it becomes `01-plan.md`, then `slides-day1.md` etc.

## How to read this

The course is one story: **teaching a machine to see**. Each act opens with a **problem**, shows the **obvious attempt and why it fails**, then gives the **fix**. The fix creates the next problem, which opens the next act. This gives students a reason for every topic. It's the same shape as Hussein's decks ("why the model alone is not enough" → the layers), applied to CV.

Each act lists its slide topics. These aren't final slides; `slides-dayN.md` expands each bullet into 1–3 slides. The slide estimates are rough, and the total runs 80–100 per day.

Tags:
- **[F]** Floor: the weakest student can follow it.
- **[C]** Climb.
- **[T]** Ceiling: non-trivial for the strongest student.
- **[STRETCH]** A block you deploy if a supervisor or camera is in the room, and drop silently otherwise.
- **[READ]** Kept in the deck for self-study, not taught live.

Source column: KAUST lecture numbers from `KAUST-Academy/Artificial-Intelligence-Courses/Lectures/Computer_Vision`. KAUST is the depth reference. Everything is re-explained at our level, with KAUST's maths turned into worked numbers.

## Daily clock (all three days)

Students see 9:00 on the site and in announcements. The plan below uses the real times.

| Block | Time | Length |
|---|---|---|
| B1 | 9:15–10:05 | 50 |
| B2 | 10:15–11:05 | 50 |
| B3 | 11:15–12:00 | 45 |
| Lunch | 12:00–1:00 | |
| B4 | 1:00–1:50 | 50 |
| B5 | 2:00–2:50 | 50 |
| Close | 2:50–3:00 | exit ticket / tomorrow |

[STRETCH] material sits at the end of each day's content, so if you run ahead it fills the gap. If you run behind, it simply doesn't happen.

---

## Day 1 · From pixels to features
*"Why is seeing so hard for a computer, and how did we stop hand-writing the rules?"*

**Fixed items:** icebreaker (20 min), pre-test (15 min), project brief published (10 min).
**Teaching time:** about 3h50.
**Deliverable by 3:00:** a trained CNN, with a written comparison against an MLP baseline and a pretrained model.

### Act 1 · The seeing problem [F] (KAUST 01) · ~8 slides
- What computer vision is. Vision vs image processing vs graphics: what goes in and what comes out.
- CV is everywhere: phone face unlock, Saher traffic cameras, pipeline corrosion inspection, crowd management at Hajj, medical scans, date-palm disease, retail shelves.
- **The semantic gap:** you see a cat, the computer sees 150,528 numbers.
- **Seven reasons it's hard:** viewpoint, lighting, scale, occlusion, deformation, background clutter, variation within a class. One photo per reason.
- The core question for the course: how do we turn numbers into meaning?

### Act 2 · Images are just numbers [F] (KAUST 01) · ~12 slides
- Pixels. Grayscale as a 2D grid of 0–255 values (the uint8 range).
- Colour: three channels (R, G, B), and the shape `(H, W, C)`.
- Coordinates: origin at the top-left, y grows downward, and `img[row, col]` means `img[y, x]`. This is the most common source of bugs.
- dtypes: uint8 vs float32, normalising to 0–1, and the overflow trap (`200 + 100 = 44` in uint8).
- **BGR vs RGB:** OpenCV loads BGR, everything else expects RGB, so faces turn blue.
- Resolution and aspect ratio. What resizing does, and interpolation (nearest vs bilinear).
- Other colour spaces: HSV, and why "find the red object" is easy there and hard in RGB.
- Files vs arrays: JPEG compression artifacts vs PNG. A loaded image is just an array.
- Batches: why models take `(N, C, H, W)` in PyTorch vs `(N, H, W, C)` elsewhere.

### Act 3 · Classical image processing: writing the rules by hand [F→C] (KAUST 01, 27) · ~14 slides
- **Point operations:** brightness, contrast, inversion. Histograms, and histogram equalisation for dark images.
- **Thresholding:** global vs adaptive vs Otsu. Worked example: document scanning.
- **Neighbourhood operations = convolution.** A kernel slides over the image, multiplies and sums. Worked by hand on a 5×5 grid.
- Kernel gallery: box blur, Gaussian blur, sharpen, Sobel-x, Sobel-y. What each one "looks for".
- Edges as gradient magnitude. The idea behind Canny (smooth → gradient → thin → hysteresis).
- Morphology: erosion, dilation, opening, closing, for cleaning masks.
- Hand-crafted features: corners, HOG ("histogram of edge directions"), SIFT in one slide. The classic pipeline: features → classifier (SVM).
- **The problem:** hand-designed features break with lighting, viewpoint and new classes. Every new task needs a new expert. *Could the machine learn the kernels itself?*

### Act 4 · Learning from data, and why the obvious network fails [C] (KAUST 01) · ~10 slides
- Supervised learning in one picture: examples + labels → model → prediction → loss → adjust.
- Train / validation / test splits, and why the test set is sealed.
- Loss as "how wrong". Gradient descent as walking downhill. Learning rate as step size, shown too small, right and too big.
- Softmax turns scores into probabilities. Cross-entropy is the penalty for confident wrong answers.
- **The obvious attempt:** flatten the image into a fully connected network (MLP).
- **Why it fails:**
  - Parameter explosion: 224×224×3 inputs × 1,000 neurons ≈ 150M weights in the first layer alone.
  - No sense of neighbourhood: shuffle the pixels and the MLP doesn't care.
  - Shift the cat 10 pixels and it's a new problem.
- What we actually need: local connectivity, shared weights, and building up from small parts to big ones.

### Act 5 · The convolutional neural network [C→T] (KAUST 01) · ~18 slides
- A convolution layer is Act 3's kernels, but learned.
- Local connectivity and weight sharing: one 3×3 filter is reused at every position.
- Convolution on RGB: the kernel has depth 3. Many filters → many output channels (feature maps).
- **Parameter count, worked:** `(k·k·C_in + 1)·C_out`, compared directly with the MLP number from Act 4.
- Padding (valid vs same) and stride (downsampling by skipping). Dilation in one slide.
- **Output size formula:** `⌊(W − K + 2P)/S⌋ + 1`, worked on three cases.
- Pooling: max vs average, and what each throws away.
- Activations: why stacking linear layers is pointless without them. ReLU.
- Flatten → fully connected → softmax head.
- **Tracing shapes through a small CNN, layer by layer.** This is the slide the exam tests.
- Feature hierarchy: edges → textures → parts → objects, shown as visualised filters.
- Receptive field: how a deep neuron "sees" a large region. Worked for 3 stacked 3×3 layers.

### Act 6 · Training it properly [C→T] (KAUST 02) · ~14 slides
- Batches, epochs, iterations. The PyTorch DataLoader as a conveyor belt.
- The training loop line by line: forward → loss → backward → step → zero_grad.
- Reading learning curves: underfitting vs good fit vs overfitting.
- **Fixes for overfitting:** more data, augmentation (flip, crop, colour jitter, and which ones are wrong for which task, e.g. flipping text or digits), dropout, early stopping, weight decay.
- BatchNorm: what it normalises and why training gets more stable. Train vs eval mode is a gotcha.
- Classification metrics: accuracy, the confusion matrix, precision / recall / F1. Why accuracy lies on imbalanced data.
- Reproducibility: seeds, and why the same seed can still give a different number on a GPU.
- Run discipline: change one thing at a time, keep a run log, and save checkpoints.

### Act 7 · Standing on giants: architectures and transfer learning [T] (KAUST 03, 02) · ~14 slides
Told as a chain of problems:
- LeNet: it works on digits.
- AlexNet: why 2012 happened (data + GPU + ReLU).
- VGG: just go deeper with 3×3. Why two 3×3 layers beat one 5×5.
- Inception: objects come in many sizes, so use several kernel sizes in parallel.
- **ResNet:** deeper got *worse* (the degradation problem). The fix is skip connections, as in "learn the change, not the whole thing".
- **MobileNet:** phones can't afford this. Depthwise-separable convolution, with the cost maths worked: about 8–9× fewer operations.
- EfficientNet: scale depth, width and resolution together.
- ImageNet and why pretrained weights are valuable.
- **Transfer learning:** freeze the backbone and train the head, vs fine-tune everything. A decision table based on data size and how similar the new data is.
- Limits of CNNs, which sets up Day 3: they're local, have no global context, and are tied to fixed classes.

### [STRETCH] Day 1 · Spot the bug (~20 min)
Five real CV pipeline bugs on slides, each fixable by a non-coder who followed today: BGR shown as RGB, uint8 overflow, a swapped x/y crop, eval mode forgotten, test data leaked into training. Teams race to find them.

### Day 1 labs (Colab, solved + unsolved)
- **Lab 1A · Images as arrays** (B3): load, inspect shape and dtype, channels, BGR→RGB, crop with slicing, histogram, threshold. **Convolution by hand in NumPy**, then checked against `cv2.filter2D`. Kernel gallery and Sobel edges. Extra tasks: an Otsu document scan, HSV colour masking.
- **Lab 1B · Your first CNN** (B5): CIFAR-10. MLP baseline → small CNN → print the shape after every layer → add augmentation and dropout → plot curves and a confusion matrix → transfer learning with pretrained ResNet-18 on the same data. Extra tasks: parameter count by formula vs `sum(p.numel())`, visualise first-layer filters, break it on purpose (set the learning rate to 1.0).

### Day 1 mini-activities (browser, a non-coder can win)
- **Pixel Detective:** a heavily zoomed grid of numbers. Guess the object as more of the image is revealed.
- **Be the Kernel:** apply a 3×3 kernel to a 5×5 grid by hand. Fastest correct team wins.
- **Shape Race:** given a layer stack, predict the output shape. Score saved locally.

### Day 1 ladder check
- Floor at 9:15: "an image is a grid of numbers".
- Ceiling at 2:00: residual connections, depthwise-separable cost maths, and diagnosing transfer learning from curves.

These can't be reached in the morning. ✓

---

## Day 2 · Where is it, what shape is it, where is it going?
*"Knowing what's in the picture isn't enough. Now find it, outline it, count it, follow it."*

**Teaching time:** about 4h30 (no fixed items besides the recap).
**Deliverable:** a fine-tuned detector with a mAP number, plus a tracking-and-counting demo on a video.

### Act 1 · The task ladder [F] (KAUST 04, 05) · ~8 slides
- Classification → classification + localisation → detection → semantic segmentation → instance segmentation → panoptic → keypoints / pose → tracking. One image, eight outputs.
- Things vs stuff (cars vs road).
- Which task does the business need? Examples: parking (count), PPE (detect), crack inspection (segment), sports (pose), traffic (track).

### Act 2 · Describing a box [F→C] (KAUST 04) · ~10 slides
- Box formats: `xyxy`, `xywh`, `cxcywh`, normalised 0–1 (the YOLO format). Converting between them is a gotcha.
- **IoU:** intersection over union, worked on three pairs of boxes. What 0.5 "looks like".
- Localising one object = classification + box regression, trained with a multi-task loss.
- **The problem:** what if there are many objects, or none?

### Act 3 · Many objects: the two-stage story [C] (KAUST 04) · ~14 slides
- Sliding window: count the windows and the cost explodes.
- Region proposals (selective search): about 2,000 "maybe" boxes.
- **R-CNN:** run a CNN on each proposal. Accurate but slow (~47 s per image). Why.
- **Fast R-CNN:** run the CNN once and crop features instead of pixels (RoI pooling).
- **Faster R-CNN:** let the network propose regions itself (RPN). Anchors as "template boxes".
- The two-stage pattern in one diagram.

### Act 4 · Scale and duplicates [C] (KAUST 04) · ~10 slides
- **Small vs large objects:** image pyramid (slow) vs Feature Pyramid Network (reuse every layer).
- **Duplicate boxes:** the NMS algorithm step by step on 6 boxes, and what happens when the IoU threshold is too high or too low.
- Confidence threshold vs NMS threshold. Two knobs that do different things.
- Crowds: why NMS kills real overlapping people.

### Act 5 · One look: the YOLO story [C→T] (KAUST 04, 08) · ~14 slides
- YOLO v1 idea: split the image into a grid, and each cell predicts boxes + classes in one forward pass.
- The YOLO loss in plain words: box error + "is there an object" error + class error.
- v1 limits: small objects, clusters of objects.
- Evolution as fixes: anchors (v2), multi-scale heads (v3), training tricks (v4/v5), anchor-free (v8), and the current Ultralytics generation. *Verify the latest version against docs when building.*
- **DETR:** detection as set prediction with transformers, with no anchors and no NMS. This previews Day 3.
- One-stage vs two-stage trade-off table: speed, accuracy, small objects.
- Licences: Ultralytics is AGPL-3.0. What that means for a developer shipping a product. This is a real-world gotcha.

### Act 6 · How good is the detector? [C→T] · ~14 slides
- TP / FP / FN for boxes: a match depends on IoU ≥ threshold *and* the class being right.
- Precision vs recall, with a security-camera example vs a medical-screening example.
- **Precision-recall curve → AP → mAP.** Worked by hand on 8 predictions.
- mAP@0.5 vs mAP@0.5:0.95, and why the second is stricter.
- Speed: latency, FPS, and the trade-off curve.
- Choosing the operating threshold from business cost, not from the default 0.25.
- What a high mAP still hides: per-class performance, small objects, rare conditions.

### Act 7 · Pixel-level understanding: segmentation [C→T] (KAUST 05) · ~14 slides
- Semantic segmentation as classifying every pixel.
- The obvious attempt: a sliding window per pixel, which is absurdly slow.
- Fully convolutional networks: downsample to understand, upsample to locate.
- Upsampling: unpooling, max-unpooling, transposed convolution (worked in 1D).
- **Skip connections → U-Net:** the encoder knows *what*, the decoder needs *where*.
- Instance segmentation: Mask R-CNN = Faster R-CNN + a mask head.
- Panoptic segmentation, and keypoints / pose as "points instead of masks".
- Metrics: pixel accuracy lies; mask IoU and Dice are what to use.

### Act 8 · From frames to motion: tracking [T] (KAUST 05, 17, 27) · ~10 slides
- Video = a stack of frames, plus FPS and motion blur.
- Tracking by detection: predict → match → update.
- The motion model in plain words ("where should it be now?"), the Kalman intuition, matching by IoU.
- ID switches and lost tracks. ByteTrack's idea: keep the low-confidence boxes.
- Counting with line crossing and region occupancy. Traffic analytics as the worked case.

### [STRETCH] Day 2 · Your own data (~25 min)
- Labelling tools, label formats (YOLO txt vs COCO JSON), and how many images you really need.
- Class imbalance, near-duplicates leaking across splits, and label noise.
- Industrial anomaly detection when you have no defect examples (the PatchCore idea).

### Day 2 labs
- **Lab 2A · Detection by hand** (B2/B3): IoU function → NMS in NumPy → checked against `torchvision.ops.nms`. **mAP by hand** on a small prediction list. Then Ultralytics inference for detect, segment and pose on images, reading the results object field by field. Extra tasks: an NMS threshold sweep with visualisation, xywh↔xyxy converters with tests.
- **Lab 2B · Fine-tune and track** (B4/B5): fine-tune a small YOLO on a small built-in dataset for a few epochs. Candidates to verify: crack-seg, african-wildlife, carparts-seg. Read the results: curves, PR curve, confusion matrix, val mAP. Then track + count on a provided video file. Extra tasks: change the confidence threshold and re-measure, compare two model sizes on speed vs mAP, add a counting line.

### Day 2 mini-activities
- **IoU Darts:** draw a box to hit a target IoU (e.g. exactly 0.5).
- **Be NMS:** click to suppress boxes in the right order.
- **Threshold Tycoon:** choose a confidence threshold for three businesses (airport security, retail counting, medical screening). Scored against hidden costs.

### Day 2 ladder check
- Floor: "a box is four numbers".
- Ceiling: mAP by hand, the DETR idea, tracking ID-switch reasoning, and reading a training run.

---

## Day 3 · Seeing beyond labels: transformers, foundation models, language
*"Every model so far only knows the classes we labelled. What if it could learn without labels, and understand words?"*

**Fixed items:**
- 9:15–9:55 theory exam (30 MCQ, closed book)
- 2:00–2:50 presentations (~7 teams × 6 min)
- 2:50–3:00 post-test

**Teaching time:** about 2h50 (B2, B3, B4).
**Deliverable:** a CLIP-powered zero-shot classifier and image search, plus an open-vocabulary detection + segmentation pipeline.

Day 3 has a lot more content than teaching time. Acts 6–8 are written to work as **[READ]** if you run short. That fits "more is better, they can read on".

### Act 1 · The label problem [F] (KAUST 09, 19, 24) · ~8 slides
- Labels are expensive: ImageNet took years, and medical labels need doctors.
- The **closed-set assumption:** the classifier must pick one of its classes, even for things it has never seen.
- Softmax overconfidence: a cat classifier says "dog, 97%" for a car.
- Two escape routes: learn without labels (self-supervised) and learn from text (language supervision).

### Act 2 · Attention and the Vision Transformer [C] (KAUST 07, 08) · ~14 slides
- Recap: CNNs see locally and grow their view slowly.
- **Attention in plain words:** every part looks at every other part and decides what matters. A sentence example first, then an image.
- Query / key / value as "question / label / content", with a tiny worked dot-product.
- Positional encoding: attention has no sense of order, so we add position.
- **ViT:** cut the image into 16×16 patches → tokens → transformer → CLS token. Count the tokens for a 224 image (196).
- CNN vs ViT: built-in assumptions vs data hunger. Why ViT needs much more data.
- DETR revisited, with Swin and ConvNeXt in one slide each ("the CNN strikes back").

### Act 3 · Learning without labels [C→T] (KAUST 19, 20, 23) · ~12 slides
- Self-supervised learning: make up a task from the data itself (pretext tasks: colourisation, jigsaw, masking).
- **Contrastive learning (SimCLR):** two augmented views of one image = a positive pair, everything else = negatives. Pull together, push apart.
- **Embeddings:** an image becomes a vector. Similar images get close vectors. Cosine similarity, worked.
- DINO / DINOv2: one frozen backbone, many tasks. Its features segment objects without ever being told to.
- What you can build on embeddings: image search, duplicate detection, clustering, few-shot classification with k-NN.

### Act 4 · Connecting images and words: CLIP [T] (KAUST 21, 23, 25) · ~14 slides
- 400M image–caption pairs from the web, with no hand labels.
- **Contrastive pre-training:** a batch of N images and N captions forms an N×N similarity matrix, and training makes the diagonal win.
- A shared embedding space: text and images live in the same "room".
- **Zero-shot classification:** turn classes into sentences ("a photo of a {class}"), embed them, pick the closest.
- Prompt templates and ensembling, and why wording changes accuracy.
- **Where CLIP fails:** counting, left/right and spatial relations, the bag-of-words problem, typographic attacks (a paper label saying "iPod" stuck on an apple), bias from web data.
- SigLIP in one slide.

### Act 5 · Open vocabulary: detect and segment anything you can name [T] (KAUST 23) · ~12 slides
- **Closed vs open vocabulary:** the central shift of the day.
- Open-vocabulary detection: type the class names at run time (Grounding DINO, YOLO-World / YOLOE). *Verify current Ultralytics support when building.*
- **SAM:** promptable segmentation with point, box or text prompts. The data engine behind it (1B masks). SAM 2 for video, SAM 3 for concept prompts.
- Combining them: detect with words → segment with SAM → measure.
- Depth Anything: depth from a single photo, in one slide.
- **When to use what:** a decision table (classical CV / trained CNN / fine-tuned YOLO / foundation model zero-shot) by data, speed, accuracy and cost.

### Act 6 · Vision-language models [T, READ if short] (KAUST 25) · ~12 slides
- What a VLM does: image + question → answer (captioning, VQA, OCR, grounding).
- **The blueprint:** vision encoder → connector → LLM. The image becomes "visual tokens".
- Counting visual tokens, worked. Why high resolution is expensive.
- Hallucination in VLMs: objects that aren't there, and "answering without looking" (language priors).
- Using one in practice: an API vs a small local model, and how to evaluate it.

### Act 7 · Machines that draw: generative vision [T, READ] (KAUST 10, 13, 14, 16) · ~12 slides
- Autoencoders: compress and rebuild. The latent space.
- GANs: forger vs detective, in one slide plus results.
- **Diffusion:** destroy an image with noise step by step, then learn to undo one step.
- Text conditioning: CLIP text embeddings steer the denoiser. Latent diffusion (Stable Diffusion) and why it's cheaper.
- Deepfakes, watermarking and responsible use.

### Act 8 · From notebook to product [T, READ] (KAUST 02, 03, 27) · ~10 slides
- Deployment constraints: latency, hardware, edge vs cloud, cost per image.
- Export (ONNX) and quantisation (FP32 → INT8) in plain words, plus what you lose.
- Data drift: the camera moves, the season changes, and accuracy quietly drops.
- Privacy and ethics: faces, re-identification, surveillance, Saudi PDPL awareness.
- A course recap map: every act on one slide, showing how each fix created the next problem.

### Day 3 labs
- **Lab 3A · CLIP: zero-shot and search** (B3/B4): load CLIP → embed images and texts → zero-shot classify → compare prompt templates → a CLIP image search engine over a provided image folder (text → images, image → images). Extra tasks: build a typographic attack, few-shot k-NN vs zero-shot.
- **Lab 3B · Open-vocabulary toolbox** (take-home + project fuel): open-vocabulary detection with text prompts → SAM masks from those boxes → area measurement. Optional: a small VLM captioning cell. Extra tasks: find three prompts that break it and explain why.

### Day 3 mini-activity
- **Zero-Shot Showdown:** pick the caption that a (pre-computed, offline) CLIP model ranks highest for each image. It shows how wording changes predictions. A non-coder can win by thinking like the model.
- **Fool the Model** gallery: spot the failure type (out-of-distribution, typographic, counting, bias).

### Day 3 ladder check
- Floor: "labels are expensive, and the classifier is forced to pick".
- Ceiling: the contrastive objective as a matrix, open-vocabulary pipelines, and VLM token maths.

---

## Project (published Day 1, presented Day 3)
**"A vision system for a real problem"**, in teams of 2–3 (about 7 teams), as a GitHub repo, built at night. It must include:
1. A clearly stated use case.
2. At least one **trained or fine-tuned** model from Days 1–2.
3. At least one **foundation-model component** from Day 3.
4. An evaluation with real numbers.
5. A failure analysis.

Grading split: 60 build / 10 presentation / 30 theory exam, with a +5 deploy bonus capped at 100. Same as Applied GenAI. The full brief and rubric go in the plan.

## Assessments
- Pre-test: 20 MCQ, Day 1 morning.
- Post-test: the same 20 concepts with different questions, Day 3 at 2:50.
- Theory exam: 30 MCQ, Day 3 at 9:15, covering Days 1–2 plus Day 3 Acts 1–5 from the decks.

## Things to verify when building (libraries move fast)
- Current Ultralytics model generation, task names, and open-vocabulary (YOLO-World / YOLOE) API.
- Which small Ultralytics datasets exist and auto-download, for Lab 2B.
- CLIP loading path (`open_clip` vs `transformers`) and the T4 memory needed.
- SAM version available through Ultralytics vs HuggingFace.
- Free Colab T4 quotas with 20 students in one room. Keep training to 5 minutes or less and add a CPU fallback.

## Rough size

| Day | Acts | Est. slides | Labs | Activities |
|---|---|---|---|---|
| 1 | 7 + stretch | ~90 | 2 | 3 + icebreaker |
| 2 | 8 + stretch | ~95 | 2 | 3 |
| 3 | 8 (3 readable) | ~95 | 2 | 2 |
