# prompts.md — build SDAIA_ComputerVision overnight

Run these prompts in order in Claude Code, from inside the `SDAIA_ComputerVision` repo. Every prompt stands on its own.

Global rules for every prompt (repeat them to yourself every time):
- Do not use subagents or the Task/Agent tool. Do the work yourself, sequentially.
- Source of truth, in this order: `content/01-plan.md` → `content/slides-day1.md`, `slides-day2.md`, `slides-day3.md` (already written, never shorten them) → `content/00-topic-proposal.md`.
- Everything in English. No Arabic anywhere.
- Plain HTML/CSS/vanilla JS. No build step. No CDN, Google Fonts, or network assets. Relative paths only (the site serves from `/SDAIA_ComputerVision/`).
- Never compress content. One `###` slide in markdown = one slide in HTML.
- Students see 9:00 as the start time. Never write 9:15 on any student-facing page.
- Check current library docs (web) before writing any code into notebooks.
- After each prompt: run the acceptance checks, then `git add -A && git commit -m "<prompt number>: <title>"`.

---

## Prompt 1 — Scaffold the site from the GenAI course

Read the full site at `C:\Users\mibnr\OneDrive - KFUPM\Documents\00 SDAIA\SDAIA_AppliedGenerativeAI`: its folder structure, CSS, JS, `assets/` (SDAIA and SDAIA Academy logos, colour and white variants), deck engine (slides with presenter notes and a print-to-PDF button), activity pages with localStorage scoring, assessment pages, project page and resources page. Copy its design system and shared code into this repo, then build an empty skeleton for **Computer Vision for Developers**: SDAIA Academy, 22–24 November 2026, instructor Musa Ibn Rashid.

Pages:
- `index.html`
  - Hero
  - Pre-test card
  - 3 day cards:
    - Day 1 "From pixels to features"
    - Day 2 "Where is it, what shape is it, where is it going?"
    - Day 3 "Seeing beyond labels"
  - Each day card has Slides / Labs / Activities links
  - Project card, resources card, progress section
- `slides/day1.html`, `slides/day2.html`, `slides/day3.html` (empty decks on the same engine)
- `notebooks/index.html`
- `activities/index.html`
- `assessment/pretest.html`, `assessment/posttest.html`, `assessment/exam.html`
- `project/index.html`
- `resources/index.html`

Also create `content/` (it already holds the md files) and leave it unlinked from the site.

**Acceptance**
- Opening `index.html` from disk works with zero console errors.
- Every internal link resolves (write and run a small Node or Python link checker).
- No leftover Applied GenAI text: grep for "Generative", "RAG", "Gemini", "token" and confirm none remain on student pages.
- No `http` URLs in any `src` or `href` except Colab and GitHub links.

---

## Prompt 2 — Check the Day 2 and Day 3 slide files (already written)

`content/slides-day2.md` (121 slides) and `content/slides-day3.md` (105 slides) are already written. **Do not rewrite or shorten them.**

Only check them:
- Same format as Day 1.
- Every slide has Type, Screen and Notes.
- Numbering is continuous.
- The "Total slides" line matches the real count of `###` slide headings.

If a count is wrong, fix only the Total line. If a heading is malformed, fix only that heading. Write any issues you find to `content/BLOCKERS.md`.

**Acceptance:** a script prints the slide counts 128 / 121 / 105 and they match each file's Total line.

## Prompt 3 — (merged into Prompt 2, skip)

## Prompt 4 — Build the three HTML decks

Using the existing deck engine copied from the GenAI site, render `content/slides-day1.md`, `content/slides-day2.md` and `content/slides-day3.md` into `slides/day1.html`, `slides/day2.html` and `slides/day3.html`.

Rules:
- One `###` = one slide.
- Map each `Type` to a layout:
  - `title` / `section`: big heading
  - `definition`: highlighted definition box
  - `compare`: two or three columns
  - `cards`: numbered card grid
  - `rule`: one large statement
  - `worked`: step lines with the numbers emphasised
  - `diagram`: an inline SVG drawn by you (boxes and arrows), no images from the web
  - `table`: an HTML table
  - `code`: a monospace block with syntax colouring done in CSS
  - `list`: a clean list
  - `activity`: a coloured card with a link to the activity page
  - `quiz`: numbered questions
- Notes go into the presenter-notes panel.
- Strip `[STRETCH]` and `(cut first)` from anything visible, but keep them in the notes.
- Footer: `SECTION · Day N · nn / total`.
- Print-to-PDF prints one slide per page without notes.

Build the three decks one at a time and verify each before starting the next.

**Acceptance**
- For each day, the number of `.slide` elements equals the "Total slides" line in the md file. Write a script that counts both and fails on a mismatch.
- No slide text overflows at 1280×720. Check by measuring `scrollHeight > clientHeight` in a headless browser if one is available, otherwise by a CSS max-height with auto-shrinking font.
- Keyboard arrows, presenter notes toggle and print all work.

---

