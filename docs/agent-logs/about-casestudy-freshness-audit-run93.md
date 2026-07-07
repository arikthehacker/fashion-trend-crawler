# About / case-study freshness re-audit — run 93

Re-verified `web/app/about/page.tsx` and `web/app/case-study/page.tsx` for staleness,
12+ runs after the run-80 audit (85 reports now vs. ~73 then; crawler-hang fix landed
run 67; report_date convention bug+fix landed runs 91-92; confidence-discipline-
precedents.md now has 14 precedents).

## 1. Case-study "Current Limitations" section

Text: "Every report in the archive is hand-authored or research-assembled rather than
produced by a live crawl merged into the archive; a real crawl-and-summarize run has
succeeded once but its output was not merged, pending a deliberate resolution of a
same-date collision. Migration off the legacy cache-file pipeline is nearly, not fully,
complete."

Checked against TODO.md history:
- The crawler-hang fix (run 67) patched `crawl_all_sources()` to flush output
  incrementally instead of only at the end, verified only via `py_compile` — the
  crawler was never actually executed/merged as a result of that fix. It's a
  robustness patch to an unresolved pipeline, not a resolution of the pipeline being
  unresolved.
- The report_date validation fix (run 92) fixed a filename/date convention bug in the
  hand-authored report-authoring workflow (documented the `report_date ==
  collection_window.end` convention, added a non-fatal validator warning). It has
  nothing to do with the live-crawl-merge status.
- The one successful real crawl-and-summarize run and its unresolved same-date
  collision (`docs/agent-logs/live-crawl-2026-07-06-real-output.json`) are unchanged
  since run 80 — still not merged, still pending.

Conclusion: the "Current Limitations" framing remains accurate. Neither fix changed
what's automated vs. manual/pending — both fixes made existing processes (crawler
robustness, hand-authored report filing) more correct without changing which process
produces the live archive. No edit made.

## 2. About page re-read in full

No claim in About page is tied to a specific report count, run number, or pipeline
milestone — it describes what the Index is/isn't, editorial independence, and the
current single-researcher / same-automated-process-reviews-itself state, all of which
remain true. The "AI assists with crawling, extraction, and summarization... review is
currently carried out by the same automated process that drafts the report" claim is
still accurate — no separate human editor has been introduced. No staleness found.

## 3. confidence-discipline-precedents.md mention?

Read `docs/confidence-discipline-precedents.md` (437 lines, 14 precedents) — it's an
internal agent-operating reference (documents manual overrides to
`derive_confidence()` for future report-writing agents), not reader-facing
methodology. The Methodology page's "How Confidence Is Assigned" section already
covers the reader-relevant substance in prose (corroboration requirement, the
single-source high-reliability-sector override, downstream-reprint exclusion) without
naming the internal tracking doc. Run 92 already made and logged the judgment call not
to duplicate this content onto the Taxonomy page for the same reason.

Applying the same judgment here: About and Case Study sit at an even higher altitude
than Methodology/Taxonomy (audience-facing framing vs. process detail), so naming a
14-precedent internal implementation doc there would be over-detailed and
inconsistent with those pages' tone. No addition made — consistent with the run-92
precedent-setting decision, no redundant content added across pages.

## Result

No staleness found. Both pages remain accurate as of run 93. No code changes made.

## Validation

`cd web && npx tsc --noEmit && npx eslint . && npm run build` — all pass (no files
changed, but ran per instructions to confirm baseline is clean).
