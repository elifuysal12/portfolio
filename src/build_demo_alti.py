#!/usr/bin/env python3
"""Build the ALTI prototype room into ../demo/alti/.

Unlike NORE and base360, ALTI has no coded prototype to serve: it is a
79-screen mobile app whose five flows are wired in Figma, and rebuilding that
by hand would be a different project, not a demo. So this room runs Figma's
own player — with its chrome switched off (`hide-ui=1`), inside a device shell
in ALTI's colours, so what a visitor sees is the app running rather than a
file open in somebody's design tool.

There is a second Figma-backed room, build_demo_figma.py, and this is not it:
that one hands a 1440x900 dashboard a full-bleed dark stage. A phone is not a
stage — it is an object — so ALTI gets a device shell in its own navy, and the
two rooms stay separate on purpose. What they do share is the finding below.

Two things the player needs, both learned the hard way:

  * `scaling=scale-down-width` + `content-scaling=fixed`. `contain` is the
    obvious guess and it is wrong: the player fits the frame at roughly half
    size and rings it in black (measured first on the Jotform room). With
    scale-down-width the frame fills the width, and because the shell is cut
    to the frame's own 393:852 ratio the height lands exactly too — no
    letterbox, nothing to scroll.
  * the Figma file must be shared as *Anyone with the link · can view*. It is
    today — the file's thumbnail comes back to an anonymous request — but that
    is a setting on Elif's account, not something the build can hold in place,
    which is why the header keeps a visible way through to Figma.

    python3 src/build_demo_alti.py

Output is committed; re-run when the prototype's start point moves.
"""
import base64, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'demo', 'alti')

FILE_KEY = 'lgAW9lKNHrC3XFm7735tOq'
FILE_NAME = 'Commencis-I-Elif-Beyza-Uysal'
NODE = '2510-1760'                     # the section the five flows live in

EMBED = (f'https://embed.figma.com/proto/{FILE_KEY}/{FILE_NAME}'
         f'?node-id={NODE}&scaling=scale-down-width&content-scaling=fixed'
         f'&hide-ui=1&embed-host=elifbeyzauysal')
FIGMA = (f'https://www.figma.com/proto/{FILE_KEY}/{FILE_NAME}?node-id={NODE}')

TITLE = 'ALTI — interactive prototype · Elif Beyza Uysal'
DESC = ('ALTI, a location-based cultural heritage app for Ankara — the wired '
        'prototype, five flows across 79 screens. By Elif Beyza Uysal.')

BEACON = ("<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"589b26a9898440e583a7272ff182a1e4\"}'></script>")
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'"
           "%20viewBox='0%200%201%201'%3E%3C/svg%3E")

b64 = lambda p: base64.b64encode(open(os.path.join(HERE, 'assets', p), 'rb').read()).decode()

# Poppins is ALTI's own type, inlined the way the site inlines its own — the
# room makes no external request except the player it exists to hold.
FONTS = ''.join(
    f"@font-face{{font-family:Poppins;font-style:normal;font-weight:{w};font-display:swap;"
    f"src:url(data:font/woff2;base64,{b64(f'poppins-{w}{suf}.woff2')}) format('woff2');"
    f"unicode-range:{ur}}}"
    for w in (400, 700)
    for suf, ur in (
        ('', 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,'
             'U+0304,U+0308,U+0329,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,'
             'U+2193,U+2212,U+2215,U+FEFF,U+FFFD'),
        ('-ext', 'U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,'
                 'U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,'
                 'U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF'),
    ))

