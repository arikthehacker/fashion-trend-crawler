# Prompt tuning — run 19

Scope: `src/summarize.py`'s `build_prompt()` only, prompt text, no control-flow changes.

## What was fixed

Run 18's bias-audit pass (b) found that `independent_criticism` signals land at "low"
confidence far more often than `editorial` at equal `source_corroboration_count` (75%
vs. 40% at count == 2, across the 10 real reports), even though `report_schema.py`'s
`HIGH_RELIABILITY_SECTORS` gate already treats both sectors equally since run 16. That
means the asymmetry isn't in the deterministic formula — it's in how the model itself
weighs source sector during generation.

## Change

Added one instruction to `build_prompt()`, directly after the existing "Do not treat
editorial sources as neutral confirmation" line, so it reads as a continuation of the
same anti-hierarchy framing rather than a new, separate rule:

> "Independent criticism (named-author, attributed commentary) and editorial coverage
> are both curated, attributed commentary, not raw social volume. When assigning
> confidence, do not let source sector alone push independent criticism lower than
> editorial at an equal corroboration count — evaluate both on the same evidentiary
> basis. This is not a case for treating independent criticism as more reliable than
> editorial; it is a case for not treating it as less reliable by default."

Deliberately symmetric in framing (matches project's anti-gatekeeping stance, not a new
elevation of independent criticism over editorial).

## Verification

`python -m py_compile src/*.py` — passed, no errors.

## Files touched

- `src/summarize.py` (prompt text only, inside `build_prompt()`)
- `docs/PROMPT_CHANGELOG.md` (new dated entry, run 19)
- `docs/agent-logs/prompt-tuning-run19.md` (this file)

Not committed, per instructions.
