#!/usr/bin/env python3
"""Build the portfolio into one self-contained page.

Two outputs, same HTML body:
  ../index.html                 → what GitHub Pages serves (carries its own <head>)
  ../dist/portfolio-artifact.html → what gets published as a Claude Artifact
                                    (the host supplies the <head> there)

Everything is inlined as data: URIs — fonts, the character, the case screens —
so the site is a single file with no external requests.
"""
import base64, mimetypes, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
b64 = lambda p: base64.b64encode(open(os.path.join(HERE, p), 'rb').read()).decode()

SUB = {
    '{{F_BRIC_LATIN}}':    b64('assets/f3.woff2'),   # Bricolage Grotesque — latin
    '{{F_BRIC_LATINEXT}}': b64('assets/f1.woff2'),   # Bricolage Grotesque — latin-ext (TR)
    '{{F_IS_LATIN}}':      b64('assets/f4.woff2'),   # Instrument Sans — latin
    '{{F_IS_LATINEXT}}':   b64('assets/f5.woff2'),   # Instrument Sans — latin-ext (TR)
    '{{IMG_BUST}}':        b64('assets/bust_q92.webp'),
}

html = open(os.path.join(HERE, 'portfolio-artifact.tmpl.html'), encoding='utf-8').read()
for k, v in SUB.items():
    if k not in html:
        sys.exit(f'placeholder missing: {k}')
    html = html.replace(k, v)

# {{ASSET:case/s1.webp}} resolves differently per output:
#
#   the hosted site  → a real file under assets/, copied next to index.html.
#     Case screens are 4× Figma exports; inlining them would put a megabyte of
#     base64 in front of the first paint for a page most visitors never open.
#     As files they are lazy, cacheable, and can stay at full resolution.
#
#   the Artifact copy → a data: URI, because the Artifact CSP blocks every
#     external host. Same full-resolution files: a compact re-encode kept the
#     page under the share-size ceiling but read as soft, which is the one
#     thing these screens cannot be. Publishing is fine up to ~2.3 MB; a page
#     this size may refuse to produce a share link, and the shareable address
#     is the domain anyway.


def inline(m):
    rel = os.path.join('assets', m.group(1))
    path = os.path.join(HERE, rel)
    if not os.path.exists(path):
        sys.exit(f'asset missing: {rel}')
    mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    data = base64.b64encode(open(path, 'rb').read()).decode()
    return f'data:{mime};base64,{data}'


def linked(m):
    rel = m.group(1)                       # e.g. case/s1.webp
    if not os.path.exists(os.path.join(HERE, 'assets', rel)):
        sys.exit(f'asset missing: assets/{rel}')
    # root-relative, not relative: the same markup is served from /, /cv/ and
    # /case/cursor/, and a relative path would look for the screens inside the
    # route folder. Ties the site to the domain root, which is where it lives.
    return f'/assets/{rel}'


artifact_html, n = re.subn(r'\{\{ASSET:([^}]+)\}\}', inline, html)
html, _ = re.subn(r'\{\{ASSET:([^}]+)\}\}', linked, html)

# The sheets get real addresses on the hosted copy (see ROUTES in the template).
# In the Artifact the URL belongs to the host, so the whole thing stays off.
artifact_html = artifact_html.replace('{{ROUTES}}', 'false')
html = html.replace('{{ROUTES}}', 'true')

os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
artifact = os.path.join(ROOT, 'dist', 'portfolio-artifact.html')
open(artifact, 'w', encoding='utf-8').write(artifact_html)

# the linked copies, next to index.html
copied = []
for sub in ('case', 'cover', 'alti'):         # case screens, cover shots, ALTI
    src_dir = os.path.join(HERE, 'assets', sub)
    if not os.path.isdir(src_dir):
        continue
    dst = os.path.join(ROOT, 'assets', sub)
    os.makedirs(dst, exist_ok=True)
    for f in sorted(os.listdir(src_dir)):
        if f.endswith('.webp'):
            shutil.copyfile(os.path.join(src_dir, f), os.path.join(dst, f))
            copied.append(os.path.join(dst, f))

