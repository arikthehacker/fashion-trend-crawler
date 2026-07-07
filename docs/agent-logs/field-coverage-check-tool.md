# Field coverage check tool

Built `src/check_field_coverage.py` per TODO.md's request for a structural fix
to the "populated but unrendered" bug pattern found in three consecutive
sweeps (runs 21, 23, 24 — see `docs/agent-logs/transparency-field-sweep-run24.md`).

## What it does

1. Enumerates every field name on `Report` and `Signal` via
   `dataclasses.fields()` (read-only import from `report_schema.py`, no
   changes to that file).
2. Greps `web/lib/reports.ts` for each field name (word-boundary regex) to
   check whether it's typed in the TS interfaces.
3. Greps every `web/app/**/*.tsx` file for each field name to check whether
   it's referenced anywhere in JSX.
4. Prints a per-field yes/no table, then a warning list: fields typed in TS
   but never referenced in any `.tsx` — the same signature as the bug the
   prior sweeps found.

Like `audit_confidence.py`, this is non-blocking (always exits 0, not wired
into CI) and explicitly a rough heuristic, not precise static analysis — it's
a plain substring/word-boundary search, so it can't tell a real render from a
comment or a same-named unrelated field. A `KNOWN_BACKEND_ONLY_FIELDS` set
(`confidence_source`, `content_hash`) suppresses fields already confirmed
legitimate backend-only metadata by prior sweeps, so the tool doesn't nag
about known-good decisions on every run.

## Verification

- `python -m py_compile src/*.py` — passes.
- Ran `python src/check_field_coverage.py`: 33 fields scanned, 0 warnings.
  - `confidence_source` correctly shows `typed in TS: no` / not flagged
    (it isn't in the TS interface at all, and is also in the suppression
    set as a belt-and-suspenders check).
  - `revision_history` and `thin_week_note` (fixed in earlier runs) both
    show `yes`/`yes` — typed and referenced — confirming they're no longer
    flagged.
  - `human_editor_note` is not a `Report`/`Signal` dataclass field (it lives
    as an ad hoc key enforced by `manual_sample.py`, not in the schema
    dataclasses), so it's out of scope for this enumeration and doesn't
    appear in output either way.
  - Two fields, `review_status` and `reviewed_by`, show `no`/`no` (not
    typed in TS, not referenced) — not flagged as warnings since they fail
    the "typed but unreferenced" precondition, but worth a human glance:
    they may be a legitimate backend-only provenance pair, or a newer gap
    the tool's precondition doesn't catch. Recommend a manual look before
    adding them to `KNOWN_BACKEND_ONLY_FIELDS`.

## Files touched

- `src/report_schema.py` — read-only, no edits.
- `src/check_field_coverage.py` — new file.
