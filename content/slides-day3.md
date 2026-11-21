# Slides — Day 3 · Seeing beyond labels

Computer Vision for Developers · SDAIA Academy · Tue 24 Nov 2026

## How to read this file
Same format as `slides-day1.md`. One `###` = one slide. Acts 6–8 carry a small on-screen badge "Read at home". `[STRETCH]` and `(cut first)` appear only in Notes. Footer: `SECTION LABEL · Day 3 · NN / TOTAL`.

---

## Opening

### 3.01 · Computer Vision for Developers — Day 3
Type: title
Screen: Day 3 — Seeing beyond labels · Transformers · Self-supervised learning · CLIP · Open vocabulary · Your presentations
Notes: Today the models stop being limited to the classes we labelled.

### 3.02 · First: the theory exam
Type: list
Screen: 30 questions · 40 minutes · closed book · Covers Day 1 and Day 2 · Open the course site → Exam · Copy your result when you finish
Notes: Run the exam now. Remind them to type their full name. After it ends, start Act 1.

### 3.03 · From Day 2 to Day 3
Type: compare
Screen: Day 2 · detectors that find the classes they were trained on · "car, person, helmet" | Day 3 · models that learn without labels and understand words · "find the red forklift near the door"
Notes: Yesterday's detector is today's "closed vocabulary" baseline.

### 3.04 · Today's question
Type: rule
Screen: Every model so far only knows the classes someone labelled. What if a model could learn without labels — and understand any word we type?
Notes: This question drives the whole day.

### 3.05 · Today, in eight acts
Type: list
Screen: 1 · The label problem · 2 · Attention and the Vision Transformer · 3 · Learning without labels · 4 · Connecting images and words: CLIP · 5 · Open vocabulary · 6 · Vision-language models (read at home) · 7 · Machines that draw (read at home) · 8 · From notebook to product (read at home)
Notes: We teach Acts 1 to 5 live. Acts 6 to 8 are in the deck for you to read; they are not in the exam.

### 3.06 · Goals for today
Type: cards
Screen: 01 · Explain the closed-set assumption and why it fails · 02 · Explain attention and how ViT turns an image into tokens · 03 · Explain contrastive learning and embeddings · 04 · Explain how CLIP does zero-shot classification · 05 · Combine open-vocabulary detection with SAM · 06 · Choose the right tool for a vision problem
Notes: Goal 6 is the one you will use in every job.

---

## Act 1 · The label problem

### 3.07 · Act 1
Type: section
Screen: 01 · The label problem · Labels are the bottleneck of everything we built
Notes: Floor block. Everyone can follow this.

### 3.08 · Labels are expensive
Type: cards
Screen: ImageNet · 1.2 million images, years of human labelling · A segmentation mask · minutes per object · Medical labels · need doctors · Every new class · new labels from scratch
Notes: Day 1 and Day 2 models all depend on someone labelling thousands of examples.

### 3.09 · The closed-set assumption
Type: definition
Screen: Closed-set assumption — a classifier assumes every input belongs to one of its training classes. It has no way to say "none of these".
Notes: A 10-class model must answer one of 10, even for something it has never seen.

### 3.10 · Overconfidence on the unknown
Type: worked
Screen: A cat-vs-dog classifier is shown a car · softmax must sum to 1 → "dog 97%" · High confidence does not mean the model knows · It just means one class scored higher than the other
Notes: Softmax confidence is not a measure of "I have seen something like this before".

### 3.11 · Out-of-distribution inputs
Type: definition
Screen: Out-of-distribution (OOD) — an input unlike anything in the training data: a new object, a new camera, night instead of day. Models often fail on these silently and confidently.
Notes: In production, OOD inputs arrive every day. The camera moves, the season changes.

### 3.12 · Two escape routes
Type: compare
Screen: Route 1 · learn without labels · the data supervises itself (Act 3) | Route 2 · learn from text · captions on the internet supervise vision (Act 4)
Notes: Both routes lead to foundation models, the big pretrained models behind today's tools.

### 3.13 · But first, a new architecture
Type: rule
Screen: To learn from huge unlabelled data and from text, vision borrowed the architecture that transformed language: the transformer.
Notes: Act 2 explains attention without heavy maths.

---

## Act 2 · Attention and the Vision Transformer

### 3.14 · Act 2
Type: section
Screen: 02 · Attention and the Vision Transformer · What if every part of the image could look at every other part?
Notes: Climb starts here.

