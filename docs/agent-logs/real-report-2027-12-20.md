# Report authored: 2027-12-20 (window 2027-12-14 to 2027-12-20)

## What was done

Added `data/reports/2027-12-20.json`, the next weekly window after the most recent
existing report (`2027-12-13.json`). Hand-authored per instructions (crawler.py not run).
Added two new glossary DEFINITIONS entries plus two supporting entries (`dior`,
`the realreal`) to `web/app/glossary/page.tsx` for the new terms/sources introduced.

Mid-December themes used: tail end of resort 2028 preview coverage (a new silhouette,
distinct from the already-tracked obi-sash cocoon coat and Bogota/Sao Paulo structured-waist
threads) and holiday retail peak (a resale-platform demand signal). Per instructions, the
obi-sash coat, opera-glove/"restraint dressing", and year-end-retrospective threads were
explicitly NOT forced forward this window since they had no new development -- the
executive_summary and limitations both say so rather than repeating stale carry-forward
prose.

## Signals and confidence reasoning

**`resort-2028-puffer-shell-skirt`** (designer_origin: dior.com, editorial: vogue.com,
corroboration_count=2, confidence=high, confidence_source=derived).
`derive_confidence()` computes "high" mechanically: count >= 2 and 2 distinct sectors.
Adopted as computed, no override. Checked against every documented precedent that could
argue for holding it down and found none applicable:
- Precedent 3 (unclear-domain gap): both `dior.com` and `vogue.com` are mapped,
  high-reliability sectors in `DOMAIN_SECTOR_MAP` -- not unclear.
- Precedent 7 (mislabeled sector): Dior's lookbook is a first-party designer statement,
  not editorial secondhand description of a runway show.
- Precedent 4/5 (citation-free rehash): Vogue's account independently frames the
  silhouette as a cross-house season-wrap pattern, not a rehash of Dior's lookbook
  specifically.
- Precedent 6 (same-week coincidence, not corroboration): both sources describe the
  identical garment feature, not two unrelated signals sharing a window.
This is structurally identical to the 2027-12-06 obi-sash cocoon coat signal (also
adopted at "high" as computed), and the same reasoning is applied.

**`bogota-waist-tailoring-resale-holiday-demand`** (resale: therealreal.com,
corroboration_count=1, confidence=low, confidence_source=derived). `derive_confidence()`
computes "low" mechanically: count=1 and "resale" is not in `HIGH_RELIABILITY_SECTORS`
(editorial, designer_origin, institutional, independent_criticism), so neither the
cross-sector-high nor single-source-medium exceptions apply. Adopted as derived --
this is a plain, non-borderline application of the formula, not a case matching any of
the 12 documented override precedents. No new exception was invented for it. Per the
explicit instruction to flag rather than silently apply an undocumented exception if one
seemed warranted: I considered whether resale-platform data (unlike raw social/UGC)
might deserve a `HIGH_RELIABILITY_SECTORS`-style discount similar to the
`independent_criticism` addition (run 19), since TheRealReal's own reporting is a
first-party retailer disclosure, not anonymous social volume. I did **not** apply any
such exception here -- it has no precedent, and one single case is not enough basis to
invent one. Instead this is named explicitly in the report's own `limitations` field as
"a candidate for future review... flagged as an open question for the
confidence-discipline precedents doc rather than resolved unilaterally," so a future
run/human can decide whether to formalize it, without this report having quietly acted
as if it were already decided.

## Glossary

Added 4 entries to `web/app/glossary/page.tsx` DEFINITIONS: `dior` and `the realreal`
(new cultural_references sources that would otherwise trigger the glossary's build-time
"no DEFINITIONS entry" warning), and `puffer-shell skirt` / `quilted puffer-shell
silhouette` (new garment/silhouette terms introduced this window, added per task
instructions even though the glossary page's `loadGlossaryTerms()` only scans
`aesthetic_terms`/`cultural_references`/`top_signals[].name`, not the `garments`/
`silhouettes` arrays directly -- these two entries won't render unless referenced from
one of those three fields in a future report, but are present so the vocabulary is
defined before it's needed).

## Validation output

- `python -m py_compile src/*.py` -- PASS, no output.
- `python src/validate_all_reports.py` -- PASS: "OK: all 77 report(s) in data/reports/
  passed schema validation."
- `python src/check_field_coverage.py` -- PASS, 0 warnings ("0 field(s) typed in TS but
  never referenced in any .tsx").
- `python src/check_signal_reuse_claims.py --all` -- PASS, 0 mismatches ("No
  signal-reuse-claim mismatches found in the checked report(s)," scanned 77 reports).
- `cd web && npx tsc --noEmit` -- PASS, no output/errors.
- `npx eslint .` -- PASS, no output/errors.
- `npm run build` -- PASS: build completed successfully, 190 static pages generated
  including `/signals/resort-2028-puffer-shell-skirt` and
  `/signals/bogota-waist-tailoring-resale-holiday-demand`, Pagefind indexing completed
  (185 pages, 6108 words), no glossary build-time warnings printed (confirming both new
  terms and both new source entries resolved against DEFINITIONS).

All checks pass at baseline (0 warnings/errors).
