#!/usr/bin/env python3
"""Turn a Figma cover export into the file the work card ships.

    python3 src/make_cover.py cursor  ~/Downloads/cover@4x.png
    python3 src/make_cover.py whallet ~/Downloads/cover@4x.png --crop
    python3 src/make_cover.py alti    ~/Downloads/cover@2x.png --trim \
                                      --ratio native --width 2600

Options: --ratio W:H (default 16:10, the small card) or `native` to keep the
artwork's own shape and let the card follow it — for the featured slot, where
reshaping ALTI's banner to 24:9 would have cut the phones off at the top and
her feet off at the bottom. --width N sets the export width (default 1800);
the featured card is twice as wide as the others and wants the pixels.
--trim drops a uniform border first: exporting a group rather than a frame
carries a strip of Figma's own canvas along with it.

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
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))

argv = sys.argv[1:]


def opt(flag, default):
    """--flag VALUE, pulled out of argv so what is left is name + source."""
    if flag not in argv:
        return default
    i = argv.index(flag)
    argv.pop(i)                       # the flag; the value shifts down into i
    return argv.pop(i)


ratio_s = opt('--ratio', '16:10')
WIDTH = int(opt('--width', 1800))     # the small card is ~870 CSS wide; 2× that
crop = '--crop' in argv
trim = '--trim' in argv
RATIO = None if ratio_s == 'native' else (
    lambda a, b: a / b)(*(float(v) for v in ratio_s.split(':')))

args = [a for a in argv if not a.startswith('--')]
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

if trim:
    # a group export carries a band of Figma's own canvas; drop the uniform
    # border before anything measures the artwork's edges
    edge = Image.new('RGB', im.size, im.getpixel((0, 0)))
    box = ImageChops.difference(im, edge).convert('L').point(
        lambda v: 255 if v > 8 else 0).getbbox()
    if box:
        im = im.crop(box)

w, h = im.size

if RATIO is None:
    canvas = im                       # the card follows the artwork, not the reverse
elif crop:
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
how = ('kept whole' if RATIO is None else
       f'cropped {h - canvas.height}px off the bottom' if crop else
       f'widened, rule {strip}px')
print(f'{os.path.relpath(out, os.path.dirname(HERE))}  {final.size[0]}×{final.size[1]}'
      f'  ratio {final.size[0]/final.size[1]:.3f}  {os.path.getsize(out)/1024:.0f} KB'
      f'  (ground {ground}, {how})')