### 3.15 · Recap: CNNs see locally
Type: cards
Screen: A 3 × 3 kernel sees 9 pixels · The view grows slowly with depth · Two far-apart parts of an image only "meet" deep in the network · Global context arrives late
Notes: This was the first limit we listed at the end of Day 1.

### 3.16 · Attention in plain words
Type: definition
Screen: Attention — each part of the input looks at every other part, decides how relevant each one is, and builds its new meaning as a weighted mix of the relevant parts.
Notes: Every part asks: who in this image matters to me?

### 3.17 · Attention with a sentence first
Type: worked
Screen: "The animal didn't cross the street because it was too tired." · What does "it" refer to? · Attention puts high weight on "animal", low weight on "street" · The meaning of "it" is built mostly from "animal"
Notes: Change "tired" to "wide" and the weight moves to "street". Context decides.

### 3.18 · Attention in an image
Type: diagram
Screen: A patch showing part of a wheel attends strongly to the patches showing the rest of the car · weakly to the sky · Its meaning becomes "car wheel", not just "round dark thing"
Notes: One layer of attention gives every patch a global view.

### 3.19 · Query, key, value
Type: cards
Screen: Query · "what am I looking for?" · Key · "what do I contain?" (a label on each part) · Value · "what information do I pass on?" · Relevance = how well a query matches each key
Notes: Like searching a library: your question is the query, book titles are keys, book contents are values.

### 3.20 · Attention — tiny worked example
Type: worked
Screen: Query q = (1, 0) · Keys: k₁ = (1, 0), k₂ = (0, 1) · Scores: q·k₁ = 1, q·k₂ = 0 · softmax → weights ≈ 0.73 and 0.27 · Output = 0.73 × v₁ + 0.27 × v₂
Notes: Dot product measures match, softmax turns the scores into weights, then we mix the values. That is all attention is.

### 3.21 · Attention has no sense of order
Type: rule
Screen: Attention treats its input as a set. Shuffle the patches and attention gives the same result. So we add position information to every patch.
Notes: This is called positional encoding. Without it, the model would not know top from bottom.

### 3.22 · The Vision Transformer (ViT)
Type: diagram
Screen: Image → cut into 16 × 16 patches → flatten each patch → linear layer → patch embeddings + position embeddings + a [CLS] token → transformer layers → [CLS] output → class
Notes: An image is treated like a sentence, where each patch is a word.

### 3.23 · ViT — counting tokens
Type: worked
Screen: Image 224 × 224 · patch 16 × 16 · 224 / 16 = 14 → 14 × 14 = 196 patches · + 1 [CLS] token = 197 tokens · each patch = 16 × 16 × 3 = 768 numbers
Notes: Attention compares every token with every other token: about 197 squared, roughly 39,000 pairs per layer. That cost grows fast with resolution.

### 3.24 · The [CLS] token
Type: definition
Screen: [CLS] token — an extra learned token added to the sequence. Through attention it gathers information from all patches, and its final value is used for classification.
Notes: It is like a reporter that listens to every patch and writes the summary.

### 3.25 · CNN vs ViT
Type: table
Screen: Built-in assumptions · CNN: locality and shift-tolerance built in · ViT: almost none — learns them | Data needed · CNN: works on moderate data · ViT: needs huge data or pretraining | Global context · CNN: late · ViT: from the first layer | Cost with resolution · CNN: grows linearly · ViT: grows with tokens squared
Notes: CNNs come with good instincts. ViTs must learn them, which needs a lot of data. That is why self-supervision matters for ViTs.

### 3.26 · When ViT wins
Type: rule
Screen: Small data → CNNs usually win. Huge data or a strong pretrained model → ViTs match or beat them and transfer extremely well.
Notes: In practice you rarely train a ViT from scratch. You use a pretrained one.

### 3.27 · DETR revisited
Type: cards
Screen: Yesterday · DETR uses "object queries" and needs no NMS · Today you can read it · object queries are queries in attention · each one attends to the image and claims one object
Notes: Yesterday's mystery box now makes sense.

### 3.28 · The family grows
Type: cards
Screen: Swin Transformer · attention inside local windows, shifted each layer · cheaper, hierarchical like a CNN · ConvNeXt · a CNN modernised with transformer design choices · "the CNN strikes back"
Notes: (cut first) The two families borrow from each other. Neither won outright.

