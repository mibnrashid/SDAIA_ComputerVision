# Computer Vision for Developers: course plan

SDAIA Academy · Sun 22 – Tue 24 Nov 2026 · Instructor: Musa Ibn Rashid
About 20 students, year 2–5 undergrads. Everything in English. Repo: `SDAIA_ComputerVision`.

## How to read this

This is the master plan. Every other file follows it:
- `slides-day1/2/3.md` expand the acts slide by slide.
- `notebooks-spec.md` covers the labs.
- `activities-spec.md`, `assessments.md` and `project-brief.md` cover the rest.
- `prompts.md` builds the site from all of them.

The sections are: the course story, then the stack, then the three days (clock, ladder, act-to-block map), then labs and activities, the project, assessments, gotchas, and the file roadmap.

**Pace assumption:** about 1.5 minutes per concept slide and 3 minutes per worked-example slide. At that pace each day fills 9:15–3:00 almost exactly. If you run ahead, deploy [STRETCH]. If you run behind, cut the parts marked *(cut first)*.

---

## The story

**Teaching a machine to see.** Each act opens with a problem, shows the obvious attempt failing, then gives the fix. The fix creates the next problem.

| Day | Title | The question |
|---|---|---|
| 1 | From pixels to features | Why is seeing hard, and how did we stop hand-writing the rules? |
| 2 | Where is it, what shape is it, where is it going? | Knowing *what* isn't enough. Find it, outline it, count it, follow it. |
| 3 | Seeing beyond labels | What if the model could learn without labels and understand words? |

Each day's output feeds the next one:
- Day 1's CNN backbone becomes the feature extractor inside Day 2's detectors.
- Day 2's detector becomes the "closed vocabulary" baseline that Day 3's open-vocabulary models beat, and also fail against.

## Stack (decided)

| Layer | Library | Licence | Used for |
|---|---|---|---|
| Arrays and images | NumPy, OpenCV, Pillow, Matplotlib | permissive | Day 1 |
| Deep learning | PyTorch + torchvision | BSD | Day 1 CNNs, Day 2 Faster/Mask/Keypoint R-CNN, `torchvision.ops` (IoU, NMS) |
| Transformers | HuggingFace `transformers` | Apache 2.0 | RT-DETRv2 fine-tuning, CLIP/SigLIP, Grounding DINO, SAM, Depth Anything |
| Tracking and counting | `supervision` | MIT | ByteTrack, LineZone, drawing boxes |
| Beginner extra | Ultralytics (YOLO26) | **AGPL-3.0** | Lab 2C only, plus the licence slide |

Current facts to build against (checked 21 Nov 2026):
- Ultralytics' latest model is YOLO26, publicly released 14 Jan 2026. It does end-to-end detection with no NMS step, and Ultralytics added YOLOE-26 for open-vocabulary segmentation.
- RT-DETRv2 has been in HF Transformers since Feb 2025.
- Transformers is on v5.x, so every snippet gets re-checked against v5 docs before it goes in a notebook.
- supervision's ByteTrack works with any detector: pass a `Detections` object to `tracker.update_with_detections()` and it adds `tracker_id`. LineZone counting needs that `tracker_id`.
- Grounding DINO in Transformers takes classes as period-separated text ("a cat. a dog.") and uses `post_process_grounded_object_detection`. It can be combined with SAM for text-to-mask (the "Grounded SAM" pattern).

Compute: each student has their own free Colab T4. Every training cell is capped at about 5 minutes, and every notebook has a CPU fallback cell plus a "pretrained weights instead" escape cell.

---

## Daily clock

Students see 9:00 on the site. Never mention 9:15.

| Block | Real time | Minutes |
|---|---|---|
| B1 | 9:15–10:05 | 50 |
| B2 | 10:15–11:05 | 50 |
| B3 | 11:15–12:00 | 45 |
| Lunch | 12:00–1:00 | |
| B4 | 1:00–1:50 | 50 |
| B5 | 2:00–2:50 | 50 |
| Close | 2:50–3:00 | 10 |

Contracted hours are 9–3. [STRETCH] blocks are written in the deck as normal slides tagged `[STRETCH]` in presenter notes only. Students never see the tag.

---

## Day 1 · Sun 22 Nov · From pixels to features

**Deliverable tonight:**
- Lab 1A finished.
- Lab 1B finished, with one paragraph comparing MLP vs CNN vs pretrained ResNet-18 (accuracy plus one confusion-matrix observation).
- Teams formed and a project idea submitted on the site.