## Prompt 5 — Write `content/notebooks-spec.md`, then build the notebooks

First, check the current docs for:
- torchvision detection models (`fasterrcnn_resnet50_fpn_v2`, `maskrcnn_resnet50_fpn_v2`, `keypointrcnn_resnet50_fpn`)
- `torchvision.ops.nms` / `box_iou`
- HF Transformers v5: RT-DETRv2 fine-tuning (`PekingU/rtdetr_v2_r18vd` or r50vd), the object-detection fine-tuning guide, and the `cppe-5` dataset id
- CLIP (`openai/clip-vit-base-patch32`)
- Grounding DINO (`IDEA-Research/grounding-dino-tiny`, `post_process_grounded_object_detection`)
- SAM (`facebook/sam-vit-base`)
- Depth Anything V2 Small via `pipeline("depth-estimation")`
- supervision: `Detections.from_transformers`, `ByteTrack`, `LineZone`, `VideoAssets`
- Ultralytics YOLO26 (`yolo26n.pt`), its `track` mode and YOLOE-26 text prompts

Note any API differences from what the plan says.

Then write `content/notebooks-spec.md`. For each lab (1A, 1B, 2A, 2B, 2C, 3A, 3B) give a cell-by-cell table with these columns:
- cell #
- markdown or code
- what it does
- PRE-WRITTEN or TODO (TODOs are one line)
- the exact expected output (shape, number range, image description)
- what will break and the fix

Every notebook includes:
- A "How to use this notebook" cell.
- A GPU check plus a CPU fallback cell.
- Sections numbered to match the deck acts.
- 3–5 TODOs, each followed by an assert cell that prints ✅ or a hint.
- An "Extra tasks" section with 3–4 tasks.
- Training capped at about 5 minutes on a T4.
- A "load pretrained instead" escape cell after any training step.

Data must download automatically inside Colab. Use:
- `skimage.data` for Lab 1A
- `torchvision` CIFAR-10 for Lab 1B
- the Ultralytics sample `bus.jpg` URL or `skimage` images for Lab 2A
- `cppe-5` (verify the id) for Lab 2B
- `supervision` `VideoAssets.VEHICLES` for tracking
- a small Hugging Face image dataset for 3A (for example a 300-image Imagenette slice; verify it)

Then generate the notebooks into `notebooks/`, each as `Lab_1A_unsolved.ipynb` and `Lab_1A_solved.ipynb` (and so on). Solved and unsolved versions are identical except the TODO lines and the extra-task answers.

Update `notebooks/index.html` with one card per lab: title, a one-line goal, which day/block, buttons "Open unsolved in Colab" and "Open solved in Colab". Use the URL pattern `https://colab.research.google.com/github/mibnrashid/SDAIA_ComputerVision/blob/main/notebooks/<file>`, plus a download link.

**Acceptance**
- 14 notebooks, all valid JSON (`python -c "import nbformat; nbformat.read(...)"` on each).
- Every unsolved notebook contains `# TODO` and the solved one has none.
- Cell order matches the spec.
- You cannot run on a GPU here, so mark in `content/notebooks-spec.md` the cells Ice must check by running on Colab, listed first under "Run before class".

---

## Prompt 6 — Write `content/activities-spec.md` and build the activities

Write the spec, then build each page in `activities/`. All data is bundled as inline JSON, there is no model in the browser, scores go to localStorage, and each page has a big-screen projector mode and a team name field.

1. **Pixel Detective (Day 1):** 10 images drawn by you as 24×24 grayscale pixel-art grids (cup, car, cat face, palm tree, mosque dome, key, phone, house, fish, star) stored as number arrays. The page shows the raw numbers first, then reveals the image gradually in 5 steps. Fewer steps used = more points.
2. **Be the Kernel (Day 1):** random 3×3 patch + kernel (Sobel-x, blur, sharpen). The team types the output. Timer and streaks; 10 rounds.
3. **Shape Race (Day 1):** a random stack of conv/pool layers (W, K, P, S given). Predict the final shape. Show the formula ⌊(W−K+2P)/S⌋+1 on demand for a point penalty.
4. **IoU Darts (Day 2):** drag a box over a fixed ground-truth box to hit a target IoU (0.3, 0.5, 0.75, 0.9). Score = closeness.
5. **Be NMS (Day 2):** 6–10 overlapping scored boxes over 2–3 objects. The player clicks boxes to keep in the right order at IoU 0.5. Show the correct NMS sequence after each round.
6. **Threshold Tycoon (Day 2):** for 3 businesses (airport security, shop people-counting, clinic screening), a slider for the confidence threshold over a bundled list of 40 predictions with labels. Live precision and recall. Score = hidden cost (FP cost and FN cost differ per business). Reveal the optimum.
7. **Zero-Shot Showdown (Day 3):** 10 simple SVG scenes you draw. For each, 4 captions. Players pick the caption a CLIP model would rank highest. Create `tools/precompute_clip.py`: Ice runs it once in Colab, it renders the same SVGs to PNG, runs `openai/clip-vit-base-patch32`, and writes `activities/data/showdown.json`. Until that file exists, the page shows "Teacher setup needed" with instructions; do not invent scores.
8. **Fool the Model (Day 3):** 12 cards (text plus a simple SVG), each describing a real model failure. Players label its type: out-of-distribution, typographic attack, counting/spatial, bias/shortcut, or hallucination. Explanations appear after answering.
9. **Spot the Bug (Day 1, STRETCH):** 5 short code snippets (BGR shown as RGB, uint8 overflow, `img[x1:x2, y1:y2]`, missing `model.eval()`, tuning on the test set). Click the buggy line, then see the fix.

