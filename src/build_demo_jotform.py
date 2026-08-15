#!/usr/bin/env python3
"""Build the Jotform chatbot dashboard demo into ../demo/jotform/.

Two files, because this demo is a *desktop* product:

    demo/jotform/app/index.html   the prototype itself, untouched
    demo/jotform/index.html       the room: Elif's bar, and a monitor with the
                                  prototype running inside it

    python3 src/build_demo_jotform.py [path-to-prototype]

Why a monitor at all. The prototype is a 1440-wide WordPress admin screen. Let
it reflow into a portfolio-sized window and it stops being the thing it is —
the two-column cards stack, the sidebar goes, and what people see is a
responsive page rather than the dashboard as it ships. So the room holds the
page at its own 1440×900 and scales the whole screen down to fit, the way a
photograph of a monitor would, except that this one is live: every chart, tab
and modal still works at any size.

That is also the reason the frame is a frame and not a picture. This replaced a
Figma embed — a player behind someone else's chrome — after Elif asked for a
demo that actually runs.
"""
import os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.abspath(sys.argv[1] if len(sys.argv) > 1
                      else os.path.join(ROOT, '..', 'jotform-dashboard', 'index.html'))
OUT = os.path.join(ROOT, 'demo', 'jotform')

if not os.path.isfile(SRC):
    sys.exit(f'prototype not found: {SRC}')
app = open(SRC, encoding='utf-8').read()

# The prototype is the product's own screen, so it carries no credit line and
# no beacon: it lives inside the room's frame, and a second beacon on the same
# visit would count one person twice.
APP_HEAD = (
    '<link rel="canonical" href="https://elifbeyzauysal.com/demo/jotform/">\n'
    "<link rel=\"icon\" href=\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'"
    "%20viewBox='0%200%201%201'%3E%3C/svg%3E\">\n</head>")
app = app.replace('</head>', APP_HEAD, 1)

BEACON = ("<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"589b26a9898440e583a7272ff182a1e4\"}'></script>")
TITLE = 'Chatbot Dashboard — live prototype · Elif Beyza Uysal'
DESC = ('An analytics dashboard for Jotform AI Chatbot, embedded in WordPress — '
        'the running prototype, by Elif Beyza Uysal.')

ROOM = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="canonical" href="https://elifbeyzauysal.com/demo/jotform/">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%201%201'%3E%3C/svg%3E">
<style>
@font-face{{font-family:'Instrument Sans';src:url(/assets/font/is-latin.woff2) format('woff2');
  font-weight:400 700;font-display:swap;
  unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}}
@font-face{{font-family:'Instrument Sans';src:url(/assets/font/is-latinext.woff2) format('woff2');
  font-weight:400 700;font-display:swap;
  unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF}}
*{{box-sizing:border-box}}
html,body{{height:100%}}
/* The room is dark for the same reason a screening room is: the only lit thing
   should be the screen. Elif's case-study near-black, not the site's cream. */
body{{margin:0;display:flex;flex-direction:column;background:#0F1115;color:#F3EFE7;
  font:400 15px/1.4 'Instrument Sans',system-ui,sans-serif;-webkit-font-smoothing:antialiased;
  overflow:hidden}}
a{{color:inherit;text-decoration:none}}
.bar{{display:flex;align-items:center;gap:18px;padding:14px clamp(14px,3vw,26px);
  border-bottom:1px solid rgba(243,239,231,.12);flex:0 0 auto;z-index:2}}
.back{{display:inline-flex;align-items:center;gap:8px;font-size:14.5px;color:#A9A49B;
  padding:6px 12px 6px 9px;margin-left:-9px;border-radius:999px;
  transition:background .18s ease,color .18s ease}}
