#!/usr/bin/env python3
"""Sync staged pages into docs/ for the GitHub Pages review site, unindexed.

    python3 _publish/publish.py            # copy + inject, report
    python3 _publish/publish.py --check    # verify only, exit 1 on drift

Two jobs, both mechanical so neither can be forgotten at 6pm on a Friday:

1 · COPY the staged, self-contained page out of ~/Drive-staging into docs/. The staged file
    is already the derivative (fonts + sheets inlined, dev notes stripped) — this never
    transforms content, it only moves it.

2 · INJECT `<meta name="robots" content="noindex, nofollow">` into every page in docs/.
    These are design references on a PUBLIC repo: reachable by link, never in search results.

⚠️ WHY THERE IS NO `Disallow` IN robots.txt. The two mechanisms fight each other: a crawler
blocked by robots.txt never FETCHES the page, so it never sees `noindex` — and Google may
still list the bare URL it found from a link elsewhere. `noindex` is the directive that
removes a page from the index, and it only works if crawling is allowed. So robots.txt here
explicitly ALLOWS, and every page carries the meta.

The noindex belongs to the REVIEW PUBLICATION, not to the design: it is injected here and is
deliberately absent from `pages/*/`, so a page handed to dev never carries it into production.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOCS = HERE / "docs"
STAGING = Path.home() / "Drive-staging/wolfram-alpha/pages"

# staged page → its name in docs/. Add a row to publish a new page.
PAGES = {
    "step-by-step/step-by-step.html": "step-by-step.html",
    "web-apps/web-apps.html": "web-apps.html",
    "problem-generator/problem-generator.html": "problem-generator.html",
    "chat-mode/chat-mode.html": "chat-mode.html",
}

META = '<meta name="robots" content="noindex, nofollow">'
ROBOTS = """# Design references, published for review.
# Crawling is ALLOWED on purpose: every page carries <meta name="robots" content="noindex">,
# and a crawler must be able to fetch a page to see that directive. Blocking here would
# leave the URLs eligible to appear in results with no description — the opposite of intent.
#
# THE ASSET FOLDERS ARE THE EXCEPTION, and for the opposite reason. An SVG or a PNG is not
# HTML: it cannot carry a robots meta, and GitHub Pages cannot set an X-Robots-Tag header.
# So for a binary asset, BLOCKING is the only noindex there is — Google Images cannot index
# what it is not allowed to fetch. The gallery page above them stays crawlable so its own
# meta is seen, and it is noindex,nofollow, so the assets are never discovered through it.
User-agent: *
Allow: /
Disallow: /plates/svg/
Disallow: /plates/png/
# The ten flat /plates/*.svg are the pre-2026-09-15 layout, kept because a direct file URL
# may have been handed to someone and this repo does not break a review URL. They are exact
# duplicates of /plates/svg/ and blocked for the same reason.
Disallow: /plates/*.svg$
"""

# staged asset folder → its folder in docs/. Vectors and rasters keep the split they have
# in Drive staging, so a dev picks a format by folder rather than out of a mixed listing.
ASSETS = {
    "step-by-step/plates/svg": "plates/svg",
    "step-by-step/plates/png": "plates/png",
}

GALLERY_TITLE = "Step-by-Step plates"


def inject(html: str) -> str:
    """Put the robots meta right after <meta charset>. Idempotent."""
    if META in html:
        return html
    html = re.sub(r'<meta name="robots"[^>]*>\s*', "", html)          # replace any weaker one
    m = re.search(r'<meta charset=["\']?[\w-]+["\']?\s*/?>', html, re.I)
    if not m:
        sys.exit("no <meta charset> to anchor the robots meta to")
    return html[:m.end()] + "\n" + META + html[m.end():]


