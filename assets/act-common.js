/* ============================================================
   act-common.js — shared behaviour for every activity page.

   Act.init({ id, max }) wires up the scoring strip:
     · team name field (saved on this device, shared by all activities)
     · projector mode toggle (big type for the room screen; remembered)
     · reset button (clears this activity's saved best score)
     · best score display, read from Store on load (survives reload)
   Act.setScore(n) updates the live score; Act.finish(n) saves the best.
   Depends on store.js and activities.js.
   ============================================================ */

var Act = (function () {
  'use strict';

  var cfg = null;
  var el = {};

  function $(id) { return document.getElementById(id); }

  function init(opts) {
    cfg = opts;
    el.score = $('act-score');
    el.best = $('act-best');
    el.team = $('act-team');
    el.proj = $('act-projector');
    el.reset = $('act-reset');
    el.round = $('act-round');

    var team = Store.get('team', '');
    if (el.team) {
      el.team.value = team;
      el.team.addEventListener('input', function () { Store.set('team', el.team.value.trim()); });
    }

    var proj = !!Store.get('projector', false);
    setProjector(proj);
    if (el.proj) el.proj.addEventListener('click', function () { setProjector(!document.body.classList.contains('projector')); });

    if (el.reset) {
      el.reset.addEventListener('click', function () {
        if (window.confirm('Clear the saved best score for this activity on this device?')) {
          Store.clearScore(cfg.id);
          showBest();
          if (typeof cfg.onReset === 'function') cfg.onReset();
        }
      });
    }
    showBest();
    setScore(0);
  }

  function setProjector(on) {
    document.body.classList.toggle('projector', on);
    if (el.proj) {
      el.proj.setAttribute('aria-pressed', on ? 'true' : 'false');
      el.proj.textContent = on ? 'Exit projector mode' : 'Projector mode';
    }
    Store.set('projector', on);
  }

  function showBest() {
    if (!el.best) return;
    var b = Store.getScore(cfg.id);
    el.best.textContent = b ? b.score + ' / ' + b.max : '—';
  }

  function setScore(n) { if (el.score) el.score.textContent = String(n); }
  function setRound(text) { if (el.round) el.round.textContent = text; }

  function finish(score) {
    Store.saveScore(cfg.id, score, cfg.max, el.team ? el.team.value.trim() : '');
    showBest();
  }

  function team() { return el.team ? el.team.value.trim() : ''; }

  /* Deterministic random numbers, so a round looks the same on every
     laptop in the room when teams play along with the projector. */
  function rng(seed) {
    var s = seed >>> 0;
    return function () {
      s = (s + 0x6D2B79F5) >>> 0;
      var t = s;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c];
    });
  }

  return { init: init, setScore: setScore, setRound: setRound, finish: finish, team: team, rng: rng, esc: esc, showBest: showBest };
})();
