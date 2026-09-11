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
User-agent: *
Allow: /
"""


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
