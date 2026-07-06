# Prompt style cross-check — summarize.py

Checked `build_prompt()` in `src/summarize.py` against doc §21's core prompt spec, doc §2's
voice rules, and `docs/agent-logs/journalism-research.md`'s Reuters Handbook findings.

## Already aligned
The existing prompt matches doc §21's core prompt near-verbatim (objective framing, no
stylist/influencer/marketer voice, no purchase recommendations, no hype, source-incentive
classification, TikTok/social treated as high-noise by default, no "must-have"/"essential"/
"next big thing" language). This covers voice rules 1-10, 13-16.

## Gaps found and closed
1. **No ban on evaluative/editorializing verbs.** Journalism-research finding #5 (Reuters
   Handbook) explicitly recommends banning verbs like "declared," "revealed," "proves" in
   favor of attribution-anchored verbs ("said," "reported," "noted," "showed"). The prompt
   had no such instruction. Added a sentence naming both the banned and preferred verb sets.
2. **Voice rule 11 ("uncertainty is allowed") and rule 9 ("no vague 'everyone is wearing'")
   were not represented in the prompt at all.** The schema has `limitations` and
   `index_note` fields but nothing told the model to actually use them to flag thin/
   contradictory evidence rather than smoothing it into confident-sounding prose, or to
   avoid vague ubiquity claims. Added one sentence banning "everyone is wearing"/"everywhere
   right now" phrasing and one instructing the model to state thin/contradictory evidence
   plainly in `evidence`/`index_note` rather than omitting it.

## Not changed
No changes to control flow, the Anthropic API call, JSON schema/field list, or I/O — only
the instructional sentences inside the prompt string in `build_prompt()`.

## Verification
`python -m py_compile src/*.py` — passed, no syntax errors.