# --- the hosted copy ---
# On a plain web server nobody supplies a <head>: without the charset the em
# dashes and Turkish characters arrive as mojibake, and without the viewport
# tag phones render the page at 980px.
# No tab icon: the title carries the tab. An empty SVG rather than no <link> at
# all — drop the link and the browser goes looking for /favicon.ico, misses, and
# falls back to its own generic page glyph, which is the thing being removed.
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'"
           "%20viewBox='0%200%201%201'%3E%3C/svg%3E")
DESC = ('Elif Uysal — product designer. Selected work, the CV, '
        'and the Cursor Assistant case study.')

# Cloudflare Web Analytics. The token is a public site tag, not a secret — it
# ships in every visitor's page source. Cookieless, so the site needs no consent
# banner, and it follows the History API, which is what makes the routes below
# worth having: /case/cursor shows up as its own page rather than as one more
# hit on the home page.
BEACON = ("<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
          "data-cf-beacon='{\"token\": \"589b26a9898440e583a7272ff182a1e4\"}'></script>")


def wrap(body, title, desc, open_attr='', canonical='/'):
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>{title}</title>\n'
        f'<meta name="description" content="{desc}">\n'
        f'<meta property="og:title" content="{title}">\n'
        f'<meta property="og:description" content="{desc}">\n'
        '<meta property="og:type" content="website">\n'
        f'<link rel="canonical" href="https://elifbeyzauysal.com{canonical}">\n'
        f'<link rel="icon" href="{FAVICON}">\n'
        '<style>:root{color-scheme:light}body{margin:0;padding:0}img{max-width:100%}</style>\n'
        f'{BEACON}\n'
        f'</head>\n<body{open_attr}>\n' + body + '\n</body>\n</html>\n')


# the template opens with a <title> because the Artifact host supplies the head
# and that is the only way to name the tab there. Here the head is ours, and a
# second title in the body is one a crawler could pick over the right one.
html = html.replace('<title>Elif Uysal — Product Designer</title>\n', '', 1)

index = os.path.join(ROOT, 'index.html')
open(index, 'w', encoding='utf-8').write(
    wrap(html, 'Elif Uysal — Product Designer', DESC))

# One real file per sheet address, so a shared link survives a cold load: the
# same page, told on <body> which sheet to open. A 404.html catches the rest —
# GitHub Pages serves it for anything unknown, and it walks people home rather
# than leaving them on GitHub's own error page.
ROUTE_PAGES = [
    ('case/cursor', 'case:cursor', 'Cursor Assistant — Elif Uysal',
     'An assistant that speaks up when you need it. Not from a window — from '
     'the cursor. A case study by Elif Uysal.'),
    ('case/whallet', 'case:whallet', 'Whallet — Elif Uysal',
     'A crypto wallet that answers the two questions that make people leave one: '
     'what just happened, and is this token real? A case study by Elif Uysal.'),
    ('case/alti', 'case:alti', 'ALTI — Elif Uysal',
     'A city that tells its own story — not from a museum label, from the '
     'streets you pass. ALTI, a location-based cultural heritage app for '
     'Ankara. A case study by Elif Uysal.'),
    ('cv', 'cv', 'CV — Elif Uysal',
     'Elif Uysal — product designer. Experience, education and what she works with.'),
]
for path, opens, title, desc in ROUTE_PAGES:
    d = os.path.join(ROOT, path)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(
        wrap(html, title, desc, f' data-open="{opens}"', f'/{path}/'))

open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8').write(
    wrap(html, 'Elif Uysal — Product Designer', DESC))

shot = sum(os.path.getsize(f) for f in copied)
print(f'index.html                   {os.path.getsize(index)/1024:.0f} KB'
      f'  + assets {shot/1024:.0f} KB ({n} images)')
print('routes                       ' + ', '.join('/%s/' % p for p, *_ in ROUTE_PAGES) + ', 404.html')
print(f'dist/portfolio-artifact.html {len(artifact_html.encode())/1024:.0f} KB  (screens inlined at full resolution)')
