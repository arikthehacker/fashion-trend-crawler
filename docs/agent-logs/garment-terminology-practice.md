# Garment terminology consistency — formalized in prompt (run 20)

`docs/agent-logs/costume-core-research.md` recommended a lightweight interim practice:
append-only garment terms per carried-forward `signal_id` unless a note documents a
change. That recommendation was never adopted anywhere — not in code, not in a doc,
not in the prompt — so the model had no instruction discouraging silent terminology
drift when a signal continues across reports.

## Change made

Added one instruction to `build_prompt()` in `src/summarize.py`, placed right before
the existing thin-week honesty instruction:

> "When a signal continues an existing signal_id carried forward from a prior report,
> keep garment/material terminology describing it consistent with prior usage unless
> the change is genuine — in which case note it explicitly (e.g. 'garment description
> updated from X to Y because...') rather than letting the terminology silently drift."

This is prompt text only — no control flow, no schema change. `docs/ARI3LLA INDEX.txt`
was not touched (read-only per task).

Logged a corresponding entry (Run 20) in `docs/PROMPT_CHANGELOG.md` per its stated
convention of tracking substantive instruction changes with rationale.

## Verification

`python -m py_compile src/*.py` — passed, no syntax errors.

## Note

This formalizes the interim recommendation at the instruction level only. It doesn't
introduce enforcement/validation of `signal_id` continuity or terminology diffing in
`report_schema.py` — that would be a separate, larger change if the practice needs to
be made structurally binding rather than model-guided.
