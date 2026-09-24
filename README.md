# Wolfram|Alpha — page designs

Design versions of Wolfram|Alpha marketing pages, published for review.

## Live pages

https://colettewz.github.io/wolfram-alpha-pages/

| Page | Link |
|---|---|
| Step-by-Step Solutions | https://colettewz.github.io/wolfram-alpha-pages/step-by-step.html |
| Chat mode | https://colettewz.github.io/wolfram-alpha-pages/chat-mode.html?seed=gold |
| Site header (interactive) | https://colettewz.github.io/wolfram-alpha-pages/nav-header.html |
| Pro page animations (CSS + SVG and Lottie) | https://colettewz.github.io/wolfram-alpha-pages/pro-animations.html |

## About the files

Each page in `docs/` is a self-contained HTML file — CSS, JS, fonts and artwork are all
inlined. Open one directly in a browser; no server or build step needed.

`docs/plates/` carries the same nine product panels and the hero animation as standalone
SVGs, for development. See `docs/plates/README.md` for placement and the inline-vs-`<img>`
rule (they carry both light and dark palettes, so they only theme correctly when inlined).

## What changed on Step-by-Step

- The nine product screenshots are now **SVGs** rather than PNGs — they stay sharp at any
  size, theme with the page, and weigh a fraction of the images they replace.
- The hero image is now an **animation**, built in SVG/CSS.
- Hero and banner colours were adjusted to meet **contrast requirements**.
- A **Pro cross-promotion** section was added at the foot of the page.

Copy is unchanged from the approved page apart from the closing band and the new Pro
section.

## Notes for developers

- Type is Source Sans Pro, self-hosted and embedded in the file.
- The page carries a light and a dark theme; the toggle is in the nav.
- Scroll animations are progressive enhancement — with JavaScript off the page loses the
  animation and keeps every word of content.

## Publishing

```bash
python3 _publish/publish.py            # sync staged pages into docs/, inject noindex
python3 _publish/publish.py --check    # verify, exit 1 on drift
```

**Every page here is unindexed.** The repo is public, so these pages are reachable by link
but carry `<meta name="robots" content="noindex, nofollow">` and must stay out of search
results. `robots.txt` deliberately ALLOWS crawling: a crawler that is blocked never fetches
the page, so it never sees the `noindex`, and the bare URL stays eligible to appear in
results. Allow the fetch, refuse the index.

The noindex is injected at publish time and is deliberately absent from `pages/*/` in the
main repo, so a page handed to dev never carries it into production.

**Unlisted vs listed.** A page is listed when it appears in `docs/index.html` and in the table
above. Publishing a page does not list it: some pages here are live for review and deliberately
absent from both, so their URL works and nothing points at it. This README is public — do not
name an unlisted page in it.

---

Derivative — do not edit these files. Source of truth:
`wolfram-alpha/pages/step-by-step/step-by-step.html`; regenerate the page with
`python3 pages/step-by-step/stage.py`, then copy the staged output into `docs/`.
