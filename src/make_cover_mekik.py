#!/usr/bin/env python3
"""Render the MEKİK work-card cover from cover_mekik/cover.html.

    python3 src/make_cover_mekik.py            # the plate -> assets/cover/mekik.webp
    python3 src/make_cover_mekik.py --shot     # re-shoot the prototype first

Same pipeline as make_cover_thy.py and make_cover_alti.py, and for the same
reason — the type. The tracked mark, the ramp poured through the line under it
and the lift under the screen are things a browser does correctly and a
rasteriser has to be talked into.

`--shot` needs the site served locally (`python3 -m http.server 8765` from the
repo root) and `demo/mekik/` built: it opens the room, clicks the prototype's
own remote through to the canvas state, hides that remote, and keeps the frame
as `cover_mekik/shot.jpg`. Without the flag the existing shot is reused, which
is the usual case — the plate changes far more often than the prototype.
"""
import os, shutil, subprocess, sys, time

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORK = os.path.join(HERE, 'cover_mekik')
CARD = os.path.join(HERE, 'assets', 'cover', 'mekik.webp')
SHOT = os.path.join(WORK, 'shot.jpg')
PLATE = os.path.join(WORK, '_render.png')

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
W, H = 2600, 1625                      # 16:10, the shape of every small card
ROOM = 'http://localhost:8765/demo/mekik/'

if not os.path.isfile(CHROME):
    sys.exit(f'Chrome not found at {CHROME}')


def shoot(url, out, w, h, scale=1, extra=()):
    """One headless frame. A throwaway profile each time: Chrome refuses to
    start a second run against a profile the first one is still holding."""
    prof = os.path.join(WORK, '_profile')
    shutil.rmtree(prof, ignore_errors=True)
    if os.path.exists(out):
        os.remove(out)
    subprocess.Popen(
        [CHROME, '--headless=new', f'--user-data-dir={prof}',
         f'--window-size={w},{h}', f'--force-device-scale-factor={scale}',
         '--hide-scrollbars',
         '--allow-file-access-from-files',   # the woff2 and the shot sit beside it
         '--virtual-time-budget=9000', f'--screenshot={out}', *extra, url],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Chrome writes the file and then lingers, so the wait is on the file, not
    # the process — and the size has to settle before it is opened.
    for _ in range(120):
        if os.path.exists(out) and os.path.getsize(out) > 0:
            size = -1
            while size != os.path.getsize(out):
                size = os.path.getsize(out)
                time.sleep(0.4)
            break
        time.sleep(0.5)
    else:
        sys.exit('Chrome produced no screenshot')
    subprocess.run(['pkill', '-f', f'user-data-dir={prof}'], capture_output=True)
    for _ in range(10):
        shutil.rmtree(prof, ignore_errors=True)
        if not os.path.exists(prof):
            break
        time.sleep(1)


# ── the artefact ─────────────────────────────────────────────────────────────
if '--shot' in sys.argv:
    room = os.path.join(ROOT, 'demo', 'mekik', 'index.html')
    if not os.path.isfile(room):
        sys.exit('build the room first: python3 src/build_demo_mekik.py')
    # The state the cover shows is the canvas — the one that argues the project.
    # It is reached through the prototype's own remote rather than by setting
    # `data-s` by hand: the pane is rendered on the way in, so the attribute on
    # its own would give an empty panel. The remote itself then goes.
    tmp = os.path.join(ROOT, 'demo', 'mekik', '_shot.html')
    open(tmp, 'w', encoding='utf-8').write(
        open(room, encoding='utf-8').read().replace('</body>', (
            '<style>.remote{display:none!important}</style>\n'
            '<script>setTimeout(function(){'
            'document.querySelector(\'[data-go="3"]\').click();}, 60);</script>\n'
            '</body>'), 1))
    png = os.path.join(WORK, '_shot.png')
    try:
        shoot(ROOM + '_shot.html', png, 1600, 1000, scale=2)
    finally:
        os.remove(tmp)
    im = Image.open(png).convert('RGB')
    if im.size != (3200, 2000):
        sys.exit(f'expected 3200x2000, got {im.size} — is the site served on 8765?')
    # Cropped to the panel and a margin of blurred store around it, at the
    # card's own 16:10. The full frame was tried first: on a card 870px wide
    # the panel came out a third of that and the whole shot read as a grey
    # rectangle. At 1600x1000 the widget is 1140x700 centred at top:150 (its
    # own `min()` rules), so the box is that plus 70px of surround.
    x, y, w, h = (1600 - 1140) // 2, 150, 1140, 700
    box = (x - 70, y - 70, x + w + 70, y + h + 70)      # 1280x840 at 1x
    box = (box[0] * 2, (box[1] + 20) * 2, box[2] * 2, (box[3] - 20) * 2)   # 16:10, at 2x
    im = im.crop(box)
    im.save(SHOT, 'JPEG', quality=92)
    im.close()
    os.remove(png)
    print(f'cover_mekik/shot.jpg  {os.path.getsize(SHOT)/1024:.0f} KB')

if not os.path.exists(SHOT):
    sys.exit('no shot yet — run with --shot (and serve the site on 8765)')

# ── the plate ────────────────────────────────────────────────────────────────
shoot('file://' + os.path.join(WORK, 'cover.html'), PLATE, W, H)
im = Image.open(PLATE).convert('RGB')
if im.size != (W, H):
    sys.exit(f'expected {W}x{H}, got {im.size} — check the .cover box')

out = im.resize((1800, round(im.height * 1800 / im.width)), Image.LANCZOS)
out.save(CARD, 'WEBP', quality=88, method=6)
print(f'{os.path.relpath(CARD, ROOT):28} {out.width}x{out.height}'
      f'  {os.path.getsize(CARD)/1024:.0f} KB')
im.close()
os.remove(PLATE)
