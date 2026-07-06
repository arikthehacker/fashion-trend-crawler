# Dormancy / prolonged-silence audit — run 82

## Purpose

Periodic audit (SKILL.md convention #10) of the full 74-report archive for any
`signal_id` that crossed `is_prolonged_silence()`'s threshold (>=4 recurrences,
`src/report_schema.py`), stayed open several more windows with no new coverage, and
was never transitioned to "untracked going forward pending new information" prose
per convention #10 — i.e. a real violation, not a hypothetical.

## Methodology

1. Loaded all 74 files under `data/reports/*.json`, sorted by `report_date`.
2. Collected every distinct `signal_id` appearing in any report's `top_signals`
   (90 distinct ids across the archive).
3. For each, called the real `get_signal_status_history()` / `is_prolonged_silence()`
   from `src/report_schema.py` (not a re-implementation) with `threshold=4`.
4. For every id where `is_prolonged_silence(...)` returns `True`, found the report
   date of its 4th appearance (the crossing point), then scanned every report dated
   at or after the crossing date for:
   - transition language: "untracked going forward", "untracked pending",
     "pending new information", "deprioritiz..." (in `limitations`, `index_note`,
     `human_editor_note`, `archive_tags`, `revision_history` reasons), or
   - resolution language: `\bresolved\b`, "editorial close-out", `\bclose-out\b`,
     "closed out", `\bfaded\b` (word-boundary regexes — first pass used naive
     substring matching and produced a false positive on `"resolved"` matching
     inside `"unresolved"`; fixed before treating any result as a finding).
5. Manually read the actual limitations/archive_tags text around every apparent
   match rather than trusting the keyword hit alone, since a keyword appearing
   *anywhere* in a report doesn't prove it's attached to the *right* signal_id
   (a report can transition one signal while still normally tracking another in
   the same limitations paragraph).

Script used: `scratch_dormancy_audit.py` at repo root (not committed — temporary,
left in place per task instructions not to commit; safe to delete).

Data audited was report JSON only; no `.env` or API key values were read, printed,
or referenced at any point.

## Signals that crossed the threshold

| signal_id | appearances | crossed at (4th appearance) | last appearance | outcome |
|---|---|---|---|---|
| `cfda-fashion-fund-winner` | 11 | 2026-11-16 | 2027-01-04 | transitioned — "untracked" tag family from 2026-12-07 onward, consistent through 2027-12-06 |
| `cfda-fashion-awards-2026` | 6 | 2026-12-21 | 2027-01-04 | transitioned — same "untracked" tag family, consistent through 2027-12-06 |
| `wales-bonner-hermes-debut` | 8 | 2027-02-08 | 2027-03-08 | transitioned — `wales-bonner-hermes-debut-untracked` tag first appears 2027-10-18, carried consistently through the rest of the archive |
| `met-gala-2027-coverage-gap` | 5 | 2027-06-28 | 2027-07-05 | transitioned same window as crossing — `met-gala-2027-untracked-pending-new-information` tag present 2027-06-28 onward |
| `paris-post-show-coverage-gap` | 6 (top_signals) + continued limitations mentions through 2027-04-26 | 2027-02-22 | last top_signals appearance 2027-03-08; last limitations mention 2027-04-26 | **was genuinely left hanging for a stretch, but this was already caught and fixed by run 57** — see below |

## The one real gap found, and its status

`paris-post-show-coverage-gap` crossed `is_prolonged_silence()` at 2027-02-22 and
continued to be referenced in `limitations` as "kept under normal tracking" /
"tracked under paris-post-show-coverage-gap" through 2027-04-26 (twelve consecutive
zero-coverage windows), with no transition language — a genuine violation of
convention #10 at that point in the archive's history.

However, per the 2027-05-31 report's own `revision_history`/limitations text, this
was already found and corrected by a prior periodic audit (run 57):

> "Correction (periodic audit, run 57): the Haute Couture Spring/Summer 2027
> post-show coverage gap (signal_id paris-post-show-coverage-gap ... itself well
> past this archive's prolonged-silence threshold) was inadvertently dropped from
> reports without any close-out note starting 2027-05-03 ... Per SKILL.md workflow
> note 10, this signal is formally marked 'untracked going forward pending new
> information' as of this report."

Checked every report from 2027-05-31 through the end of the archive (2027-12-06):
the `paris-post-show-coverage-gap` signal_id does not resurface with re-litigation
language; it simply drops out, consistent with a completed transition. No
regression found.

## Conclusion

**No unaddressed violation of convention #10 exists anywhere in the current
74-report archive.** All five signal_ids that ever crossed
`is_prolonged_silence()`'s threshold — `cfda-fashion-fund-winner`,
`cfda-fashion-awards-2026`, `wales-bonner-hermes-debut`, `met-gala-2027-coverage-gap`,
and `paris-post-show-coverage-gap` — have all been explicitly transitioned to
"untracked going forward pending new information" in prose/archive_tags, either at
the time (the CFDA pair, Wales Bonner/Hermes, Met Gala) or via a documented
retroactive correction (`paris-post-show-coverage-gap`, fixed run 57, verified
still holding as of this audit).

The `wales-bonner-hermes-debut` signal specifically named in the task prompt as the
one flagged in earlier runs (crossing recorded as of the 2027-06-28-era window) has
in fact already received its transition tag (`wales-bonner-hermes-debut-untracked`,
first appearing 2027-10-18) and has not been re-litigated since.

## No fix applied

Since no genuine unaddressed case was found, no `save_report(revision_reason=...,
corrected_at=...)` correction was made in this run, and
`python src/validate_all_reports.py` was not needed for a data change (repository
data was not modified). `scratch_dormancy_audit.py` was left at the repo root,
uncommitted, as the reusable methodology artifact for the next periodic audit;
TODO.md/CHANGELOG.md were not touched per task instructions.
