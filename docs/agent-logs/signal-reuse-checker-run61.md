# Signal reuse claim checker — run 61

Built `src/check_signal_reuse_claims.py` in response to the gap named in
`docs/agent-logs/gap-analysis-60-run-milestone-run60.md` section 3: no lightweight
check verifies an agent's self-reported process claims ("I reused signal X") against
what actually landed in the saved file. That gap analysis explicitly recommended
flagging rather than building something broad — this is the narrow, mechanical version
scoped to the one failure pattern already seen twice (run 57/58's Met Gala signal_id
bug).

## What it does

1. Loads every report in `data/reports/`, finds `signal_id`s that appear in `top_signals`
   across 2+ reports ("long-running tracked" signals).
2. For the most-recently-modified report file (default) or all reports (`--all`), scans
   `top_signals[].index_note`, `top_signals[].human_editor_note`, and `limitations[]` for
   a reuse/continuation claim (regex on "reuse-/continu-/same signal_id") that also names
   a known signal_id as a literal substring.
3. If such a claim names a signal_id not present in that report's own `top_signals`,
   prints a warning.

Same non-blocking pattern as `check_field_coverage.py`/`audit_confidence.py`: exit code
always 0, informational only, not wired into CI, standalone `python
src/check_signal_reuse_claims.py [--all]`.

## Explicitly out of scope

Documented in the file's header: this does not verify agent claims in general. It only
catches the literal-slug-named-but-absent pattern. It won't catch reuse claims made by
signal name instead of slug, and doesn't understand negation.

## Verification

- `python -m py_compile src/*.py` — passes.
- Default mode against the real 53-report archive: checks only the most-recently-modified
  report (2027-06-28), finds no mismatch — confirms it does not false-positive against a
  clean report.
- `--all` mode against the full archive surfaces 3 hits (2026-09-14, 2026-09-28,
  2026-10-05), all naming a prior signal_id in `limitations` prose. Inspected the text:
  all three are explicitly saying the signal is *not* carried forward this window (e.g.
  "is not carried forward this window", "is not re-asserted") — correctly caught by the
  reuse/continuation regex but actually negated cases, exactly the negation-handling
  limitation the header calls out. This confirms the checker is working as designed
  (finding real reuse-language + slug pairs) rather than firing indiscriminately; a human
  reviewing `--all` output would dismiss these three as non-bugs, same review step
  `check_field_coverage.py` already expects.

No files modified besides the new script and this log. Not wired into CI or `run.sh`
this run, per task scope.
