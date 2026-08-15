#!/usr/bin/env python3
"""Build the base360 landing prototype into ../demo/base360/, on Elif's domain.

The same move as build_demo.py makes for NORE: the prototype itself is the
demo, running, not a picture of one and not a Figma player in a frame. This one
is already a single self-contained file — no external requests, no images to
copy — so the build is a head, a credit line and the beacon.

    python3 src/build_demo_base360.py [path-to-prototype]

Re-run it whenever the prototype changes; the output is committed.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.abspath(sys.argv[1] if len(sys.argv) > 1
                      else os.path.join(ROOT, '..', 'base360-journey.html'))
OUT = os.path.join(ROOT, 'demo', 'base360')

if not os.path.isfile(SRC):
    sys.exit(f'prototype not found: {SRC}')
html = open(SRC, encoding='utf-8').read()

# the prototype's <title> sits in the <body> — harmless in a browser, but this
# page is now a real address with a real head, so it moves up where it belongs
BODY_TITLE = '<title>Base360 — Own the conversation</title>\n'
if BODY_TITLE not in html:
    sys.exit('the stray body <title> moved — check the prototype')
html = html.replace(BODY_TITLE, '', 1)

# it is her work, so it is signed — the demo is reached from her portfolio and
# should say whose it is without breaking the page's own fiction
CREDIT = ('<span>© 2026 Base360 — the social commerce superapp'
          ' · concept and design by Elif Beyza Uysal</span>')
OLD = '<span>© 2026 Base360 — the social commerce superapp</span>'
if OLD not in html:
    sys.exit('the footer line moved — check the prototype')
html = html.replace(OLD, CREDIT, 1)

# the same cookieless beacon the site carries, so a visit to the demo shows up
# as its own page rather than disappearing off the end of the funnel
BEACON = ("<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"589b26a9898440e583a7272ff182a1e4\"}'></script>")
TITLE = 'base360 — live prototype · Elif Beyza Uysal'
DESC = ('A landing page redesign for base360, the social commerce superapp — '
        'the running prototype, by Elif Beyza Uysal.')
HEAD = (f'<title>{TITLE}</title>\n'
        f'<meta name="description" content="{DESC}">\n'
        f'<meta property="og:title" content="{TITLE}">\n'
        f'<meta property="og:description" content="{DESC}">\n'
        '<meta property="og:type" content="website">\n'
        '<link rel="canonical" href="https://elifbeyzauysal.com/demo/base360/">\n'
        # no tab icon, as on the site: the title carries the tab
        "<link rel=\"icon\" href=\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'"
        "%20viewBox='0%200%201%201'%3E%3C/svg%3E\">\n"
        f'{BEACON}\n</head>')
html = html.replace('</head>', HEAD, 1)

os.makedirs(OUT, exist_ok=True)
page = os.path.join(OUT, 'index.html')
open(page, 'w', encoding='utf-8').write(html)
print(f'{os.path.relpath(page, ROOT)}  {len(html.encode())/1024:.0f} KB  (one file, no requests)')
