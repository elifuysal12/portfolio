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
    if slug == "02-retro-toon":
        bust_page = page
        # Keep the previous placement available for direct comparison.
        (HERE / f"{slug}-floating.html").write_text(page)
        fade = page.replace("</head>", """<style>
#char{mask-image:linear-gradient(to bottom,black 78%,transparent 100%)}
</style></head>""")
        (HERE / f"{slug}-fade.html").write_text(fade)
        # The source is a bust, so its cut edge belongs below the viewport.
        # Seven screen pixels cover the existing breath/lean even at dock size.
        assert page.count("y:vh-22, s:dockS") == 1
        page = page.replace("y:vh-22, s:dockS", "y:vh+7, s:dockS")
        # Keep the dialogue's original clearance while lowering only the figure.
        assert page.count("const sayH=sayEl.offsetHeight, half=(CW*s)/2;") == 1
        page = page.replace(
            "const sayH=sayEl.offsetHeight, half=(CW*s)/2;",
            "const sayH=sayEl.offsetHeight, half=(CW*s)/2;\n"
            "  const dialogueY=y-29*dockPLerp;",
        )
        page = page.replace(
            "sy = P.mobile ? y-CH*s-sayH-14 : y-CH*s*.92;",
            "sy = P.mobile ? dialogueY-CH*s-sayH-14 : dialogueY-CH*s*.92;",
        )
        (HERE / f"{slug}-edge.html").write_text(page)
        # Keep the original upper-body coordinate system. The extended drawing
        # overflows BELOW it at its natural aspect ratio, rather than squeezing
        # the taller figure into the old square and shrinking the face.
        extended = HERE / "assets" / f"{slug}-aligned.png"
        if not extended.is_file():
            raise FileNotFoundError(extended)
        page = bust_page.replace(f"assets/{slug}.png", f"assets/{slug}-aligned.png")
        page = page.replace("</head>", """<style>
#stage #char img{height:auto;object-fit:initial;transform-origin:50% 713px}
#stage #charMotion{position:relative;width:100%;transform-origin:50% 713px;
  will-change:transform;filter:drop-shadow(0 18px 30px rgba(23,20,15,.18))}
#stage #charMotion img{filter:none}
#stage #charImg{clip-path:inset(38% 0 0)}
#stage #headMotion{position:absolute;left:0;top:0;width:100%;aspect-ratio:1060/1484;
  transform-origin:50% 38%;will-change:transform}
#stage #charHead{position:absolute;left:0;top:0;clip-path:inset(0 0 61.6%)}
#stage #charMouth{position:absolute;left:0;top:0;clip-path:inset(27% 44% 68% 43%);
  opacity:0;will-change:opacity}
html.flat-preview #stage #charMotion{filter:none}
</style></head>""")
        # Both layers share one asset and overlap slightly at the neck. Only the
        # head rotates; breath and pointer movement apply to the common parent.
        img_tag = re.search(r'<img id="charImg"[^>]+>', page).group(0)
        head_tag = img_tag.replace('id="charImg"', 'id="charHead"').replace(
            'alt="Elif Uysal"', 'alt="" aria-hidden="true"')
        mouth_tag = head_tag.replace('id="charHead"', 'id="charMouth"').replace(
            f"{slug}-aligned.png", f"{slug}-speaking.png")
        round_tag = mouth_tag.replace('id="charMouth"', 'id="charMouthRound" class="mouth-shape"').replace(
            f"{slug}-speaking.png", "mouth-round.png")
        assert (HERE / "assets" / f"{slug}-speaking.png").is_file()
        page = page.replace(img_tag,
            '<div id="charMotion"><div id="neutralPose">' + img_tag +
            '<div id="headMotion">' + head_tag + mouth_tag + round_tag + '</div></div></div>')
        page = page.replace("</head>", "<style>" +
            (HERE / "retro-motion.css").read_text() + "</style></head>")
        page = page.replace(
            "const charImg=document.getElementById('charImg');",
            "const charImg=document.getElementById('charImg');\n"
            "const charMotion=document.getElementById('charMotion');\n"
            "const charHead=document.getElementById('headMotion');\n"
            "const charMouth=document.getElementById('charMouth');")
        # Preserve the source's large, centered hero and scroll into the right dock.
        # Leave room for the raised hand beside the hero's face.
        page = page.replace("sy = y - CH*s*.78;", "sy = y - CH*s*.98;")
        page = page.replace("sayEl.classList.toggle('stacked',P.mobile&&dockPLerp>.5);",
                            "sayEl.classList.toggle('stacked',P.mobile);")
        page = page.replace(
            "  sx=Math.max(10, Math.min(sx, innerWidth-cardW-14));",
            "  if(P.mobile){\n"
            "    sx=dockPLerp>.5 ? innerWidth-sayEl.offsetWidth-16"
            " : (innerWidth-sayEl.offsetWidth)/2;\n"
            "    sy=y-CH*s-sayH-18;\n"
            "  }\n"
            "  sx=Math.max(10, Math.min(sx, innerWidth-cardW-14));")
        page = page.replace(
            "const tx=(mx-.5)*(P.mobile?5:12), ty=(my-.5)*(P.mobile?3:7);",
            "const tx=RM?0:(mx-.5)*(P.mobile?5:12), "
            "ty=RM?0:(my-.5)*(P.mobile?3:7);")
        page = page.replace("Math.sin(now/1450)*1.7",
                            "(RM?0:Math.sin(now/1450)*3)")
        page = page.replace("charImg.style.transform =", "charMotion.style.transform =")
        page = page.replace(
            "  /* ---- strips drift ---- */",
            "  updateCharacterMotion(now);\n\n"
            "  /* ---- strips drift ---- */")
        page = page.replace("function tick(now){",
            (HERE / "retro-motion.js").read_text() + "\nfunction tick(now){")
        page = page.replace(
            "function sayProject(k){ const p=t().proj[k]; if(p) say(p.i,p.t); }",
            "function sayProject(k){ pointToProject(k); }")
        page = page.replace("  clearTimeout(typeTimer);",
                            "  clearTimeout(typeTimer);\n  typing=false;\n"
                            "  sayEl.classList.remove('project-cue');")
        page = page.replace(
            "setTimeout(step, 16+Math.random()*22)",
            "setTimeout(step, /[,.!?;:]/.test(text[i-1])?160:22+Math.random()*24)")
        (HERE / f"{slug}-extended-compact.html").write_text(page)
        assert page.count("const dockH = mobile ? 92 : 124;") == 1
        page = page.replace("const dockH = mobile ? 92 : 124;",
                            "const dockH = mobile ? 124 : 160;")
    (HERE / f"{slug}.html").write_text(page)

(HERE / "00-original.html").write_text(preview)

# Reuse the exact compiled portfolio typography, tokens and component styling.
css = "\n".join(re.findall(r"<style>(.*?)</style>", source, re.S))
(HERE / "portfolio.css").write_text(css)

cards = []
for slug, title, description in variants:
    dock_option = (
        f'<a class="chip" href="{slug}-extended-compact.html#about">Smaller companion</a>'
        f'<a class="chip" href="{slug}.html?motion=1">Try the gestures</a>'
        f'<a class="chip" href="{slug}.html?gestures=hover">React on interaction</a>'
        '<a class="chip" href="mobile-preview.html">Mobile preview</a>'
        if slug == "02-retro-toon" else ""
    )
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
{dock_option}
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
