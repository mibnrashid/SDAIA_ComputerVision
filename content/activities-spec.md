# Activities spec

Nine browser activities plus the Day 1 icebreaker. Built by `tools/build_activities.py` into `activities/`.

## Rules every activity follows

- **Offline:** plain HTML/CSS/JS, all data inline (JSON inside the page or a local `.js` file). No `fetch`, no model in the browser, no network. Opens from disk (`file://`) and from GitHub Pages.
- **Scoring:** `Store.saveScore(id, score, max, team)` in `assets/store.js` keeps the **best** score per activity in `localStorage` (key prefix `cvd:`), so it survives a reload. The home page and the activities hub read the same registry (`assets/activities.js`).
- **Strip on every page:** round counter, live score, best score, **team name** field (saved once, shared by all activities), **Projector mode** toggle (bigger type, hero hidden, remembered) and **Reset best** (clears this activity's saved score). Code: `assets/act-common.js`.
- **Same rounds for everyone:** random rounds use a fixed seed, so every laptop in the room sees the same puzzle as the projector.
- **Feedback after every answer:** a verdict box explains the right answer with the slide reference.

| # | Activity | Day / slot | id | Rounds | Max |
|---|---|---|---|---|---|
| 01 | Pixel Detective | Day 1 · B2 (slide 1.33) | `pixel-detective` | 10 images | 50 |
| 02 | Be the Kernel | Day 1 · B3 (slide 1.51) | `be-the-kernel` | 10 | 40 |
| 03 | Shape Race | Day 1 · B4 (slide 1.86) | `shape-race` | 8 | 24 |
| 04 | Spot the Bug | Day 1 · [STRETCH] (slide 1.123) | `spot-the-bug` | 5 | 10 |
| 05 | IoU Darts | Day 2 · B1 (slide 2.25) | `iou-darts` | 4 | 40 |
| 06 | Be NMS | Day 2 · B2 (slide 2.52) | `be-nms` | 5 | 25 |
| 07 | Threshold Tycoon | Day 2 · B4 (slide 2.82) | `threshold-tycoon` | 3 businesses | 30 |
| 08 | Zero-Shot Showdown | Day 3 · B3 (slide 3.53) | `zero-shot-showdown` | 10 scenes | 10 |
| 09 | Fool the Model | Day 3 · B4 (slide 3.69) | `fool-the-model` | 12 cards | 12 |

## 01 · Pixel Detective (Day 1, 10 min)

- **Data:** 10 grayscale 24 × 24 pixel-art images drawn with simple shapes and averaged down (`tools/act/pixelart.py`): cup, car, cat face, palm tree, mosque dome, key, phone, house, fish, star. Stored as number arrays 0–255.
- **Play:** the grid shows the raw numbers first. Five steps: (1) numbers only, (2) cells shaded by 4 × 4 block averages, (3) 2 × 2 block averages, (4) every pixel at low contrast, (5) the full image. Teams pick one of four names at any step.
- **Score:** correct at step k = 6 − k points (5 … 1); wrong = 0. 10 × 5 = **50**.
- **Teaching point:** a computer receives only numbers — the semantic gap (slide 1.14).

## 02 · Be the Kernel (Day 1, 10 min)

- **Play:** a random 3 × 3 patch (values 0–9) and a kernel, cycling Sobel-x, box blur (÷ 9) and sharpen. The team types the single output pixel. Blur patches are adjusted so the answer is a whole number.
- **Score:** correct = 2, answered within 20 s = +1, three or more correct in a row = +1. 10 rounds = **40**. A running timer and streak counter are shown.
- **After each round:** the full multiply-and-add is printed (e.g. `0·−1 + 9·1 + … = 27`).

## 03 · Shape Race (Day 1, 8 min)

- **Play:** a random stack of 3–4 layers (conv with C_out, K, P, S, or 2 × 2 max-pool) on a 3 × W × W input (W ∈ 32, 64, 96, 128, 224). Predict the final channels and height = width.
- **Score:** both right = 3, or 2 if the team opened the formula ⌊(W − K + 2P)/S⌋ + 1. 8 rounds = **24**.
- **After each round:** each layer's calculation is shown line by line.

## 04 · Spot the Bug (Day 1, [STRETCH], 20 min)

Five snippets; click the buggy line; the fix and explanation appear.

| # | Bug | Buggy line | Fix |
|---|---|---|---|
| 1 | BGR shown as RGB | `plt.imshow(img)` after `cv2.imread` | `cv2.cvtColor(img, cv2.COLOR_BGR2RGB)` |
| 2 | uint8 overflow | `brighter = img + 100` | convert to int16, add, clip |
| 3 | swapped crop | `img[x1:x2, y1:y2]` | `img[y1:y2, x1:x2]` |
| 4 | missing `model.eval()` | the load line with no eval after it | `model.load_state_dict(...); model.eval()` |
| 5 | tuning on the test set | `acc = evaluate(model, test_set)` inside the search | tune on `val_set`, test once |

- **Score:** right first click = 2, second click = 1. 5 × 2 = **10**.

## 05 · IoU Darts (Day 2, 10 min)

- **Play:** a fixed ground-truth box on a 600 × 400 board. Drag (mouse or touch) to draw a box, redraw freely, then *Throw*. Targets: IoU 0.3, 0.5, 0.75, 0.9 (a different ground-truth shape each round).
- **Score:** `max(0, round(10 − |IoU − target| / 0.02))`. 4 × 10 = **40**. The intersection is shaded after the throw.

## 06 · Be NMS (Day 2, 8 min)

- **Data:** five fixed rounds generated with a seed (`nms_rounds()` in `tools/act/day2.py`): 2–3 objects, 6–10 jittered scored boxes. The correct sequence is computed with real NMS at IoU 0.5 at build time (kept boxes = one per object in every round).
- **Play:** click boxes to keep, in order (letters on the boxes, scores in the legend); *Undo* available; *Check*.
- **Score:** 5 − (number of positions that differ from the correct sequence), minimum 0. 5 × 5 = **25**. Suppressed boxes are shown dashed after checking.

## 07 · Threshold Tycoon (Day 2, 10 min)

- **Data:** for each business, 40 bundled detections (18 real objects with high-leaning scores, 22 false detections with low-leaning scores, fixed seed), each with its true label.
- **Businesses and hidden costs:** airport security (FP 1, FN 50), shop people-counting (FP 1, FN 1), clinic screening (FP 3, FN 15).
- **Play:** a slider for the confidence threshold; live TP, FP, FN, precision and recall; every detection is shown as a chip (in or out). *Lock in* reveals the hidden costs and the optimum threshold (computed exhaustively at build time).
- **Score:** `round(10 × best_cost / your_cost)`. 3 × 10 = **30**.

## 08 · Zero-Shot Showdown (Day 3, 12 min)

- **Scenes:** 10 simple SVG scenes drawn by hand (`tools/act/day3.py`), each with four captions designed to show CLIP's habits: caption-style wording, counting (three vs five apples, two vs four cups), left/right, a typographic attack (an apple labelled "iPod"), the word STOP, reading a clock.
- **Scores are never invented.** `tools/precompute_clip.py` (run once by Ice in Colab) renders the same SVGs to PNG with cairosvg, scores the captions with `openai/clip-vit-base-patch32` (softmax over the four, CLIP logit scale) and writes `activities/data/showdown.json` and `showdown.js`. Until then the committed placeholder `showdown.js` sets `window.SHOWDOWN = null` and the page shows **"Teacher setup needed"** with instructions, plus a preview of the scenes.
- **Score:** 1 point when the team picks CLIP's top caption. **10**. After each pick, all four probabilities are shown as bars.

## 09 · Fool the Model (Day 3, 10 min)

- **Data:** 12 cards, each a short real failure story with a small SVG icon. Types: out-of-distribution (cat/dog model on a car; factory camera moved; night rain), typographic attack (iPod apple; "dog" T-shirt), counting/spatial (three vs five apples; dog left of cat), bias/shortcut (husky on snow; scanner text marker; face recognition on darker skin), hallucination (green banana → "yellow"; invented cutlery).
- **Score:** 1 per correct label. **12**. The explanation appears after each answer.

## Icebreaker run-sheet: "This or That" (Day 1, B1, 20 min)

**Before class:** print `activities/print-signs.html` (two A4 landscape pages). Tape **THIS** on the left wall and **THAT** on the right wall. Clear a walking lane.

| Time | What happens |
|---|---|
| 0:00 | "Stand up. I read a pair. Walk to THIS for the first, THAT for the second. No middle. No wrong answers." |
| 0:01 | Round 1 · **Kabsa** (THIS) or **mandi** (THAT) |
| 0:03 | Round 2 · **Early bird** or **night owl** → pick one person from each side to defend their choice in 15 seconds |
| 0:06 | Round 3 · **Beach** or **desert camping** |
| 0:08 | Round 4 · **Call** or **voice note** → defend, 15 s each |
| 0:11 | Round 5 · **Tea** or **coffee** |
| 0:13 | Round 6 · **Window** or **aisle** → defend, 15 s each |
| 0:15 | Round 7 · **Messi** or **Ronaldo** (this one films loud — let it be loud) |
| 0:16 | **Finale, "Find your twin":** everyone finds the person who matched them on the most rounds (they compare answers). |
| 0:17 | Each pair introduces **the other person**: name, university, major. Keep it to ~15 s per person. |
| 0:20 | "Your twin is a good first teammate for the project." Sit down; open the pre-test. |

**Tips:** read each pair once, loudly; count down "3, 2, 1, walk". If the room is small, use the two ends of the room instead of walls. Note who talks easily — useful for the presentation order on Day 3.
