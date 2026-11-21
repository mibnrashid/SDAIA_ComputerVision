# Project brief — A vision system for a real problem

Computer Vision for Developers · Musa Ibn Rashid · SDAIA Academy · 22–24 November 2026

Teams of 2–3 (about 7 teams). The deliverable is a GitHub repo, built at night and presented on Day 3 at 2:00.

## Must include

1. **Use case card:** who the user is, what goes in, what comes out, what a wrong answer costs, and how success is measured.
2. **A trained or fine-tuned model** using Day 1 or Day 2 techniques: a CNN / transfer-learning classifier, or a fine-tuned detector or segmenter.
3. **A foundation-model component** from Day 3: CLIP zero-shot or search, open-vocabulary detection, SAM, or a VLM.
4. **Evaluation with numbers:** a test set kept separate, the right metric for the task (accuracy/F1, mAP, IoU) and a confusion matrix or PR curve.
5. **Failure analysis:** at least 5 failure images, each with a written cause and one fix the team tried or would try.
6. **Honest limitations** and a README that lets someone else run it.

## Grading (course total 100)

Every team member gets the same build mark. The deploy bonus can raise a total to 100 but not above it.

| Part | Points |
|---|---|
| Project build | 60 |
| Presentation | 10 |
| Theory exam (Day 3 morning, Days 1–2) | 30 |
| **Total** | **100** |
| Optional deploy bonus (Hugging Face Spaces or Streamlit) | +5 (total capped at 100) |

## Build rubric (60)

| Criterion | Points | Full marks looks like |
|---|---|---|
| Use case card | 8 | Specific user, input, output, cost of error, and a measurable success metric |
| Trained or fine-tuned model | 14 | Training ran, curves shown, baseline compared, choices justified |
| Foundation-model component | 10 | Integrated, not a separate demo; a clear reason why it was needed |
| Evaluation | 14 | Separate test set, correct metric, real numbers, threshold chosen deliberately |
| Failure analysis + limitations | 10 | 5+ failures with causes and a fix attempted; limits stated plainly |
| Repo quality | 4 | README with run steps, requirements, no secrets committed |

**Presentation (10):** clarity 4 · live demo or recorded fallback 3 · answers to questions 3. Five minutes, strict.

Evaluation and failure analysis carry 24 of the 60 build points, because they show the model was really trained and tested.

## Deadlines

| When | What |
|---|---|
| **Day 1 night** (Sun 22 Nov) | Team formed and project idea submitted on the site (project page → "Team & idea", then paste the exported text in the class group) |
| **Day 2 night** (Mon 23 Nov) | GitHub repo exists with a README containing the use case card and the data source |
| **Day 3 at 2:00** (Tue 24 Nov) | Final repo pushed; 5-minute presentation |

## Example project ideas (pick one or bring your own)

| # | Idea | Trained model (Day 1–2) | Foundation component (Day 3) | Metric |
|---|---|---|---|---|
| 1 | **PPE compliance on a site camera** — flag workers without a helmet or vest | Fine-tuned detector (RT-DETRv2) on helmet/vest boxes | Grounding DINO to pre-label new site photos, or to catch items not in the label set | mAP@0.5, recall on "no helmet" |
| 2 | **Parking occupancy** — count free spaces in a car park | Classifier on space crops (free/occupied) or a car detector | CLIP zero-shot as a baseline; SAM to outline irregular spaces | Accuracy/F1 per space, count error |
| 3 | **Crack detection on walls or roads** | Segmenter (U-Net-style) or crack/no-crack classifier | SAM to refine crack masks; area measurement | Mask IoU / Dice, recall |
| 4 | **Date-palm leaf disease** | Transfer-learning classifier (ResNet-18) on leaf photos | CLIP search to find similar cases; Grounding DINO to crop leaves | Per-class F1, confusion matrix |
| 5 | **Shelf product counting** | Detector for products or gaps on shelves | Open-vocabulary detection for new products without retraining | mAP, count error per shelf |
| 6 | **X-ray image triage** (public dataset only) | Classifier normal / abnormal with a chosen operating threshold | DINOv2/CLIP embeddings for few-shot rare classes | Recall at a fixed precision, PR curve |
| 7 | **Waste sorting** — plastic, paper, metal, glass | Transfer-learning classifier or detector | CLIP zero-shot comparison; SAM to isolate items | Accuracy, confusion matrix |
| 8 | **CLIP-powered photo search for a club archive** | A fine-tuned classifier for the club's own categories (events, teams) | CLIP text → image and image → image search | Recall@5 on a labelled query set, classifier F1 |

Use public data or data you have the right to use. No faces of people who did not agree to it; blur faces if identity is not needed.

## Repo template

```
your-project/
├── README.md               # the sections below, in this order
├── requirements.txt        # pinned versions
├── data/
│   └── README.md           # where the data comes from, licence, how to download (do not commit large data)
├── notebooks/
│   ├── 01_data.ipynb       # explore, split (train / val / test), check labels
│   ├── 02_train.ipynb      # baseline + trained/fine-tuned model, curves
│   ├── 03_foundation.ipynb # the Day 3 component, integrated with the model
│   └── 04_evaluate.ipynb   # test-set numbers, confusion matrix or PR curve, threshold, failures
├── src/                    # optional: reusable code (dataset, model, inference)
├── results/
│   ├── curves.png
│   ├── confusion_matrix.png  (or pr_curve.png)
│   └── failures/           # 5+ failure images
└── app.py                  # optional deploy bonus (Streamlit or Gradio on HF Spaces)
```

**README sections:**

1. **Use case card** — user · input · output · cost of a wrong answer (false positive vs false negative) · success metric and target.
2. **Data** — source, licence, size, classes, how it was split (by video/location, not by frame), known problems.
3. **Model** — baseline, what you trained or fine-tuned, key settings, training curves.
4. **Foundation component** — which model (CLIP, Grounding DINO, SAM, a VLM), what it does in the system, and why it was needed.
5. **Evaluation** — test-set numbers with the right metric, confusion matrix or PR curve, the operating threshold and why.
6. **Failure analysis** — at least 5 failure images, each with a cause and a fix tried or proposed.
7. **Limitations** — where it will not work; what you would need to make it production-ready.
8. **How to run** — exact steps from a fresh Colab or machine, including how to get the data.

## 5-minute presentation structure

| Time | Slide(s) | Content |
|---|---|---|
| 0:00–0:45 | 1 | The problem and the use case card: who, input, output, cost of a mistake |
| 0:45–1:30 | 1 | Data: source, size, split, one example image |
| 1:30–2:30 | 1–2 | Model + foundation component: what you trained, what the foundation model adds, why |
| 2:30–3:30 | 1–2 | Numbers: test metric, curve or confusion matrix, chosen threshold |
| 3:30–4:15 | 1 | Failures: two of your five failure images, cause and fix |
| 4:15–5:00 | 1 | Live demo (or recorded fallback) and what's next |
| then | — | One question from the room (1 minute) |

Strict: at 5:00 the next team starts. Record a 60-second demo video in case the live demo fails.

## AI-use policy

AI tools (ChatGPT, Claude, Copilot and similar) **are allowed** — for code, debugging, writing and ideas. But **every number, curve and failure image must come from your own runs**, in your own notebooks, committed in the repo. If a number in your README cannot be reproduced from your notebooks, it scores zero. You must be able to explain any line of code in your repo when asked.
