"""Shared page chrome used once to stamp sub-page skeletons.
Pages are plain static HTML after this; nothing runs at serve time."""

def header(root):
    return f'''      <header class="site-header site-header--hero">
        <div class="container">
          <a class="logo" href="{root}index.html" aria-label="Computer Vision for Developers — course home">
            <img class="logo--dark"  src="{root}assets/academy_color.png" alt="SDAIA Academy">
            <img class="logo--light" src="{root}assets/academy_white.png" alt="SDAIA Academy">
          </a>
          <span class="logo">
            <img class="logo--dark"  src="{root}assets/sdaia_color.png" alt="Saudi Data and AI Authority (SDAIA)">
            <img class="logo--light" src="{root}assets/sdaia_white.png" alt="Saudi Data and AI Authority (SDAIA)">
          </span>
        </div>
      </header>'''

def footer(root):
    return f'''  <footer class="site-footer">
    <div class="container">
      <span class="logo">
        <img class="logo--dark"  src="{root}assets/academy_color.png" alt="SDAIA Academy">
        <img class="logo--light" src="{root}assets/academy_white.png" alt="SDAIA Academy">
      </span>
      <p class="footer-text">Computer Vision for Developers · SDAIA Academy · Instructor: Musa Ibn Rashid</p>
      <span class="logo">
        <img class="logo--dark"  src="{root}assets/sdaia_color.png" alt="Saudi Data and AI Authority (SDAIA)">
        <img class="logo--light" src="{root}assets/sdaia_white.png" alt="Saudi Data and AI Authority (SDAIA)">
      </span>
    </div>
  </footer>'''

def page(root, title, h1, lede, body, css_links=(), style='', scripts='', back=None, eyebrow='SDAIA Academy · Computer Vision for Developers', hero_extra=''):
    back = back or (f'{root}index.html', '← Course home')
    links = '\n'.join(f'  <link rel="stylesheet" href="{c}">' for c in css_links)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} · Computer Vision for Developers</title>
  <link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{root}assets/theme.css">
  <link rel="stylesheet" href="{root}assets/site.css">
{links}
  <style>
{style}
  </style>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>

  <main id="main">
    <section class="page-hero on-dark">
{header(root)}

      <div class="container page-hero-inner">
        <a class="back" href="{back[0]}">{back[1]}</a>
        <p class="eyebrow">{eyebrow}</p>
        <h1>{h1}</h1>
        <p>{lede}</p>{hero_extra}
      </div>
    </section>

{body}
  </main>

{footer(root)}
{scripts}
</body>
</html>
'''
