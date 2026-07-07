# Real report: 2027-04-19 (43rd weekly window)

Created `data/reports/2027-04-19.json`, collection window Apr 13-19, 2027.

## A genuinely new signal instead of another status update

WebSearch confirmed FW27-28 women's ready-to-wear and Haute Couture SS27 remain
without reachable post-show coverage, unchanged from the prior eleven windows.
Unlike the last several windows, this one has a real new development:
Moschino named Loris Messina and Simone Rizzo (the former Sunnei founders) as
co-creative directors, two days after Adrian Appiolaza's departure --
independently reported by WWD, W Magazine, and FashionUnited, among others.
Logged as a new signal (`moschino-messina-rizzo-appointment`), confidence
"medium" (all corroborating sources are editorial-sector, so `derive_confidence()`'s
cross-sector bar for "high" isn't met), volatility "flash" (a discrete dated
event, not a building trend). `collection_status` set to "normal" -- the first
non-"thin" window in a while, an honest call reflecting real new discourse
rather than continued republication of old material.

## Glamoratti: not repeated as a top signal this window

Checked `glamoratti-revival` again per convention; search surfaced no outlets
beyond those already logged in the 2027-04-05 and 2027-04-12 reports. Rather
than repeat an unchanged status as a top_signals entry, it's noted once in
`limitations` that its last recorded status (medium/saturated) stands
unchanged. `human_editor_note` on the new Moschino signal explains the
confidence/volatility reasoning explicitly rather than restating the evidence.

## Wales Bonner/CFDA: not re-litigated

Per SKILL.md workflow note 10, checked briefly -- no coverage beyond what's
already archived was found for either. Both remain noted as untracked
pending new information; not re-opened.

## Verification

- Checked existing `signal_id`s across all 42 prior reports before writing --
  `moschino-messina-rizzo-appointment` is new, no collisions.
- `python -m py_compile src/*.py` -- passed.
- `python src/validate_all_reports.py` -- `OK: all 43 report(s)... passed
  schema validation.`
- Saved via `report_schema.save_report()`.
- Scratch script (in the session scratchpad, not the repo) deleted after use.

Not committed, per instructions.