---

## Act 3 · Learning without labels

### 3.29 · Act 3
Type: section
Screen: 03 · Learning without labels · Make the data supervise itself
Notes: Route 1 from Act 1.

### 3.30 · Self-supervised learning
Type: definition
Screen: Self-supervised learning — training on a task created automatically from the data itself, so no human labels are needed. The real goal is the features the model learns along the way.
Notes: We do not care about the made-up task. We care about what the network learns while solving it.

### 3.31 · Pretext tasks
Type: cards
Screen: Colourisation · predict colours from a gray image · Jigsaw · put shuffled patches back in order · Rotation · predict how much the image was rotated · Masking · hide patches, predict what was there
Notes: To colour a banana yellow, the model must first recognise a banana. That is the trick.

### 3.32 · Contrastive learning: the idea
Type: rule
Screen: Two different views of the same image should look similar to the model. Views of different images should look different.
Notes: This simple rule trains some of the strongest vision models in existence.

### 3.33 · SimCLR — how it works
Type: diagram
Screen: Take one image → make two random augmentations (crop, colour change, blur) → encode both → pull the two vectors together → push them away from every other image in the batch
Notes: Positive pair: two views of one image. Negatives: everything else. Day 1's augmentation becomes the teacher.

### 3.34 · Why augmentation is the teacher
Type: cards
Screen: Crop · teaches "part of a dog is still the dog" · Colour change · teaches "colour is not identity" · Blur · teaches "fine texture is not identity" · The model learns what stays the same under all of them: the object
Notes: Augmentation choice decides what the model learns to ignore.

### 3.35 · Embeddings
Type: definition
Screen: Embedding — a list of numbers (a vector) that represents an image's meaning. Similar images get vectors that are close together.
Notes: Think of every image as a point on a map, where similar images sit near each other.

### 3.36 · Cosine similarity — worked
Type: worked
Screen: a = (1, 2) · b = (2, 4) · c = (2, −1) · cos(a, b) = 10 / (√5 · √20) = 1.0 → same direction · cos(a, c) = 0 / (√5 · √5) = 0 → unrelated · Range −1 to 1
Notes: Cosine similarity cares about direction, not length. It is how we compare embeddings everywhere today.

### 3.37 · DINO and DINOv2
Type: cards
Screen: Self-supervised training on huge image collections · Features so good that one frozen backbone works for many tasks · Its attention separates objects from background without ever seeing a mask
Notes: Nobody told DINO what an object is. It discovered object boundaries on its own.

### 3.38 · One frozen backbone, many tasks
Type: diagram
Screen: DINOv2 backbone (frozen) → small head → classification · → small head → segmentation · → small head → depth · → nearest neighbours → image retrieval
Notes: Train the expensive part once, reuse it everywhere. That is the foundation-model idea.

### 3.39 · What you can build on embeddings
Type: cards
Screen: Image search · find similar photos · Duplicate detection · Clustering · group a photo dump · Few-shot classification · label 5 examples per class, use nearest neighbours
Notes: None of these need training a model. Lab 3A builds image search.

### 3.40 · Few-shot with nearest neighbours
Type: worked
Screen: 5 labelled photos per class → embed them · New photo → embed → find the 3 closest labelled embeddings · 2 say "crack", 1 says "stain" → predict "crack"
Notes: With good embeddings, five examples can be enough. Compare that with Day 1's 50,000 CIFAR images.

---

## Act 4 · Connecting images and words: CLIP

### 3.41 · Act 4
Type: section
Screen: 04 · Connecting images and words · What if the label is any sentence?
Notes: Route 2 from Act 1. This is the most important act of the day.

### 3.42 · The idea behind CLIP
Type: rule
Screen: The internet already contains hundreds of millions of images with captions written by people. Use the captions as labels.
Notes: No one labels anything new. The captions were already there.

### 3.43 · CLIP
Type: definition
Screen: CLIP (Contrastive Language–Image Pre-training) — two encoders, one for images and one for text, trained so that an image and its caption produce similar embeddings. Trained on about 400 million image–text pairs.
Notes: Same contrastive idea as SimCLR, but the positive pair is an image and its caption.

### 3.44 · Contrastive training as a matrix
Type: diagram
Screen: A batch of N images and N captions → N × N similarity grid · Diagonal = correct image–caption pairs → push up · Everything else = wrong pairs → push down
Notes: For a batch of 4 there are 16 scores: 4 right, 12 wrong. Real batches have tens of thousands of pairs.

