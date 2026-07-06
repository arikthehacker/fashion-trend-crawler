# Real report: 2027-04-05 (41st weekly window)

Created `data/reports/2027-04-05.json`, collection window Mar 30 - Apr 5, 2027.

## Fashion month and Haute Couture SS27 still unconfirmed; new item is a Pinterest Predicts aesthetic term

WebSearch confirmed FW27-28 women's ready-to-wear remains closed. Haute Couture SS27
is scheduled per FHCM's calendar for Jan 25-28, 2027, but no reachable post-show
coverage exists yet in search results -- consistent with the prior nine windows, since
real-time search indexing lags behind that future date. The one new item is
"Glamoratti," an 1980s power-dressing revival named in Pinterest's annual Predicts
trend report (sculpted shoulders, funnel-neck jackets, metallic fabrics, unsubtle
jewelry), amplified across multiple editorial outlets (Marie Claire, Grazia, others).
Logged as a new, distinct signal (`glamoratti-revival`) rather than folded into last
window's `ss27-trend-forecast`: that signal was commercial-forecasting-outlet
terminology for an upcoming season, this one is a season-agnostic annual aesthetic
call originating from a social platform's first-party data product. Also checked
"Poet-Core" as a possible recurrence, but confirmed `poetcore-aesthetic` was already
archived (2026-07-20) as a distinct, unrelated literary/preppy aesthetic -- not
reused here to avoid a false-recurrence claim. Medium confidence, emerging
volatility, social_amplified origin (platform data, not scraped/UGC, per SKILL.md
workflow note 6). `collection_status` set to `"thin"` again: fashion month remains
closed and the only in-window discourse is a single platform-originated signal.

## Wales Bonner/Hermes and CFDA: not re-litigated

Per SKILL.md workflow note 10, checked briefly but did not reopen. Searches surfaced
only already-known appointment/team-building coverage (WWD's designer-hire story) and
no 2027 CFDA announcement. Both remain untracked pending new information.

## Verification

- Checked existing `signal_id`s across all reports before naming the new one
  (`glamoratti-revival`) -- no collisions.
- `python -m py_compile src/*.py` -- passed.
- `python src/validate_all_reports.py` -- `OK: all 41 report(s)... passed schema
  validation.`
- Saved via `report_schema.save_report()`.
- Scratch script (`scratch_build_20270405.py`, in the session scratchpad, not the
  repo) deleted after use.

Not committed, per instructions.
