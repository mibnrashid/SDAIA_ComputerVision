"""build_project.py — render content/project-brief.md into project/index.html.

    python tools/build_project.py

The markdown is converted with a tiny converter (headings, paragraphs,
lists, tables, code blocks, bold) so the page never drifts from the brief.
The page adds the "Team & idea" form (saved to localStorage, exportable as
text). Also checks that the rubric adds to 60 and the grading to 100 + 5.
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _page import page  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![\w*])\*([^*]+)\*(?!\w)', r'<em>\1</em>', s)
    return s


def md_to_html(md):
    lines = md.split('\n')
    out, i = [], 0
    while i < len(lines):
        l = lines[i]
        if l.startswith('```'):
            j = i + 1
            while not lines[j].startswith('```'):
                j += 1
            out.append('<pre class="tree">' + html.escape('\n'.join(lines[i + 1:j])) + '</pre>')
            i = j + 1
        elif l.startswith('## '):
            t = l[3:]
            slug = re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')
            out.append(f'</div></section><section class="panel brief" id="{slug}"><div><h2>{inline(t)}</h2>')
            i += 1
        elif l.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip('|').split('|')])
                i += 1
            head, body = rows[0], [r for r in rows[2:]]
            t = '<div class="tablewrap"><table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr></thead><tbody>'
            t += ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in body)
            out.append(t + '</tbody></table></div>')
        elif re.match(r'^(\d+\.|-) ', l):
            ordered = l[0].isdigit()
            items = []
            while i < len(lines) and re.match(r'^(\d+\.|-) ', lines[i]):
                items.append(re.sub(r'^(\d+\.|-) ', '', lines[i]))
                i += 1
            tag = 'ol' if ordered else 'ul'
            out.append(f'<{tag}>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + f'</{tag}>')
        elif l.strip() == '' or l.startswith('# ') or l.startswith('Computer Vision for Developers ·'):
            i += 1
        else:
            out.append(f'<p>{inline(l)}</p>')
            i += 1
    h = '\n'.join(out)
    h = h.replace('</div></section>', '', 1)
    return h + '</div></section>'


def check_points(md):
    rub = re.search(r'## Build rubric \(60\).*?\n\n(\|.*?)\n\n', md, re.S).group(1)
    rubric = sum(int(r.split('|')[2]) for r in rub.split('\n')[2:])
    grade = re.search(r'## Grading.*?\n\n.*?\n\n(\|.*?)\n\n', md, re.S).group(1).split('\n')[2:]
    base = sum(int(re.sub(r'\D', '', r.split('|')[2])) for r in grade if '**Total**' not in r and '+' not in r.split('|')[2])
    bonus = [r for r in grade if '+' in r.split('|')[2]][0]
    total_row = [r for r in grade if '**Total**' in r][0]
    print(f'rubric = {rubric} (must be 60) · grading = {base} (must be 100), total row says {re.sub(r"[^0-9]", "", total_row)} · bonus {bonus.split("|")[2].strip()}')
    assert rubric == 60 and base == 100 and '+5' in bonus
    return rubric, base


FORM = '''    <section class="panel brief" id="team">
      <div>
        <h2>Team &amp; idea</h2>
        <p>Fill this in on Day 1 night. It saves on this device as you type. Then press <strong>Export as text</strong> and paste the text in the class group so Musa has your team.</p>
        <form id="team-form" class="tform">
          <label>Team name <input type="text" name="team" maxlength="60"></label>
          <label>Member 1 (full name) <input type="text" name="m1" maxlength="80"></label>
          <label>Member 2 <input type="text" name="m2" maxlength="80"></label>
          <label>Member 3 (optional) <input type="text" name="m3" maxlength="80"></label>
          <label>Project idea
            <select name="idea">
              <option value="">— choose —</option>
              <option>PPE compliance on a site camera</option><option>Parking occupancy</option>
              <option>Crack detection on walls or roads</option><option>Date-palm leaf disease</option>
              <option>Shelf product counting</option><option>X-ray image triage</option>
              <option>Waste sorting</option><option>CLIP-powered photo search for a club archive</option>
              <option>Our own idea (describe below)</option>
            </select></label>
          <label class="wide">One-sentence pitch <input type="text" name="pitch" maxlength="200" placeholder="We help … to … by …"></label>
          <label>User <input type="text" name="user" maxlength="120"></label>
          <label>Input <input type="text" name="input" maxlength="120" placeholder="e.g. site camera frame"></label>
          <label>Output <input type="text" name="output" maxlength="120" placeholder="e.g. boxes for people without helmets"></label>
          <label>Cost of a wrong answer <input type="text" name="cost" maxlength="160" placeholder="false positive vs false negative"></label>
          <label>Success metric <input type="text" name="metric" maxlength="120" placeholder="e.g. recall ≥ 0.9 at precision 0.7"></label>
          <label>Data source <input type="text" name="data" maxlength="160"></label>
          <label>Foundation component <input type="text" name="foundation" maxlength="120" placeholder="CLIP / Grounding DINO / SAM / VLM"></label>
          <label class="wide">GitHub repo URL <input type="text" name="repo" maxlength="200" placeholder="https://github.com/…"></label>
        </form>
        <div class="rowline" style="margin-top:var(--s3)">
          <button type="button" class="btn" id="export">Export as text</button>
          <button type="button" class="btn btn--ghost" id="copy">Copy</button>
          <button type="button" class="btn btn--ghost" id="clear">Clear form</button>
          <span class="small" id="status" aria-live="polite"></span>
        </div>
        <textarea id="out" class="hidden" rows="14" readonly></textarea>
      </div>
    </section>'''

STYLE = '''    .brief { margin-bottom: var(--s4); }
    .brief h2 { font-family: var(--font-display); font-size: var(--fs-h2); margin-bottom: var(--s3); }
    .panel { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: var(--s4); }
    .brief p, .brief li { max-width: 78ch; }
    .tablewrap { overflow-x: auto; margin: var(--s3) 0; }
    .brief table { width: 100%; border-collapse: collapse; min-width: 34rem; }
    .brief th, .brief td { text-align: left; padding: 0.6rem 0.75rem; border-bottom: 1px solid var(--border); vertical-align: top; font-size: var(--fs-small); }
    .brief thead th { background: var(--ink); color: var(--text-on-dark); font-size: 0.72rem; letter-spacing: .08em; text-transform: uppercase; }
    .brief tbody tr:nth-child(even) td { background: var(--card-2); }
    pre.tree { background: var(--ink); color: #e8ecf5; padding: var(--s3); border-radius: var(--radius-sm); overflow-x: auto; font-size: 0.85rem; }
    .toc { display: flex; flex-wrap: wrap; gap: var(--s2); margin-bottom: var(--s4); }
    .toc a { font-size: var(--fs-small); font-weight: 600; text-decoration: none; padding: 0.3rem 0.8rem; border: 1px solid var(--border); border-radius: 999px; background: var(--card); }
    .tform { display: grid; gap: var(--s3); grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
    .tform label { display: grid; gap: 4px; font-size: var(--fs-small); font-weight: 700; }
    .tform .wide { grid-column: 1 / -1; }
    .tform input, .tform select, #out { font: inherit; font-weight: 400; padding: 0.55rem 0.7rem; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--paper); }
    #out { width: 100%; margin-top: var(--s3); font-family: var(--font-mono); font-size: 0.85rem; }
    .hidden { display: none; }
    .rowline { display: flex; gap: var(--s3); align-items: center; flex-wrap: wrap; }'''

SCRIPT = '''  <script src="../assets/store.js"></script>
  <script>
    (function () {
      'use strict';
      var form = document.getElementById('team-form'), out = document.getElementById('out'), status = document.getElementById('status');
      var KEY = 'project-team', saved = Store.get(KEY, {});
      Array.prototype.forEach.call(form.elements, function (el) { if (el.name && saved[el.name]) el.value = saved[el.name]; });
      form.addEventListener('input', function () {
        var data = {};
        Array.prototype.forEach.call(form.elements, function (el) { if (el.name) data[el.name] = el.value.trim(); });
        Store.set(KEY, data);
        status.textContent = 'Saved on this device';
      });
      function text() {
        var d = Store.get(KEY, {}), L = [];
        L.push('PROJECT TEAM — Computer Vision for Developers');
        L.push('Team: ' + (d.team || ''));
        L.push('Members: ' + [d.m1, d.m2, d.m3].filter(Boolean).join(', '));
        L.push('Idea: ' + (d.idea || ''));
        L.push('Pitch: ' + (d.pitch || ''));
        L.push('Use case card — user: ' + (d.user || '') + ' | input: ' + (d.input || '') + ' | output: ' + (d.output || ''));
        L.push('Cost of a wrong answer: ' + (d.cost || ''));
        L.push('Success metric: ' + (d.metric || ''));
        L.push('Data source: ' + (d.data || ''));
        L.push('Foundation component: ' + (d.foundation || ''));
        L.push('Repo: ' + (d.repo || ''));
        return L.join('\\n');
      }
      document.getElementById('export').addEventListener('click', function () {
        out.value = text(); out.classList.remove('hidden'); out.focus(); out.select();
      });
      document.getElementById('copy').addEventListener('click', function () {
        out.value = text(); out.classList.remove('hidden'); out.select();
        function ok() { status.textContent = 'Copied — paste it in the class group'; }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(out.value).then(ok, function () { document.execCommand('copy'); ok(); });
        } else { document.execCommand('copy'); ok(); }
      });
      document.getElementById('clear').addEventListener('click', function () {
        if (window.confirm('Clear the team form on this device?')) { form.reset(); Store.remove(KEY); out.classList.add('hidden'); status.textContent = 'Cleared'; }
      });
    })();
  </script>'''


def main():
    md = open(os.path.join(ROOT, 'content', 'project-brief.md'), encoding='utf-8').read()
    check_points(md)
    body_html = md_to_html(md)
    sections = re.findall(r'<section class="panel brief" id="([^"]+)"><div><h2>(.*?)</h2>', body_html)
    toc = '<nav class="toc" aria-label="On this page">' + ''.join(f'<a href="#{s}">{t}</a>' for s, t in sections) + '<a href="#team">Team &amp; idea</a></nav>'
    body = f'''    <section class="section--tight">
      <div class="container">
        {toc}
{body_html}
{FORM}
      </div>
    </section>
'''
    out = page('../', 'Project', 'A vision system for a real problem',
               'Teams of 2–3. A GitHub repo built at night, presented on Day 3 at 2:00. This page has the requirements, grading, deadlines, project ideas, a repo template, the presentation plan, the AI-use policy, and the form to register your team.',
               body, style=STYLE, scripts=SCRIPT)
    with open(os.path.join(ROOT, 'project', 'index.html'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(out)
    print('wrote project/index.html')


if __name__ == '__main__':
    main()
