#!/usr/bin/env python3
"""Build the portfolio into one self-contained page.

Two outputs, same HTML body:
  ../index.html                 → what GitHub Pages serves (carries its own <head>)
  ../dist/portfolio-artifact.html → what gets published as a Claude Artifact
                                    (the host supplies the <head> there)

Everything is inlined as data: URIs — fonts, the character, the case screens —
so the site is a single file with no external requests.
"""
import base64, mimetypes, os, re, sys

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

# {{ASSET:case/s1.webp}} → a full data: URI, so a new screen only needs
# dropping into src/assets and referencing by path
def asset(m):
    rel = os.path.join('assets', m.group(1))
    path = os.path.join(HERE, rel)
    if not os.path.exists(path):
        sys.exit(f'asset missing: {rel}')
    mime = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    return f'data:{mime};base64,{b64(rel)}'

html, n = re.subn(r'\{\{ASSET:([^}]+)\}\}', asset, html)

os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
artifact = os.path.join(ROOT, 'dist', 'portfolio-artifact.html')
open(artifact, 'w', encoding='utf-8').write(html)

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

print(f'index.html                   {len(page.encode())/1024:.0f} KB  ({n} screens inlined)')
print(f'dist/portfolio-artifact.html {len(html.encode())/1024:.0f} KB')
