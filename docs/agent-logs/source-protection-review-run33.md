# Source-outlet protection review (run 33)

## Question
Distinct from anonymous-source protection (doesn't apply — all sourcing is public web
pages): could crawler behavior or published report content expose small/independent
outlets (e.g. dewimagazine.com, savoirflair.com) to targeted traffic surges or
harassment as a side effect of being cited by this project?

## Research
No single canonical "aggregator code of conduct" addresses this exact concern, but
adjacent guidance converges on two practices:
- **Ethical aggregation norms** (Plagiarism Today's "Brief Guide to Ethical
  Aggregation," CJR's "We're all aggregators now," Poynter's "aggregator's dilemma")
  agree aggregators should credit source + outlet and drive click-through traffic
  *to* the original, not replace it — but none of them discuss capping outlet-level
  attribution when the outlet is small.
- The **"hug of death"** phenomenon (a small site's infrastructure/attention capacity
  overwhelmed by a sudden traffic spike from a larger platform linking to it) is a
  well-documented technical/reputational risk distinct from anonymous-sourcing harm,
  but no dedicated journalism-ethics document was found that names it as a
  crediting-practice risk. This appears to be a genuine gap in public discourse — this
  review is closer to a first-principles hazard check than application of established
  guidance.

## Code review

**`web/app/sources/page.tsx`**: lists outlet *names only* by sector (e.g. "Vogue
Runway," "Substack fashion writers" as a category, not named individuals), no URLs,
no per-article links, no traffic/frequency data. No risk here.

**`web/app/reports/[date]/page.tsx`**: signal `evidence` field is aggregated
descriptive prose ("Repeated references to transparent fabrics... across editorial
sources") — never a URL, never a single-outlet attribution, never a specific article
title. Confirmed via grep across `data/reports/*.json`: no `http`/URL strings appear
in any `evidence` field.

**`src/report_schema.py`**: no `source_links` field exists in the `Signal` or
`Report` dataclass at all (confirmed: not in `REQUIRED_SIGNAL_KEYS`, not a dataclass
field). It appears only as an ad hoc, unvalidated extra key in one legacy report file
(`data/reports/2026-05-07.json`, `"source_links": []`) and in `web/lib/reports.ts`'s
TypeScript type (`source_links?: string[]`) — flagged in
`docs/agent-logs/schema-convention-audit-run31.md` as a stray key not in the
canonical schema. It is empty in the one file that has it, is never populated by
`summarize.py`, and is never read/rendered by any `.tsx` file (confirmed via grep —
only the type declaration and the one empty array reference it).

**`src/crawler.py`**: identifies itself honestly (`User-Agent:
fashion-trend-crawler/1.0 (educational project)`), respects `robots.txt`. No
aggressive/repeated-hit pattern that would itself look like an attack on a small
site; this is a one-time BFS crawl per report window, not continuous polling.

## Conclusion: no real risk under current practice

Current data flow never surfaces a specific article URL or a single small outlet
singled out with a link a reader could click through to pile onto. Evidence text is
sector-level aggregate prose; the sources page names outlet categories, not URLs.
`source_links` is dead, unused schema drift, not a live feature.

## Residual risk / mitigation if `source_links` is ever activated

If a future run wires up `source_links` (the field exists in the TS type and one
legacy file, so it's a plausible next step someone could take without re-reading this
review), that would be the moment real risk appears: a direct URL to a specific small
outlet's specific article, published on a report page, is exactly the "hug of death"
/ pile-on vector this review was asked to check for. Recommended mitigation *at that
time*, not now: link to the outlet's homepage/section rather than the specific
article permalink for small/independent-criticism-sector sources, or omit
per-article URLs entirely and keep attribution at the outlet-name level (as
`sources/page.tsx` already does). Not implementing now since `source_links` isn't
live — flagging so whoever activates it sees this reasoning first.
