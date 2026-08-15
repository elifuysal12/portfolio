#!/usr/bin/env python3
"""Build the Figma-prototype demo rooms under ../demo/.

Same idea as build_demo.py — one room per demo — but these prototypes are not
code: they live in Figma and run in Figma's player. So the room is a thin shell
of Elif's own chrome around an embedded prototype: her paper, her type, a way
back to the work, and the beacon, so a visit shows up as its own page rather
than falling off the end of the funnel.

    python3 src/build_demo_figma.py

This is the *second* choice. Where a prototype exists as running code it ships
as the page itself (see build_demo.py, build_demo_base360.py) — an embedded
player is a picture of the work inside someone else's chrome. The rooms here
are for work that has no coded counterpart.

The prototype must be shared publicly in Figma — Share → "Anyone with the link"
→ can view. Without that, an embed shows visitors a Figma login wall, which is
why the shell carries a visible "open in Figma" escape hatch underneath.
Note that embed.figma.com opened *directly in a tab* shows a login wall even
when the file is public; only the test inside the page means anything.
"""
import os, shutil
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# key = the room under /demo. file/node/page/start come straight off the
# prototype's share link:
#   .../proto/<file>/<name>?node-id=<node>&page-id=<page>&starting-point-node-id=<start>
DEMOS = [
    dict(key='jotform',
         title='Chatbot Dashboard — prototype',
         brand='Chatbot Dashboard',
         sub='Jotform · analytics dashboard',
         file='2x6KiLkwK5G2oheLZrzSaS',
         name='Jotform',
         node='1384-158976',
         page='930:24958',
         start='1384:146915',
         # `contain` was the obvious guess for a fixed 1440×900 app screen and
         # is wrong: the player fits the frame at roughly half size and rings
         # it in black, so the dashboard arrives as a postage stamp. Measured
         # against it, `scale-down-width` fills the stage edge to edge at the
         # size the screen was drawn, and the last 90px scroll inside the
         # player — which is how the real admin page behaves anyway.
         scaling='scale-down-width'),
]

BEACON = ("<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"589b26a9898440e583a7272ff182a1e4\"}'></script>")


def urls(d):
    """The player URL for the iframe, and the plain share URL for the escape hatch."""
    q = (f"node-id={d['node']}&page-id={quote(d['page'], safe='')}"
         f"&starting-point-node-id={quote(d['start'], safe='')}"
         f"&scaling={d['scaling']}&content-scaling=fixed")
    return (f"https://embed.figma.com/proto/{d['file']}/{d['name']}?{q}"
            "&hide-ui=1&embed-host=elifbeyzauysal",
            f"https://www.figma.com/proto/{d['file']}/{d['name']}?{q}")


# The bar is a few words, but they are set in the site's own type — a demo that
# opens in Arial reads as somebody else's page. Linked rather than inlined:
# rooms share one cached file, and the shell should stay light in front of a
# player that is about to pull down a whole prototype.
FONT_DIR = os.path.join(ROOT, 'assets', 'font')
os.makedirs(FONT_DIR, exist_ok=True)
for src, dst in (('f4.woff2', 'is-latin.woff2'), ('f5.woff2', 'is-latinext.woff2')):
    shutil.copyfile(os.path.join(HERE, 'assets', src), os.path.join(FONT_DIR, dst))

SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Elif Beyza Uysal</title>
<meta name="description" content="{sub} — a clickable prototype by Elif Beyza Uysal.">
<meta property="og:title" content="{title} · Elif Beyza Uysal">
<meta property="og:description" content="{sub} — a clickable prototype.">
<link rel="canonical" href="https://elifbeyzauysal.com/demo/{key}/">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%201%201'%3E%3C/svg%3E">
<style>
@font-face{{font-family:'Instrument Sans';src:url(/assets/font/is-latin.woff2) format('woff2');
  font-weight:400 700;font-display:swap;
  unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}}
@font-face{{font-family:'Instrument Sans';src:url(/assets/font/is-latinext.woff2) format('woff2');
  font-weight:400 700;font-display:swap;
  unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF}}
