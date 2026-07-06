# Prompt consistency audit — run 42

Re-checked `build_prompt()` in `src/summarize.py` against `docs/PROMPT_CHANGELOG.md`'s
full accumulated instruction set (run 0 baseline through run 37's `source_domains`
addition — 11 runs after run 30's clean pass). Checked for (a) contradictions between
instructions, (b) instructions made redundant by a later, more complete one, (c)
instructions referencing a renamed/removed schema field or convention (e.g. the deleted
`source_links` field).

## Finding — real, fixed

Line 70 ("Do not treat editorial sources as neutral confirmation. Classify each source
by incentive context: designer-originated, editorial, commerce, social, retail,
independent criticism, or institutional archive.") hard-coded a *different, stale* list
of sector names than `taxonomy.py`'s actual `SOURCE_SECTORS` (`designer_origin`,
`runway`, `editorial`, `retail`, `social`, `visual_archive`, `independent_criticism`,
`institutional`, `street_ugc`, `resale`). Notably "commerce" is not a real sector at
all — it never existed in `SOURCE_SECTORS` — and `runway`, `visual_archive`,
`street_ugc`, `resale` were missing from the prose list entirely. This is exactly the
"referenced convention has since changed/is stale" failure mode the audit was scoped to
catch: the prompt already prints the real, authoritative list two paragraphs later
("Valid source sectors are: {...}"), so this hard-coded prose list was a second,
drifted definition of the same vocabulary — the kind of duplication run 24's
docs-workflow item warned about (point at the live source of truth instead of a
hardcoded copy that goes stale).

**Fix:** replaced the stale enumeration with a reference to the vocabulary printed
below it ("using the source sector vocabulary given below (see 'Valid source
sectors')"), removing the drift risk permanently rather than just re-syncing the list
(which would drift again on the next taxonomy change).

## Checked and clean

- No contradictions found between any pair of instructions (editorial-neutrality,
  independent-criticism parity, TikTok/social noise default, ubiquity ban, thin-week
  honesty, garment-terminology consistency, non-English disclosure, `source_domains`
  population all coexist without conflict).
- No redundant pairs — each instruction covers a distinct concern; thin-evidence honesty
  (line 78) and thin-week collection_status (line 84) look similar but operate at
  different granularity (per-signal evidence caveat vs. whole-report signal volume) and
  both are still needed.
- No other stale field references — `source_domains`, `collection_status`,
  `thin_week_note` all match current `report_schema.py`; `source_links` is not
  referenced in `build_prompt()` at all (it's a separate, still-live field populated
  elsewhere in the pipeline, not deleted).

Verified with `python -m py_compile src/*.py` — passes.
