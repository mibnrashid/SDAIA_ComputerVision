"""build_test_pages.py — write assessment/pretest.html, posttest.html, exam.html.

    python tools/build_test_pages.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _page import page  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = {
    'pretest': ('Pre-test', '20 questions across all three days, about 15 minutes. Not graded — it shows what you already know, and on Day 3 we compare it with the post-test. Guessing is fine.',
                'Answers are checked only when you submit. Afterwards you see the score and an explanation for every question.'),
    'posttest': ('Post-test', '20 questions on the same ideas as the pre-test, with different questions. About 10 minutes. At the end you see how far you moved since Day 1.',
                 'Answers are checked only when you submit. Afterwards you see the score, your change since the pre-test and an explanation for every question.'),
    'exam': ('Theory exam', '30 questions on Days 1 and 2. Closed book, 40 minutes. Type your full name exactly as on the attendance sheet.',
             'You can move between questions freely until you submit. You submit once. Explanations are not shown for the exam.'),
}

BODY = '''    <section class="section--tight">
      <div class="container narrow">

        <div class="card tcard" id="t-start" hidden>
          <h2>Before you start</h2>
          <p class="muted">{rules}</p>
          <ul class="small muted">
            <li>One question per screen. Use <kbd>A</kbd>–<kbd>D</kbd> to answer and the arrow keys to move.</li>
            <li>Every answer is saved on this device as you go — a refresh loses nothing.</li>
          </ul>
          <form id="t-start-form" class="tstart">
            <label for="t-name">Your full name</label>
            <input type="text" id="t-name" maxlength="80" autocomplete="name" required>
            <button type="submit" class="btn">Start →</button>
          </form>
          <p class="small" id="t-resume" hidden>You have saved answers on this device — Start continues where you left off.</p>
        </div>

        <div id="t-question" hidden>
          <div class="tbar">
            <span class="small muted" id="t-count">0 answered</span>
            <div class="meter" id="t-meter" role="progressbar" aria-label="Questions answered" aria-valuemin="0" aria-valuemax="{n}" aria-valuenow="0"><span id="t-bar"></span></div>
          </div>
          <div class="qdots" id="t-dots" aria-label="Jump to a question"></div>
          <div class="card tcard">
            <p class="q__meta"><span id="t-qnum">Question 1</span> <span class="q__topic" id="t-topic"></span></p>
            <h2 class="q__text" id="t-q"></h2>
            <div class="opts" id="t-opts" role="radiogroup" aria-labelledby="t-q"></div>
            <div class="tnav">
              <button type="button" class="btn btn--ghost" id="t-prev">← Previous</button>
              <button type="button" class="btn" id="t-next">Next →</button>
            </div>
          </div>
        </div>

        <div class="card tcard" id="t-review" hidden>
          <h2>Ready to submit?</h2>
          <p id="t-review-text"></p>
          <div class="tnav">
            <button type="button" class="btn btn--ghost" id="t-back">← Back to the questions</button>
            <button type="button" class="btn" id="t-submit">Submit my answers</button>
          </div>
        </div>

        <div class="card tcard result" id="t-result" hidden>
          <p class="small muted" id="t-who"></p>
          <p class="result__score" id="t-score">0 / {n}</p>
          <p class="result__delta" id="t-delta" hidden></p>
          <p class="muted">Press <strong>Copy results</strong> and paste them where your instructor asks (name, score and your answer string).</p>
          <div class="result__actions">
            <button type="button" class="btn" id="t-copy">Copy results</button>
            <a class="btn btn--ghost" href="../index.html">Course home</a>
            <button type="button" class="btn btn--ghost" id="t-restart">Take it again</button>
          </div>
          <p class="small" id="t-copy-status" aria-live="polite"></p>
        </div>

        <div id="t-answers-wrap" hidden>
          <h2 class="review-title">Answers and explanations</h2>
          <ol class="rvlist" id="t-answers"></ol>
        </div>

      </div>
    </section>
'''


def main():
    for mode, (title, lede, rules) in PAGES.items():
        n = 30 if mode == 'exam' else 20
        scripts = (f'  <script src="../assets/store.js"></script>\n  <script src="./questions.js"></script>\n'
                   f'  <script src="./keys.js"></script>\n  <script>window.TEST_MODE = "{mode}";</script>\n'
                   f'  <script src="./test.js"></script>')
        html = page('../', title, title, lede, BODY.replace('{rules}', rules).replace('{n}', str(n)),
                    css_links=['./test.css'], scripts=scripts)
        with open(os.path.join(ROOT, 'assessment', f'{mode}.html'), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(html)
        print(f'wrote assessment/{mode}.html')


if __name__ == '__main__':
    main()
