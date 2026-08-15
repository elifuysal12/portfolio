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

```bash
python3 src/build_demo_base360.py    # reads ../base360-journey.html
```

base360's prototype is already one self-contained file — no external requests,
nothing to copy — so that build is a head, a credit line in the footer and the
beacon. A Figma embed was tried here first and taken out: an embedded player is
a picture of the work behind someone else's chrome, and the point of a demo is
that it runs.

```bash
python3 src/build_demo_jotform.py     # reads ../jotform-dashboard/index.html
```

**`/demo/jotform`** is the Jotform AI Chatbot analytics dashboard: Elif's Figma
prototype **running inside a monitor** on a dark desk, under the site's own nav
— the desktop counterpart of the phone in `/case/alti/demo`. The screen is cut to
the frame's own 1440×900, so `scale-down-width` lands it exactly: no letterbox,
no scrolling inside the player. `hide-ui=1` takes Figma's restart away with the
rest of the chrome, so the caption under the desk carries *Start over* and
*Open in Figma*.

Two earlier attempts are worth not repeating, both recorded in the build file.
A bare edge-to-edge embed reads as somebody's player dropped into a page, and
loads as a white rectangle the size of the room. Then the dashboard was
**rebuilt in code** — it ran, but the icons and a hundred small decisions were
the rebuild's rather than Elif's, and a portfolio piece has to be the
designer's own artefact, not a faithful copy of it. That source is kept outside
the repo at `~/Projects/jotform-dashboard`.

```bash
python3 src/build_demo_sunninja.py    # reads ../sunninja-redesign
```

**`/demo/sunninja`** is the Sun Ninja storefront redesign, and the first room
with **two pages**: the landing, and the product page it links into. Three
things the prototype does for itself that a real address should not, all fixed
in the build — Google Fonts (the six faces its own Artifact build already
subset are unpacked into `assets/font/` and linked from there), 12 MB of PNG
and JPEG (re-encoded to WebP, 4.5 MB, references rewritten), and a footer still
carrying a live-looking phone number and support address (it takes the
disclaimer the product page already had). The CSS and JS stay as files rather
than inlined: two pages share `style.css`, and inlining would ship it twice and
throw the cache away on the click between them.

Its work-card cover is the only one not exported from Figma. The project was
made in code, so the cover is drawn in code too — `src/cover_sunninja.html`,
in the prototype's own Poppins over the Sunrise ramp from its own `DAY` table,
laid out the way the Figma covers are: eyebrow, the page's own sentence with
the second line in the accent, one support line, and the artefact bleeding off
the right edge. The artefact is a slice of the page at **noon** while the
ground is dawn, so the claim is proved on the card rather than described.
Shoot it and downscale (already 16:10, hence `--ratio native` — the widening
path reads the peach gradient at the bottom as a rule and paints a band across
it); the exact command is in the file's own comment.

```bash
python3 src/build_demo_alti.py        # /case/alti/demo — ALTI, in a phone
```

**`/case/alti/demo`** is the same second choice for the same reason — 79 screens
across five flows, wired in Figma, with no coded twin — but it is a separate
room rather than an entry in the file above, because the stage there is a
1440×900 dashboard and this is a phone. A phone is an object, not a stage, so
it gets a device shell cut to the frame's own 393:852 ratio, in ALTI's navy
with the pink→orange ramp as its edge. `hide-ui=1` takes Figma's restart away
with the rest of the chrome, so the room supplies its own, and the player opens
on **flow 2** — `node-id` picks the frame but the player still starts the flow
at its own starting point, so `starting-point-node-id` and `page-id` both have
to be said.

**It is the only room not in the `/demo` yard**, and that is the point: the
others are separate exhibits, this one is a case study's own demo, so it sits
under it. *See demo* opens it **in the same tab** — every demo runs on this
domain and every room carries the way back, so taking a tab buys nothing.

It wears **the site's own nav** — same pill, same order, same EN/TR switch,
carried into the dark the way `body.case-open` carries it on a case study — so
the demo reads as a room in the site rather than a page that links back to one.
The section links are absolute (`/#work`, `/cv/`, `/#contact`) because this is
a separate address.

The room's own controls sit to the **right of the phone**, ranked: one filled
ramp button (*Read the case study* — the step after playing, and the mirror of
*See demo* on the case) and two quiet icon rows. They started as three
identical outlined pills under the phone, which cost the prototype ~190px of
height and gave the page three equal things to press; an outline-only control
is also on the list of tells to keep off this site. The copy and ALTI's own
mark take the left column. Below 1000px it all goes back under the phone.

Fonts in the rooms are **linked, not inlined** (`assets/font/`, written by
whichever demo build runs last — each writes them, so no build depends on
another): the rooms share one cached copy, and a shell about to pull down a
whole prototype should not carry 150 KB of base64 in front of it.

Where a room still holds a Figma player, the scaling is **`scale-down-width`**
and should not be changed to `contain`, which fits a frame at about half size
inside a black surround — see the note in `build_demo_alti.py`.

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
  `claim · two · mid · gap · play · ladder · grid · four · fork · notes · end`,
  plus ALTI's own `personas · band · trio · devices · flow · rows`.

Each case carries its board's art direction, not one house style. The colours
were already tokens (`--c-bg`, `--c-ink`, `--c-ramp`, …), so a case sets
`theme` and the sheet picks them up from `#case[data-theme="…"]`. ALTI is the
first **light** one: `light:true` also adds `body.case-light`, which is what
keeps the nav and the close pill on paper instead of following the sheet into
the dark. Its sections alternate white and `#F7F8FC` through `alt:1` — not
decoration, but a requirement: the phones are cut out of the board's own
section exports and carry whichever band they were drawn on.

New ALTI screens: re-export the whole **section frame** at 4× and cut it with
`python3 src/slice_alti.py <folder>` — fifteen phones exported one at a time is
fifteen round-trips through Figma, and the section already holds them at the
right scale. The node ids and the expected filenames are in that script.

Both are full-screen sheets over the site rather than separate pages. EN/TR
throughout.

## Addresses

The sheets are what people come for, so they have their own URLs — `/cv/`,
`/case/cursor/`, `/case/whallet/`, `/case/alti/`. `build.py` writes a real file at each one (the same page, told
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
