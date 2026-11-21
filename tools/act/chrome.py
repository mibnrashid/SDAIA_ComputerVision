"""Shared page chrome for the activity pages."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _page import header, footer  # noqa: E402


def act_page(meta, how, body, script, style='', rounds_label='Round', extra_scripts=''):
    """meta: dict(id, num, day, minutes, max, title). how: one paragraph of rules."""
    day_badge = f'badge--day{meta["day"]}'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{meta["title"]} · Computer Vision for Developers</title>
  <link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../assets/theme.css">
  <link rel="stylesheet" href="../assets/site.css">
  <link rel="stylesheet" href="../assets/activity.css">
  <style>
{style}
  </style>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <main id="main">
    <section class="page-hero act-hero on-dark">
{header('../')}
      <div class="container act-hero-inner">
        <a class="back" href="./index.html">← All activities</a>
        <div class="act-meta">
          <span class="badge {day_badge}">Day {meta["day"]}</span>
          <span class="badge badge--time">{meta["minutes"]} minutes</span>
          <span class="badge badge--time">Max {meta["max"]} points</span>
        </div>
        <h1>Activity {meta["num"]} · {meta["title"]}</h1>
        <p>{how}</p>
      </div>
    </section>

    <div class="scorestrip">
      <div class="container">
        <div class="scorestrip__item"><span class="scorestrip__label">{rounds_label}</span><span class="scorestrip__value" id="act-round">—</span></div>
        <div class="scorestrip__item"><span class="scorestrip__label">Score</span><span class="scorestrip__value" id="act-score">0</span></div>
        <div class="scorestrip__item"><span class="scorestrip__label">Best</span><span class="scorestrip__value scorestrip__value--muted" id="act-best">—</span></div>
        <div class="act-tools">
          <label for="act-team">Team</label>
          <input type="text" id="act-team" placeholder="Team name" autocomplete="off" maxlength="40">
          <button type="button" class="btn btn--ghost btn--sm" id="act-projector" aria-pressed="false">Projector mode</button>
          <button type="button" class="btn btn--ghost btn--sm" id="act-reset">Reset best</button>
        </div>
      </div>
    </div>

    <section class="section--tight">
      <div class="container">
{body}
      </div>
    </section>
  </main>

{footer('../')}

  <script src="../assets/store.js"></script>
  <script src="../assets/activities.js"></script>
  <script src="../assets/act-common.js"></script>
{extra_scripts}
  <script>
{script}
  </script>
</body>
</html>
'''