PAGE = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:type" content="website">
<link rel="canonical" href="https://elifbeyzauysal.com/demo/alti/">
<link rel="icon" href="{FAVICON}">
<style>
{FONTS}
*{{box-sizing:border-box}}
:root{{
  --navy:#0A1551; --navy-2:#050C33;
  --pink:#FF557B; --orange:#FF751D;
  --ramp:linear-gradient(96deg,#FF557B,#FF751D);
  --dim:#8E97CF;
}}
html,body{{height:100%}}
body{{
  margin:0; background:var(--navy-2); color:#fff;
  font-family:Poppins,system-ui,-apple-system,sans-serif;
  display:flex; flex-direction:column; min-height:100dvh;
  /* the same light source as the case study's gap band: warm, low, off to
     one side, so the phone sits in front of something rather than on black */
  background-image:
    radial-gradient(120% 90% at 12% 104%, rgba(255,85,123,.30), rgba(5,12,51,0) 62%),
    radial-gradient(90% 70% at 92% -8%, rgba(255,117,29,.20), rgba(5,12,51,0) 60%);
  background-attachment:fixed;
}}
a{{color:inherit}}
header{{
  display:flex; align-items:center; justify-content:space-between; gap:16px;
  flex-wrap:wrap; padding:18px clamp(16px,4vw,40px);
}}
.brand{{display:flex; align-items:baseline; gap:14px; min-width:0}}
.brand b{{font-weight:700; font-size:21px; letter-spacing:.26em}}
.brand span{{font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:var(--dim)}}
.links{{display:flex; align-items:center; gap:8px; flex-wrap:wrap}}
.links a,.links button{{
  font-family:inherit; font-size:13px; color:#D7DCF5; text-decoration:none; cursor:pointer;
  border:1px solid rgba(255,255,255,.16); background:transparent; border-radius:999px;
  padding:9px 16px; transition:color .2s ease,border-color .2s ease,background .2s ease;
}}
.links a:hover,.links button:hover{{color:#fff; border-color:rgba(255,255,255,.42); background:rgba(255,255,255,.06)}}

main{{flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center;
  gap:clamp(14px,2.4vh,22px); padding:4px clamp(16px,4vw,40px) clamp(10px,2vh,20px)}}

/* the shell is sized off the frame ratio, so `contain` lands at 1:1 and the
   whole thing shrinks together instead of the player letterboxing itself */
.phone{{
  position:relative; aspect-ratio:393/852;
  height:min(852px, calc(100dvh - 232px), calc((100vw - 40px) * 852 / 393));
  padding:2px; border-radius:34px; background-image:var(--ramp);
  box-shadow:0 40px 90px rgba(0,0,0,.55);
}}
.phone > *{{position:absolute; inset:2px; width:calc(100% - 4px); height:calc(100% - 4px);
  border:0; border-radius:32px; background:var(--navy)}}
iframe{{opacity:0; transition:opacity .5s ease}}
iframe.ready{{opacity:1}}

/* something to look at while the player boots — the app's own marker, not a
   spinner borrowed from somewhere else */
.wait{{display:flex; flex-direction:column; align-items:center; justify-content:center; gap:16px;
  font-size:12.5px; letter-spacing:.14em; text-transform:uppercase; color:var(--dim)}}
.wait svg{{width:44px; height:44px; animation:bob 1.9s cubic-bezier(.4,0,.5,1) infinite}}
@keyframes bob{{0%,100%{{transform:translateY(-4px)}}50%{{transform:translateY(4px)}}}}
.wait.gone{{opacity:0; pointer-events:none; transition:opacity .4s ease}}

.hint{{margin:0; font-size:13.5px; line-height:1.6; color:var(--dim); text-align:center; max-width:46ch}}
.hint b{{font-weight:400; color:#fff}}

footer{{padding:0 clamp(16px,4vw,40px) 20px; text-align:center;
  font-size:12px; line-height:1.7; color:rgba(142,151,207,.8)}}
footer a{{color:rgba(142,151,207,.8)}}

@media (max-width:560px){{
  .brand span{{display:none}}
  header{{padding-bottom:10px}}
}}
@media (prefers-reduced-motion:reduce){{
  .wait svg{{animation:none}}
}}
</style>
{BEACON}
</head>
<body>

<header>
  <span class="brand"><b>ALTI</b><span>Ankara · on foot</span></span>
  <span class="links">
    <button type="button" id="restart">Start over</button>
    <a href="{FIGMA}" target="_blank" rel="noopener noreferrer">Open in Figma</a>
    <a href="https://elifbeyzauysal.com/case/alti/">Read the case study</a>
  </span>
</header>

<main>
  <div class="phone">
    <div class="wait" id="wait">
      <svg viewBox="0 0 60 60" fill="none" aria-hidden="true">
        <path d="M30 8C20.6 8 13 15.6 13 25c0 11.7 17 27 17 27s17-15.3 17-27C47 15.6 39.4 8 30 8Z"
              fill="url(#g)"/>
        <circle cx="30" cy="24.5" r="6" fill="#0A1551"/>
        <defs><linearGradient id="g" x1="13" y1="30" x2="47" y2="30" gradientUnits="userSpaceOnUse">
          <stop stop-color="#FF557B"/><stop offset="1" stop-color="#FF751D"/></linearGradient></defs>
      </svg>
      Loading the prototype
    </div>
    <iframe id="proto" title="ALTI — interactive prototype"
            src="{EMBED}" allowfullscreen loading="eager"></iframe>
  </div>

  <p class="hint">This is the real thing, not a video. <b>Tap the screen to move.</b>
     Wander, Gather and Capsule are all wired — 79 screens, five flows.</p>
</main>

<footer>
  ALTI — a location-based cultural heritage app for Ankara.<br>
  Concept and design by <a href="https://elifbeyzauysal.com/">Elif Beyza Uysal</a> · graduation project with Commencis.
</footer>

<script>
const proto = document.getElementById('proto'), wait = document.getElementById('wait');
/* the player paints a while after `load`, so the shell is held a beat longer
   than the event — a hard swap shows a white frame */
proto.addEventListener('load', () => setTimeout(() => {{
  proto.classList.add('ready'); wait.classList.add('gone');
}}, 700));
/* hide-ui takes Figma's own restart away with the rest of the chrome, so the
   room supplies one: same src, fresh player, back at the starting point */
document.getElementById('restart').addEventListener('click', () => {{
  proto.classList.remove('ready'); wait.classList.remove('gone');
  proto.src = proto.src;
}});
</script>
</body>
</html>
"""

os.makedirs(OUT, exist_ok=True)
page = os.path.join(OUT, 'index.html')
open(page, 'w', encoding='utf-8').write(PAGE)
print(f'{os.path.relpath(page, ROOT)}  {len(PAGE.encode())/1024:.0f} KB'
      f'  (Poppins inlined; the player is the only request)')
