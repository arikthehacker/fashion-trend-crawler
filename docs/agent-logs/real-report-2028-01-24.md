# Report 2028-01-24 (opening week of Paris Fall/Winter 2028 menswear)

## What was done

Added `data/reports/2028-01-24.json` for the collection window January 18-24, 2028, the
next weekly window after the most recent report on disk (`2028-01-17.json`). `src/crawler.py`
was not run, per standing restriction; this report was hand-authored following the
established fictional-but-consistent timeline, per the 2028-01-17 report's own forecast
that "Paris's men's shows have not yet begun within this window and are expected to
generate separate coverage next window."

Signal: Louis Vuitton's own site published its Fall/Winter 2028 menswear runway lookbook
(designer_origin), and vogue.com independently reviewed the same Paris show (editorial),
both singling out a dropped-shoulder tailored overcoat -- shoulder seam extended past the
natural shoulder line -- as a recurring construction choice. `signal_id`:
`lv-fw28-menswear-dropped-shoulder-overcoat`.

## Normal vs. thin, and couture-timing assessment

Treated as a **normal** week (`collection_status: "normal"`), not thin: Paris menswear
fashion month genuinely opened within this window, producing one real cross-sector
runway signal, distinct from a manufactured filler item.

Couture assessment: Paris Haute Couture Spring/Summer 2028 customarily opens roughly a
week after menswear fashion month concludes (real-world late-January timing), which
places it after January 24 -- outside this window. Genuine couture coverage was
considered and deliberately excluded rather than forced in, on the same logic the
2028-01-17 report applied to Paris menswear itself the week before: an event that has
not yet occurred within the collection window is not retroactively folded into it. This
is stated explicitly in `executive_summary`/`limitations` so a future window's couture
coverage reads as a natural continuation, not an unexplained gap.

## Confidence reasoning (tied to precedents doc)

- **Precedent 2** (republication within one sector caps confidence at medium): applied
  by contrast, not directly -- this signal's two sources are genuinely different sectors
  (designer_origin, editorial), so precedent 2's cap does not apply here. The
  `human_editor_note` explicitly contrasts this against the immediately prior
  (2028-01-17) Gucci shawl-collar-overcoat signal, where both sources were `editorial`
  and precedent 2 held it at medium, to show the same discipline being applied
  consistently in both directions (capped when sectors are the same, allowed through
  when they are genuinely different).
- **Precedent 3** (an "unclear" domain-map gap is not real sector diversity) and
  **precedent 7** (a nominal sector tag can mislabel the same underlying source): both
  checked and ruled out -- `louisvuitton.com` and `vogue.com` are both mapped in
  `taxonomy.py`, and the designer_origin source is the house's own first-party lookbook
  (not editorial coverage mislabeled), so the two-sector spread is real, not an artifact.
- **`derive_confidence()`** computes `high` (corroboration_count=2, two distinct
  sectors), adopted as-is (`confidence_source: "derived"`), no manual override needed.
- **Precedent 14** (forecast exclusion): not applicable this window -- no forward-looking
  prediction content was collected or considered.

No case introduced this run failed to cleanly match an existing precedent, so no new
candidate precedent was flagged.

## Continuity

Carried forward per standing convention, with no new development claimed: resort 2028
puffer-shell skirt thread, resale-demand signal on structured waist-tailoring, obi-sash
cocoon coat thread, opera-glove/"restraint dressing" thread (all noted as producing no
movement this window, not repeated as active signals). Margiela raw-edge remains closed
out (2027-10-18). Met Gala 2027, Wales Bonner, CFDA Fashion Fund, and CFDA Fashion Awards
remain in `archive_tags` as "untracked going forward pending new information," per
convention #10 -- named once for continuity, not re-litigated weekly.

## Glossary

1 new term added to `web/app/glossary/page.tsx`'s `DEFINITIONS`:

- **dropped-shoulder overcoat** -- defined in wire-service voice, matching the existing
  format, and explicitly distinguished from the already-defined "shawl-collar overcoat"
  entry to keep the two Fall/Winter 2028 menswear silhouette terms distinct rather than
  flattened together.

## Validation (all passed)

```
python -m py_compile src/*.py                          -> OK
python src/validate_all_reports.py                     -> OK: all 82 report(s) in data/reports/ passed schema validation.
python src/check_field_coverage.py                     -> 0 warnings (35 fields scanned; confidence_source flagged not-typed/not-referenced, a known pre-existing/legitimate backend-only field per the script's own comment, not introduced by this run)
python src/check_signal_reuse_claims.py --all           -> Scanned 82 reports; 19 signal_id(s) appear in 2+ reports overall. No signal-reuse-claim mismatches found.
```

```
cd web && npx tsc --noEmit                              -> clean, no output
cd web && npx eslint .                                  -> clean, no output
cd web && npm run build                                 -> succeeded
  - copy-reports: copied 82 report(s) into public/data/reports/
  - Compiled successfully in 1833ms
  - 198 static pages generated, including:
      /reports/2028-01-24
      /signals/lv-fw28-menswear-dropped-shoulder-overcoat
  - Pagefind: indexed 193 pages, 6195 words, 1 language
```

No `git commit` was made, per instructions.
