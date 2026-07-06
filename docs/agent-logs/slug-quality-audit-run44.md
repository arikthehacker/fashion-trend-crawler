# Slug quality audit (run 44)

Checked all `signal_id`s across all 37 current reports for length (2-4 word
convention). Everything renamed in run 36/38 stayed clean. Found 4 over-length
slugs introduced in the 8 reports added since run 36 (runs 38-43, dated
2027-01-11 through 2027-03-01):

| old | new |
|---|---|
| `golden-globes-2027-ceremony-date` (5 words) | `golden-globes-2027` |
| `wales-bonner-hermes-menswear-debut-2027` (6 words) | `wales-bonner-hermes-debut` |
| `paris-menswear-couture-fw27-calendar` (5 words) | `paris-couture-fw27-calendar` |
| `paris-january-2027-weeks-post-show-coverage-gap` (8 words) | `paris-post-show-coverage-gap` |

Confirmed distinct meaning vs. sibling slug `paris-menswear-fw27-lineup` (kept
as-is, 4 words, no rename needed) before renaming the couture-calendar one, to
avoid conflating two different Paris-menswear signals.

Applying run 38's lesson directly: instead of touching only the field where
each slug first appears, grepped raw report text for all 4 old strings across
every file in `data/reports/` up front. Found 14 total occurrences across 8
files (`2027-01-11`, `2027-01-18`, `2027-01-25`, `2027-02-01`, `2027-02-08`,
`2027-02-15`, `2027-02-22`, `2027-03-01`) — both the `top_signals[].signal_id`
field and later prose recurrences (`human_editor_note`/`index_note` mentions
of the same tracked signal in later weeks). Fixed all of them in one pass via
a single script doing whole-file string substitution before JSON parsing
(so both the JSON field and any prose sentence mentioning the slug as a bare
identifier are caught identically), then `save_report(revision_reason=...,
corrected_at="2026-07-06")` per file.

Pre-rename collision check: none of the 4 new slugs already existed elsewhere
in `data/reports/`.

## Verification

- Re-grepped all 4 old slugs across `data/reports/*.json` after the fix: the
  only remaining matches are inside the 8 new `revision_history[].reason`
  entries this run added (documenting what was fixed) — no stale references
  remain in `index_note`, `human_editor_note`, `executive_summary`, or
  `limitations` prose.
- `python -m py_compile src/*.py` — OK
- `python src/validate_all_reports.py` — OK, all 37 reports pass

No commits made, per instructions.
