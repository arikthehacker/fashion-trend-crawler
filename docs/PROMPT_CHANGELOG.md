# Prompt Changelog — `summarize.py` `build_prompt()`

## Purpose

`build_prompt()` in `src/summarize.py` is the one piece of code that directly shapes
what the model is told to do when generating report content — it is an editorial
instrument, not ordinary application logic. Per the AI-journalism-standards gap analysis
(`docs/agent-logs/ai-journalism-standards-research.md`), AP treats generative-AI
instructions as policy subject to quarterly review, and Reuters requires "the same
standards and safeguards" for AI use as for any other editorial practice. `git log`
already records every commit that touches `summarize.py`, but a routine commit log
buries the instruction changes among refactors, bug fixes, and unrelated feature work —
nothing forces deliberate scrutiny of *what the model is being told*, as opposed to how
the surrounding code is structured.

This file exists to separate the two. It tracks only substantive changes to the
model-facing instructions inside `build_prompt()` — new bans, new tone requirements, new
honesty/disclosure instructions — not code refactors, parameterization, or output-format
plumbing that leaves the instructions themselves unchanged. Every entry below should be
addable to going forward: when `build_prompt()`'s instructions change, log it here with
rationale, in addition to (not instead of) the normal `docs/CHANGELOG.md` entry.

**Review cadence (proposed, not yet enforced by tooling):** treat this file the way AP
treats its generative-AI guidelines — review it at least quarterly, or whenever a new
prompt-instruction change lands, to check the accumulated instruction set still matches
doc section 21's objective-tone requirement and hasn't drifted.

---

## History (reconstructed retroactively from `git log -p -- src/summarize.py`,
`docs/CHANGELOG.md`, and `docs/changelog-entries/*.md`)

### Run 0 (branch setup) — commit `91a7ea0` — initial editorial prompt
**2026-07-06 ~02:06 PDT**

`build_prompt()` was rewritten from a bare headline-flattening function with no
editorial framing into the first version matching doc section 21's objective report
tone. Established the baseline instruction set:
- No first-person, no stylist/influencer/marketer/forecaster voice, no purchase
  recommendations, no hype.
- Classify signals by recurrence, source diversity, volatility, visual coherence,
  historical/aesthetic context, and source incentive.
- Use only provided source material — do not invent trends, brands, or claims.
- TikTok/social signals default to high-noise/volatile unless corroborated by
  non-social evidence across multiple periods.
- Classify each source by incentive context (designer-originated, editorial, commerce,
  social, retail, independent criticism, institutional archive) — editorial is not
  treated as neutral confirmation.
- Ban on "must-have," "essential," "the next big thing" language; distinguish lived
  style practice from market-instruction trend framing.

Why: section 21/2 of the concept doc require this distinction as the project's core
differentiator from a trend blog: nothing else in the pipeline enforces this if the
prompt doesn't.

### Run 3 — commit `7435adb` — Reuters-attribution tightening + ubiquity-language ban
**2026-07-06 ~05:30 PDT** — `docs/agent-logs/prompt-style-crosscheck.md`,
`docs/changelog-entries/run-03.md`

Cross-checked the existing prompt against the Reuters Handbook's attribution
conventions and closed two gaps:
- **Evaluative-verb ban.** Added: "Do not use evaluative or editorializing verbs such as
  'declared,' 'revealed,' or 'proves.' Use measured, attribution-anchored verbs instead,
  such as 'said,' 'reported,' 'noted,' or 'showed.'"
- **Ubiquity-language ban + thin-evidence honesty.** Added: "Avoid vague, unsupported
  claims of ubiquity such as 'everyone is wearing' or 'everywhere right now.' If
  evidence is thin, limited to one source sector, or contradictory, state that plainly
  in the evidence or index_note field rather than smoothing it over or omitting it."

Why: closes a real wire-service-norms gap identified by run-2's carried-forward open
item ("wire-service style cross-check against `summarize.py`'s prompt still open") —
without this, the model could produce copy that reads as editorializing or as
unsupported hype, which section 2's voice rules explicitly forbid.

### Run 7 — commit `6634e39` — thin-week honesty instruction
**2026-07-06 ~10:10 PDT** — `docs/agent-logs/thin-week-fallback.md`,
`docs/changelog-entries/run-07.md`

Added `collection_status`/`thin_week_note` schema fields (in `report_schema.py`) and a
corresponding prompt instruction so a genuinely low-signal collection window is reported
honestly instead of padded to look comprehensive:

> "If the source material yields only a small number of genuinely distinct,
> well-supported signals, do not stretch, duplicate, or manufacture additional signals
> to appear more comprehensive. Instead, set 'collection_status' to 'thin' and use
> 'thin_week_note' to state plainly that this reporting period had limited signal
> volume, so the report reflects the actual state of coverage rather than an inflated
> one. Use 'collection_status': 'normal' and leave 'thin_week_note' empty when signal
> volume is adequate."

Why: per Nieman Lab-style guidance surfaced in run 6's research — a report that always
looks "full" regardless of actual signal volume is itself a form of AI-generated
distortion, even without any single false claim.

---

## Changes reviewed and found to be non-substantive (excluded from this log)

- Commit `ff299b0` (run 7, migration step 2/5): parameterized `load_trends()`/
  `summarize()` signatures for testability; default runtime behavior and the prompt text
  itself were unchanged.
- Commit `eb740ac` (run 8): raised `max_tokens` from 2000 to 4000 to stop truncating real
  API output — a generation-limit fix, not an instruction change.
- Commit `5d14b69`: wired `revision_history` through the pipeline — data plumbing, no
  prompt text touched.
