# Real report: 2026-10-05 (15th weekly window)

Created `data/reports/2026-10-05.json`, collection window Sept 29 - Oct 5,
2026 — inside Paris Fashion Week's SS27 women's season, the final leg of
fashion month, and the window this archive uses to close out fashion-month
coverage.

## Research (WebSearch, verifiable facts only)

- **PFW SS27 dates**: confirmed via multiple sources as Sept 28-Oct 6, 2026
  (women's), one day earlier than this archive's own editorial-calendar
  reference (Sept 29-Oct 6). Logged as a new `media_integrity` signal
  (`pfw-ss27-schedule-date-inconsistency`), explicitly framed as a
  continuation of the same pattern flagged for Milan in the Sept 28 report
  (`mfw-ss27-schedule-date-inconsistency`) — that Milan signal was **not**
  re-verified this window (effort went to Paris), so it stays open, not
  resolved.
- **`versace-mulier-debut-timing-unconfirmed`**: resolved. Hypebeast,
  FashionUnited, and RUSSH all report Versace/Prada Group confirmed Mulier's
  first collection is delayed to early 2027 — outside this fashion month
  entirely. Carried forward under the same signal_id, volatility moved
  emerging -> declining, confidence held at medium (single-sector,
  likely one underlying brand statement echoed three times).
- **`armani-post-founder-transition-continues`**: resolved. WWD confirms a
  Giorgio Armani mainline show Sept 28, 2026 at Brera Pinacoteca (Emporio
  Armani shows Sept 27). Both dates fall just before this window opened, so
  logged as a retrospective resolution, not an in-window event — no show
  content/reception is asserted.
- **`lfw-eligibility-wholesale-requirement-dropped`**: still continuing-but-
  quiet, no new downstream reporting found; not re-asserted.

No fabricated show reviews or content — only pre/post-event schedule and
confirmation facts, per the discipline established in runs 19-21.

## Post-fashion-month volume note

Flagged explicitly in `limitations`: this window closes the Sept 8-Oct 6
fashion-month stretch. Consistent with the pattern across runs 19-22, volume
and volatility should be expected to drop back to the lower pre-fashion-month
baseline (thin-but-normal reports) starting with the next window — that
expected drop should not be read as a crawl/sourcing regression.

## Verification

- `python -m py_compile src/*.py` — passed.
- `python src/validate_all_reports.py` — `OK: all 15 report(s)... passed
  schema validation.` No confidence-derivation warnings emitted.
- Saved via `report_schema.save_report()` (two saves: initial, then one
  correction after fixing a mojibake character in an accented word, which
  produced a `revision_history` entry per the schema's correction-tracking
  design).

Not committed, per instructions.
