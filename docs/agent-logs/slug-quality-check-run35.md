# Slug quality check (run 35)

Grepped all `signal_id` values across `data/reports/*.json`
(`"signal_id":\s*"[^"]+"`). Checked against run 6's precedent threshold
(~4 hyphenated words).

**Found 11+ signal_ids exceeding the threshold** — well over the 5-candidate
cap for this task's scope, so per instructions: no changes made, findings
only.

Candidates found (5+ words each):

- `lfw-eligibility-wholesale-requirement-dropped`
- `pfw-ss27-schedule-date-inconsistency`
- `versace-mulier-debut-timing-unconfirmed`
- `armani-post-founder-transition-continues`
- `cfda-vogue-fashion-fund-2026-winner` (recurs across 7+ reports)
- `cfda-vogue-fashion-fund-2026-finalists`
- `nyfw-ss27-trend-forecast-content-integrity-flag`
- `mfw-ss27-schedule-date-inconsistency`
- `back-to-school-2026-y2k-preppy`
- `2026-black-friday-cyber-monday-outcome`
- `2026-black-friday-early-retail-calendar`
- `pantone-fall-2026-devil-wears-prada-tie-in`

Note: several of these (`cfda-vogue-fashion-fund-2026-winner`,
`cfda-fashion-awards-2026`) are tracked per the "prolonged silence" /
FACTUAL-question convention (skill doc item 10) and recur across many
reports — renaming them would need careful cross-report consistency
checking, not a quick shortening pass. This is exactly the kind of
judgment call the task scope flagged as out of bounds (>5 candidates).

No files modified. No verification run (no changes made).

**Recommendation:** a follow-up task should scope this properly — decide
on a per-signal basis whether shortening is safe (checking for external
references e.g. `web/app/signals/[slug]/page.tsx` usage) before renaming
any of these, especially the recurring CFDA ones.
