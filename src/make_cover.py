#!/usr/bin/env python3
"""Turn a Figma cover export into the file the work card ships.

    python3 src/make_cover.py cursor ~/Downloads/cover@4x.png
    python3 src/make_cover.py whallet ~/Downloads/cover@4x.png --crop

The card is 16:10; Elif's cover frames are not. Two ways out, one flag:

  default — widen to 16:10 with the artwork's own ground, exactly as she asked
    for the Cursor cover ("boşluk çıkarsa #0F1115 ile doldur"), and continue the
    coral rule along the bottom edge across the new width so it reaches both
    corners instead of stopping mid-card. Nothing in the composition is lost.

  --crop — take the height off the BOTTOM only. For the Whallet cover (1600 ×
    1200, phones bleeding off the lower edge already) widening would have laid
    flat navy bars over a canvas whose gradient runs corner to corner; cropping
    from the bottom keeps every element where she put it, the phones just bleed
    off sooner. Never crop from the top — that is where the eyebrow and the
    logotype sit.

Downscaled from the 4× export rather than exported at final size: supersampling
gives cleaner edges on the thin strokes.
"""
import os, sys
from PIL import Image

RATIO = 16 / 10
WIDTH = 1800                      # the card is ~870 CSS wide at most; 2× that
HERE = os.path.dirname(os.path.abspath(__file__))

args = [a for a in sys.argv[1:] if not a.startswith('--')]
crop = '--crop' in sys.argv[1:]
if len(args) != 2:
    sys.exit(__doc__)
name, src = args[0], os.path.expanduser(args[1])

im = Image.open(src)
ground = im.convert('RGB').getpixel((3, 3))          # the artwork's own black
if im.mode == 'RGBA':
    flat = Image.new('RGB', im.size, ground)
    flat.paste(im, mask=im.split()[3])
    im = flat
else:
    im = im.convert('RGB')

w, h = im.size

if crop:
    canvas = im.crop((0, 0, w, round(w / RATIO)))
else:
    # the rule along the bottom: how tall, and what it runs between
    rows = [y for y in range(h - 1, h - h // 40, -1)
            if max(im.getpixel((w // 2, y))) - min(im.getpixel((w // 2, y))) > 40]
    strip = (h - min(rows)) if rows else 0
    ends = (im.getpixel((2, min(rows) + 1)), im.getpixel((w - 3, min(rows) + 1))) if rows else None

    # widen to the card's ratio, artwork centred
    canvas = Image.new('RGB', (round(h * RATIO), h), ground)
    canvas.paste(im, ((canvas.width - w) // 2, 0))

    if strip:
        cw = canvas.width
        px = canvas.load()
        for x in range(cw):
            t = x / (cw - 1)
            c = tuple(round(a + (b - a) * t) for a, b in zip(*ends))
            for y in range(h - strip, h):
                px[x, y] = c

out_dir = os.path.join(HERE, 'assets', 'cover')
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, f'{name}.webp')
final = canvas.resize((WIDTH, round(canvas.height * WIDTH / canvas.width)), Image.LANCZOS)
final.save(out, 'WEBP', quality=90, method=6)
how = f'cropped {h - canvas.height}px off the bottom' if crop else f'widened, rule {strip}px'
print(f'{os.path.relpath(out, os.path.dirname(HERE))}  {final.size[0]}×{final.size[1]}'
      f'  {os.path.getsize(out)/1024:.0f} KB  (ground {ground}, {how})')
