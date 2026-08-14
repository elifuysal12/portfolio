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
    return f'assets/{rel}'


artifact_html, n = re.subn(r'\{\{ASSET:([^}]+)\}\}', inline, html)
html, _ = re.subn(r'\{\{ASSET:([^}]+)\}\}', linked, html)

os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
artifact = os.path.join(ROOT, 'dist', 'portfolio-artifact.html')
open(artifact, 'w', encoding='utf-8').write(artifact_html)

# the linked copies, next to index.html
dst = os.path.join(ROOT, 'assets', 'case')
os.makedirs(dst, exist_ok=True)
for f in sorted(os.listdir(os.path.join(HERE, 'assets', 'case'))):
    if f.endswith('.webp'):
        shutil.copyfile(os.path.join(HERE, 'assets', 'case', f), os.path.join(dst, f))

# --- the hosted copy ---
# On a plain web server nobody supplies a <head>: without the charset the em
# dashes and Turkish characters arrive as mojibake, and without the viewport
# tag phones render the page at 980px.
FAVICON = ('data:image/svg+xml,'
           "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E"
           "%3Ctext y='.9em' font-size='90'%3E%F0%9F%8E%A8%3C/text%3E%3C/svg%3E")
DESC = ('Elif Uysal — product designer. Selected work, the CV, '
        'and the Cursor Assistant case study.')
page = (
    '<!doctype html>\n<html lang="en">\n<head>\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<title>Elif Uysal — Product Designer</title>\n'
    f'<meta name="description" content="{DESC}">\n'
    '<meta property="og:title" content="Elif Uysal — Product Designer">\n'
    f'<meta property="og:description" content="{DESC}">\n'
    '<meta property="og:type" content="website">\n'
    f'<link rel="icon" href="{FAVICON}">\n'
    '<style>:root{color-scheme:light}body{margin:0;padding:0}img{max-width:100%}</style>\n'
    '</head>\n<body>\n' + html + '\n</body>\n</html>\n')

index = os.path.join(ROOT, 'index.html')
open(index, 'w', encoding='utf-8').write(page)

shot = sum(os.path.getsize(os.path.join(dst, f)) for f in os.listdir(dst))
print(f'index.html                   {len(page.encode())/1024:.0f} KB'
      f'  + assets/case {shot/1024:.0f} KB ({n} screens)')
print(f'dist/portfolio-artifact.html {len(artifact_html.encode())/1024:.0f} KB  (screens inlined at full resolution)')
