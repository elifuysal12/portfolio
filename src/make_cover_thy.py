#!/usr/bin/env python3
"""Render the Remote Controller cover from cover_thy/cover.html.

    python3 src/make_cover_thy.py

Same pipeline as make_cover_alti.py and for the same reason — the type. The
tracked eyebrow, the ramp poured through the tagline and the three soft blobs
off the right edge are all things a browser does correctly and a rasteriser
has to be talked into. Change the words or swap the array in
`cover_thy/cover.html` and re-run.

Unlike ALTI's, nothing has to be cut out first: the plate is white, which is
the ground the array was already drawn on.

One plate, two jobs — the work card (16:10) and the case sheet's cover, which
is why it renders at 2600 wide and is written out twice at different sizes.
"""
import os, shutil, subprocess, sys, time

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, 'cover_thy')
CARD = os.path.join(HERE, 'assets', 'cover', 'thy.webp')
SHEET = os.path.join(HERE, 'assets', 'thy', 'hero.webp')
SHOT = os.path.join(WORK, '_render.png')

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
W, H = 2600, 1625                      # 16:10, the shape of every small card

if not os.path.isfile(CHROME):
    sys.exit(f'Chrome not found at {CHROME}')

# A throwaway profile each time: Chrome refuses to start a second headless run
# against a profile the first one is still holding.
prof = os.path.join(WORK, '_profile')
shutil.rmtree(prof, ignore_errors=True)
if os.path.exists(SHOT):
    os.remove(SHOT)

subprocess.Popen(
    [CHROME, '--headless=new', f'--user-data-dir={prof}',
     f'--window-size={W},{H}', '--hide-scrollbars',
     '--allow-file-access-from-files',       # the woff2 and the array sit beside it
     '--virtual-time-budget=6000', f'--screenshot={SHOT}',
     'file://' + os.path.join(WORK, 'cover.html')],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Chrome writes the file and then lingers, so the wait is on the file, not the
# process — and the size has to settle before it is opened.
for _ in range(120):
    if os.path.exists(SHOT) and os.path.getsize(SHOT) > 0:
        size = -1
        while size != os.path.getsize(SHOT):
            size = os.path.getsize(SHOT)
            time.sleep(0.4)
        break
    time.sleep(0.5)
else:
    sys.exit('Chrome produced no screenshot')

im = Image.open(SHOT).convert('RGB')
if im.size != (W, H):
    sys.exit(f'expected {W}x{H}, got {im.size} — check the .cover box')

for path, width, q in ((SHEET, 2600, 88), (CARD, 1800, 88)):
    out = im if im.width == width else im.resize(
        (width, round(im.height * width / im.width)), Image.LANCZOS)
    out.save(path, 'WEBP', quality=q, method=6)
    print(f'{os.path.relpath(path, os.path.dirname(HERE)):28} '
          f'{out.width}x{out.height}  {os.path.getsize(path)/1024:.0f} KB')
im.close()

os.remove(SHOT)
for _ in range(10):
    shutil.rmtree(prof, ignore_errors=True)
    if not os.path.exists(prof):
        break
    time.sleep(1)
