# BLOCKERS and open issues

Anything that could not be finished or verified overnight is listed here, newest prompt last.

## Prompt 2 — slide file check

`python tools/check_slides.py` → 128 / 121 / 105, matching each file's `Total slides` line.
Every slide has Type, Screen and Notes in that order, numbering is continuous, all Types are known
layouts, and no `[STRETCH]` / `(cut first)` appears on a Screen line. No heading or Total line needed fixing.
Nothing blocked.

## Prompt 5 — notebooks

- **No GPU on the build machine.** All 14 notebooks were generated and pass `tools/check_notebooks.py`
  (valid nbformat, `# TODO` only in unsolved, 3–5 TODOs, 3–4 extra tasks, cell order = spec).
  The solved notebooks were then *executed* locally on CPU in FAST mode with torch 2.15 / transformers 5.23 /
  supervision 0.32: **1A, 2C, 3A, 3B ran end to end** (2C's only error is the optional ONNX-export extra, blocked
  by a Windows application-control policy on this machine). Running them surfaced and fixed five real bugs
  (quote escaping in check cells, a negative-stride array in tracking, `accelerate` missing for `Trainer`,
  the COCO label `motorbike`, ffmpeg fallback).
- **Network on the build machine was flaky** (intermittent DNS failures for cs.toronto.edu, download.pytorch.org,
  media.roboflow.com, PyPI). Cells that depend on those downloads in 1B, 2A and 2B could not always be executed
  here. Their code paths were checked where the download succeeded (2A's IoU/NMS/AP sections, 2B's dataset,
  processor, post-processing, mAP and tracker set-up). **Ice must run 1B, 2A and 2B on a Colab T4 before class** —
  see "Run before class" in `content/notebooks-spec.md` and `content/RUN-BEFORE-CLASS.md`.
- **Lab 2B timing** (8 epochs of RT-DETRv2-R18 at 480 px ≈ 5 min on a T4) is an estimate; confirm on Colab.
- **Colab links** only work once the repo is public and pushed (they point at `main`).
