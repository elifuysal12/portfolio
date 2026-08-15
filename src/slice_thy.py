#!/usr/bin/env python3
"""Cut the Remote Controller assets out of the deck's 4× slide exports.

    python3 src/slice_thy.py [folder-with-the-exports]

Elif's board for this one is a four-slide deck (Portfolyo_2026, page 345:3793:
`12_` cover, `13_` research, `14_` IA + wireframes, `15_` finalization), so the
slides are exported once each at 4× and cut up here rather than exported piece
by piece. Same rule as ALTI: 1× exports drop the 2px strokes on the wireframes
below a pixel and they vanish.

Two things worth remembering:

  · every slide is drawn on WHITE, so unlike ALTI there is no second band to
    paint — the case page is white end to end and the crops sit flat on it.

  · slide 15's own export kept failing at 4× (the tilted array is heavy), so
    the two showcase groups are exported as their own nodes: 345:4313 (the
    portrait array) and 345:5397 (the landscape one). They bleed off their
    frames on purpose — that is the composition, not a bad crop.

Expects, in the folder given (default: ./thy-exports next to this script):
    s14@4.png comp@4.png final_p@4.png final_l@4.png
    tile1@4.png tile2@4.png tile3@4.png     (the research photos, exported as
                                             their own nodes — see below)
"""
import os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(sys.argv[1] if len(sys.argv) > 1
                      else os.path.join(HERE, 'thy-exports'))
OUT = os.path.join(HERE, 'assets', 'thy')
COVER_OUT = os.path.join(HERE, 'assets', 'cover')
if not os.path.isdir(SRC):
    sys.exit(f'exports not found: {SRC}\n(re-export the slides from Figma at '
             f'4× and drop them there — names in the docstring)')
os.makedirs(OUT, exist_ok=True)
os.makedirs(COVER_OUT, exist_ok=True)

S = 4                                  # the exports are 4× the board


def flat(name):
    """The slides export with a transparent ground; the board's ground is white."""
    im = Image.open(os.path.join(SRC, name)).convert('RGBA')
    bg = Image.new('RGB', im.size, (255, 255, 255))
    bg.paste(im, mask=im.split()[3])
    return bg


def save(im, name, width, q=84, where=OUT):
    if width and im.width != width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    p = os.path.join(where, name + '.webp')
    im.save(p, 'WEBP', quality=q, method=6)
    print(f'{name:9} {im.width}x{im.height}  {os.path.getsize(p)/1024:5.0f} KB')


def cut(img, x, y, w, h, name, width, m=8, q=84):
    """Board coordinates in, webp out. `m` is air, in board px."""
    save(img.crop((round((x - m) * S), round((y - m) * S),
                   round((x + w + m) * S), round((y + h + m) * S))), name, width, q)


# ---- 13_ · research: the three photographs, in their own pink frames.
# NOT cut out of s13: the slide draws a red callout line from each photo to a
# label beside it, and those lines are siblings of the frames, not children —
# so any crop tight enough to leave the labels behind takes the lines with it
# and they come away as stubs pointing at nothing. Exported as their own nodes
# (345:3840 / 345:3820 / 345:3843) the frames render alone, lines excluded, and
# what the labels said is said by the caption instead.
#
# The middle frame is also 23 board px narrower than the other two; left alone,
# three equal columns render it taller and the captions stop lining up, so it
# is padded back to the others' shape.
AR = 303 / 293                         # the shape the outer two export at
for i in (1, 2, 3):
    im = flat(f'tile{i}@4.png')
    if im.width < round(im.height * AR):
        pad = Image.new('RGB', (round(im.height * AR), im.height), (255, 255, 255))
        pad.paste(im, ((pad.width - im.width) // 2, 0))
        im = pad
    save(im, f'p{i}', 900)

# ---- 14_ · the wireframes. Five portrait, then the two landscape ones.
s14 = flat('s14@4.png')
for i in range(5):
    cut(s14, 69 + 227 * i, 643, 147, 354, f'w{i+1}', 620, m=6)
for i, y in enumerate((636, 839), 1):
    cut(s14, 1202, y, 354, 158, f'l{i}', 1200, m=6)

# ---- 15_ · the component set (flat, and the only place the final UI is drawn
# at full size) and the two showcase arrays.
save(flat('comp@4.png'), 'comp', 1700)
save(flat('final_p@4.png'), 'fin1', 1800)
save(flat('final_l@4.png'), 'fin2', 1800)

# ---- 12_ · the cover slide is NOT used.
# It was, at first — padded from 16:9 to the card's 16:10 with white. Elif
# looked at it once: "bu 3 değil, onu kaldırman lazım ve cover fotosu çok
# dandik duruyor." Both true. It is a slide, not a plate: the type sits small
# in the left third, the deck's section numeral "3" is welded to the first
# word, and the middle is empty. assets/cover/thy.webp and assets/thy/hero.webp
# are rendered by make_cover_thy.py instead — run that after this.
