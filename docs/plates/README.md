# Step-by-Step plates — dev assets

Nine rebuilt product panels (4:3, viewBox 533×400) plus the hero animation, exactly as
inlined in `../step-by-step.html`.

## Two folders, one per format
| folder | what | use |
|---|---|---|
| **`svg/`** | the deliverable — vectors, light + dark palettes in one file | **inline these** |
| **`png/`** | raster fallbacks, 1440 wide, light + dark baked separately | only where an inline SVG is impossible (email, slides, a CMS that strips `<svg>`) |

1440 is 2× the plate's widest rendered size (718 CSS px, at the 768 tablet breakpoint where
the layout goes single-column), so a PNG is sharp on retina at every breakpoint and never
upscaled. A PNG cannot switch theme — that is why each ships twice. Source of truth: `wolfram-alpha/pages/step-by-step/plates/`
(built by `scripts/build-plate.py` from the product's own step text; regenerate with
`stage.py`).

## Placement
| file | where on the page | weight |
|---|---|---|
| `step-by-step-solutions.svg` | — not placed (row retired 2026-09-14); retained for reuse | 19 KB |
| `show-intermediate-steps.svg` | Features row 1 | 76 KB |
| `choose-a-method.svg` | Features row 2 | 30 KB |
| `show-hints.svg` | Features row 3 | 22 KB |
| `limit-with-hints.svg` | Examples · Calculus | 20 KB |
| `equation-solving.svg` | Examples · Equation Solving | 28 KB |
| `basic-math-long-division.svg` | Examples · Basic Math | 32 KB |
| `eigenvalues.svg` | Examples · More Math Topics | 24 KB |
| `ru-orbital-diagram.svg` | Examples · Chemistry | 68 KB |
| `partial-fractions.svg` | Hero animation (viewBox 826×616) | 10 KB |

## Contract
- **Inline them** (`<figure class="shot">` + the SVG). Each carries its own `<style>` with
  a light palette and a dark twin under `[data-theme="dark"] #<id>`, so it themes with the
  page root — as an `<img>` it would only ever show light.
- Ids are unique per plate (`#limit-with-hints` etc.); glyphs are `<use>` references to
  per-plate `<defs>`, so a plate is self-contained and several can share one page.
- Type is Charter (product face) outlined to paths; the header label is live text in
  Lexia, falling back to a slab serif where Lexia is not licensed.
- The well: 4:3, `--r-lg` 16 radius, 1px `--s-border-primary` border on the page element.
