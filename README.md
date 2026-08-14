# elifbeyzauysal.com — portfolio

One page. Fonts and the character illustration are inlined as `data:` URIs, so
the page draws in its own type with no external requests. Case-study screens are
the exception: they are 4× Figma exports and ship as real files under `assets/`,
lazy and cacheable, rather than a megabyte of base64 in front of the first paint.

## Editing

Edit **`src/portfolio-artifact.tmpl.html`** — never `index.html`, which is
generated and will be overwritten.

```bash
python3 src/build.py
```

Writes two copies from the same body:

| file | for |
| --- | --- |
| `index.html` + `assets/` | what GitHub Pages serves — carries its own `<head>` (charset, viewport, title, favicon), screens linked at full resolution |
| `dist/portfolio-artifact.html` | what gets published as a Claude Artifact — screens inlined from `src/assets/case/sm/`, because that CSP blocks every external host and the share ceiling is under a megabyte |

New screens: export from Figma at **4×** (a 1× export downscaled to card width
turns the 2px gradient stroke into a sub-pixel smear), drop the file into
`src/assets/case/`, add a compact copy in `src/assets/case/sm/`, reference it in
the template as `{{ASSET:case/name.webp}}`, rebuild.

The hover loop (`case/hover.webp`) is an **animated WebP**, rebuilt from
`../nore-hover-gif` — same frames as the GIF on the Behance board, full colour
at a seventh of the bytes.

## The demos

Runnable prototypes live under `/demo`, one room each, named after the shop
they are set in: **`/demo/nore`** is the Cursor Assistant prototype today, and
`/demo/mekik` can move in beside it. They run on this domain rather than on the
Artifacts they were first published to, so *See demo* keeps people on the site.

```bash
python3 src/build_demo.py            # reads ../mavi-cursor-chat
```

It inlines the prototype's CSS/JS, retitles the page after the *project* rather
than the shop, and copies the photographs in as plain files — the prototype's
own builds either hotlink Unsplash or base64 everything, and neither belongs on
a real site. Output is committed; re-run when the prototype changes.

## Structure

- **Home** — hero, "Who am I?", the drifting project strip, the work index, contact.
- **CV** — opens from the *About* link (`#cv`), printable as PDF.
- **Case studies** — a project card opens its page (`#case`). Content lives in
  `CASES`, keyed by project, as a list of sections with a `k` (kind) each:
  `claim · two · mid · gap · play · ladder · grid · end`.

Both are full-screen sheets over the site rather than separate pages. EN/TR
throughout.

The Cursor Assistant case keeps the art direction of Elif's own board — near
black, the coral→pink ramp, heavy uppercase headings — and alternates centred
and left-aligned on purpose: centred where the page states something in its own
voice, left-aligned where it argues. `body.case-open` carries the nav and the
close button into the dark and hides the character, so the case study speaks
without her commenting over it.

## Deploy

GitHub Pages, from `main` / root. A custom domain goes in Settings → Pages,
which writes a `CNAME` file here; keep it committed.