| Block | Content | Ladder |
|---|---|---|
| B1 | Welcome and about me (5) · **Icebreaker: This or That** (20) · **Pre-test** (15) · Course map + project brief walkthrough (10) | — |
| B2 | **Act 1** The seeing problem (12) · **Act 2** Images are just numbers (20) · **Activity: Pixel Detective** (10) · Act 3 opens (8) | Floor |
| B3 | **Act 3** Classical image processing (15) · **Activity: Be the Kernel** (10) · **Lab 1A launch**: run to the end of "convolution by hand" (20) | Floor → Climb |
| B4 | **Act 4** Learning from data, the MLP and why it fails (15) · **Act 5** The CNN (27) · **Activity: Shape Race** (8) | Climb |
| B5 | **Act 6** Training it properly (18) · **Act 7** Architectures and transfer learning (22) · **Lab 1B launch**: run MLP vs CNN, the rest tonight (10) | Ceiling |
| Close | Exit ticket (5 questions on the site) · tomorrow preview | |
| [STRETCH] | **Spot the Bug:** five pipeline bugs, team race (20) | |

*(cut first)*: Act 7's Inception and EfficientNet slides, and Act 3's morphology.

**Ladder check:**
- Floor at 9:15: "an image is a grid of numbers".
- Ceiling from 1:20: parameter-count and output-shape formulas, receptive field, BatchNorm train/eval, degradation → residuals, and depthwise-separable cost maths.

None of this can be reached in the morning. ✓

## Day 2 · Mon 23 Nov · Where is it, what shape is it, where is it going?

**Deliverable tonight:**
- Lab 2A finished.
- Lab 2B finished with a val mAP number and a counted video.
- Lab 2C optional.
- The project repo has a README with the use case and data source.

| Block | Content | Ladder |
|---|---|---|
| B1 | Recap quiz (5) · **Act 1** The task ladder (12) · **Act 2** Describing a box, IoU (15) · **Activity: IoU Darts** (10) · Act 3 opens (8) | Floor |
| B2 | **Act 3** Two-stage story, R-CNN → Faster R-CNN (15) · **Act 4** Scale and duplicates, FPN and NMS (15) · **Activity: Be NMS** (8) · **Lab 2A launch**: IoU + NMS (12) | Climb |
| B3 | **Act 5** One look: YOLO, DETR, licences (21) · **Act 6** How good is the detector? part 1: TP/FP, PR curve (24) | Climb |
| B4 | **Act 6** part 2: AP, mAP worked, operating threshold (10) · **Activity: Threshold Tycoon** (10) · **Act 7** Segmentation (22) · Lab 2A mAP-by-hand section (8) | Climb → Ceiling |
| B5 | **Lab 2B: start the RT-DETRv2 fine-tune** (8) → teach **Act 8** Tracking *while it trains* (17) → read training results together: curves, mAP, failure images (15) → run tracking + line counting on the video (10) | Ceiling |
| Close | Exit ticket · tomorrow: exam at "9:00" | |
| [STRETCH] | **Your own data:** labelling, formats, leakage, anomaly detection (25) | |

*(cut first)*: Act 5's YOLO v2–v8 evolution slides and Act 7's transposed-convolution maths.

**Ladder check:**
- Floor: "a box is four numbers".
- Ceiling: mAP by hand, U-Net skip logic, reading a real training run, ID switches.

## Day 3 · Tue 24 Nov · Seeing beyond labels

**Deliverable:** project presentations today. Labs 3A and 3B are finished at home after the course (portfolio).

| Block | Content | Ladder |
|---|---|---|
| B1 | Logistics (5) · **Theory exam**: 30 MCQ, closed book, on the site (40) · buffer (5) | — |
| B2 | **Act 1** The label problem (12) · **Act 2** Attention and ViT (21) · **Act 3** Learning without labels, part 1 (17) | Floor → Climb |
| B3 | **Act 3** part 2: embeddings, DINOv2 (8) · **Act 4** CLIP (21) · **Activity: Zero-Shot Showdown** (12) | Climb → Ceiling |
| B4 | **Act 5** Open vocabulary: Grounding DINO, SAM, when-to-use-what (18) · **Lab 3A launch**: CLIP image search (20) · **Activity: Fool the Model** (10) | Ceiling |
| B5 | **Project presentations**: ~7 teams × 5 min + 1 min Q&A (45) · wrap (5) | Ceiling |
| Close | **Post-test** (10) | |
| [READ] | Act 6 VLMs · Act 7 Generative vision · Act 8 From notebook to product. They're in the deck, flagged "read at home" on the site. | |
| [STRETCH] | If the exam ends early, teach Act 6 VLMs live (15) | |

