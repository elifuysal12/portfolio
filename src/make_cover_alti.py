#!/usr/bin/env python3
"""Render the ALTI work-card cover from cover_alti/cover.html.

    python3 src/make_cover_alti.py

The other covers are exports of frames Elif drew in Figma; this one is built
here because it is assembled from screens that already live in the repo
(`src/assets/alti/`) and set in Poppins, which the repo already carries. Change
the words or swap a screen in `cover_alti/cover.html` and re-run.

It goes through headless Chrome rather than PIL for one reason: the type. The
tracked uppercase eyebrow, the ramp poured through the tagline and the mesh are
all things a browser does correctly and a rasteriser has to be talked into.

Note the screens are cut out of the board's own section exports, so each one
arrives sitting on the band it was drawn on; the bounding box of everything
that is *not* that band is the phone, bezel included.
"""
import os, shutil, subprocess, sys, time

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'assets', 'alti')
WORK = os.path.join(HERE, 'cover_alti')
OUT = os.path.join(HERE, 'assets', 'cover', 'alti.webp')
SHOT = os.path.join(WORK, '_render.png')

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
W, H = 2600, 1113                      # the featured card's band (coverRatio)
SCREENS = ('w1', 'd2', 'd3')


def trim(name):
    """the phone, cut free of the section band it was exported on"""
    im = Image.open(os.path.join(SRC, name + '.webp')).convert('RGB')
    a = np.array(im).astype(int)
    band = a[im.height // 2, 2]
    ys, xs = np.where(np.abs(a - band).sum(2) > 40)
    im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(
        os.path.join(WORK, name + '.png'))


if not os.path.isfile(CHROME):
    sys.exit(f'Chrome not found at {CHROME}')

for s in SCREENS:
    trim(s)

# A throwaway profile each time: Chrome refuses to start a second headless run
# against a profile the first one is still holding, and these renders are
# frequent enough to trip over that.
prof = os.path.join(WORK, '_profile')
shutil.rmtree(prof, ignore_errors=True)
if os.path.exists(SHOT):
    os.remove(SHOT)

subprocess.Popen(
    [CHROME, '--headless=new', f'--user-data-dir={prof}',
     f'--window-size={W},{H}', '--hide-scrollbars',
     '--allow-file-access-from-files',       # the woff2 files sit beside it
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
im.save(OUT, 'WEBP', quality=86, method=6)
im.close()

# Chrome is still alive at this point — it writes the screenshot and lingers —
# so the profile it is holding open cannot always be removed on the first ask.
# .gitignore covers the leftover either way; this just keeps the tree tidy.
os.remove(SHOT)
for s in SCREENS:
    os.remove(os.path.join(WORK, s + '.png'))
for _ in range(10):
    shutil.rmtree(prof, ignore_errors=True)
    if not os.path.exists(prof):
        break
    time.sleep(1)

print(f'{os.path.relpath(OUT, os.path.dirname(HERE))}  {im.width}x{im.height}'
      f'  {os.path.getsize(OUT)/1024:.0f} KB'
      f'  (coverRatio {W}/{H}, coverBg #0A1551)')
