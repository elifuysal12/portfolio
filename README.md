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
`src/assets/case/`, reference it in the template as `{{ASSET:case/name.webp}}`,
rebuild.

Work-card covers go through one more step, because the cards are 16:10 and the
cover frames are not:

```bash
python3 src/make_cover.py cursor ~/Downloads/cover@4x.png
```

It widens the artwork to 16:10 with the artwork's own background rather than
cropping it, carries the coral rule along the bottom edge out to both corners,
and downscales from 4× so the thin strokes stay clean. Set `cover` on the
project and `coverBg` to that background.

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

Prototypes that live in Figma rather than in code get the same kind of room,
built from a table of share links:

```bash
python3 src/build_demo_figma.py      # /demo/base360
```

Elif's own chrome — her paper, her type, a way back to the work — around the
Figma player. Two things matter in that URL: the prototype must be shared
publicly in Figma (Share → *Anyone with the link* → can view), or visitors get
a login wall where the work should be; and the scaling must be
`scale-down-width`. `contain` fits a whole landing-page frame into the window
and hands you a postage stamp, `min-zoom` refuses to go below 100% and crops
the right-hand side.

## The work cards

A card goes to the project's case study, or — when that page isn't written yet
but the prototype runs — straight to its demo room, and says so on the card
(*Open the prototype →*). `DEMOS` in the template holds the second kind; a key
that appears in both `CASES` and `DEMOS` shows the case study, which carries
its own *See demo* button.

## Structure

- **Home** — hero, "Who am I?", the drifting project strip, the work index, contact.
- **CV** — opens from the *About* link (`#cv`), printable as PDF.
- **Case studies** — a project card opens its page (`#case`). Content lives in
  `CASES`, keyed by project, as a list of sections with a `k` (kind) each:
  `claim · two · mid · gap · play · ladder · grid · end`.

Both are full-screen sheets over the site rather than separate pages. EN/TR
throughout.

## Addresses

The sheets are what people come for, so they have their own URLs — `/cv/` and
`/case/cursor/`. `build.py` writes a real file at each one (the same page, told
on `<body data-open>` which sheet to open), so a shared link survives a cold
load and there is no redirect flash; in the browser they are `pushState`, so
Back closes a sheet instead of leaving the site. `404.html` catches the rest.

Turned off in the Artifact build — that URL belongs to the host. Asset paths are
root-relative for the same reason the routes exist: one page body is served from
three depths.

Add a route: append it to `ROUTE_PAGES` in `build.py`.

## Analytics

**Cloudflare Web Analytics**, cookieless, so the site needs no consent banner.
The beacon is in `build.py` (and `build_demo.py`); the token in it is a public
site tag, not a secret. It follows the History API, which is what makes the
routes above worth having — `/case/cursor/` reads as its own page rather than as
one more hit on the home page.

The Cursor Assistant case keeps the art direction of Elif's own board — near
black, the coral→pink ramp, heavy uppercase headings — and alternates centred
and left-aligned on purpose: centred where the page states something in its own
voice, left-aligned where it argues. `body.case-open` carries the nav and the
close button into the dark and hides the character, so the case study speaks
without her commenting over it.

## Deploy

GitHub Pages, from `main` / root. A custom domain goes in Settings → Pages,
which writes a `CNAME` file here; keep it committed.
