# Project brief — Train a vision model on a Kaggle dataset

Computer Vision for Developers · Musa Ibn Rashid · SDAIA Academy · 22–24 November 2026

Teams of 2–3. Each team hands in **one Colab notebook** in a **GitHub repo with a README**, and presents it on Day 3 at 2:00.

The project uses what you did in the Day 1 and Day 2 labs. Lab 1B (training a CNN, reading the curves) and Lab 2B (fine-tuning) are the best starting points. Copy from them freely.

## What you do

1. **Pick a dataset on Kaggle.** An image dataset with labels: classes for a classifier, or boxes for a detector. Keep it small enough to train in Colab in under 30 minutes.
2. **Split it** into train, validation and test sets. The test set is not touched until the end.
3. **Measure the model before training.** Build the model and run it on the test set before any training step. Write down the loss, accuracy and any other metric. It should be close to guessing.
4. **Train it** with a technique from Day 1 or Day 2: a small CNN, a pretrained ResNet with a new head (transfer learning), or a fine-tuned detector.
5. **Plot the curves.** Training and validation loss per epoch, and accuracy (or mAP) per epoch.
6. **Measure the model after training** on the same test set, with the same metrics.
7. **Compare before and after** in one table, and say in two or three sentences what changed and why.

## Grading (course total 100)

Every team member gets the same project mark.

| Part | Points |
|---|---|
| Project notebook and repo | 60 |
| Presentation | 10 |
| Theory exam (Day 3 morning, Days 1–2) | 30 |
| **Total** | **100** |

## Project rubric (60)

| Criterion | Points | Full marks looks like |
|---|---|---|
| Dataset | 10 | Kaggle link, number of images and classes, one grid of sample images, a clean train / val / test split |
| Model and training | 15 | A Day 1 or Day 2 model that really trained; settings (epochs, learning rate, batch size) stated |
| Curves | 10 | Train and validation loss per epoch, and accuracy (or mAP) per epoch, with one sentence on what they show (still learning, overfitting, or flat) |
| Before vs after | 15 | Same test set, same metrics, one table: loss, accuracy, and precision / recall / F1 (or mAP for detection); a confusion matrix after training |
| Notebook and README | 10 | The notebook runs top to bottom in Colab; the README explains the project and how to run it |

**Presentation (10):** clarity 4 · showing the curves and the before/after table 3 · answers to questions 3. Five minutes, strict.

## Deadlines

| When | What |
|---|---|
| **Day 1 night** (Sun 22 Nov) | Team formed and Kaggle dataset chosen (form at the bottom of this page, then paste the exported text in the class group) |
| **Day 2 night** (Mon 23 Nov) | GitHub repo exists with a README naming the dataset, and a notebook that loads the data |
| **Day 3 at 2:00** (Tue 24 Nov) | Final notebook and README pushed; 5-minute presentation |

## Getting a Kaggle dataset into Colab

Most public Kaggle datasets download with `kagglehub`, which is already installed in Colab:

```
import kagglehub
path = kagglehub.dataset_download("owner/dataset-name")   # the part of the Kaggle URL after /datasets/
print(path)
```

If it asks you to log in, make a Kaggle account, go to Settings → API → Create New Token, and add the username and key in Colab's Secrets panel (the key icon) as `KAGGLE_USERNAME` and `KAGGLE_KEY`. Never paste the key into the notebook itself.

For a folder of class subfolders, `torchvision.datasets.ImageFolder(path)` gives you a dataset in one line.

## Example datasets (pick one or bring your own)

Search Kaggle for these. Any labelled image dataset of a similar size is fine.

| Idea | Task | Suggested model |
|---|---|---|
| Waste or garbage classification (plastic, paper, metal, glass) | Classification | Pretrained ResNet-18, new head |
| Plant or leaf disease | Classification | Pretrained ResNet-18, new head |
| Flowers, fruits or vegetables | Classification | Small CNN from Lab 1B, then ResNet-18 |
| Chest X-ray, normal vs pneumonia | Classification | Pretrained ResNet-18; report recall too |
| Surface crack detection (crack / no crack) | Classification | Small CNN from Lab 1B |
| Weather or scene type | Classification | Pretrained ResNet-18, new head |
| Helmet or face-mask detection (boxes) | Detection | Fine-tuned detector as in Lab 2B or 2C |

Classification is the safer choice for three days. Pick detection only if you are comfortable with Lab 2B.

## What "before training" means

- **Small CNN from scratch:** the model with its random starting weights.
- **Pretrained ResNet with a new head:** the model with the new last layer not yet trained.
- **Detector:** the model right after you replace its head for your classes.

In every case, run the same evaluation function on the test set before the first training step and after the last one. For 5 classes, accuracy before training should be around 20% (one in five). If it is much higher, check that the test set is not leaking into training.

## Repo layout

```
your-project/
├── README.md        # the sections below
└── project.ipynb    # the one notebook, saved with its outputs
```

Do not commit the dataset. The notebook downloads it.

**README sections:**

1. **Project** — one paragraph: what the model recognises and who might use it.
2. **Dataset** — Kaggle link, number of images, classes, how you split it.
3. **Model** — what you trained and the main settings.
4. **Results** — the curves image and the before/after table.
5. **How to run** — "Open `project.ipynb` in Colab, set the runtime to GPU, run all."

## 5-minute presentation

| Time | Content |
|---|---|
| 0:00–1:00 | The dataset: what it is, a few sample images, the split |
| 1:00–2:00 | The model and how you trained it |
| 2:00–3:30 | The curves and what they tell you |
| 3:30–4:30 | The before/after table, and one or two images the model got wrong |
| 4:30–5:00 | What you would try next |

Then one question from the room.

## AI-use policy

AI tools (ChatGPT, Claude, Copilot and similar) **are allowed** for code, debugging and writing. But **every number and curve must come from your own run**, saved in the notebook in your repo. A number in the README that the notebook does not produce scores zero. You must be able to explain any line in your notebook when asked.