Also include the **icebreaker run-sheet** in the spec ("This or That" rounds and the "Find your twin" finale from the plan), plus printable THIS / THAT A4 signs as `activities/print-signs.html`.

Update `activities/index.html` with cards grouped by day.

**Acceptance**
- Each activity works offline from disk.
- Scores persist across reload.
- A reset button exists.
- No console errors.

---

## Prompt 7 — Write `content/project-brief.md` and build `project/index.html`

Use the project section of `01-plan.md` word for word for the requirements, grading and rubric. Add these:
- Example project ideas, 8 total:
  - PPE compliance on a site camera
  - parking occupancy
  - crack detection on walls or roads
  - date-palm leaf disease
  - shelf product counting
  - X-ray image triage
  - waste sorting
  - CLIP-powered photo search for a club archive
- A repo template (folder layout plus README sections: Use case card, Data, Model, Foundation component, Evaluation, Failure analysis, Limitations, How to run).
- A 5-minute presentation structure.
- Deadlines: idea Day 1 night, README with use case Day 2 night, final Day 3 at "2:00".
- An AI-use policy: AI tools are allowed, but every number, curve and failure image must come from your own runs.

The page shows the brief, the rubric table, and a "Team & idea" form saved to localStorage, with an "export as text" button so teams can paste it.

**Acceptance**
- The rubric points add to 60.
- The grading table adds to 100 plus the +5 bonus.

---

## Prompt 8 — Write `content/assessments.md` and build the three assessments

Write the pre-test (20), post-test (20, same concepts as the pre-test with different questions) and theory exam (30, **Days 1–2 only**, since it runs before Day 3 teaching).

Rules:
- Every item has 4 options.
- Test understanding, not memorisation: scenarios, "what happens if", short code reading, and numeric items using the formulas from the slides.
- Keep all four options within about ±20% of each other in length.
- Use the wording from the slide md files.
- Every item gets a one-line explanation.

Answer keys must be fixed in advance:
- Pre-test: 5 A, 5 B, 5 C, 5 D, in an irregular order.
- Post-test: 5 each, in a different irregular order.
- Exam: 8 A, 8 B, 7 C, 7 D, irregular.
- Print a distribution table and a longest-option check (a script that counts how often the correct option is the longest; it must be at most 30% of items) at the bottom of `assessments.md`.

Coverage:
- Pre-test and post-test: about 7 items Day 1, 7 Day 2, 6 Day 3.
- Exam: about 15 Day 1, 15 Day 2.

Build `assessment/pretest.html`, `posttest.html` and `exam.html`:
- One question per screen, with a progress bar.
- Name field.
- Answers saved to localStorage.
- At the end: the score, plus a "copy results" button that copies the name, score and answer string for Ice.
- The exam hides explanations. The pre-test and post-test show them only after submission.
- The answer key is stored obfuscated (base64 is fine) in a separate JS file, not as plain text in the HTML.

**Acceptance**
- The item counts and key distribution exactly match the rules.
- The longest-option check passes.
- All three pages work offline.

---

## Prompt 9 — Resources page and final QA

Build `resources/index.html`:
- Library docs links (PyTorch, torchvision, Transformers, supervision, OpenCV, Ultralytics with the AGPL note).
- A "Go deeper" list pointing to the KAUST Academy CV lectures repo `https://github.com/KAUST-Academy/Artificial-Intelligence-Courses/tree/main/Lectures/Computer_Vision`, labelled advanced.
- A glossary of every bold or defined term in the three slide md files (auto-extracted from the `definition` slides).

Then do full QA:
- Link checker across all pages.
- No network assets (grep for `http` in `src=`, `@import` and `url(`).
- No "9:15" on any page.
- No Arabic characters (grep `[\u0600-\u06FF]`).
- Slide counts match the md files.
- Every notebook card has both Colab links.
- `index.html` progress section reads the localStorage keys of the activities and assessments.

Fix everything that fails.

Write `content/RUN-BEFORE-CLASS.md`: a short checklist for Ice covering which notebooks to run on Colab first, running `tools/precompute_clip.py`, printing signs, enabling GitHub Pages (Settings → Pages → main / root), and testing the live URL.

**Acceptance:** all checks pass, and the final commit is pushed with `git push`.
