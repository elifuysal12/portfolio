"""Build isolated character previews from the committed portfolio page.

Run after src/build.py when the portfolio itself changes. Only this experiment's
files are written. Serve the worktree root to resolve existing /assets/ paths.
"""
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
source = (ROOT / "index.html").read_text()
variants = [
    ("01-clean-animation", "Clean animation",
     "Fine contours, simple eyes and a longer face. The closest to the animated scene references."),
    ("02-retro-toon", "Retro toon",
     "Rounder shapes and oversized eyes. A more playful, mascot-like presence."),
    ("03-pencil-pastel", "Pencil & pastel",
     "Visible strokes and irregular edges. More expressive up close; finer texture softens at small sizes."),
]

# Preview sheets stay on their own URL when opening/closing case studies.
preview = source.replace("const ROUTES = true;", "const ROUTES = false;")
preview = re.sub(
    r"<script\b[^>]*src=['\"]https://static\.cloudflareinsights\.com/[^>]*></script>",
    "", preview,
)
preview = preview.replace("</head>", '<meta name="robots" content="noindex,nofollow"></head>')
flat_mode = """<style>
html.flat-preview .grain,html.flat-preview .glow{display:none}
html.flat-preview #char img{filter:none}
</style><script>
if(new URLSearchParams(location.search).has('flat'))
  document.documentElement.classList.add('flat-preview');
</script>"""
preview = preview.replace("</head>", flat_mode + "</head>")

for slug, title, _ in variants:
    image = HERE / "assets" / f"{slug}.png"
    if not image.is_file():
        raise FileNotFoundError(image)
    page, count = re.subn(
        r'(<img id="charImg" src=")[^"]+',
        rf'\g<1>assets/{slug}.png',
        preview,
    )
    assert count == 1, "Expected one character swap point"
    page = re.sub(r"<title>.*?</title>", f"<title>Elif — {title}</title>", page)
    (HERE / f"{slug}.html").write_text(page)

(HERE / "00-original.html").write_text(preview)

# Reuse the exact compiled portfolio typography, tokens and component styling.
css = "\n".join(re.findall(r"<style>(.*?)</style>", source, re.S))
(HERE / "portfolio.css").write_text(css)

cards = []
for slug, title, description in variants:
    cards.append(f"""<article class="study">
  <a class="portrait" href="{slug}.html" aria-label="Open {title} portfolio preview">
    <img src="assets/{slug}.png" alt="Elif illustrated in the {title.lower()} style">
  </a>
  <div class="entry-body">
    <h2 class="entry-title">{title}</h2>
    <p class="entry-line">{description}</p>
    <div class="chips">
      <a class="chip" href="{slug}.html">In the portfolio</a>
      <a class="chip" href="{slug}.html?flat=1">Flat background</a>
    </div>
  </div>
</article>""")

(HERE / "index.html").write_text("""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Elif — Character studies</title>
<link rel="stylesheet" href="portfolio.css">
<style>
main{padding-block:clamp(44px,7vh,80px)}
.intro{max-width:62ch}
h1{font-family:var(--display);font-size:clamp(28px,4.4vw,58px);
  font-weight:800;letter-spacing:-.035em;line-height:.95;margin-bottom:26px}
.studies{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));
  gap:clamp(28px,6vw,80px);margin-top:clamp(34px,5vh,56px)}
.study{min-width:0}
.portrait{display:flex;align-items:flex-end;justify-content:center;
  aspect-ratio:1;text-decoration:none;margin-bottom:26px}
.portrait img{display:block;width:100%;height:100%;object-fit:contain}
.chip{text-decoration:none;letter-spacing:normal;border:0;background:var(--paper-2);
  display:inline-flex;align-items:center;min-height:44px}
.entry-title{-webkit-text-fill-color:var(--ink)}
.entry-line{color:var(--ink-2)}
.chips{padding-left:0}
@media(max-width:820px){.studies{grid-template-columns:1fr}.portrait{max-width:440px;
  width:100%;margin-inline:auto}}
</style></head><body><main class="pad">
<header class="intro"><h1>One Elif. Three drawing languages.</h1>
<p class="entry-line">Same bandana, glasses and navy top. Compare on a flat cream
background, then open each version in the portfolio and scroll.</p>
<div class="chips"><a class="chip" href="00-original.html">Original character</a></div>
</header>
<section class="studies" aria-label="Character style comparisons">
""" + "\n".join(cards) + "</section></main></body></html>")
print("Built comparison, original and three style previews.")
