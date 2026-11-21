/* ============================================================
   activities.js — the activity registry.

   One list, read by the home page progress section and by the
   activities hub, so the ids and the maximum scores can never
   disagree. Every activity page calls Store.saveScore() with the id
   used here.
   ============================================================ */

var ACTIVITIES = [
  {
    id: 'pixel-detective', num: '01', day: 1, minutes: 10, max: 50,
    file: 'pixel-detective.html', title: 'Pixel Detective',
    desc: 'A grid of raw numbers slowly turns into a picture. Name the object in as few steps as you can.'
  },
  {
    id: 'be-the-kernel', num: '02', day: 1, minutes: 10, max: 40,
    file: 'be-the-kernel.html', title: 'Be the Kernel',
    desc: 'Multiply and add a 3 × 3 kernel over a patch by hand. Ten rounds, a timer and streak bonuses.'
  },
  {
    id: 'shape-race', num: '03', day: 1, minutes: 8, max: 24,
    file: 'shape-race.html', title: 'Shape Race',
    desc: 'A stack of conv and pool layers. Predict the final output size with one formula.'
  },
  {
    id: 'spot-the-bug', num: '04', day: 1, minutes: 20, max: 10, stretch: true,
    file: 'spot-the-bug.html', title: 'Spot the Bug',
    desc: 'Five short vision snippets, each with one real bug. Click the buggy line, then see the fix.'
  },
  {
    id: 'iou-darts', num: '05', day: 2, minutes: 10, max: 40,
    file: 'iou-darts.html', title: 'IoU Darts',
    desc: 'Drag a box over the ground truth to hit a target IoU of 0.3, 0.5, 0.75 and 0.9.'
  },
  {
    id: 'be-nms', num: '06', day: 2, minutes: 8, max: 25,
    file: 'be-nms.html', title: 'Be NMS',
    desc: 'Overlapping scored boxes. Keep the right ones, in the right order, at IoU 0.5.'
  },
  {
    id: 'threshold-tycoon', num: '07', day: 2, minutes: 10, max: 30,
    file: 'threshold-tycoon.html', title: 'Threshold Tycoon',
    desc: 'Pick a confidence threshold for an airport, a shop and a clinic. Hidden costs decide the winner.'
  },
  {
    id: 'zero-shot-showdown', num: '08', day: 3, minutes: 12, max: 10,
    file: 'zero-shot-showdown.html', title: 'Zero-Shot Showdown',
    desc: 'Ten scenes, four captions each. Pick the caption CLIP ranks highest — think like the model.'
  },
  {
    id: 'fool-the-model', num: '09', day: 3, minutes: 10, max: 12,
    file: 'fool-the-model.html', title: 'Fool the Model',
    desc: 'Twelve real failure cases. Label each one: out-of-distribution, typographic, counting, bias or hallucination.'
  }
];

/* Total points available across every activity. */
var ACTIVITIES_MAX = ACTIVITIES.reduce(function (sum, a) { return sum + a.max; }, 0);

/* The three assessments, read by the home page progress section.
   Each page writes Store.set(<key>, {score, max, at}). */
var ASSESSMENTS = [
  { key: 'pretest',  title: 'Pre-test',    file: 'assessment/pretest.html',  max: 20 },
  { key: 'exam',     title: 'Theory exam', file: 'assessment/exam.html',     max: 30 },
  { key: 'posttest', title: 'Post-test',   file: 'assessment/posttest.html', max: 20 }
];