def main() -> int:
    check = "--check" in sys.argv
    problems, changed = [], []

    for src_rel, name in PAGES.items():
        src, dst = STAGING / src_rel, DOCS / name
        if not src.exists():
            problems.append(f"{name}: staged source missing ({src}) — run its stage.py first")
            continue
        want = inject(src.read_text())
        if not dst.exists() or dst.read_text() != want:
            if check:
                problems.append(f"{name}: docs/ copy differs from the staged source")
            else:
                dst.write_text(want)
                changed.append(name)

    # index.html is authored here, not staged — inject in place.
    idx = DOCS / "index.html"
    if idx.exists():
        want = inject(idx.read_text())
        if idx.read_text() != want:
            if check:
                problems.append("index.html: missing the robots meta")
            else:
                idx.write_text(want)
                changed.append("index.html")

    # ── asset folders: copy verbatim, then build a gallery page that IS unindexed ──
    import shutil
    gallery_rows = []
    for src_rel, dst_rel in ASSETS.items():
        src, dst = STAGING / src_rel, DOCS / dst_rel
        if not src.exists():
            problems.append(f"{dst_rel}: staged source missing ({src}) — run its stage.py first")
            continue
        files = sorted(f for f in src.iterdir() if f.suffix.lower() in (".svg", ".png"))
        for f in files:
            target = dst / f.name
            same = target.exists() and target.read_bytes() == f.read_bytes()
            if not same:
                if check:
                    problems.append(f"{dst_rel}/{f.name}: docs/ copy differs from the staged source")
                else:
                    dst.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, target)
                    changed.append(f"{dst_rel}/{f.name}")
        gallery_rows.append((dst_rel, files))

    if gallery_rows and not check:
        kinds = {k.rsplit("/", 1)[-1]: fs for k, fs in gallery_rows}
        def cards(fs, folder):
            return "\n".join(
                f'<li><a href="{folder}/{f.name}"><img src="{folder}/{f.name}" alt="" loading="lazy">'
                f'<span>{f.name}<em>{f.stat().st_size // 1024} KB</em></span></a></li>' for f in fs)
        html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
{META}
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{GALLERY_TITLE}</title>
<style>
:root{{color-scheme:light dark}}
body{{margin:0;padding:40px 24px;font:16px/1.55 "Source Sans Pro",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#fff;color:#1a1a1a}}
.wrap{{max-width:1080px;margin:0 auto}}
h1{{font-size:28px;margin:0 0 4px;font-weight:600}}
h2{{font-size:18px;margin:36px 0 12px;font-weight:600}}
p.sub{{margin:0 0 8px;color:#5b5b5b}}
ul{{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px}}
a{{display:block;color:inherit;text-decoration:none;border:1px solid #e3e3e3;border-radius:10px;overflow:hidden;background:#fafafa}}
a:hover{{border-color:#b8b8b8}}
img{{display:block;width:100%;height:auto;background:#6C5694}}
span{{display:block;padding:10px 12px;font-size:13px;font-weight:600}}
em{{display:block;font-style:normal;font-weight:400;color:#5b5b5b}}
footer{{margin-top:36px;font-size:14px;color:#5b5b5b}}
@media (prefers-color-scheme:dark){{body{{background:#1a1a1a;color:#f2f2f2}}a{{background:#232323;border-color:#3a3a3a}}p.sub,em,footer{{color:#a8a8a8}}}}
</style></head><body><div class="wrap">
<h1>{GALLERY_TITLE}</h1>
<p class="sub">Nine product panels and the hero animation. <strong>The SVGs are the deliverable</strong> — inline them; each carries a light and a dark palette in one file. The PNGs are fallbacks for contexts that cannot take an inline SVG.</p>
<p class="sub">PNGs export at 1440 wide — 2× the plate's widest rendered size (718 CSS px at the tablet breakpoint) — so they stay sharp on retina and are never upscaled. A PNG cannot switch theme, which is why each ships twice.</p>
<h2>SVG — the deliverable</h2>
<ul>
{cards(kinds.get("svg", []), "svg")}
</ul>
<h2>PNG — fallbacks</h2>
<ul>
{cards(kinds.get("png", []), "png")}
</ul>
<footer>Design references, not production code. Unlisted and unindexed.</footer>
</div></body></html>
"""
        gp = DOCS / "plates" / "index.html"
        if not gp.exists() or gp.read_text() != html:
            gp.parent.mkdir(parents=True, exist_ok=True)
            gp.write_text(html)
            changed.append("plates/index.html")

    robots = DOCS / "robots.txt"
    if not robots.exists() or robots.read_text() != ROBOTS:
        if check:
            problems.append("robots.txt: missing or edited")
        else:
            robots.write_text(ROBOTS)
            changed.append("robots.txt")

    # every published page must end up unindexed, whatever route it arrived by
    for f in sorted(DOCS.glob("*.html")):
        if META not in f.read_text():
            problems.append(f"{f.name}: NOT unindexed — no robots meta")

    if problems:
        sys.stderr.write("PUBLISH " + ("CHECK FAILED" if check else "FAILED") + ":\n  "
                         + "\n  ".join(problems) + "\n")
        return 1
    print("docs/ in sync, every page unindexed"
          + (" — updated: " + ", ".join(changed) if changed else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
