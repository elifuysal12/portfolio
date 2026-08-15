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
import os, shutil
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'demo', 'alti')

# straight off the prototype's own share link (Present → Share prototype):
#   .../proto/<file>/<name>?node-id=<node>&page-id=<page>&starting-point-node-id=<start>
FILE_KEY = 'lgAW9lKNHrC3XFm7735tOq'
FILE_NAME = 'Commencis-I-Elif-Beyza-Uysal'
PAGE = '2510:1760'                     # the page the five flows live on
# Elif's choice: the room opens on flow 2, not flow 1. A visitor who lands here
# has not read anything yet, and flow 1 starts before the product does — this
# is the screen the app is actually about. `node-id` alone is not enough: it
# picks the frame, and the player still starts the flow at its own starting
# point, so both have to be said.
NODE = '3493-6819'
START = '3493:6819'

Q = (f'node-id={NODE}&page-id={quote(PAGE, safe="")}'
     f'&starting-point-node-id={quote(START, safe="")}'
     f'&scaling=scale-down-width&content-scaling=fixed')

EMBED = (f'https://embed.figma.com/proto/{FILE_KEY}/{FILE_NAME}?{Q}'
         f'&hide-ui=1&embed-host=elifbeyzauysal')
FIGMA = f'https://www.figma.com/proto/{FILE_KEY}/{FILE_NAME}?{Q}'

TITLE = 'ALTI — interactive prototype · Elif Beyza Uysal'
DESC = ('ALTI, a location-based cultural heritage app for Ankara — the wired '
        'prototype, five flows across 79 screens. By Elif Beyza Uysal.')

BEACON = ("<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"589b26a9898440e583a7272ff182a1e4\"}'></script>")
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'"
           "%20viewBox='0%200%201%201'%3E%3C/svg%3E")

# The room wears the site's own nav, so it needs the site's own two families
# as well as ALTI's Poppins. Linked rather than inlined, the way the other
# Figma room does it: the rooms share one cached copy, and a shell that is
# about to pull down a whole prototype should not carry 150 KB of base64 in
# front of it. (build_demo_figma.py writes the Instrument Sans pair too —
# same names, same bytes, so whichever runs last is fine.)
FONT_DIR = os.path.join(ROOT, 'assets', 'font')
os.makedirs(FONT_DIR, exist_ok=True)
for src, dst in (('f4.woff2', 'is-latin.woff2'), ('f5.woff2', 'is-latinext.woff2'),
                 ('f3.woff2', 'br-latin.woff2'), ('f1.woff2', 'br-latinext.woff2'),
                 ('poppins-400.woff2', 'po-400.woff2'),
                 ('poppins-400-ext.woff2', 'po-400-ext.woff2'),
                 ('poppins-700.woff2', 'po-700.woff2'),
                 ('poppins-700-ext.woff2', 'po-700-ext.woff2')):
    shutil.copyfile(os.path.join(HERE, 'assets', src), os.path.join(FONT_DIR, dst))

LATIN = ('U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,'
         'U+0304,U+0308,U+0329,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,'
         'U+2193,U+2212,U+2215,U+FEFF,U+FFFD')
LATIN_EXT = ('U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,'
             'U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,'
             'U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF')


def face(family, file, ur, weight='400'):
    return (f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weight};"
            f"font-display:swap;src:url(/assets/font/{file}) format('woff2');"
            f"unicode-range:{ur}}}")