### 3.45 · A shared embedding space
Type: diagram
Screen: Images and sentences live on the same map · photo of a dog ≈ "a photo of a dog" · photo of a palm tree ≈ "a palm tree in the desert" · Distance = how well they match
Notes: Once text and images share a space, you can compare any image with any sentence.

### 3.46 · Zero-shot classification
Type: definition
Screen: Zero-shot classification — classifying images into classes the model was never explicitly trained on, by describing the classes in words.
Notes: Zero shots means zero training examples for your classes.

### 3.47 · Zero-shot — step by step
Type: worked
Screen: Classes: cat, dog, car · Write sentences: "a photo of a cat", "a photo of a dog", "a photo of a car" · Embed the image and the 3 sentences · Cosine similarities: 0.31, 0.24, 0.12 · Highest → "cat"
Notes: No training. To add a class, add a sentence. That is the power.

### 3.48 · Prompt wording matters
Type: compare
Screen: "cat" · bare words often score worse | "a photo of a cat" · matches how captions are written · Prompt ensembling · average several templates ("a photo of a …", "a close-up of a …") · often a few points more accurate
Notes: CLIP learned from captions, so talk to it like a caption.

### 3.49 · CLIP as infrastructure
Type: cards
Screen: Image search by text · Zero-shot classifiers · The text encoder that steers image generators (Act 7) · The vision encoder inside many vision-language models (Act 6)
Notes: CLIP is a building block hidden inside much of today's AI.

### 3.50 · Where CLIP fails — 1
Type: cards
Screen: Counting · "three apples" vs "five apples" scores almost the same · Left / right · "a dog to the left of a cat" ≈ "a cat to the left of a dog" · Bag of words · it notices which words appear, not how they relate
Notes: CLIP matches overall meaning, not precise structure.

### 3.51 · Where CLIP fails — 2
Type: cards
Screen: Typographic attack · an apple with a paper label "iPod" → classified as an iPod · Web bias · learns the stereotypes in internet captions · Fine-grained classes · bird species, car models, medical findings
Notes: Text in the image can hijack the prediction. Fool the Model has examples.

### 3.52 · SigLIP
Type: cards
Screen: Same idea as CLIP · changes the training loss to score each image–caption pair on its own · trains efficiently at large scale · a common modern replacement for CLIP
Notes: (cut first) If you see SigLIP in a model card, think "an improved CLIP".

### 3.53 · Zero-Shot Showdown
Type: activity
Screen: Activity · Zero-Shot Showdown · Pick the caption CLIP ranks highest · Think like the model, not like a person · Site → Activities → Zero-Shot Showdown
Notes: Twelve minutes. The trick: CLIP prefers caption-style wording and is weak at counting and position.

---

## Act 5 · Open vocabulary: detect and segment anything you can name

### 3.54 · Act 5
Type: section
Screen: 05 · Open vocabulary · From "the classes we trained" to "anything you can describe"
Notes: Ceiling block. This connects Day 2 and Day 3.

### 3.55 · Closed vs open vocabulary
Type: compare
Screen: Closed vocabulary · a fixed list of classes chosen at training time · new class → new labels, retrain | Open vocabulary · classes given as text at run time · new class → type a new word
Notes: This is the central shift of the day.

### 3.56 · Open-vocabulary detection
Type: definition
Screen: Open-vocabulary detection — a detector that takes text prompts and returns boxes for whatever the text describes, including classes it never saw in box-labelled training data.
Notes: It is CLIP's idea applied to every region of the image instead of the whole image.

### 3.57 · Grounding DINO
Type: diagram
Screen: Image + text ("a forklift. a person without a helmet.") → image features and text features fused together → boxes, each linked to a phrase · Classes separated by full stops
Notes: The prompt format matters: lowercase, with a full stop between classes. Lab 3B uses this.

### 3.58 · YOLO-World and YOLOE
Type: cards
Screen: Open vocabulary at real-time speed · YOLOE-26 in the Ultralytics family · Same idea: type the classes, get boxes and masks · Remember the AGPL licence
Notes: Faster than Grounding DINO, usually less accurate on unusual phrases.

