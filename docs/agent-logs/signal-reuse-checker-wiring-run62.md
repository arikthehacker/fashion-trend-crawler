# Signal reuse checker — wiring decision, run 62

## What was run

`python src/check_signal_reuse_claims.py --all` against the full archive: 54 reports,
17 signal_ids appearing in 2+ reports. Result: 4 warnings, 0 real mismatches.

All 4 are false positives from the checker's documented negation/precedent-mention
limitation:
- 2026-09-14, 2026-09-28, 2026-10-05: same pattern run 61 already found — "is not
  carried forward" / "is not re-asserted" language correctly matched by the reuse
  regex but actually negated.
- 2027-06-28 (new): `met-gala-2027-coverage-gap`'s index_note cites
  `wales-bonner-hermes-debut` as a *precedent example* of the same close-out handling,
  not as a claim that this report reuses that id. Same class of false positive —
  literal slug substring + reuse-language nearby, no actual reuse claim.

Two full-archive runs (61, 62), zero true positives, consistent false-positive class.
The checker is working as designed; it just hasn't caught a live instance of the bug
it targets since run 57/58.

## Decision: standing step, not ad hoc

Made `check_signal_reuse_claims.py --all` a standing part of the periodic-audit
routine, documented in `.claude/skills/ari3lla-index/SKILL.md` (file-map entry plus a
new numbered convention, item 12). Reasoning: it's cheap, non-blocking, exit-code-0
always, and targets a real bug class (run 57/58) even though it hasn't fired a true
positive since. Ad hoc/"remember to run it sometime" is how narrow scripts like this
get built and then forgotten — `audit_confidence.py` and `check_field_coverage.py`
already made the jump from "reusable script" to "expected periodic-audit step," and
this fits the same shape. The one real cost is a human needing to skim ~4 false
positives per run, which is fast once the negation/precedent pattern is known (now
documented inline in SKILL.md so future runs don't re-diagnose it from scratch).

## Decision: leave `validate_all_reports.py` alone

Considered having it mention `check_signal_reuse_claims.py` exists. Declined —
`validate_all_reports.py` doesn't reference `audit_confidence.py` or
`check_field_coverage.py` either (its own non-blocking warning is only about
`derive_confidence()`, generated internally, not a pointer to a sibling script).
Adding a cross-reference to just this one new script would be inconsistent and is
scope creep relative to its job (CI-blocking schema gate). SKILL.md's file map + item
12, and TODO.md, are the already-established place non-blocking sibling scripts are
tracked.

## Files changed

- `.claude/skills/ari3lla-index/SKILL.md` — file-map entry for
  `check_signal_reuse_claims.py` updated with run 62 findings + standing-step
  decision; new convention item 12.

No code changes. `python -m py_compile src/*.py` passes.
