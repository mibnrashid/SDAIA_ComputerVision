# Run before class: checklist

Everything below needs a GPU, a Colab session, a printer or a GitHub setting, so it could not be done on the build machine. Do it in this order. Sunday's items first.

## 1 · Turn on GitHub Pages (5 min) — before anything else

1. github.com/mibnrashid/SDAIA_ComputerVision → **Settings → Pages**.
2. *Source:* **Deploy from a branch** · *Branch:* **main** · folder **/ (root)** → **Save**.
3. Wait 1–2 minutes, then open **https://mibnrashid.github.io/SDAIA_ComputerVision/**.
4. Test the live site:
   - [ ] Home page loads with both logos; the three day cards open their slides.
   - [ ] A deck: arrow keys move, **P** opens notes, **Print to PDF** gives one slide per page with no notes.
   - [ ] Labs page: click one **Open unsolved in Colab** and one **Open solved in Colab** button — both must open the notebook in Colab (this only works once the repo is public and pushed).
   - [ ] Pre-test: enter a name, answer two questions, refresh — the answers must still be there.
   - [ ] One activity (e.g. Pixel Detective): play a round, refresh, check that **Best** is kept.
   - [ ] Try the site on a phone too.

## 2 · Run the notebooks on a Colab T4 (Saturday night / Sunday early)

Open each **solved** notebook from the labs page, *Runtime → Change runtime type → T4 GPU*, *Runtime → Run all*, and compare with the expected outputs in `content/notebooks-spec.md` (the cells to watch are listed there under **"Run before class"**).

| Priority | Notebook | Needed | What to check | Verified locally (CPU, FAST mode) |
|---|---|---|---|---|
| 1 | `Lab_1A_solved` | Sunday B3 | every ✅ prints | ✅ fully run, all checks pass |
| 2 | `Lab_1B_solved` | Sunday B5 | training times (MLP ~1 min, CNN ~2 min, aug ~3 min, ResNet ~3 min) and accuracies (~0.50 / ~0.72 / ~0.78 / ~0.87) | ⚠️ not run end to end (CIFAR download failed here); checks for TODO 1–3 pass |
| 3 | `Lab_2A_solved` | Monday B2/B4 | AP = 0.683, kept A C F, detector images | ✅ IoU / NMS / AP sections and all checks pass; detector cells depend on weight downloads |
| 4 | `Lab_2B_solved` | Monday B5 | **training finishes in ≤ 5–6 min**, val mAP printed, vehicle video plays | ⚠️ data, processor, mAP and tracker set-up verified; training and video not run here |
| 5 | `Lab_2C_solved` | optional | YOLO26 / YOLOE-26 download and run | ✅ fully run (only the ONNX-export extra was blocked by this PC's policy) |
| 6 | `Lab_3A_solved` | Tuesday B4 | zero-shot accuracy ≥ 0.9 | ✅ fully run |
| 7 | `Lab_3B_solved` | take-home | Grounding DINO + SAM + depth | ✅ fully run |

If **Lab 2B training takes longer than 6 minutes** on the T4, lower `EPOCHS` in the training cell (6 is fine) and rebuild with `python tools/build_notebooks.py`, or simply tell students to use the escape cell.

**Escape weights for Lab 1B (to do):** the escape cells download `notebooks/weights/*.pt` from this repo, and that folder does not exist yet. Run `python tools/train_1b_weights.py` once on Colab (≈ 10 min on a T4) and commit the three `.pt` files.

## 3 · Zero-Shot Showdown scores: done

`tools/precompute_clip.py` was run on 21 November with `openai/clip-vit-base-patch32` (scenes rendered with headless Chrome) and `activities/data/showdown.json` / `showdown.js` are committed. Open the activity once to confirm the game starts. To regenerate after editing a scene, run `python tools/precompute_clip.py` again (cairosvg on Linux/Colab, Chrome on Windows).

## 4 · Print (Sunday morning)

- [ ] `activities/print-signs.html` → **Print both signs** (A4 landscape, colour). Tape THIS on the left wall, THAT on the right.
- [ ] Optional: print the day's deck as PDF from the deck's **Print to PDF** button as a backup if the projector laptop fails.

## 5 · In the room, Sunday 9:00

- [ ] Projector laptop: open the home page and the Day 1 deck; press **F** for fullscreen; check the notes with **P** on your own screen.
- [ ] Put the site URL in the class group.
- [ ] Activities have a **Projector mode** button for the big screen and a **Team** field.
- [ ] Students see 9:00 everywhere; the real block plan is in `content/01-plan.md`.

## 6 · Collecting results

- Tests: students press **Copy results** (name | test | score | answer string) and paste it where you ask — a form or the class group.
- Project teams: students export the **Team & idea** form on the project page as text and paste it in the class group (Day 1 night).
