# elifuysal.com — portfolio

One self-contained page. Fonts, the character illustration and every case-study
screen are inlined as `data:` URIs, so the site is a single `index.html` with no
external requests, no build step on the server and nothing to break when a CDN
changes.

## Editing

Edit **`src/portfolio-artifact.tmpl.html`** — never `index.html`, which is
generated and will be overwritten.

```bash
python3 src/build.py
```

Writes two files from the same body:

| file | for |
| --- | --- |
| `index.html` | what GitHub Pages serves — carries its own `<head>` (charset, viewport, title, favicon) |
| `dist/portfolio-artifact.html` | what gets published as a Claude Artifact, where the host supplies the `<head>` |

New screens: drop the image into `src/assets/case/`, reference it in the
template as `{{ASSET:case/name.webp}}`, rebuild.

## Structure

- **Home** — hero, "Who am I?", the drifting project strip, the work index, contact.
- **CV** — opens from the *About* link (`#cv`), printable as PDF.
- **Case studies** — a project card opens its page (`#case`). Content lives in
  `CASES`, keyed by project; anything not written yet renders as a *draft*
  prompt instead of a claim.

Both are full-screen sheets over the site rather than separate pages, so the
whole thing stays one file. EN/TR throughout.

## Deploy

GitHub Pages, from `main` / root. A custom domain goes in Settings → Pages,
which writes a `CNAME` file here; keep it committed.