/* Dark, not the site's cream — the near-black of Elif's case studies. What is
   inside the stage is somebody else's product at full brightness, and cream
   around it reads as two papers fighting; the lights-down room lets the screen
   be the only lit thing. It also covers the player's own ground, which is
   near-black and cannot be changed: `bg=` works on a share link and is
   ignored on embed.figma.com. */
*{{box-sizing:border-box}}
html,body{{height:100%}}
body{{margin:0;display:flex;flex-direction:column;background:#0F1115;color:#F3EFE7;
  font:400 15px/1.4 'Instrument Sans',system-ui,sans-serif;-webkit-font-smoothing:antialiased}}
.bar{{display:flex;align-items:center;gap:18px;padding:14px clamp(14px,3vw,26px);
  border-bottom:1px solid rgba(243,239,231,.12);flex:0 0 auto}}
a{{color:inherit;text-decoration:none}}
.back{{display:inline-flex;align-items:center;gap:8px;font-size:14.5px;color:#A9A49B;
  padding:6px 12px 6px 9px;margin-left:-9px;border-radius:999px;
  transition:background .18s ease,color .18s ease}}
.back:hover{{background:rgba(243,239,231,.07);color:#F3EFE7}}
.who{{display:flex;align-items:baseline;gap:10px;margin-left:auto;margin-right:auto}}
.who b{{font-weight:600;letter-spacing:-.01em}}
.who span{{color:#77726A;font-size:14px}}
.ext{{font-size:14px;color:#A9A49B;border-bottom:1px solid rgba(243,239,231,.2);padding-bottom:1px}}
.ext:hover{{color:#FF7643;border-color:#FF7643}}
/* the player carries its own ground, so the frame around it is one hairline */
.stage{{flex:1 1 auto;min-height:0;position:relative;background:#0F1115}}
iframe{{position:absolute;inset:0;width:100%;height:100%;border:0}}
.note{{flex:0 0 auto;padding:9px clamp(14px,3vw,26px);font-size:13px;color:#77726A;
  border-top:1px solid rgba(243,239,231,.07)}}
.note a{{color:#A9A49B;border-bottom:1px solid rgba(243,239,231,.2)}}
.note a:hover{{color:#FF7643;border-color:#FF7643}}
.hint{{display:none}}
/* A 1440-wide screen fitted to a phone is a strip of postage stamps floating
   in the middle of a tall black stage. The player will not scale past the
   width, so instead the stage stops pretending to be full height: it takes
   exactly the frame's ratio, the dead black collapses, and the note says out
   loud what the visitor is looking at. */
@media (max-width:900px){{
  .stage{{flex:0 0 auto;aspect-ratio:1440/900}}
  .hint{{display:inline}}
}}
@media (max-width:640px){{ .who span{{display:none}} .ext{{display:none}} }}
</style>
{beacon}
</head>
<body>
<header class="bar">
  <a class="back" href="/">&larr; Elif Beyza Uysal</a>
  <span class="who"><b>{brand}</b> <span>{sub}</span></span>
  <a class="ext" href="{proto}" target="_blank" rel="noopener noreferrer">Figma&rsquo;da a&ccedil; &#8599;</a>
</header>
<main class="stage">
  <iframe title="{title}" src="{embed}" allowfullscreen loading="eager"></iframe>
</main>
<p class="note">T&#305;klanabilir prototip.<span class="hint"> Masa&uuml;st&uuml; i&ccedil;in
  tasarland&#305;; geni&#351; ekranda okumas&#305; kolay.</span>
  Y&uuml;klenmiyorsa <a href="{proto}" target="_blank" rel="noopener noreferrer">Figma&rsquo;da a&ccedil;&#305;n</a>.</p>
</body>
</html>
"""

for d in DEMOS:
    embed, proto = urls(d)
    out = os.path.join(ROOT, 'demo', d['key'])
    os.makedirs(out, exist_ok=True)
    page = SHELL.format(key=d['key'], title=d['title'], sub=d['sub'],
                        brand=d['brand'], embed=embed, proto=proto, beacon=BEACON)
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(page)
    print(f"demo/{d['key']}/index.html  {len(page.encode())/1024:.1f} KB  → {d['file']} {d['node']}")
