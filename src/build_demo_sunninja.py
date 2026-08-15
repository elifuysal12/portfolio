#!/usr/bin/env python3
"""Build the Sun Ninja redesign into ../demo/sunninja/, on Elif's own domain.

The same move as build_demo.py makes for NORE and build_demo_base360.py for
base360: the prototype itself is the demo, running — not a picture of one, not
a player in a frame. This one is the biggest of the three, so it is also the
first room with **two pages**: the landing (`/demo/sunninja/`) and the product
page it links into (`/demo/sunninja/product.html`).

    python3 src/build_demo_sunninja.py [path-to-prototype]

Three things the prototype does for itself that a real address should not:

* **Google Fonts.** The prototype links Poppins off fonts.gstatic.com. The site
  serves no third-party requests, so the six faces its own Artifact build
  already subset (`artifact-fonts.css`) are unpacked into `assets/font/` and
  linked from there — one cached copy shared by both pages.
* **12 MB of PNG and JPEG.** Re-encoded to WebP here, references rewritten with
  them. The two big cut-outs (blanket, cooler) carry alpha and go lossless-ish
  at high quality; the photographs go lossy. Nothing is resized: the sizes are
  the ones the layout was drawn against.
* **A live-looking footer.** The landing still says "© 2026 Sun Ninja" over a
  real phone number and support address. This is spec work on a public URL, so
  it takes the same disclaimer the product page already carries.

Unlike the single-page rooms, the CSS and JS stay as **files** rather than being
inlined: two pages share `style.css`, and inlining it would ship 54 KB twice and
throw the cache away on the click between them. The `?v=` query strings come
across untouched — they are what stops a stale build being reviewed as a broken
one.

Re-run it whenever the prototype changes; the output is committed.
"""
import base64, io, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.abspath(sys.argv[1] if len(sys.argv) > 1
                      else os.path.join(ROOT, '..', 'sunninja-redesign'))
OUT = os.path.join(ROOT, 'demo', 'sunninja')
FONT_DIR = os.path.join(ROOT, 'assets', 'font')

if not os.path.isdir(SRC):
    sys.exit(f'prototype not found: {SRC}')

read = lambda n: open(os.path.join(SRC, n), encoding='utf-8').read()
PAGES = ('index.html', 'product.html')
CODE = ('style.css', 'product.css', 'app.js', 'product.js')
src = {n: read(n) for n in PAGES + CODE + ('artifact-fonts.css',)}

BEACON = ("<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"589b26a9898440e583a7272ff182a1e4\"}'></script>")
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'"
           "%20viewBox='0%200%201%201'%3E%3C/svg%3E")

# ── fonts ────────────────────────────────────────────────────────────────────
# `artifact-fonts.css` is the prototype's own Artifact build: six Poppins faces
# (400/500/600/700 upright, 500/600 italic), already subset, base64 in a data:
# URI each. Unpacked back to files here — the room links them, so the landing
# and the product page pull one copy between them.
os.makedirs(FONT_DIR, exist_ok=True)
faces = re.findall(
    r"@font-face\s*\{[^}]*?font-style:\s*(\w+);[^}]*?font-weight:\s*(\d+);"
    r"[^}]*?src:\s*url\(data:font/woff2;base64,([A-Za-z0-9+/=]+)\)[^}]*?\}",
    src['artifact-fonts.css'], re.S)
if len(faces) != 6:
    sys.exit(f'expected 6 Poppins faces in artifact-fonts.css, found {len(faces)}')

FONT_CSS = []
for style, weight, b64 in faces:
    name = f"sn-po-{weight}{'i' if style == 'italic' else ''}.woff2"
    open(os.path.join(FONT_DIR, name), 'wb').write(base64.b64decode(b64))
    FONT_CSS.append(f"@font-face{{font-family:'Poppins';font-style:{style};"
                    f"font-weight:{weight};font-display:swap;"
                    f"src:url(/assets/font/{name}) format('woff2')}}")
FONT_CSS = '<style>' + ''.join(FONT_CSS) + '</style>'

GOOGLE = re.compile(
    r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*'
    r'<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\s*'
    r'<link href="https://fonts\.googleapis\.com/css2\?family=Poppins[^"]*" '
    r'rel="stylesheet">')

# ── images ───────────────────────────────────────────────────────────────────
# Only what the pages, the stylesheets and the two scripts actually name: the
# prototype's img/ folder carries 69 files and the site needs 28 of them.
from PIL import Image

os.makedirs(os.path.join(OUT, 'img'), exist_ok=True)
used = sorted(set(re.findall(r'img/([A-Za-z0-9_.-]+\.(?:png|jpg|jpeg))',
                             ''.join(src[n] for n in PAGES + CODE))))