### 3.59 · Promptable segmentation: SAM
Type: definition
Screen: SAM (Segment Anything Model) — a model that returns a precise mask for whatever you point at: a click, a box, or (in newer versions) a text phrase.
Notes: SAM does not tell you what the object is. It gives you the exact pixels of the thing you pointed to.

### 3.60 · How SAM works
Type: diagram
Screen: Heavy image encoder (run once per image) → image embedding · Light prompt encoder (point, box) · Light mask decoder → several candidate masks with quality scores
Notes: The expensive part runs once, so each new click is fast enough for interactive use.

### 3.61 · The data engine behind SAM
Type: cards
Screen: SA-1B dataset · about 1.1 billion masks on about 11 million images · built by a loop: model suggests masks → people fix them → retrain → repeat · eventually fully automatic
Notes: The model helped label its own training data. That is how they reached a billion masks.

### 3.62 · SAM 2 and SAM 3
Type: cards
Screen: SAM · images, point and box prompts · SAM 2 · also video: masks follow the object across frames · SAM 3 · concept prompts: "every yellow school bus" → all instances
Notes: Each version widens what you can prompt with.

### 3.63 · Combining them: text → box → mask
Type: diagram
Screen: Text prompt → Grounding DINO → boxes → SAM (box prompts) → precise masks → measure area, count, crop
Notes: Detect with words, segment with SAM, then measure. This is often called Grounded SAM. Lab 3B builds it.

### 3.64 · Depth from one photo
Type: cards
Screen: Depth Anything · predicts a depth map from a single image · Relative depth: what is nearer, what is further · Useful for robotics, AR, blur effects, rough distance estimates
Notes: Another foundation model you can use with no training.

### 3.65 · When to use what
Type: table
Screen: Fixed simple rule, controlled lighting · classical CV (Day 1 Act 3) | Your own classes, a few hundred labels, need speed · fine-tuned CNN or detector (Day 1–2) | New classes often, no labels · open-vocabulary detection + SAM | Search or group photos · CLIP / DINOv2 embeddings | Questions about an image in words · a vision-language model
Notes: This table is the practical outcome of the whole course. Your project should justify its choice from it.

### 3.66 · The trade-off
Type: compare
Screen: Foundation model, zero-shot · no labels, fast to start · slower, larger, less accurate on your specific case | Fine-tuned model · needs labels and training · smaller, faster, more accurate on your case · Common pattern: use the foundation model to label data, then fine-tune a small fast model
Notes: The last line is how many companies work today: big model labels, small model ships.

### 3.67 · Lab 3A — CLIP zero-shot and search
Type: list
Screen: Embed images and text · zero-shot classify · compare prompt templates · build text → image search · build image → image search · Extra: build a typographic attack
Notes: Start it now. Finish at home; it makes a great portfolio piece.

### 3.68 · Lab 3B — open-vocabulary toolbox
Type: list
Screen: Grounding DINO with text prompts → boxes · SAM → masks from those boxes → area · Depth map with Depth Anything · Find three prompts that break it and explain why
Notes: Take-home lab. Many project teams will use this as their foundation-model component.

### 3.69 · Fool the Model
Type: activity
Screen: Activity · Fool the Model · Label each failure: out of distribution, typographic, counting or spatial, bias, hallucination · Site → Activities → Fool the Model
Notes: Ten minutes. Then break and set up for presentations.

---

## Act 6 · Vision-language models (Read at home)

### 3.70 · Act 6 — Read at home
Type: section
Screen: 06 · Vision-language models · Ask an image a question in plain words · Badge: Read at home
Notes: [STRETCH] If the exam ended early, teach this act live (15 minutes). Otherwise it is reading.

### 3.71 · What a VLM does
Type: definition
Screen: Vision-language model (VLM) — a model that takes an image and text as input and produces text: descriptions, answers, extracted fields, or coordinates.
Notes: The chat assistants that read your screenshots are VLMs.

### 3.72 · VLM tasks
Type: cards
Screen: Captioning · describe the image · Visual question answering · "Is the worker wearing gloves?" · OCR and documents · read text, tables, receipts · Grounding · return the box of "the red car"
Notes: One model, many tasks, all controlled by the text prompt.

