#!/usr/bin/env python3
"""Turn a Figma cover export into the file the work card ships.

    python3 src/make_cover.py cursor ~/Downloads/cover@4x.png

The card is 16:10; Elif's cover frame is 808 × 632 (≈ 1.28). Rather than crop
20% off its height — which would have clipped the eyebrow at the top and the
pill at the bottom — the canvas is widened to 16:10 with the artwork's own
ground, exactly as she asked ("boşluk çıkarsa #0F1115 ile doldur"), and the
coral rule along the bottom edge is continued across the new width so it
reaches both corners instead of stopping mid-card.

Downscaled from the 4× export rather than exported at final size: supersampling
gives cleaner edges on the thin strokes.
"""
import os, sys
from PIL import Image

RATIO = 16 / 10
WIDTH = 1800                      # the card is ~870 CSS wide at most; 2× that
HERE = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) != 3:
    sys.exit(__doc__)
name, src = sys.argv[1], os.path.expanduser(sys.argv[2])

im = Image.open(src)
ground = im.convert('RGB').getpixel((3, 3))          # the artwork's own black
if im.mode == 'RGBA':
    flat = Image.new('RGB', im.size, ground)
    flat.paste(im, mask=im.split()[3])
    im = flat
else:
    im = im.convert('RGB')

# the rule along the bottom: how tall, and what it runs between
w, h = im.size
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
print(f'{os.path.relpath(out, os.path.dirname(HERE))}  {final.size[0]}×{final.size[1]}'
      f'  {os.path.getsize(out)/1024:.0f} KB  (ground {ground}, rule {strip}px)')