**Correction to the proposal:** the exam happens *before* any Day 3 teaching, so it **covers Days 1–2 only**. The post-test covers all three days.

---

## Labs

Every lab comes as `Lab_XX_unsolved.ipynb` and `Lab_XX_solved.ipynb`, with identical cells except the TODOs and extra tasks.

Structure of every notebook:
- A "how to use" cell and a GPU check + CPU fallback.
- Sections numbered to match the deck's act numbers.
- 3–5 one-line TODOs, each with an assert that prints ✅ or a hint.
- An "Extra tasks" section with 3–4 tasks at the end.
- Nobody writes a cell from empty.

| Lab | Title | Libraries | In class | Core idea |
|---|---|---|---|---|
| 1A | Images as arrays | NumPy, OpenCV, Pillow | Day 1 B3 | shape/dtype, BGR→RGB, crop by slicing, histogram, threshold, **convolution by hand vs `cv2.filter2D`**, Sobel |
| 1B | Your first CNN | PyTorch, torchvision | Day 1 B5 | CIFAR-10: MLP baseline → CNN → shape print per layer → augmentation + dropout → curves + confusion matrix → pretrained ResNet-18 |
| 2A | Detection by hand | NumPy, `torchvision.ops`, torchvision detection models | Day 2 B2/B4 | IoU → NMS by hand vs `torchvision.ops.nms` → mAP on a toy list → Faster R-CNN / Mask R-CNN / Keypoint R-CNN inference, reading outputs field by field |
| 2B | Fine-tune and track | `transformers` RT-DETRv2, `supervision` | Day 2 B5 | fine-tune on a small PPE-style dataset (verify: `cppe-5`) for a few epochs → mAP → failure gallery → ByteTrack + LineZone on a provided video |
| **2C** | **Ultralytics for beginners** | `ultralytics` (YOLO26) | self-paced / tonight | the same ideas in about 5 lines: predict, read results, track, train on a tiny dataset, YOLOE-26 text prompts. Ends with "what Ultralytics hid from you" (it points back to 2A/2B) and the AGPL note |
| 3A | CLIP: zero-shot and search | `transformers` CLIP/SigLIP | Day 3 B4 | embed images and text → zero-shot classify → prompt templates → text→image and image→image search over a provided folder |
| 3B | Open-vocabulary toolbox | `transformers` Grounding DINO, SAM, Depth Anything | take-home | text → boxes → masks → area; depth map; find three prompts that break it |

Cell-by-cell specs (pre-written vs TODO, expected output, what will break) go in `notebooks-spec.md`. Each spec is checked against current docs before it's written.

## Mini-activities (browser, offline, localStorage scores)

| Day | Activity | A non-coder wins by… |
|---|---|---|
| 1 | **Pixel Detective** | guessing the object from a zoomed number grid as it un-blurs |
| 1 | **Be the Kernel** | doing multiply-and-add on a 3×3 patch faster than the other teams |
| 1 | **Shape Race** | applying one formula: output size after each layer |
| 2 | **IoU Darts** | dragging a box to hit a target IoU |
| 2 | **Be NMS** | suppressing boxes in the right order |
| 2 | **Threshold Tycoon** | picking a confidence threshold per business (airport, shop, clinic) against hidden costs |
| 3 | **Zero-Shot Showdown** | picking the caption a pre-computed CLIP ranks highest |
| 3 | **Fool the Model** | labelling each failure type (out-of-distribution, typographic, counting, bias) |

All the data is bundled as JSON, with no model running in the browser and no network. Day 3's CLIP scores are pre-computed offline and shipped as JSON.

## Icebreaker (Day 1, 20 min): "This or That"

Nothing to do with CV. Both walls of the room are labelled with sheets reading **THIS** and **THAT**. You read a pair, and everyone walks to a side. Rounds:
1. Kabsa or mandi
2. Early bird or night owl
3. Beach or desert camping
4. Call or voice note
5. Tea or coffee
6. Window or aisle
7. Messi or Ronaldo (this one films loud)

After every second round, you pick one person from each side to defend their choice in 15 seconds.

**Finale, "Find your twin":** everyone finds the person who matched them on the most rounds, then introduces that person by name, uni and major. Students talk to each other and to you, it gets everyone moving and laughing, and needs no skill. It also seeds team formation for the project.

---

## Project (published on the site Day 1)

**Brief: "A vision system for a real problem."** Teams of 2–3 (about 7 teams). The deliverable is a GitHub repo, built at night and presented Day 3 at 2:00.

