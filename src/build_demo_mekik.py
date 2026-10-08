#!/usr/bin/env python3
"""Build the MEKİK prototype into ../demo/mekik/, on Elif's own domain.

The room build_demo.py always said would move in beside /demo/nore. Same move
as the others: the prototype itself is the demo, running — not a picture of one
and not a player in a frame.

The prototype lives in its own project (`~/Projects/mekik`, the denim atelier
with the assistant that grows out of its own search bar). It ships in two
flavours there: `index.html`, which reads its fifteen photographs off `img/`,
and `artifact.html`, which base64s downscaled copies of them into the file
because that CSP blocks every external host.

The second one is 1.7 MB of the same page and belongs to the Artifact. Here the
photographs are re-encoded to WebP and copied next to the page as plain files:
they stay at full size, the browser caches them, and nothing sits in front of
the first paint.

    python3 src/build_demo_mekik.py [path-to-prototype]

Re-run it whenever the prototype changes; the output is committed.
"""
import os, re, sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.abspath(sys.argv[1] if len(sys.argv) > 1
                      else os.path.join(ROOT, '..', 'mekik'))
OUT = os.path.join(ROOT, 'demo', 'mekik')

if not os.path.isdir(SRC):
    sys.exit(f'prototype not found: {SRC}')
html = open(os.path.join(SRC, 'index.html'), encoding='utf-8').read()

# ── photographs ──────────────────────────────────────────────────────────────
# All fifteen are 1000px wide already — the width the layout was drawn against —
# so nothing is resized, only re-encoded. The hero and the band photograph run
# full-bleed and get the higher pass; the rest are card-sized.
os.makedirs(os.path.join(OUT, 'img'), exist_ok=True)
files = sorted(f for f in os.listdir(os.path.join(SRC, 'img')) if f.endswith('.jpg'))
# the page names most of them in JS, so the folder is the list; the ones written
# out in the markup are checked against it rather than assumed
named = set(re.findall(r'img/([a-z0-9]+)\.jpg', html))
missing = sorted(n for n in named if n + '.jpg' not in files)
if missing:
    sys.exit('img/ is missing: ' + ', '.join(missing))
FULL = {'p4', 'p2'}                       # hero, band
before = after = 0
for f in files:
    p = os.path.join(SRC, 'img', f)
    out = os.path.join(OUT, 'img', os.path.splitext(f)[0] + '.webp')
    Image.open(p).convert('RGB').save(
        out, 'WEBP', quality=86 if os.path.splitext(f)[0] in FULL else 80, method=6)
    before += os.path.getsize(p)
    after += os.path.getsize(out)

# Two ways the page names a photograph: written out in the markup, and built in
# a JS string — `src="img/'+p[0]+'.jpg"`. Both keep their folder and their name,
# so only the extension moves.
html = re.sub(r'(src="img/[a-z0-9]+)\.jpg"', r'\1.webp"', html)
html = re.sub(r"""(src="img/'\+[^"]+?\+')\.jpg\"""", r'\1.webp"', html)
left = re.findall(r'.{0,40}\.jpg.{0,10}', html)
if left:
    sys.exit('a .jpg reference survived: ' + ' / '.join(left))

# ── the head ─────────────────────────────────────────────────────────────────
# the same cookieless beacon the site carries, so a visit to the demo shows up
# as its own page rather than disappearing off the end of the funnel
BEACON = ("<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"589b26a9898440e583a7272ff182a1e4\"}'></script>")
# what the tab says: the prototype's own title names the shop, which tells a
# visitor arriving from the work card nothing about which project this is
TITLE = 'MEKİK — live prototype · Elif Beyza Uysal'
DESC = ('A denim atelier storefront and the AI discovery layer on top of it — '
        'the running prototype, by Elif Beyza Uysal.')
HEAD = (f'<title>{TITLE}</title>\n'
        f'<meta name="description" content="{DESC}">\n'
        f'<meta property="og:title" content="{TITLE}">\n'
        f'<meta property="og:description" content="{DESC}">\n'
        '<meta property="og:type" content="website">\n'
        '<link rel="canonical" href="https://elifbeyzauysal.com/demo/mekik/">\n'
        # no tab icon, as on the site: the title carries the tab
        "<link rel=\"icon\" href=\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'"
        "%20viewBox='0%200%201%201'%3E%3C/svg%3E\">\n"
        f'{BEACON}\n</head>')
html = re.sub(r'<title>.*?</title>\s*', '', html, count=1, flags=re.S)
html = html.replace('</head>', HEAD, 1)

# ── the footer ───────────────────────────────────────────────────────────────
# it is her work, so it is signed — the demo is reached from her portfolio and
# should say whose it is without breaking the shop's own fiction. The line it
# joins already says this is a concept and where the photographs come from.
CREDIT = '<span class="lot">Konsept çalışması · fotoğraflar Unsplash</span>'
if CREDIT not in html:
    sys.exit('the footer line moved — check the prototype')
html = html.replace(
    CREDIT, CREDIT + '\n    <span class="lot">Tasarım · Elif Beyza Uysal</span>', 1)

# The assistant was drawn against an Orbina brief, and the stylesheet says so in
# a comment anyone reading the source finds. On Elif's own site the work is
# hers, so the brand comes out — of the page and of the source. Exact string, so
# this fails loudly rather than quietly shipping the name if the wording changes.
SCRUB = [("Orbina'nın AI katmanı — markadan bağımsız sabit. Kabuk MEKİK'in, bu imza Orbina'nın.",
          'Asistanın AI katmanı — markadan bağımsız sabit. Kabuk MEKİK’in, bu imza asistanın.')]
for old, new in SCRUB:
    if old not in html:
        sys.exit(f'scrub target moved, check the prototype: {old!r}')
    html = html.replace(old, new)
stray = re.findall(r'.{0,40}[Oo]rbina.{0,40}', html)
if stray:
    sys.exit('Orbina still in the demo: ' + ' / '.join(stray))

page = os.path.join(OUT, 'index.html')
open(page, 'w', encoding='utf-8').write(html)
print(f'demo/mekik/index.html  {len(html.encode())/1024:.0f} KB  (one file)')
print(f'  + img  {after/1024:.0f} KB  ({len(files)} photographs, WebP,'
      f' was {before/1024:.0f} KB)')
