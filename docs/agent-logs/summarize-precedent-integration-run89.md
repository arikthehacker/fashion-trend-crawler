# Run 89: confidence-discipline precedents vs. summarize.py's prompt logic

## Finding

`build_prompt()` in `src/summarize.py` was read in full. Before this run it did **not**
reference `docs/confidence-discipline-precedents.md` anywhere, and did not describe any
of the 14 accumulated precedent exceptions. The prompt's confidence-related instructions
were limited to:

- treating TikTok/social as high-noise by default (unrelated to derive_confidence()'s
  precedent history),
- one sentence on not letting source_sector alone push independent_criticism below
  editorial at equal corroboration count (a narrow paraphrase of precedent 5's positive
  case, not the precedent itself or its citation-free-rehash carve-out).

This confirmed the structural gap described in the task: every precedent has so far only
ever been applied by a Claude-agent report-writer manually reading the doc. The actual
automated pipeline (`crawler.py -> summarize.py -> LLM -> save_report()`) had no path by
which the LLM generating a real report would see any of this reasoning.

## Fix applied

Added a "Confidence discipline" paragraph to `build_prompt()` (inserted before the
existing thin-week/collection_status instruction), summarizing the five precedents
judged most likely to recur:

1. Same-sector volume cap (precedent 2)
2. Unclear-domain gap (precedent 3)
3. Citation-free rehash carve-out on `independent_criticism` (precedent 5)
4. Same-week coincidence is not cross-signal corroboration (precedent 6)
5. Forecast/speculative-content exclusion from `top_signals` (precedent 14, run 88)

The block explicitly points back to `docs/confidence-discipline-precedents.md` for full
reasoning and worked examples, and closes with a general instruction to use judgment
consistent with these examples for cases that don't cleanly match, rather than treating
the condensed list as exhaustive or defaulting to the raw mechanical `derive_confidence()`
output.

The other 9 precedents (1, 4, 7, 8, 9, 10, 11, 12, 13) were deliberately left out of the
in-prompt summary to keep it a practical length — they are narrower/rarer patterns
(single-source-multi-sector-tag, downstream-reprint, nominal-sector-mislabeling,
commercial-vertical discount, calendar-driven durability, wire-syndication discount,
casting-discourse categorization, prose-field immutability, resale-platform
supply-vs-demand) better handled by human/editor review or a future prompt revision if
they prove to recur often enough to be load-bearing at generation time.

## Validation

`python -m py_compile src/*.py` — passed, no syntax errors introduced.

No live LLM call was made. `.env` / API key contents were not read, printed, or logged.

## Scope respected

Only `src/summarize.py` (prompt-construction code, explicitly permitted for review per
task instructions) and this log were touched. `TODO.md`, `CHANGELOG.md`,
`data/reports/*.json`, and `docs/confidence-discipline-precedents.md` were not modified.
No commit was made.