**Must include:**
1. **Use case card:** who the user is, what goes in, what comes out, what a wrong answer costs, and how success is measured.
2. **A trained or fine-tuned model** using Day 1 or Day 2 techniques: a CNN / transfer-learning classifier, or a fine-tuned detector or segmenter.
3. **A foundation-model component** from Day 3: CLIP zero-shot or search, open-vocabulary detection, SAM, or a VLM.
4. **Evaluation with numbers:** a test set kept separate, the right metric for the task (accuracy/F1, mAP, IoU) and a confusion matrix or PR curve.
5. **Failure analysis:** at least 5 failure images, each with a written cause and one fix the team tried or would try.
6. **Honest limitations** and a README that lets someone else run it.

**Grading (course total 100):** build 60 · presentation 10 · theory exam 30 · optional deploy +5 (Hugging Face Spaces or Streamlit), capped at 100. Every team member gets the same build mark.

**Build rubric (60):**

| Criterion | Points | Full marks looks like |
|---|---|---|
| Use case card | 8 | Specific user, input, output, cost of error, and a measurable success metric |
| Trained or fine-tuned model | 14 | Training ran, curves shown, baseline compared, choices justified |
| Foundation-model component | 10 | Integrated, not a separate demo; a clear reason why it was needed |
| Evaluation | 14 | Separate test set, correct metric, real numbers, threshold chosen deliberately |
| Failure analysis + limitations | 10 | 5+ failures with causes and a fix attempted; limits stated plainly |
| Repo quality | 4 | README with run steps, requirements, no secrets committed |

**Presentation (10):** clarity 4 · live demo or recorded fallback 3 · answers to questions 3. Five minutes, strict.

Evidence is weighted heavily on purpose. Numbers, curves and failure images are hard to fake with an AI-written repo.

---

## Assessments (full items and keys in `assessments.md`)

| Instrument | When | Items | Covers |
|---|---|---|---|
| Pre-test | Day 1 B1 | 20 MCQ | Concepts from all 3 days (baseline) |
| Theory exam | Day 3 B1 | 30 MCQ, closed book | Days 1–2 |
| Post-test | Day 3 close | 20 MCQ | Same concepts as the pre-test, different questions |

Rules for every item:
- 4 options each.
- Tests understanding, not memorisation.
- A mix of theory and code-reading.
- All options roughly the same length.
- The answer key is spread evenly across A–D.
- Wording comes from the slides.

---

## Gotchas to flag in slides and notebooks before students hit them

- **BGR vs RGB** (OpenCV) and **`img[y, x]` not `img[x, y]`**.
- **uint8 overflow** when adding brightness.
- **`(N,C,H,W)` vs `(N,H,W,C)`.** torchvision's `ToTensor` changes the layout *and* scales to 0–1.
- **`model.eval()` + `torch.no_grad()`** forgotten at inference: BatchNorm and dropout behave differently and results go odd.
- **Box format mismatch:** torchvision uses `xyxy` in pixels, YOLO uses normalised `cxcywh`, COCO uses `xywh`.
- **Confidence threshold vs NMS IoU threshold** get confused.
- **DETR-family post-processing needs `target_sizes`,** otherwise boxes come out normalised.
- **Grounding DINO text format:** lowercase, with periods between classes.
- **CLIP is not a detector:** it scores the whole image.
- **Colab:** each session resets files, so `drive.mount` or re-download. GPU may be unavailable, so use the CPU fallback.
- **Ultralytics licence:** AGPL-3.0 if you ship it.

## File roadmap (build order)

1. `00-topic-proposal.md` ✓
2. `01-plan.md` ✓ *(this file)*
3. `slides-day1.md` → Musa compares it with Hussein's deck → `slides-day2.md`, `slides-day3.md`
4. `notebooks-spec.md` (Labs 1A–3B, solved and unsolved)
5. `activities-spec.md` (8 activities + icebreaker run-sheet)
6. `project-brief.md` (student-facing)
7. `assessments.md` (pre, post, exam, keys, answer-letter distribution table)
8. `prompts.md` (Claude Code, one prompt at a time, building `SDAIA_ComputerVision` from the GenAI site at `C:\Users\mibnr\OneDrive - KFUPM\Documents\00 SDAIA\SDAIA_AppliedGenerativeAI`)

**Priority given the date:** Day 1 slides, Labs 1A/1B, the Day 1 activities, the pre-test and the project brief must be live by Sunday 9:00. Everything for Days 2–3 can be finished Sunday night.
