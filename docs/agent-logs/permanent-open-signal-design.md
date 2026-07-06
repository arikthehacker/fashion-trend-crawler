# Design note: permanently-unresolved factual questions

TODO.md asked whether prolonged silence on the CFDA Fashion Fund winner and CFDA
Fashion Awards (both past `is_prolonged_silence()`'s threshold as of the
2026-12-21 report) should eventually get an "awaiting resolution" status.

## Why the existing close-out pattern doesn't apply

The archive already has a pattern for dormant STYLE signals going quiet
(off-duty-varsity, layered-tops-styling): an `EDITORIAL CLOSE-OUT` note in
`human_editor_note` declaring the signal resolved/faded. That's legitimate there
because "discourse about this dropped off" is itself an observable, true fact.

It is NOT legitimate for a tracked FACTUAL question like "who won the CFDA
Fashion Fund." Silence from the crawler means "not found," not "resolved" or
"didn't happen." Reusing the close-out language would assert an answer (or a
non-answer) the archive doesn't actually have — a fabrication by omission,
which violates the project's core honesty rule (uncertainty must be stated
plainly, never smoothed over).

## Convention adopted

A third, distinct state for prolonged-silence factual questions: once
`is_prolonged_silence()` has returned True for several consecutive windows
running (~3 windows past the initial crossing, a coordinator/human judgment
call, not a hardcoded second threshold), a report may mark the signal_id
**"untracked going forward pending new information"** in prose
(`human_editor_note`/`index_note`/`archive_tags`), instead of re-asserting
"still open" every single week.

This is honest in both directions:
- Not "resolved" — no answer is claimed.
- Not silently dropped — the archive states plainly that it has stopped
  actively re-litigating the question weekly, and why.

Any future report that finds real coverage should resume normal
tracking/resolution for that signal_id — this convention is a pause on
re-asking, not a permanent seal.

## Why no schema change

No new enum value or schema field was added. `is_prolonged_silence()` is
already a computed-on-demand helper (not a stored field) precisely so this
kind of cross-report judgment doesn't need a schema commitment that goes
stale. The new state is expressed the same way close-outs already are: prose
in existing free-text fields. If this convention gets used a few times and a
structured field turns out to be genuinely useful, that's a future schema
change made from evidence of actual use, not speculative now.

## Files changed

- `src/report_schema.py` — expanded `is_prolonged_silence()`'s docstring with
  this reasoning and the convention, explicitly contrasting it with the
  dormant-signal close-out pattern.
- `.claude/skills/ari3lla-index/SKILL.md` — added workflow convention #10
  documenting the same, referencing the two CFDA signal_ids as the current
  concrete case.

Verification: `python -m py_compile src/*.py` passed. No schema/report data
files touched; no commit made.