missing = [f for f in used if not os.path.exists(os.path.join(SRC, 'img', f))]
if missing:
    sys.exit('img/ is missing: ' + ', '.join(missing))

before = after = 0
for f in used:
    p = os.path.join(SRC, 'img', f)
    im = Image.open(p)
    alpha = im.mode in ('RGBA', 'LA') or 'transparency' in im.info
    im = im.convert('RGBA' if alpha else 'RGB')
    out = os.path.join(OUT, 'img', os.path.splitext(f)[0] + '.webp')
    # the cut-outs sit on the sky with no plinth under them, so their edges are
    # the whole trick — they get the high-quality pass; the photographs sit in
    # panes and take the ordinary one
    im.save(out, 'WEBP', quality=92 if alpha else 82, method=6)
    before += os.path.getsize(p)
    after += os.path.getsize(out)

# ── the pages ────────────────────────────────────────────────────────────────
HEADS = {
    'index.html': (
        'Sun Ninja — live prototype · Elif Beyza Uysal',
        'A landing page redesign for Sun Ninja, the beach shade brand — the '
        'running prototype, with the sky and the palette moving as you scroll. '
        'By Elif Beyza Uysal.',
        'https://elifbeyzauysal.com/demo/sunninja/'),
    'product.html': (
        'Sun Ninja Portable Shower — live prototype · Elif Beyza Uysal',
        'The product page from the Sun Ninja redesign — configurator, gallery '
        'and reviews, running. By Elif Beyza Uysal.',
        'https://elifbeyzauysal.com/demo/sunninja/product.html'),
}

# spec work on a public URL: the page itself is all the context a visitor gets,
# so the landing takes the line the product page already carries, and the
# contact details go to placeholders — nobody should write to a real support
# desk from a mockup
OLD_FINE = ('<span>© 2026 Sun Ninja</span><span>(844) SUN-TENT</span>'
            '<span>help@sunninja.com</span>')
NEW_FINE = ('<span>Unofficial concept redesign · not affiliated with Sun Ninja'
            '</span><span>(844) 000-0000</span><span>hello@example.com</span>')

written = []
for name in PAGES:
    html = src[name]
    title, desc, canon = HEADS[name]

    if not GOOGLE.search(html):
        sys.exit(f'the Google Fonts block moved in {name} — check the prototype')
    html = GOOGLE.sub(FONT_CSS, html, count=1)

    if name == 'index.html':
        if OLD_FINE not in html:
            sys.exit('the landing fineprint moved — check the prototype')
        html = html.replace(OLD_FINE, NEW_FINE, 1)
    elif 'not affiliated with Sun Ninja' not in html:
        sys.exit('the product page lost its disclaimer — check the prototype')

    html = re.sub(r'<title>.*?</title>', '', html, count=1, flags=re.S)
    html = html.replace('</head>', (
        f'<title>{title}</title>\n'
        f'<meta name="description" content="{desc}">\n'
        f'<meta property="og:title" content="{title}">\n'
        f'<meta property="og:description" content="{desc}">\n'
        '<meta property="og:type" content="website">\n'
        f'<link rel="canonical" href="{canon}">\n'
        # no tab icon, as on the site: the title carries the tab
        f'<link rel="icon" href="{FAVICON}">\n'
        f'{BEACON}\n</head>'), 1)

    for f in used:
        html = html.replace('img/' + f, 'img/' + os.path.splitext(f)[0] + '.webp')

    open(os.path.join(OUT, name), 'w', encoding='utf-8').write(html)
    written.append((name, len(html.encode())))

for name in CODE:
    text = src[name]
    for f in used:
        text = text.replace('img/' + f, 'img/' + os.path.splitext(f)[0] + '.webp')
    open(os.path.join(OUT, name), 'w', encoding='utf-8').write(text)

left = re.findall(r'.{0,30}fonts\.(?:googleapis|gstatic)\.com.{0,30}',
                  ''.join(open(os.path.join(OUT, n), encoding='utf-8').read()
                          for n in PAGES + CODE))
if left:
    sys.exit('a Google Fonts request survived: ' + ' / '.join(left))

for name, size in written:
    print(f'demo/sunninja/{name}  {size/1024:.0f} KB')
print(f'  + css/js  {sum(os.path.getsize(os.path.join(OUT, n)) for n in CODE)/1024:.0f} KB'
      f'  (shared by both pages)')
print(f'  + img     {after/1024/1024:.1f} MB  ({len(used)} files, WebP,'
      f' was {before/1024/1024:.1f} MB)')
print(f'  + assets/font  6 faces, {sum(os.path.getsize(os.path.join(FONT_DIR, f)) for f in os.listdir(FONT_DIR) if f.startswith("sn-po"))/1024:.0f} KB (shared, cached)')
