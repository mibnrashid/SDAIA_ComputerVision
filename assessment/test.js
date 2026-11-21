/* ============================================================
   test.js — one engine for the pre-test, post-test and theory exam.

   The page sets window.TEST_MODE = 'pretest' | 'posttest' | 'exam'.
   Questions come from questions.js (no answers). Keys and explanations
   come from keys.js, base64-encoded, and are decoded only when the
   student submits.

   One question per screen, a progress bar, a name field. Every answer is
   saved to localStorage as it is chosen (cvd:<mode>-progress), so a
   refresh or a crashed laptop loses nothing. The result is saved as
   cvd:<mode> = {score, max, at, name} for the home page progress section.
   Pre- and post-test show explanations after submission; the exam never
   shows them.
   ============================================================ */

(function () {
  'use strict';

  var MODE = window.TEST_MODE;
  var LABEL = { pretest: 'Pre-test', posttest: 'Post-test', exam: 'Theory exam' }[MODE];
  var QS = TESTS[MODE];
  var N = QS.length;
  var LETTERS = 'ABCD';
  var PKEY = MODE + '-progress';
  var state = Store.get(PKEY, null) || { name: '', answers: [], idx: 0, submitted: false };
  var $ = function (id) { return document.getElementById(id); };

  function save() { Store.set(PKEY, state); }

  function keys() {
    var json = decodeURIComponent(escape(window.atob(TEST_KEYS_B64)));
    return JSON.parse(json)[MODE];
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]; });
  }
  function fmt(s) { return esc(s).replace(/`([^`]+)`/g, '<code>$1</code>'); }

  function answered() { var n = 0; for (var i = 0; i < N; i++) if (state.answers[i] != null) n++; return n; }

  function show(id) {
    ['t-start', 't-question', 't-review', 't-result'].forEach(function (s) { $(s).hidden = s !== id; });
  }

  /* ---- Start screen ---------------------------------------- */
  function start() {
    $('t-name').value = state.name || '';
    if (state.submitted) return result();
    if (answered() > 0) $('t-resume').hidden = false;
    show('t-start');
  }

  $('t-start-form').addEventListener('submit', function (e) {
    e.preventDefault();
    var name = $('t-name').value.trim();
    if (!name) { $('t-name').focus(); return; }
    state.name = name; save();
    question(state.idx || 0);
  });

  /* ---- Question screen ------------------------------------- */
  function question(i) {
    state.idx = Math.max(0, Math.min(N - 1, i)); save();
    var q = QS[state.idx];
    $('t-qnum').textContent = 'Question ' + (state.idx + 1) + ' of ' + N;
    $('t-topic').textContent = q.topic;
    $('t-q').innerHTML = fmt(q.q);
    var box = $('t-opts'); box.innerHTML = '';
    q.options.forEach(function (o, k) {
      var id = 'opt-' + k;
      var lab = document.createElement('label');
      lab.className = 'opt' + (state.answers[state.idx] === k ? ' is-picked' : '');
      lab.setAttribute('for', id);
      lab.innerHTML = '<input type="radio" name="opt" id="' + id + '" value="' + k + '"' + (state.answers[state.idx] === k ? ' checked' : '') + '>' +
                      '<span class="opt__letter">' + LETTERS[k] + '</span><span>' + fmt(o) + '</span>';
      lab.querySelector('input').addEventListener('change', function () {
        state.answers[state.idx] = k; save();
        Array.prototype.forEach.call(box.children, function (c, j) { c.classList.toggle('is-picked', j === k); });
        progress();
      });
      box.appendChild(lab);
    });
    $('t-prev').disabled = state.idx === 0;
    $('t-next').textContent = state.idx === N - 1 ? 'Review and submit →' : 'Next →';
    progress();
    show('t-question');
  }

  function progress() {
    var n = answered();
    $('t-bar').style.width = Math.round(100 * n / N) + '%';
    $('t-meter').setAttribute('aria-valuenow', String(n));
    $('t-count').textContent = n + ' of ' + N + ' answered';
    var dots = $('t-dots'); dots.innerHTML = '';
    for (var i = 0; i < N; i++) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'qdot' + (state.answers[i] != null ? ' is-done' : '') + (i === state.idx ? ' is-now' : '');
      b.textContent = i + 1;
      b.setAttribute('aria-label', 'Go to question ' + (i + 1));
      (function (j) { b.addEventListener('click', function () { question(j); }); })(i);
      dots.appendChild(b);
    }
  }

  $('t-prev').addEventListener('click', function () { question(state.idx - 1); });
  $('t-next').addEventListener('click', function () { if (state.idx === N - 1) review(); else question(state.idx + 1); });
  document.addEventListener('keydown', function (e) {
    if ($('t-question').hidden || e.target.tagName === 'INPUT' && e.target.type === 'text') return;
    var k = e.key.toUpperCase();
    if (LETTERS.indexOf(k) >= 0 && k.length === 1) { var r = $('opt-' + LETTERS.indexOf(k)); if (r) { r.checked = true; r.dispatchEvent(new Event('change')); } }
    if (e.key === 'ArrowRight') $('t-next').click();
    if (e.key === 'ArrowLeft' && state.idx > 0) $('t-prev').click();
  });

  /* ---- Review + submit ------------------------------------- */
  function review() {
    var blank = N - answered();
    $('t-review-text').textContent = blank === 0 ? 'All ' + N + ' questions answered.' :
      blank + ' question' + (blank === 1 ? '' : 's') + ' still blank (blank counts as wrong). Click a number above to go back.';
    show('t-review');
  }
  $('t-back').addEventListener('click', function () { question(state.idx); });
  $('t-submit').addEventListener('click', function () {
    state.submitted = true; save();
    result();
  });

  /* ---- Result ---------------------------------------------- */
  function answerString() {
    var s = '';
    for (var i = 0; i < N; i++) s += state.answers[i] != null ? LETTERS[state.answers[i]] : '-';
    return s;
  }

  function result() {
    var K = keys(), score = 0;
    for (var i = 0; i < N; i++) if (state.answers[i] != null && LETTERS[state.answers[i]] === K.key[i]) score++;
    Store.set(MODE, { score: score, max: N, at: new Date().toISOString(), name: state.name });
    $('t-score').textContent = score + ' / ' + N;
    $('t-who').textContent = state.name + ' · ' + LABEL;
    var extra = '';
    if (MODE === 'posttest') {
      var pre = Store.get('pretest', null);
      extra = pre && typeof pre.score === 'number'
        ? 'Pre-test ' + pre.score + ' → post-test ' + score + ' (' + (score - pre.score >= 0 ? '+' : '') + (score - pre.score) + ').'
        : 'No pre-test score on this device to compare with.';
    }
    $('t-delta').textContent = extra;
    $('t-delta').hidden = !extra;

    var rev = $('t-answers');
    rev.innerHTML = '';
    if (MODE !== 'exam') {
      QS.forEach(function (q, i) {
        var right = K.key[i], mine = state.answers[i] != null ? LETTERS[state.answers[i]] : '–';
        var li = document.createElement('li');
        li.className = 'rv ' + (mine === right ? 'rv--ok' : 'rv--bad');
        li.innerHTML = '<p class="rv__q"><strong>' + (i + 1) + '.</strong> ' + fmt(q.q) + '</p>' +
          '<p class="rv__a">Your answer: <strong>' + mine + '</strong> · Correct: <strong>' + right + '</strong> — ' + fmt(q.options[LETTERS.indexOf(right)]) + '</p>' +
          '<p class="rv__why">' + fmt(K.why[i]) + '</p>';
        rev.appendChild(li);
      });
      $('t-answers-wrap').hidden = false;
    } else {
      $('t-answers-wrap').hidden = true;
    }
    $('t-restart').hidden = MODE === 'exam';      // the exam is taken once
    show('t-result');
  }

  function resultText() {
    var r = Store.get(MODE, {});
    return [state.name, LABEL, r.score + '/' + N, answerString()].join(' | ');
  }

  $('t-copy').addEventListener('click', function () {
    var text = resultText(), st = $('t-copy-status');
    function done() { st.textContent = 'Copied: ' + text; }
    function fallback() {
      var ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (e) { st.textContent = 'Copy this: ' + text; }
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, fallback);
    else fallback();
  });

  $('t-restart').addEventListener('click', function () {
    if (!window.confirm('Start this test again? Your saved answers on this device will be cleared.')) return;
    state = { name: state.name, answers: [], idx: 0, submitted: false }; save();
    Store.remove(MODE);
    start();
  });

  start();
})();
