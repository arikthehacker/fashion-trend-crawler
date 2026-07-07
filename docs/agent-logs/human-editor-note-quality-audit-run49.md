# human_editor_note quality audit (run 49)

Run 31 confirmed `human_editor_note` exists as a real dataclass field everywhere required.
This run checks whether its *content* is genuine editorial judgment (per doc §18/19) or has
drifted into restating `evidence`/`index_note`.

## Sample

13 reports spanning 2026-05-07 through 2027-04-05 (early curated, fashion-month, prolonged-
silence tracking, and recent), ~2-3 signals each.

## Finding: mostly genuine, but two exact-duplicate cases found

Programmatically diffed `human_editor_note` against `index_note` and `evidence` across all
41 reports (not just the sample). Result: **2 exact verbatim duplicates**, both against
`index_note`:

- `data/reports/2026-07-13.json` — signal `off-duty-varsity`
- `data/reports/2026-11-09.json` — signal `funmaxxing-maximalist-play-aesthetic` (the note is
  the identical "Diversification attempt: tried to source this window's manual signal from
  TikTok rather than Pinterest again..." sentence copy-pasted into both fields)

These are real instances of the pattern this project has hit 5+ times before (documented
field that doesn't do its job) — here specifically, the field exists and is populated, but
in these two cases carries zero judgment beyond what index_note already said.

The rest of the sample (2026-05-07 through 2027-04-05, ~30 other signals read) is
substantially better than that: notes like the 2026-08-03 sheer-layering/soft-tailoring
close-out calls, the CFDA Fashion Fund "untracked pending new information" framing
(2026-11-30, 2026-12-21), the 2027-02-08 Wales Bonner confidence-ceiling reasoning, and the
2027-04-05 Pinterest-Predicts sourcing-compliance note all add a distinct layer — a stance,
a caveat about what NOT to conclude, or a forward-looking instruction — that evidence/
index_note don't carry. That is genuine editorial judgment, not restatement.

## Root cause

`src/summarize.py`'s prompt (`build_prompt`) never mentioned `human_editor_note` at all in
its JSON schema template — the AI-generation step had zero instruction about the field, so
whichever pass populates it (report-writing agent) had no guardrail against copying
index_note verbatim under time pressure.

## Fix applied (process fix, not data rewrite)

Added `human_editor_note` to the prompt's JSON template (instructing the model to leave it
empty — it's a human pass, not AI output) and a new paragraph instructing that a
`human_editor_note` which only rephrases evidence/index_note "defeats the field's purpose"
and should not be produced. Verified with `python -m py_compile src/summarize.py
src/report_schema.py src/manual_sample.py` — passes.

Did not rewrite the two duplicate notes in `2026-07-13.json`/`2026-11-09.json` — that would
fabricate editorial judgment retroactively rather than reflect real review. Flagging here for
a human/future run to genuinely reconsider those two signals if desired.