### 3.73 · The blueprint
Type: diagram
Screen: Image → vision encoder (often CLIP or SigLIP) → connector (projects image features into the language model's space) → large language model → text answer
Notes: Nearly every open VLM follows this three-part design.

### 3.74 · Images become tokens
Type: rule
Screen: The connector turns the image into a sequence of "visual tokens" that the language model reads exactly like words.
Notes: To the language model, the image is just more tokens in the conversation.

### 3.75 · Counting visual tokens — worked
Type: worked
Screen: LLaVA-1.5 · vision encoder with 14 × 14 patches · image 336 × 336 · 336 / 14 = 24 → 24 × 24 = 576 visual tokens · Double the resolution → about 4× the tokens → slower and more expensive
Notes: High resolution helps with small text, but cost grows with the square of resolution.

### 3.76 · Tiling for high resolution
Type: cards
Screen: Split a large image into tiles · encode each tile plus a small overview · more detail for documents and small objects · many more tokens
Notes: This is how VLMs read dense documents.

### 3.77 · Training a VLM in stages
Type: cards
Screen: Stage 1 · align: train the connector on image–caption pairs · Stage 2 · instruct: train on image + question + answer conversations · Optional · preference tuning to reduce made-up answers
Notes: The vision encoder and the language model are usually pretrained separately and joined later.

### 3.78 · VLM hallucination
Type: cards
Screen: Object hallucination · mentions objects that are not in the image · Language priors · "answering without looking": "What colour is the banana?" → "yellow", even when it is green · Confident, fluent, wrong
Notes: Never trust a VLM answer for safety decisions without checking.

### 3.79 · Blind spots inherited from CLIP
Type: cards
Screen: Fine orientation and direction · counting · small details · Pairs of images that CLIP sees as nearly identical often confuse the VLM too
Notes: A VLM can only see what its vision encoder sees.

### 3.80 · Using a VLM in practice
Type: compare
Screen: API (cloud) · strongest models, pay per call, data leaves your machine | Small local model · private, free to run, weaker · Either way: build a small test set and measure before you trust it
Notes: Evaluation again. The same rule as every other model this week.

---

## Act 7 · Machines that draw (Read at home)

### 3.81 · Act 7 — Read at home
Type: section
Screen: 07 · Machines that draw · From recognising images to creating them · Badge: Read at home
Notes: Reading material, not in the exam.

### 3.82 · Autoencoders
Type: diagram
Screen: Image → encoder → small code (latent) → decoder → rebuilt image · Trained to make the rebuilt image match the original
Notes: To rebuild the image from a small code, the code must capture what matters.

### 3.83 · The latent space
Type: definition
Screen: Latent space — the compressed space of codes inside a generative model. Nearby codes produce similar images; moving through it changes the image smoothly.
Notes: Generation means picking a point in latent space and decoding it.

### 3.84 · GANs in one slide
Type: compare
Screen: Generator · the forger · makes fake images | Discriminator · the detective · tells real from fake · They train against each other until fakes look real · Powerful but unstable to train
Notes: GANs dominated image generation until about 2021.

### 3.85 · Diffusion: the idea
Type: diagram
Screen: Forward: add a little noise to an image, step by step, until it is pure noise · Reverse: train a network to remove a little noise at each step · Generate: start from pure noise and denoise step by step
Notes: Destroying an image is easy. Learning to undo one small step of destruction is learnable.

### 3.86 · Diffusion — the numbers
Type: worked
Screen: Training · about 1,000 noise steps · The network predicts the noise that was added at a given step · Generation · modern samplers need only about 20–50 steps
Notes: The denoising network is usually a U-Net, the same idea from Day 2.

### 3.87 · Text conditioning
Type: cards
Screen: A text encoder (often CLIP's) turns the prompt into embeddings · The denoiser looks at them at every step through cross-attention · The prompt steers which image emerges from the noise
Notes: CLIP from Act 4 is the steering wheel.

### 3.88 · Latent diffusion (Stable Diffusion)
Type: compare
Screen: Pixel diffusion · denoise full-size images · very expensive | Latent diffusion · compress to a small latent first, denoise there, decode at the end · much cheaper, runs on a single GPU
Notes: Denoising a small latent instead of a full image is why open image generators became practical.

### 3.89 · Controlling the output
Type: cards
Screen: Guidance scale · how strongly to follow the prompt · ControlNet · follow a pose, edge map or depth map · LoRA · small add-on weights to learn a style or a person cheaply
Notes: These are the knobs designers actually use.

### 3.90 · Responsible use
Type: cards
Screen: Deepfakes and impersonation · Consent and likeness · Watermarking and provenance labels · Copyright of training data
Notes: Being able to generate something does not mean you are allowed to publish it.

---

## Act 8 · From notebook to product (Read at home)

### 3.91 · Act 8 — Read at home
Type: section
Screen: 08 · From notebook to product · A Colab cell is not a system · Badge: Read at home
Notes: Reading material, very useful for the deploy bonus.

### 3.92 · Deployment constraints
Type: cards
Screen: Latency · how fast per frame? · Hardware · cloud GPU, laptop, phone, camera chip? · Cost per image · at real traffic, not one demo · Privacy · can images leave the site?
Notes: Write these four answers before choosing a model.

### 3.93 · Edge vs cloud
Type: compare
Screen: Edge (on the device) · fast, private, works offline · limited compute | Cloud · big models, easy updates · network delay, cost per call, data leaves the device
Notes: Many real systems detect on the edge and send only alerts to the cloud.

### 3.94 · Export: ONNX
Type: definition
Screen: ONNX — a standard file format for trained models, so a model trained in PyTorch can run in other runtimes (on servers, phones, browsers) without PyTorch.
Notes: Export once, run in many places.

### 3.95 · Quantisation
Type: worked
Screen: FP32 · 4 bytes per weight → INT8 · 1 byte per weight · Model 4× smaller and often 2–4× faster · Small accuracy drop · always re-measure after quantising
Notes: Never assume the accuracy survived. Measure again.

### 3.96 · Data drift
Type: cards
Screen: The camera is moved · lighting changes with seasons · new product packaging · accuracy drops quietly, with no error message · Monitor: sample predictions, re-label a few, track the metric
Notes: Models do not break loudly. They get worse silently.

### 3.97 · Privacy and ethics
Type: cards
Screen: Faces and re-identification can track people without consent · Collect only what you need · Blur faces when identity is not needed · Know the data-protection rules that apply to you (e.g. Saudi PDPL)
Notes: A vision system that works perfectly can still be one you should not build.

### 3.98 · Deploy bonus: the simplest route
Type: cards
Screen: Hugging Face Spaces or Streamlit · upload image → see prediction · Pin library versions · keep secrets out of the repo · +5 bonus points
Notes: A simple demo page counts. It does not need to be fancy.

---

## Close of the course

### 3.99 · The whole story on one slide
Type: table
Screen: Day 1 · pixels → hand-written kernels → learned kernels (CNN) → deeper with residuals → transfer learning | Day 2 · one label → boxes (two-stage → one-stage → NMS-free) → masks (U-Net) → tracks | Day 3 · labels are expensive → attention → self-supervision → CLIP → open vocabulary → VLMs
Notes: Every step fixed the problem left by the step before it.

### 3.100 · Ten distinctions to remember
Type: table
Screen: Closed vs open vocabulary | CNN vs ViT | Supervised vs self-supervised | Pretext task vs downstream task | Positive vs negative pair | Classification vs zero-shot classification | Detection vs promptable segmentation | Foundation model vs fine-tuned model | Edge vs cloud | Accuracy on paper vs accuracy after drift
Notes: These are for the post-test.

### 3.101 · Day 3 recap
Type: list
Screen: Classifiers are stuck with their classes and overconfident on the unknown · Attention lets every patch see every other patch · ViT turns an image into 197 tokens · Contrastive learning makes good embeddings without labels · CLIP puts images and text in one space → zero-shot · Grounding DINO + SAM: text → box → mask · Pick the tool from the problem, not the hype
Notes: Seven lines, the whole day.

### 3.102 · Project presentations
Type: list
Screen: 5 minutes per team · strict · Use case → model → foundation component → numbers → failures → what's next · 1 question per team
Notes: Keep strict time. About 45 minutes for seven teams.

### 3.103 · Post-test
Type: activity
Screen: 20 questions · 10 minutes · Site → Post-test · Compare with your pre-test score
Notes: Ask a few students to share how much they improved.

### 3.104 · Where to go next
Type: cards
Screen: Finish Labs 3A and 3B for your portfolio · KAUST Academy CV lectures (advanced) · Build one small project per month · Read model cards and licences before you build
Notes: Point them to the resources page.

### 3.105 · Thank you
Type: title
Screen: Thank you · Computer Vision for Developers · SDAIA Academy · Musa Ibn Rashid
Notes: Thank them, and take a group photo if the camera crew is there.

---
Total slides: 105
