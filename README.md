# Computer Vision for Developers

A three-day course designed and taught by **Musa Ibn Rashid**, delivered at SDAIA Academy, 22–24 November 2026.
The slides, labs, activities, assessments and project brief in this repository are his work.
Live site: https://mibnrashid.github.io/SDAIA_ComputerVision/

Plain HTML, CSS and vanilla JavaScript — no build step to serve it, no CDN, no web fonts, no network assets.
Every page works from disk and from GitHub Pages.

| Folder | What |
|---|---|
| `index.html` | Home: pre-test, the three days, project, resources, progress |
| `slides/` | Day 1–3 decks (arrow keys, **P** notes, **F** fullscreen, Print to PDF) |
| `notebooks/` | 7 Colab labs × solved/unsolved, and `weights/` for the Lab 1B escape cells |
| `activities/` | 9 browser activities + printable THIS/THAT signs |
| `assessment/` | Pre-test, post-test, theory exam |
| `project/` | Project brief, rubric and the Team & idea form |
| `resources/` | Docs links, datasets, "Go deeper", glossary |
| `content/` | Source markdown (plan, slides, specs) — not linked from the site |
| `tools/` | Generators and checks (Python) |

## Rebuilding after editing content

```
python tools/build_decks.py          # content/slides-dayN.md  → slides/dayN.html
python tools/build_notebooks.py      # tools/nb/*.py           → notebooks/*.ipynb + content/notebooks-spec.md
python tools/build_activities.py     # tools/act/*.py          → activities/*.html
python tools/build_project.py        # content/project-brief.md → project/index.html
python tools/build_assessments.py    # tools/assess/items.py   → assessment/questions.js, keys.js, content/assessments.md
python tools/build_test_pages.py     # assessment/*.html
python tools/build_resources.py      # resources/index.html (glossary from the definition slides)
```

## Checks

```
python tools/qa.py                   # links, network assets, leftovers, 9:15, Arabic, slide counts, lab cards, progress keys
python tools/check_slides.py         # slide md format and counts
python tools/check_decks.py          # .slide counts, overflow at 1280×720, keys, notes, PDF page count (needs Chrome)
python tools/check_notebooks.py      # 14 notebooks valid, TODOs only in unsolved, order = spec
python tools/browser_check.py        # every page opened headless: zero console output
```

Before class, see `content/RUN-BEFORE-CLASS.md`.

© 2026 Musa Ibn Rashid. All rights reserved. SDAIA and SDAIA Academy logos belong to their owners.
