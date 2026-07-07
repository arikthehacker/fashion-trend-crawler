# Prompt consistency audit — run 30

Read `build_prompt()` in `src/summarize.py` in full (lines 46-129, ~20 instruction
sentences before the JSON schema block), plus `docs/PROMPT_CHANGELOG.md`'s full history
(runs 0, 3, 7, 16/18 bias audits, 19, 20, 21) to see how each instruction was added and
why.

## Findings

**(a) Redundancy.** No exact duplicates. The closest overlap is three separate
anti-hype clauses: "Do not hype trends" (run 0), "Do not recommend adoption... must-have,
essential, next big thing" (run 0), and "Avoid vague, unsupported claims of ubiquity...
'everyone is wearing'" (run 3). These read similar but each bans a distinct phrasing
pattern the model has apparently needed called out separately (general hype / adoption
framing / ubiquity claims). Collapsing them risks dropping a banned-phrase example the
model currently avoids, for a purely cosmetic word-count saving. Left as-is.

Also close: "Do not recommend purchases" vs. "Do not recommend adoption" — both from
run 0's original instruction set (not an accumulated duplicate across runs), and the
distinction (purchase vs. broader lived-practice adoption) maps to doc section 2's
lived-practice-vs-market-instruction framing. Not a genuine duplicate.

**(b) Contradictions.** None found. The run 19 (independent_criticism/editorial parity)
and run 3 (editorial-not-neutral) instructions read as complementary, not conflicting —
19 explicitly says "not a case for treating independent criticism as more reliable... it
is a case for not treating it as less reliable by default," which was deliberately
phrased to avoid contradicting run 0's "do not treat editorial as neutral confirmation."
Run 20 (garment terminology consistency) and run 21 (non-English disclosure) address
disjoint failure modes (drift vs. translation transparency) and don't interact.

**(c) Length/dilution risk.** The instruction block is ~20 sentences / ~650 words before
the output schema — long, but each sentence maps to a distinct, previously-observed
failure mode (see changelog), not filler. No sentence is an unused holdover. This is
worth monitoring as more runs add instructions (a numbered/grouped restructure may help
future model attention if it keeps growing), but forcing a reorganization now for a
prompt that isn't actually confused would be scope creep on a working, tested prompt.

## Outcome

No changes made to `src/summarize.py` or `docs/PROMPT_CHANGELOG.md` — the prompt passed
this audit. `python -m py_compile src/*.py` confirmed still passing (baseline, unchanged).
