# thenationalnews.com decision — run 41

**Decision: removed.**

Run 39 added `thenationalnews.com` to `FASHION_SOURCES` for East Asia/Middle
East geographic diversity. Run 40 verified it fetches successfully and passes
robots.txt, but the fashion section's headlines are rendered client-side —
the raw HTML has no `h1`/`h2`/`h3` tags for the crawler to extract, so it
structurally yields 0 headlines with the current static-HTML scraping
approach, and left the call open for a future run.

This run makes that call: removed the URL from `FASHION_SOURCES` in
`src/crawler.py`, and removed its `"thenationalnews.com": "editorial"` entry
from `DOMAIN_SECTOR_MAP` in `src/taxonomy.py`, replacing it with an inline
comment explaining why.

Reasoning:

- Option (b) — leave it in with a comment, hoping the site changes its
  rendering approach later — is speculative and just defers the decision
  again, which the task explicitly asked not to do.
- `crawler.py`'s docstring commits to "UNCHANGED core logic": static-HTML
  fetch + tag scraping. Supporting JS-rendered sites would mean adding a
  headless-browser dependency (Playwright/Selenium) for the sake of one
  source — real complexity for zero yield.
- This matches the project's established pattern (run 32) of declining to
  force in a source just to hit a coverage goal, favoring simple, honest
  source lists over premature scraping complexity.
- A source that can never contribute headlines under the current
  architecture isn't "left open" — it's dead weight in the list. Removing it
  keeps `FASHION_SOURCES` an accurate reflection of what the crawler can
  actually read.

Historical report data (`data/reports/*.json`) that already references
`thenationalnews.com` in `source_domains` is untouched — this is a
forward-looking source-list change, not a retroactive data correction.

Verified with `python -m py_compile src/*.py` — passes.