FONTS = ''.join((
    face('Instrument Sans', 'is-latin.woff2', LATIN, '400 700'),
    face('Instrument Sans', 'is-latinext.woff2', LATIN_EXT, '400 700'),
    face('Bricolage Grotesque', 'br-latin.woff2', LATIN, '400 800'),
    face('Bricolage Grotesque', 'br-latinext.woff2', LATIN_EXT, '400 800'),
    face('Poppins', 'po-400.woff2', LATIN),
    face('Poppins', 'po-400-ext.woff2', LATIN_EXT),
    face('Poppins', 'po-700.woff2', LATIN, '700'),
    face('Poppins', 'po-700-ext.woff2', LATIN_EXT, '700'),
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

/* THE SITE'S OWN NAV, not a bar invented for this room. Same shape, same type,
   same order — carried into the dark exactly the way body.case-open carries it
   on a case study, so the demo reads as a room in her site rather than a page
   that happens to link back to it. The section links point at the home page
   because this is a separate address: /#work, /cv/, /#contact. */
nav{{
  position:fixed; top:18px; left:50%; transform:translateX(-50%);
  z-index:50; display:flex; align-items:center; gap:6px;
  padding:7px 8px 7px 18px; border-radius:16px;
  background:rgba(16,26,72,.72); backdrop-filter:blur(14px) saturate(1.3);
  border:1px solid rgba(255,255,255,.12); box-shadow:0 6px 24px rgba(0,0,0,.34);
}}
nav .mark{{font-family:'Bricolage Grotesque',system-ui,sans-serif;font-weight:800;font-size:15px;
  letter-spacing:-.02em;margin-right:14px;color:#fff;text-decoration:none;padding:0;
  border-radius:0;background:none;transition:opacity .25s ease}}
nav a.mark:hover{{background:none;opacity:.6}}
nav .mark i{{color:var(--pink);font-style:normal}}
nav a{{
  font-family:'Instrument Sans',system-ui,sans-serif; font-size:11px; letter-spacing:.01em;
  color:#B7BFE8; text-decoration:none; padding:8px 12px; border-radius:10px;
  transition:background .25s ease,color .25s ease;
}}
nav a:hover{{background:rgba(255,255,255,.09); color:#fff}}
.lang{{display:flex;gap:2px;margin-left:8px;padding:3px;border-radius:11px;background:rgba(255,255,255,.08)}}
.lang button{{
  font-family:'Instrument Sans',system-ui,sans-serif;font-size:12.5px;letter-spacing:.01em;
  border:0;cursor:pointer;padding:5px 9px;border-radius:8px;background:transparent;
  color:#8E97CF;transition:.3s cubic-bezier(.34,1.4,.5,1);
}}
.lang button.on{{background:#fff;color:#0A1551}}

/* THE PHONE GETS THE MIDDLE TO ITSELF. Stacking the copy and the controls
   under it cost the prototype 190px of height on every screen — on a page
   that is mostly empty either side of a 393px-wide object. So: three columns,
   words on the left, controls on the right, and the phone as tall as the
   window will allow. Collapses back to the stack when the columns would start
   squeezing it (below ~1000px). */
main{{flex:1; display:grid; grid-template-columns:1fr auto 1fr; align-items:center;
  gap:clamp(20px,3.4vw,56px);
  padding:clamp(58px,8vh,78px) clamp(16px,4vw,40px) clamp(10px,2vh,20px)}}
.side{{max-width:34ch}}
.side.left{{justify-self:end}}      /* hugs the phone, but the copy stays ragged-right */
.side.right{{justify-self:start}}
.room b{{display:block; font-family:'Bricolage Grotesque',system-ui,sans-serif;
  font-weight:800; font-size:26px; letter-spacing:.24em; color:#fff}}
.room span{{display:block; margin-top:6px; font-size:12px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--dim)}}

/* the room's own three controls — out of the bar, which belongs to the site
   now, and off the stack, which belongs to the phone */
.acts{{display:flex; flex-direction:column; align-items:flex-start; gap:9px}}
.acts a,.acts button{{
  font-family:inherit; font-size:13px; color:#D7DCF5; text-decoration:none; cursor:pointer;
  border:1px solid rgba(255,255,255,.16); background:transparent; border-radius:999px;
  padding:9px 16px; transition:color .2s ease,border-color .2s ease,background .2s ease;
}}
.acts a:hover,.acts button:hover{{color:#fff; border-color:rgba(255,255,255,.42); background:rgba(255,255,255,.06)}}

/* the shell is sized off the frame ratio, so `contain` lands at 1:1 and the
   whole thing shrinks together instead of the player letterboxing itself */
.phone{{
  position:relative; aspect-ratio:393/852;
  height:min(852px, calc(100dvh - 186px), calc((100vw - 40px) * 852 / 393));
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

.hint{{margin:18px 0 0; font-size:14px; line-height:1.65; color:var(--dim)}}
.hint b{{font-weight:400; color:#fff}}

footer{{padding:0 clamp(16px,4vw,40px) 20px; text-align:center;
  font-size:12px; line-height:1.7; color:rgba(142,151,207,.8)}}
footer a{{color:rgba(142,151,207,.8)}}

/* below this the side columns would start eating the phone, which is the one
   thing the layout exists to protect — so they go back under it */
@media (max-width:1000px){{
  main{{grid-template-columns:1fr; justify-items:center; gap:clamp(14px,2.4vh,20px);
    padding-top:clamp(64px,9vh,84px)}}
  .side{{max-width:48ch; text-align:center; justify-self:center}}
  .room{{display:none}}                 /* the phone says ALTI by itself */
  .hint{{margin-top:0}}
  .acts{{flex-direction:row; flex-wrap:wrap; justify-content:center; align-items:center}}
  .phone{{height:min(852px, calc(100dvh - 330px), calc((100vw - 40px) * 852 / 393))}}
}}
@media (max-width:560px){{
  nav{{padding-left:14px}} nav a{{padding:8px 9px}}
}}
@media (prefers-reduced-motion:reduce){{
  .wait svg{{animation:none}}
}}
</style>
{BEACON}
</head>
<body>

<nav>
  <a class="mark" href="https://elifbeyzauysal.com/" aria-label="Elif Uysal — home">elif<i>.</i></a>
  <a href="https://elifbeyzauysal.com/#work" data-i18n="work">Work</a>
  <a href="https://elifbeyzauysal.com/cv/" data-i18n="about">About</a>
  <a href="https://elifbeyzauysal.com/#contact" data-i18n="contact">Contact</a>
  <span class="lang"><button data-lang="en" class="on">EN</button><button data-lang="tr">TR</button></span>
</nav>

<main>
  <div class="side left">
    <p class="room"><b>ALTI</b><span data-i18n="sub">Ankara · on foot</span></p>
    <p class="hint" data-i18n-html="hint">This is the real thing, not a video.
       <b>Tap the screen to move.</b> Wander, Gather and Capsule are all wired —
       79 screens, five flows.</p>
  </div>

  <div class="phone">
    <div class="wait" id="wait">
      <svg viewBox="0 0 60 60" fill="none" aria-hidden="true">
        <path d="M30 8C20.6 8 13 15.6 13 25c0 11.7 17 27 17 27s17-15.3 17-27C47 15.6 39.4 8 30 8Z"
              fill="url(#g)"/>
        <circle cx="30" cy="24.5" r="6" fill="#0A1551"/>
        <defs><linearGradient id="g" x1="13" y1="30" x2="47" y2="30" gradientUnits="userSpaceOnUse">
          <stop stop-color="#FF557B"/><stop offset="1" stop-color="#FF751D"/></linearGradient></defs>
      </svg>
      <span data-i18n="loading">Loading the prototype</span>
    </div>
    <iframe id="proto" title="ALTI — interactive prototype"
            src="{EMBED}" allowfullscreen loading="eager"></iframe>
  </div>

  <div class="side right">
    <p class="acts">
      <button type="button" id="restart" data-i18n="restart">Start over</button>
      <a href="{FIGMA}" target="_blank" rel="noopener noreferrer" data-i18n="figma">Open in Figma</a>
      <a href="https://elifbeyzauysal.com/case/alti/" data-i18n="case">Read the case study</a>
    </p>
  </div>
</main>

<footer data-i18n-html="foot">
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

/* The nav carries the site's language switch, so it has to actually switch.
   The room is a dozen words, so this is the whole of it — no persistence,
   which is what the site does too (it opens in English every time). */
const CREDIT = '<a href="https://elifbeyzauysal.com/">Elif Beyza Uysal</a>';
const T = {{
  en:{{
    work:'Work', about:'About', contact:'Contact', sub:'Ankara · on foot',
    loading:'Loading the prototype', restart:'Start over',
    figma:'Open in Figma', case:'Read the case study',
    hint:'This is the real thing, not a video. <b>Tap the screen to move.</b> '+
         'Wander, Gather and Capsule are all wired — 79 screens, five flows.',
    foot:'ALTI — a location-based cultural heritage app for Ankara.<br>'+
         'Concept and design by '+CREDIT+' · graduation project with Commencis.'
  }},
  tr:{{
    work:'İşler', about:'Hakkında', contact:'İletişim', sub:'Ankara, yürüyerek',
    loading:'Prototip yükleniyor', restart:'Baştan başlat',
    figma:'Figma\\u2019da aç', case:'Case study\\u2019yi oku',
    hint:'Bu videosu değil, kendisi. <b>İlerlemek için ekrana dokun.</b> '+
         'Wander, Gather ve Capsule\\u2019ün üçü de bağlı — 79 ekran, beş akış.',
    foot:'ALTI — Ankara için konum tabanlı bir kültürel miras uygulaması.<br>'+
         'Konsept ve tasarım: '+CREDIT+' · Commencis ile bitirme projesi.'
  }}
}};
function setLang(l){{
  document.documentElement.lang = l;
  document.querySelectorAll('[data-i18n]').forEach(e => e.textContent = T[l][e.dataset.i18n]);
  document.querySelectorAll('[data-i18n-html]').forEach(e => e.innerHTML = T[l][e.dataset.i18nHtml]);
  document.querySelectorAll('.lang button').forEach(b => b.classList.toggle('on', b.dataset.lang === l));
}}
document.querySelectorAll('.lang button').forEach(b =>
  b.addEventListener('click', () => setLang(b.dataset.lang)));
</script>
</body>
</html>
"""

os.makedirs(OUT, exist_ok=True)
page = os.path.join(OUT, 'index.html')
open(page, 'w', encoding='utf-8').write(PAGE)
print(f'{os.path.relpath(page, ROOT)}  {len(PAGE.encode())/1024:.0f} KB'
      f'  + assets/font (shared, cached)')
