# Report build log: data/reports/2026-09-28.json

Window: 2026-09-22 to 2026-09-28 (Milan leg of fashion month, per
`docs/EDITORIAL_CALENDAR.md`). Built via WebSearch research, no live crawl.

## Continuing signals from 2026-09-21

Checked `get_signal_status_history()` for all three signal_ids before writing:

- `nyfw-ss27-close` and `lfw-ss27-week-opens`: both describe weeks that had
  already fully ended before this window opens (NYFW Sept 15, LFW Sept 21).
  Treated as closed/resolved, not carried into `top_signals`; noted in
  `limitations` instead of silently dropped.
- `lfw-eligibility-wholesale-requirement-dropped`: no new verifiable reporting
  on its downstream effects (e.g. which designers without wholesale
  distribution actually showed) surfaced this window. Treated
  continuing-but-quiet, not re-asserted without new evidence — same
  discipline the 09-21 report used for its own inherited signals.

## What's in the report and why

Three `top_signals`, all newly opened this window:

1. **`mfw-ss27-schedule-date-inconsistency`** (media_integrity, low
   confidence) — research turned up three different date ranges for Milan
   SS27 women's week across sources: Sept 16-22 (on Camera Nazionale della
   Moda Italiana's own Milano Fashion Week SS 2027 site, alongside
   suspicious pre-show "trend forecast" language describing 1980s-inflected
   tailoring as an already-observed theme before the week occurred), Sept
   22-28, and Sept 23-29 (this archive's own editorial-calendar reference).
   No authoritative single source reconciled these, so the discrepancy is
   logged as a finding rather than silently resolved. This mirrors the
   09-14 report's "trend forecast published before the week happened"
   media-integrity flag.
2. **`versace-mulier-debut-timing-unconfirmed`** — Pieter Mulier's move from
   Alaia to Versace creative director formally took effect July 1, 2026
   (WWD), but no confirmed show date within this window surfaced. Logged as
   pending, not reported.
3. **`armani-post-founder-transition-continues`** — Silvana Armani/Leo
   Dell'Orco's joint post-founder direction of the Armani house continues;
   their most recent confirmed joint show was June 22, 2026 (outside this
   window). No SS27 Milan women's show date confirmation found. Logged as
   pending.

`garments`/`silhouettes`/`colors`/`materials` left empty — no verifiable
show-specific reporting existed for a week that (per the schedule ambiguity
above) may not even have definitively started as of research time.

## Sources

WebSearch queries covering: Camera Nazionale della Moda Italiana's SS 2027
calendar page, Milan designer-calendar aggregator sites, WWD/Hypebeast/Dazed
coverage of Gucci/Versace/Armani creative-director transitions, and AP wire
coverage of Armani's succession. No fabricated show reviews or runway-look
content included, per project discipline for pre-event windows.

## Verification

`python -m py_compile src/*.py` — passed.
`python src/validate_all_reports.py` — `OK: all 14 report(s) in data/reports/
passed schema validation.` No new confidence warnings.
