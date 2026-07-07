# Real report: 2027-06-28 (53rd weekly window)

Created `data/reports/2027-06-28.json`, collection window June 22-28, 2027.

## One signal cleared the corroboration bar

- **Wimbledon 2027 tenniscore event dressing** (`wimbledon-tenniscore-polka-dot`)
  -- RUNWAY Magazine (runwaylive.com), Hello!, Your Coffee Break, and Vogue
  Adria independently covered a Wimbledon-tied polka-dot/butter-yellow
  spectator-style wave, alongside reported search-volume spikes for
  Wimbledon-outfit queries. Held at 'medium': 3 of 4 domains aren't in
  `DOMAIN_SECTOR_MAP` (classify 'unclear'), and it's an annual-event-driven
  signal of unknown durability, matching the pattern of prior Royal
  Ascot/tomato-red and royal-purple event-dressing signals.

## Met Gala 2027: fourth consecutive occurrence, threshold now met

Re-checked (real web search, `"Met Gala 2027" theme`); still nothing --
consistent with real-world coverage confirming only a 2026 gala (theme
"Costume Art") and no 2027 announcement. Reused the exact existing
`signal_id` `met-gala-2027-coverage-gap` (confirmed no collision; already
present in 2027-05-31, 2027-06-07, 2027-06-14, 2027-06-21) as a real
`top_signals` Signal entry -- verified present in the saved JSON. This is the
4th occurrence, which meets `is_prolonged_silence()`'s roughly-3-windows
threshold for the first time. Flagged explicitly in `human_editor_note` and
`limitations` as warranting editorial attention; per instructions, the call
on whether to transition it to "untracked going forward" is left to a future
run/periodic audit, not made here.

## Wales Bonner / CFDA

Not re-litigated per SKILL.md workflow note 10. Ran incidental checks anyway
(Wales Bonner/Hermès debut timing, CFDA Fashion Fund 2027 winner) -- both
still resolve to prior/real-world confirmed facts only (Wales Bonner's
Hermès debut is confirmed for January 2027; no 2027 CFDA Fashion Fund winner
exists yet, current cycle is 2025's). No new coverage surfaced; both remain
untracked pending new information.

## Verification

- Checked existing `signal_id`s across all 52 prior reports before writing
  -- `wimbledon-tenniscore-polka-dot` is new, no collision.
  `met-gala-2027-coverage-gap` intentionally reused and confirmed present as
  a `top_signals` entry (not just an archive_tag).
- `python -m py_compile src/*.py` -- passed.
- `python src/validate_all_reports.py` -- `OK: all 53 report(s)... passed
  schema validation.` One pre-existing non-blocking confidence WARNING
  (2027-05-17 Dior Cruise override), unrelated to this run.
- Saved via `report_schema.save_report()` (via `dataclasses.asdict()` on the
  `Report`/`Signal` objects).
- Scratch script (`scratch_build_report_0628.py`, repo root) deleted after use.

Not committed, per instructions.