.back:hover{{background:rgba(243,239,231,.07);color:#F3EFE7}}
.who{{display:flex;align-items:baseline;gap:10px;margin-left:auto;margin-right:auto}}
.who b{{font-weight:600;letter-spacing:-.01em}}
.who span{{color:#77726A;font-size:14px}}
.ext{{font-size:14px;color:#A9A49B;border-bottom:1px solid rgba(243,239,231,.2);padding-bottom:1px}}
.ext:hover{{color:#FF7643;border-color:#FF7643}}

/* ---- the desk ---- */
.stage{{flex:1 1 auto;min-height:0;position:relative;display:flex;flex-direction:column;
  align-items:center;justify-content:center;padding:26px 22px 18px}}
/* one cool pool of light behind the monitor, so the frame has something to sit in */
.stage:before{{content:'';position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(58% 62% at 50% 42%, rgba(94,142,255,.13), rgba(15,17,21,0) 70%)}}

.rig{{position:relative;display:flex;flex-direction:column;align-items:center}}
/* the bezel: dark aluminium, a hair lighter at the top edge where light lands */
.mon{{
  position:relative;padding:14px 14px 30px;border-radius:20px;
  background:linear-gradient(#33363F,#1C1E24 22%,#16181D);
  box-shadow:0 1px 0 rgba(255,255,255,.16) inset, 0 0 0 1px #0A0B0E,
             0 40px 70px -28px rgba(0,0,0,.85), 0 8px 24px rgba(0,0,0,.5);
}}
.screen{{position:relative;border-radius:7px;overflow:hidden;background:#F0F0F1;
  box-shadow:0 0 0 1px rgba(0,0,0,.55) inset}}
.screen iframe{{position:absolute;top:0;left:0;width:1440px;height:900px;border:0;
  transform-origin:top left;background:#F0F0F1}}
/* the power LED, the one thing on the chin */
.mon:after{{content:'';position:absolute;left:50%;bottom:13px;width:5px;height:5px;margin-left:-2.5px;
  border-radius:50%;background:#5EE38A;box-shadow:0 0 8px rgba(94,227,138,.75)}}
/* neck and foot, drawn rather than photographed so they stay crisp at any size */
.neck{{width:118px;height:52px;background:linear-gradient(90deg,#1A1C22,#2A2D35 42%,#15171C);
  clip-path:polygon(24% 0,76% 0,100% 100%,0 100%)}}
.foot{{width:280px;height:16px;border-radius:0 0 14px 14px;
  background:linear-gradient(#2A2D35,#15171C);
  box-shadow:0 22px 34px -18px rgba(0,0,0,.9)}}

.note{{flex:0 0 auto;padding:9px clamp(14px,3vw,26px);font-size:13px;color:#77726A;
  border-top:1px solid rgba(243,239,231,.07);z-index:2}}
.note a{{color:#A9A49B;border-bottom:1px solid rgba(243,239,231,.2)}}
.note a:hover{{color:#FF7643;border-color:#FF7643}}
.hintnarrow{{display:none}}

/* On a phone the monitor is theatre nobody can read: the desk goes away, the
   screen keeps the page's own 16:10 and the way out is the full-screen link. */
@media (max-width:820px){{
  body{{overflow:auto}}
  .stage{{padding:14px 10px 10px;justify-content:flex-start}}
  .mon{{padding:7px 7px 7px;border-radius:12px}}
  .mon:after{{display:none}}
  .neck,.foot{{display:none}}
  .who span,.ext{{display:none}}
  .hintnarrow{{display:inline}}
}}
</style>
{beacon}
</head>
<body>
<header class="bar">
  <a class="back" href="/">&larr; Elif Beyza Uysal</a>
  <span class="who"><b>Chatbot Dashboard</b> <span>Jotform &middot; analytics dashboard</span></span>
  <a class="ext" href="app/" target="_blank" rel="noopener">Tam ekranda a&ccedil; &#8599;</a>
</header>

<main class="stage">
  <div class="rig" id="rig">
    <div class="mon">
      <div class="screen" id="screen">
        <iframe id="app" src="app/" title="Jotform AI Chatbot — Analytics"
                loading="eager" scrolling="yes"></iframe>
      </div>
    </div>
    <div class="neck"></div>
    <div class="foot"></div>
  </div>
</main>

<p class="note">&Ccedil;al&#305;&#351;an prototip &mdash; sekmeleri, grafikleri ve
  kartlar&#305; deneyebilirsin.<span class="hintnarrow"> Telefonda k&uuml;&ccedil;&uuml;k kal&#305;yor:
  <a href="app/">tam ekranda a&ccedil;</a>.</span></p>

<script>
/* The page inside is a 1440x900 desktop screen and stays one: it is scaled as
   a whole, never reflowed, so what a visitor drives is the dashboard as it
   ships rather than a narrow version of it. */
(function(){{
  var W=1440, H=900, screen=document.getElementById('screen'),
      app=document.getElementById('app'), rig=document.getElementById('rig'),
      stage=document.querySelector('.stage'), mon=document.querySelector('.mon');
  function fit(){{
    var narrow = innerWidth<=820;
    var padX = narrow?34:76;                       // bezel + breathing room
    var chrome = narrow?30:150;                    // bezel chin + neck + foot
    var availW = stage.clientWidth - padX;
    var availH = stage.clientHeight - chrome;
    var k = Math.min(availW/W, availH/H);
    if(narrow) k = availW/W;                       // width decides; the desk is gone
    k = Math.max(.18, Math.min(k, 1));
    screen.style.width  = Math.round(W*k)+'px';
    screen.style.height = Math.round(H*k)+'px';
    app.style.transform = 'scale('+k+')';
  }}
  fit();
  addEventListener('resize', fit);
  addEventListener('orientationchange', fit);
}})();
</script>
</body>
</html>
"""

# The room's bar is set in the site's own type. Linked rather than inlined:
# the demo rooms share one cached copy, and a shell about to load a whole
# prototype should not carry 150 KB of base64 in front of it. Written here as
# well as by the other demo builds, so this one stands on its own.
FONT_DIR = os.path.join(ROOT, 'assets', 'font')
os.makedirs(FONT_DIR, exist_ok=True)
for src, dst in (('f4.woff2', 'is-latin.woff2'), ('f5.woff2', 'is-latinext.woff2')):
    shutil.copyfile(os.path.join(HERE, 'assets', src), os.path.join(FONT_DIR, dst))

os.makedirs(os.path.join(OUT, 'app'), exist_ok=True)
open(os.path.join(OUT, 'app', 'index.html'), 'w', encoding='utf-8').write(app)
room = ROOM.format(title=TITLE, desc=DESC, beacon=BEACON)
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(room)

print(f'demo/jotform/app/index.html  {len(app.encode())/1024:.0f} KB  (the prototype, no requests)')
print(f'demo/jotform/index.html      {len(room.encode())/1024:.0f} KB  (the room: bar + monitor)')
