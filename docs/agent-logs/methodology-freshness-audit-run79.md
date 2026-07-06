# Methodology freshness audit (run 79)

## Scope

Read `web/app/methodology/page.tsx`, `web/app/taxonomy/page.tsx`, and `web/app/about/page.tsx`
in full. Compared their claims against `src/report_schema.py` (`derive_confidence()`,
`HIGH_RELIABILITY_SECTORS`, `is_prolonged_silence()`, `get_signal_status_history()`),
`src/taxonomy.py` (`SOURCE_SECTORS`, `DOMAIN_SECTOR_MAP`), and recent agent-log precedents:
`docs/agent-logs/confidence-recompute-2027-09-06-run72.md`, `docs/agent-logs/real-report-2027-11-08.md`,
`docs/agent-logs/longitudinal-tracking-research-run76.md`.

## Findings

**1. Confidence discipline was under-documented — real gap, fixed.**
Methodology's "How Confidence Is Assigned" described confidence as a function of
sector-count and language consistency, with no mention of the manual-override discipline
actually in force:
- Run 72 precedent: two source domains carrying *different* sector labels are not
  automatically independent corroboration — if one is a downstream reprint of the other's
  own primary announcement (e.g. `laforma.club` republishing `fhcm.paris`'s calendar), the
  signal is substantively held at `medium` even though a mechanical `derive_confidence()`
  recompute would say `high`.
- Run 71 precedent: `HIGH_RELIABILITY_SECTORS`'s single-source-to-medium exception assumes
  the source did independent reporting. A citation-free rehash of signals already in the
  archive (even from a high-reliability sector like `independent_criticism`) is deliberately
  held at `low`, not given the exception's credit.
Added a paragraph to the Confidence section describing both precedents in wire-service
prose, without naming internal function/variable names.

**2. `unclear`-sector handling was undocumented — real gap, fixed.**
`taxonomy.py.classify_source()` returns `"unclear"` for any domain not yet in
`DOMAIN_SECTOR_MAP`, and confidence logic (per the run 72 log) does not count `unclear` as a
real distinct sector for corroboration purposes. The Source Sectors section listed the nine
named sectors but never mentioned the `unclear` fallback or its confidence implication.
Added one sentence to the Source Sectors section.

**3. Longitudinal signal tracking (`/signals/[slug]`, shipped run 4, recency status added
run 76) was never mentioned anywhere on the methodology page — real gap, fixed.**
The page's "What This Index Tracks" section gestures at "a historical record ... rather
than a single snapshot" but never describes the actual per-signal tracking capability, the
persistent `signal_id`, or how dormancy/prolonged-silence is handled (the close-out vs.
open-factual-question vs. "untracked pending new information" distinction documented in
SKILL.md workflow note 10 and `is_prolonged_silence()`'s docstring). Added a new section,
"How Signal Recurrence Is Tracked," describing the per-signal history page and the
three-state dormancy handling in prose, without inventing UI details not present in the
actual page.

## Checked and found appropriately accurate / not changed

- **Source sector list**: Methodology's nine-sector prose list and Taxonomy page's table
  both match `taxonomy.py`'s `SOURCE_SECTORS` (methodology/taxonomy combine `runway` +
  `editorial` into one "runway/editorial" bullet — an intentional, longstanding
  abstraction, not new drift). Runs 73-78's new `DOMAIN_SECTOR_MAP` entries
  (`ffw.com.br`, `voguearabia.com`, `inexmoda.org.co`, `fhcm.paris`, `laforma.club`, etc.)
  are individual domains, not new sectors — a methodology/taxonomy page correctly stays at
  the sector level of abstraction and doesn't need to enumerate every domain (that's the
  Sources page's job, out of this audit's scope per the task).
- **RSS feed (`/rss.xml`, run 78) and JSON-LD structured data**: not mentioned on
  methodology/taxonomy/about. Judged as appropriate abstraction, not staleness — these are
  delivery/SEO mechanisms, not claims about how signals are classified or reviewed, which
  is what a methodology page is for.
- **About page**: "AI Involvement"/independence/corrections claims cross-checked against
  `report_schema.py`'s `revision_history` mechanism and matched. No change needed.
- **Taxonomy page**: confidence/volatility/origin-classification tables match
  `CONFIDENCE_LEVELS`, `VOLATILITY_LABELS`, `ORIGIN_CLASSIFICATIONS` in `taxonomy.py`
  exactly. No change needed.

## Fix applied

Edited `web/app/methodology/page.tsx` only:
- Added one sentence to "Source Sectors" on the `unclear` fallback.
- Added one paragraph to "How Confidence Is Assigned" on same-sector-vs-cross-sector
  reprint discipline and the high-reliability-sector citation-free-rehash exception.
- Added a new section "How Signal Recurrence Is Tracked" (persistent signal_id,
  per-signal history page, three-state dormancy handling) between "How Low-Volatility
  Windows Are Reported" and "Corrections".

No changes to `taxonomy/page.tsx`, `about/page.tsx`, `report_schema.py`, or `taxonomy.py`.

## Validation

```
cd web && npx tsc --noEmit   # clean
npx eslint .                 # clean
npm run build                # succeeded, 176 pages incl. 87 /signals/[slug] paths, pagefind indexed 171 pages
```

No `.env` or secret values were read, logged, or printed during this audit.
