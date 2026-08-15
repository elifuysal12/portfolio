#!/usr/bin/env python3
"""Cut the ALTI case-study assets out of the board's 4× section exports.

    python3 src/slice_alti.py [folder-with-the-exports]

Exporting fifteen phones one at a time is fifteen round-trips through Figma;
the section frames already hold them at the right scale, so the four sections
are exported once each (3935:373, 3936:373, 3947:375, 3947:18683 at 4×, plus
the cover rectangle 3940:376 and the cover frame 3940:375) and cut up here.

The consequence to remember: a crop carries the band its section was drawn on
— #F7F8FC for the problem and the Wander walk, white for the rest — which is
why the page has to paint the same two greys. That is what `alt:1` does on a
section in the template.

Expects, in the folder given (default: ./alti-exports next to this script):
    sec03@4.png sec07@4.png sec08@4.png sec09@4.png facade@4.png cover@4.png
"""
import os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(sys.argv[1] if len(sys.argv) > 1
                      else os.path.join(HERE, 'alti-exports'))
OUT = os.path.join(HERE, 'assets', 'alti')
COVER_OUT = os.path.join(HERE, 'assets', 'cover')
if not os.path.isdir(SRC):
    sys.exit(f'exports not found: {SRC}\n(re-export the section frames from '
             f'Figma at 4× and drop them there — names in the docstring)')
os.makedirs(OUT, exist_ok=True)

S = 4                      # the exports are 4x the board
M = 6 * S                  # a little air, so the gradient stroke isn't clipped


def cut(img, x, y, w, h, name, width=None, q=84):
    box = (x * S - M, y * S - M, (x + w) * S + M, (y + h) * S + M)
    im = img.crop(box).convert('RGB')
    if width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    p = os.path.join(OUT, name + '.webp')
    im.save(p, 'WEBP', quality=q, method=6)
    print(f'{name:8} {im.width}x{im.height}  {os.path.getsize(p)/1024:5.0f} KB')


# 07 · My solution — three devices, on white
sec07 = Image.open(os.path.join(SRC, 'sec07@4.png'))
for i, x in enumerate((222, 567, 912), 1):
    cut(sec07, x, 300, 267, 579, f'd{i}', width=840)

# 08 · Wander, end to end / 09 · Gather, end to end — five phones each, on #F7F8FC
for src, y, pre in (('sec08@4.png', 300, 'w'), ('sec09@4.png', 336, 'g')):
    sec = Image.open(os.path.join(SRC, src))
    for i, x in enumerate((200, 409, 618, 827, 1036), 1):
        cut(sec, x, y, 165, 358, f'{pre}{i}', width=620)

# the cover photograph, without the scrim and the type — those are rebuilt in
# HTML so the cover can reflow. The source upload is only 596x798, so there is
# no point going past ~1800: the rest would be invented pixels.
fac = Image.open(os.path.join(SRC, 'facade@4.png')).convert('RGB')
fac = fac.resize((1800, round(fac.height * 1800 / fac.width)), Image.LANCZOS)
p = os.path.join(OUT, 'cover.webp')
fac.save(p, 'WEBP', quality=82, method=6)
print(f'{"cover":8} {fac.width}x{fac.height}  {os.path.getsize(p)/1024:5.0f} KB')

# CAREFUL: assets/cover/alti.webp is Elif's own cover now — she drew one and it
# replaced the crop below. Re-running this step overwrites it. Comment the last
# block out unless you actually mean to go back to a crop of the board.
#
# the work card is 16:10 and the board cover is 14:9 — 25 board px off the
# bottom, where there is only façade, rather than widening a photograph.
cov = Image.open(os.path.join(SRC, 'cover@4.png')).convert('RGB')
w, h = cov.size
cov = cov.crop((0, 0, w, round(w * 10 / 16)))
cov = cov.resize((1600, 1000), Image.LANCZOS)
p = os.path.join(COVER_OUT, 'alti.webp')
cov.save(p, 'WEBP', quality=84, method=6)
print(f'{"card":8} {cov.width}x{cov.height}  {os.path.getsize(p)/1024:5.0f} KB')
