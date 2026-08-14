#!/usr/bin/env python3
"""Build the Cursor Assistant demo into ../demo/nore/, on Elif's own domain.

Every runnable prototype gets its own room under /demo, named after the shop it
is set in — /demo/nore here, /demo/mekik when that one goes up — so the address
says which demo it is rather than which one happened to be built first.

The prototype lives in its own project (`~/Projects/mavi-cursor-chat`, the NORE
discovery-cursor). It ships in two flavours there: a local one that pulls its
photographs from Unsplash at runtime, and an Artifact one that base64s them into
the file because that CSP blocks every external host.

Neither fits a real website. Here the photos are copied next to the page as
plain files: no third-party host to go down, no megabyte of base64 in front of
the first paint, and the browser caches them.

    python3 src/build_demo.py [path-to-prototype]

Re-run it whenever the prototype changes; the output is committed.
"""
import os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.abspath(sys.argv[1] if len(sys.argv) > 1
                      else os.path.join(ROOT, '..', 'mavi-cursor-chat'))
OUT = os.path.join(ROOT, 'demo', 'nore')
# what the tab says: the prototype's own title names the shop, which tells a
# visitor arriving from the case study nothing about which project this is
TITLE = 'Cursor Assistant — NORE demo · Elif Beyza Uysal'

if not os.path.isdir(SRC):
    sys.exit(f'prototype not found: {SRC}')

read = lambda n: open(os.path.join(SRC, n), encoding='utf-8').read()
html, css = read('index.html'), read('style.css')
data, answers, cursor = read('data.js'), read('answers.js'), read('cursor.js')

# the two lines that reach for Unsplash — repoint them at the copies below
NET = ("const IMG  = id => `https://images.unsplash.com/${id}?w=900&q=80&auto=format&fit=crop`;\n"
       "const IMGW = id => `https://images.unsplash.com/${id}?w=2000&q=80&auto=format&fit=crop`;")
if NET not in data:
    sys.exit('the Unsplash helpers moved — check data.js before rebuilding')
data = data.replace(NET, 'const IMG  = id => `img/${id}.jpg`;\n'
                         'const IMGW = id => `img/${id}.jpg`;')

os.makedirs(os.path.join(OUT, 'img'), exist_ok=True)
used = set(re.findall(r"'(photo-[0-9a-f-]+)'", data))
missing = sorted(p for p in used if not os.path.exists(os.path.join(SRC, 'img-embed', p + '.jpg')))
if missing:
    sys.exit('img-embed/ is missing: ' + ', '.join(missing))
for p in sorted(used):
    shutil.copyfile(os.path.join(SRC, 'img-embed', p + '.jpg'),
                    os.path.join(OUT, 'img', p + '.jpg'))

# one file, so the demo is a single request plus its photographs
html = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', html, count=1, flags=re.S)
html = html.replace('<link rel="stylesheet" href="style.css">', '<style>\n' + css + '\n</style>')
html = re.sub(r'<script src="(data|answers|cursor)\.js"></script>\s*', '', html)
html = html.replace('</body>', '<script>\n' + '\n'.join([data, answers, cursor]) + '\n</script>\n</body>')

page = os.path.join(OUT, 'index.html')
open(page, 'w', encoding='utf-8').write(html)
shot = sum(os.path.getsize(os.path.join(OUT, 'img', f)) for f in os.listdir(os.path.join(OUT, 'img')))
print(f'{os.path.relpath(page, ROOT)}  {len(html.encode())/1024:.0f} KB'
      f'  + img {shot/1024:.0f} KB ({len(used)} photos)')
