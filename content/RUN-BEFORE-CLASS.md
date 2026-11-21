# Run before class: checklist

Students do every lab in **Google Colab** in their browser; nothing is installed on their laptops. The only thing left is to run the two GPU-heavy labs once yourself on Colab, to confirm the timing on a real T4.

## Done

- [x] GitHub Pages is on; the repo is public, so every **Open in Colab** button works.
- [x] Zero-Shot Showdown has real CLIP scores (`activities/data/showdown.js`).
- [x] PDF copies of the three decks are in `slides_pdf/` and linked from the home page.
- [x] Lab 1A, 2A, 2C, 3A and 3B run end to end (tested on CPU).
- [x] Lab 1B escape weights in `notebooks/weights/` (`mlp_cifar10.pt`, `cnn_cifar10.pt`, `cnn_aug_cifar10.pt`).
- [x] Icebreaker is an introductions round: nothing to print (slide 1.03).

## 1 · Run two labs on your Colab (about 20 minutes, Saturday or Sunday morning)

Open each link, then *Runtime → Change runtime type → T4 GPU*, then *Runtime → Run all*.

| Notebook | Needed | Open | What to check |
|---|---|---|---|
| Lab 1B solved | Sunday B5 | [Open in Colab](https://colab.research.google.com/github/mibnrashid/SDAIA_ComputerVision/blob/main/notebooks/Lab_1B_solved.ipynb) | MLP ~1 min, CNN ~2 min, augmented CNN ~3 min, ResNet ~3 min; accuracies about 0.50 / 0.72 / 0.78 / 0.87 |
| Lab 2B solved | **Monday B5** | [Open in Colab](https://colab.research.google.com/github/mibnrashid/SDAIA_ComputerVision/blob/main/notebooks/Lab_2B_solved.ipynb) | **The training cell must finish in 5–6 minutes**, because you teach tracking while it runs. Then val mAP prints and the vehicle video plays. |

If Lab 2B training takes longer than 6 minutes, lower `EPOCHS` in the training cell (6 is fine) and rebuild with `python tools/build_notebooks.py`.

## 2 · In the room, Sunday 9:00

- [ ] Projector laptop: open the Day 1 deck, press **F** for fullscreen and **P** for your notes.
- [ ] Put the site link in the class group: https://mibnrashid.github.io/SDAIA_ComputerVision/
- [ ] Introductions round (slide 1.03): you go first, then about 30 seconds each.
- [ ] Students see 9:00 everywhere; the real block plan is in `content/01-plan.md`.

## 3 · Collecting results

- Tests: students press **Copy results** (name | test | score | answer string) and paste it where you ask, such as a form or the class group.
- Project teams: students export the **Team & idea** form on the project page and paste it in the class group (Day 1 night).
