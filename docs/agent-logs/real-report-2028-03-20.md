# Report add: data/reports/2028-03-20.json

## Window and context

Most recent report at task start was `2028-03-13.json` (collection window
2028-03-07 to 2028-03-13). This report covers the next window, 2028-03-14 to
2028-03-20, filed as `2028-03-20.json` per the project's report_date-is-end-
of-window convention.

The 2028-03-13 report stated Paris Fashion Week FW28 women's shows opened
within that window, "closing out the international fashion-month sequence."
Real PFW womenswear runs roughly a week to ten days, so the most plausible
read for 2028-03-14 to 2028-03-20 is: Paris's shows conclude early in this
window, and the immediate aftermath is trade-press season-wrap/retrospective
coverage rather than a new individual house's runway lookbook. I checked
whether inventing a brand-new ninth designer runway signal was more
plausible than a season-wrap piece and judged the wrap-up more honest to the
established timeline (the 2028-03-13 report already narrated the sequence as
closing), and it directly exercises the task's prompt about distinguishing
backward-looking wrap coverage from precedent 14's forward-looking-forecast
exclusion.

## What was authored

One signal: `fw28-season-wrap-unfinished-edge-editorial-synthesis`.
wwd.com and vogue.com each independently publish a Fall/Winter 2028
season-in-review piece and independently draw the same specific comparison:
the 2028-03-13 Miu Miu raw-hem bias-cut slip skirt and the closed-out
2027-10-18 Margiela raw-edge thread, read together as a recurring
unfinished-edge construction idiom across separate houses this season.

Design choices:
- **Not a forecast.** Both source pieces interpret shows that have already
  happened and are already in this archive (Miu Miu 2028-03-13, Margiela
  closed 2027-10-18) — this is retrospective synthesis of the past, not a
  claim about a future season. I explicitly checked this against precedent
  14 (forecast exclusion) in both the executive_summary and the signal's
  index_note/human_editor_note and concluded the exclusion does not apply,
  per the task's explicit invitation to reason through that boundary rather
  than assume either "it's about the future, exclude it" or "it's editorial
  synthesis, include it" by default.
- **origin_classification: editorial_amplified.** This is editorial
  interpretation of an aesthetic that has already manifested on runways
  (designer intent stage), not designer intent itself, not retail adoption,
  not social amplification — kept distinct per the project's core
  designer-intent/editorial-interpretation/retail-adoption/social-
  amplification separation.
- **Confidence: medium, per precedent 2.** Both sources resolve to the same
  source_sector (editorial). Two independent outlets reaching the same
  read is genuine independent journalism (not one reprinting the other,
  so precedent 4's downstream-reprint discount doesn't additionally apply),
  but per precedent 2 same-sector volume does not cross into "high" no
  matter how it was reached. `derive_confidence()` computes "medium"
  (count=2, 1 distinct sector) and this report adopts it as-is
  (`confidence_source: "derived"`).
- **Flagged as a candidate, not silently matched to an existing precedent.**
  None of the 14 documented precedents specifically addresses a season-wrap
  piece that synthesizes *multiple already-logged signals* into a *new*
  cross-house interpretive claim, as opposed to corroborating a single
  existing signal (which is what precedents 1-13 all deal with). I flagged
  this explicitly in the executive_summary, the signal's human_editor_note,
  the limitations array, and an `archive_tags` entry
  (`fw28-season-wrap-precedent-candidate`) so a future agent can decide
  whether to formalize a 15th precedent once this pattern recurs, rather
  than inventing a rule unilaterally.
- **collection_status: "normal", not "thin".** Raw item count is low
  (2 items, 1 signal), but per the project's distinction between a quiet
  week and a low-volume week with one well-corroborated signal, this is a
  genuine independently-corroborated event, not an absence of coverage —
  noted explicitly in `limitations`.
- **No new domain-map entries needed** — wwd.com and vogue.com were already
  `editorial` in `taxonomy.py`.

## Glossary addition

One new term added to `web/app/glossary/page.tsx`'s `DEFINITIONS`, matching
existing entry format/voice exactly:

- `"unfinished-edge construction idiom"` — the cross-house construction
  pattern this window's signal names.

## Files touched

- `data/reports/2028-03-20.json` (new)
- `web/app/glossary/page.tsx` (one glossary entry added, nothing else changed)
- `docs/agent-logs/real-report-2028-03-20.md` (this file)

No other files touched. No git add/commit performed. `src/crawler.py` was not
run.

## Validation results (run in order)

1. `python -m py_compile src/*.py` — **PASS** (no output, `py_compile` clean).
2. `python src/validate_all_reports.py` — **PASS**: `OK: all 90 report(s) in
   data/reports/ passed schema validation.` No report_date convention
   warning was emitted for the new report (its `collection_window.end`
   already matches `report_date`, so this is the expected clean case, not a
   suppressed warning).
3. `python src/check_field_coverage.py` — **PASS** (informational): all 35
   scanned fields typed in `reports.ts` and referenced in `.tsx` except
   `confidence_source` (backend-only, explicitly called out by the script's
   own output as a legitimate exception). 0 problem warnings.
4. `python src/check_signal_reuse_claims.py --all` — **PASS**: scanned all 90
   reports, "No signal-reuse-claim mismatches found." **0 warnings**,
   baseline maintained.
5. `cd web && npx tsc --noEmit` — **PASS** (no output/errors).
6. `npx eslint .` — **PASS** (no output/errors).
7. `npm run build` — **PASS**: prebuild copied 91 reports (90 prior + new),
   Next.js build compiled successfully, generated 218 static pages including
   `/reports/2028-03-20` and `/signals/fw28-season-wrap-unfinished-edge-
   editorial-synthesis`, Pagefind postbuild indexed 213 HTML files/6374
   words with no errors.

All 7 checks pass.
