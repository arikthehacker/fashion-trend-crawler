# summarize.py revision_reason wiring

Scoped only to `src/summarize.py`, per `pipeline-rerun-design.md` option (c)
already implemented in `report_schema.save_report()`.

## Changes

- `summarize(pages=None, revision_reason=None, corrected_at=None)` now accepts
  and threads both optional params straight through to `save_report()`.
- Save call wrapped in try/except `SchemaValidationError`: if it fails because
  a differing report already exists for today's date and no
  `revision_reason` was supplied, prints a clear message telling the user to
  re-run with `--revision-reason "<why>" --corrected-at YYYY-MM-DD` and
  returns cleanly instead of a raw traceback. Any other `SchemaValidationError`
  (e.g. a genuinely malformed report) is re-raised.
- CLI (`__main__` block) gained `argparse` with `--revision-reason` and
  `--corrected-at` flags, defaulting to `None` — no interactive prompts,
  stays automatable. Default invocation (`python src/summarize.py`) behaves
  exactly as before for first-time saves.
- Imports added: `report_path`, `SchemaValidationError` from
  `report_schema`.

## Verification

- `python -m py_compile src/*.py` — passed.
- Scratch script (not committed, run from scratchpad, cleaned up after):
  used `report_schema.save_report()` directly against throwaway date
  `2099-01-01` to simulate the three cases (couldn't invoke `summarize()`
  end-to-end without a live Anthropic API call):
  1. First save (no existing report) — succeeded, no reason required.
  2. Second save with different `top_signals` content, no reason — raised
     `SchemaValidationError` with the same message `summarize.py` now
     catches and turns into a clear print.
  3. Second save with `revision_reason`/`corrected_at` supplied — succeeded,
     `revision_history` recorded one entry with the correct
     `previous_content_hash`.
  - Removed `data/reports/2099-01-01.json` afterward; confirmed no leftover
    test files in `data/reports/`.

No other files touched.
