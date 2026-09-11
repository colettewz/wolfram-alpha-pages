# Step-by-Step plates — dev assets

Nine rebuilt product panels (4:3, viewBox 533×400) plus the hero animation, exactly as
inlined in `../step-by-step.html`. Source of truth: `wolfram-alpha/pages/step-by-step/plates/`
(built by `scripts/build-plate.py` from the product's own step text; regenerate with
`stage.py`).

## Placement
| file | where on the page | weight |
|---|---|---|
| `step-by-step-solutions.svg` | Features row 1 | 20 KB |
| `show-intermediate-steps.svg` | Features row 2 | 76 KB |
| `choose-a-method.svg` | Features row 3 | 31 KB |
| `show-hints.svg` | Features row 4 | 22 KB |
| `limit-with-hints.svg` | Examples · Calculus | 21 KB |
| `equation-solving.svg` | Examples · Equation Solving | 29 KB |
| `basic-math-long-division.svg` | Examples · Basic Math | 32 KB |
| `eigenvalues.svg` | Examples · More Math Topics | 25 KB |
| `ru-orbital-diagram.svg` | Examples · Chemistry | 68 KB |
| `partial-fractions.svg` | Hero animation (viewBox 826×616) | 15 KB |

## Contract
- **Inline them** (`<figure class="shot">` + the SVG). Each carries its own `<style>` with
  a light palette and a dark twin under `[data-theme="dark"] #<id>`, so it themes with the
  page root — as an `<img>` it would only ever show light.
- Ids are unique per plate (`#limit-with-hints` etc.); glyphs are `<use>` references to
  per-plate `<defs>`, so a plate is self-contained and several can share one page.
- Type is Charter (product face) outlined to paths; the header label is live text in
  Lexia, falling back to a slab serif where Lexia is not licensed.
- The well: 4:3, `--r-lg` 16 radius, 1px `--s-border-primary` border on the page element.
