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

---

## First bias-audit pass (run 16)
**2026-07-06** — no code changed; see `docs/agent-logs/bias-audit-run16.md` for the
coordinator summary. Prompted by the "no stated bias-audit practice" gap flagged in
`docs/agent-logs/ai-journalism-standards-research.md`. Scope: seed source list
(`crawler.py FASHION_SOURCES`), classification vocabulary (`taxonomy.py`), and the
`derive_confidence()` formula (`report_schema.py`, introduced run 6/8).

**(a) Source list skew — real finding.** `FASHION_SOURCES` currently has only three
seeds: `vogue.com/fashion`, `whowhatwear.com`, `hypebeast.com/fashion`. All three are
English-language, US/UK-headquartered, editorial-or-retail in incentive (hypebeast
leans streetwear but is still a Western trade outlet). There is no seed representing
non-Western regional fashion discourse (e.g. no Japanese, South Asian, African,
Latin American editorial or independent-criticism sources), despite `taxonomy.py`
already having sector slots (`independent_criticism`, `street_ugc`) that such sources
would fit into. The crawler's BFS depth-2 traversal from these seeds can only ever
surface what these three sites link to, so the skew compounds rather than
self-corrects. Recommendation: when sources are next expanded (as in run 12's
domain-coverage work for taxonomy.py), explicitly add at least one non-Western,
non-English-language-market source per sector where one exists, and note in
`docs/methodology` that the source list's current geographic scope is a known
limitation, not an implied claim of global coverage.

**(b) Classification vocabulary — no substantive issue found.** `SOURCE_SECTORS`
names (`designer_origin`, `editorial`, `retail`, `social`, `street_ugc`, etc.) are
descriptive of incentive structure, not ranked by an implied legitimacy order in the
vocabulary itself or in `classify_source()`. The prompt in `build_prompt()` actively
works against gatekeeping here: "Do not treat editorial sources as neutral
confirmation. Classify each source by incentive context..." (line 70) and the
TikTok/social high-noise-by-default instruction (line 68) are explicit anti-hierarchy
instructions, not hierarchy-reinforcing ones. Conclusion: the vocabulary/prompt layer
already handles this reasonably; no change recommended here.

**(c) `derive_confidence()` — real finding, concrete recommendation.**
`HIGH_RELIABILITY_SECTORS` in `report_schema.py` (`editorial`, `designer_origin`,
`institutional`) grants a single-mention signal from those sectors a "medium"
confidence floor. A signal appearing exactly once in `street_ugc`,
`independent_criticism`, `social`, `resale`, or `visual_archive` cannot reach
"medium" without a second corroborating mention — it is capped at "low" regardless of
how substantive that one mention is. This reproduces the exact "designer/editorial
as inherently more legitimate" hierarchy the prompt's own instructions (finding b)
try to avoid, just moved into the confidence math instead of the prompt text. It is a
defensible starting heuristic (institutional archives and designer first-party
statements are lower-noise per mention than a single TikTok post), but as written it
hard-codes source *type* as a proxy for reliability rather than something more
falsifiable. Recommendation: either (1) rename/reframe `HIGH_RELIABILITY_SECTORS` in
comments/docs as "low-noise-per-mention sectors" so it's understood as a noise-rate
heuristic and not a legitimacy ranking, and/or (2) extend the single-mention medium
gate to `independent_criticism` — it is a curated, named-author sector (per
`docs/ARI3LLA INDEX.txt` section 11) with a comparable noise profile to editorial,
and its current exclusion looks like an oversight rather than a deliberate call.
`street_ugc`/`social`/`resale` remaining excluded from the single-mention gate is
reasonable and should stay as-is.

## Second bias-audit pass (run 18)
**2026-07-06** — no code changed; see `docs/agent-logs/bias-audit-run18.md` for the
coordinator summary. Continues the periodic-review practice TODO.md called for after
run 16. Scope this time deliberately excludes run 16's angles (source-list skew,
`HIGH_RELIABILITY_SECTORS` gate consistency) and instead covers: `taxonomy.py`
vocabulary value-loading, in-practice confidence patterns across the 10 real reports in
`data/reports/`, and platform balance in the manual-sampling workflow.

**(a) `VOLATILITY_LABELS`/`ORIGIN_CLASSIFICATIONS` vocabulary — no substantive issue
found.** Neither list ranks its members; `archive_revival` sits alongside
`designer_originated`, `editorial_amplified`, `retail_adopted`, `social_amplified`,
`platform_native`, and `unclear` in `ORIGIN_CLASSIFICATIONS` (`taxonomy.py` lines
63-71) with no ordering or scoring semantics, and nothing in `build_prompt()`
(`summarize.py`) or `report_schema.py` treats `archive_revival` as lower-legitimacy —
it isn't referenced in `HIGH_RELIABILITY_SECTORS`, `derive_confidence()`, or any
prompt instruction at all. Origin classification and confidence are orthogonal fields
in the schema; an `archive_revival` signal from `institutional` sourcing can reach
`high`/`archival` confidence exactly like a `designer_originated` one. Conclusion:
value-loading risk here is more about future authoring habits than the current code —
worth a one-line callout on `taxonomy/page.tsx` noting origin classification describes
*how a signal reached visibility*, not how legitimate or original it is, so a future
editor doesn't start reading the list as a hierarchy. No code change made.

**(b) Sector-level confidence pattern across real reports — real finding.** Aggregated
`confidence` vs. `source_corroboration_count` vs. `source_sectors` across all 10 files
in `data/reports/` (not just mismatches against `derive_confidence()`, which
`audit_confidence.py` already checks per-signal — this pass grouped by sector instead).
At equal corroboration count, `independent_criticism` signals land at `low` confidence
far more often than `editorial` or `retail` signals with the same corroboration count:
at `source_corroboration_count == 2`, `independent_criticism` is `low` in 3 of 4
occurrences (75%) versus `editorial` `low` in 4 of 10 (40%) and `retail` `low` in 0 of 5
(0%) at the same corroboration count. This is the same pattern run 16 finding (c)
identified in the `HIGH_RELIABILITY_SECTORS` code (`independent_criticism` excluded from
the single-mention medium floor while `editorial`/`designer_origin`/`institutional` are
included) — but confirmed here as a pattern that actually shows up in the assigned data,
not just a theoretical gap in the formula. This corroborates, rather than duplicates, run
16's recommendation: extending the single-mention medium gate (or at minimum the
two-mention floor) to `independent_criticism` would fix a bias that is visibly present
in the 10 real reports, not just latent in the code. No code changed this pass per
instructions — flagging as the top candidate for the next run that does touch
`report_schema.py`.

**(c) Manual-sampling platform balance — real finding, different shape than expected.**
Doc §31 and both `docs/manual-sampling-template.md` and
`docs/manual-sampling-workflow.md` consistently frame the compliant path as
"TikTok/Pinterest," and `taxonomy.py`'s `DOMAIN_SECTOR_MAP` treats `tiktok.com`,
`instagram.com`, `youtube.com`, `reddit.com`, and `pinterest.com` as equally-weighted
members of the `social` sector — no code or vocabulary favors one platform. In
practice, though, both real exercises of the workflow to date
(`docs/agent-logs/manual-sample-exercised.md`,
`docs/agent-logs/manual-sample-exercised-2.md` — "Off-Duty Varsity" and "Poetcore")
sampled exclusively from Pinterest, specifically from Pinterest's own official
"trend report" / "Pinterest Predicts" pages, and zero TikTok signals have ever been
logged. `docs/manual-sampling-workflow.md`'s own research note explains why: TikTok's
Research API is academic-institution-gated (effectively blocked for this project)
while Pinterest publishes an easy, citable, public "trend report" page — so the
*compliance friction*, not editorial judgment, is what has driven 100% of real social
signals toward one platform. That is a narrower, more concrete bias than "the taxonomy
favors TikTok/Pinterest over other platforms" (it doesn't — `youtube.com`/`reddit.com`
are equally under-sampled, just not named in doc §31's framing). The sharper issue: a
Pinterest "official trend report" page is platform self-promotion / marketing content
about its own predicted trends, not organic user-generated style discourse, yet it gets
the same `source_sectors: ["social"]` / `origin_classification: "platform_native"`
tagging as an organic TikTok post would. `taxonomy.py` has no vocabulary distinction
between "platform-published marketing/forecast content" and "organic user posts"
within the `social` sector, so the two real logged signals read, schema-wise, as
equivalent to grassroots UGC even though both editors' own `human_editor_note` fields
flag them as closer to promotional/forecast-branding language than organic discourse.
Recommendation: consider a documentation-level note (not necessarily a new controlled
vocabulary value, to avoid over-engineering a 2-signal sample) in
`manual-sampling-template.md` distinguishing "platform-published trend report/press
content" from "directly observed user posts," and flag in the workflow doc that the
current 2-for-2 Pinterest-only, official-report-only sample is itself a reflection of
which platform has the lowest compliance friction, not a signal that Pinterest is where
the interesting fashion discourse is happening. No code changed this pass.

### Run 19 — prompt fix for independent_criticism confidence asymmetry
**2026-07-06** — see `docs/agent-logs/prompt-tuning-run19.md`. Addresses run 18 finding
(b) directly at the prompt-instruction level (run 18 deliberately made no code change).
`report_schema.py`'s formula-level gate (`HIGH_RELIABILITY_SECTORS`) already treats
`editorial` and `independent_criticism` equally as of run 16's fix, but the model was
still observed assigning `independent_criticism` "low" confidence far more often than
`editorial` at equal corroboration counts — the asymmetry was happening upstream, in
how the model itself weighed source sector during generation, not in the deterministic
formula.

Added to `build_prompt()`, immediately after the existing "Do not treat editorial
sources as neutral confirmation" instruction:

> "Independent criticism (named-author, attributed commentary) and editorial coverage
> are both curated, attributed commentary, not raw social volume. When assigning
> confidence, do not let source sector alone push independent criticism lower than
> editorial at an equal corroboration count — evaluate both on the same evidentiary
> basis. This is not a case for treating independent criticism as more reliable than
> editorial; it is a case for not treating it as less reliable by default."

Why here and phrased this way: kept explicitly scoped to correcting an asymmetry, not
establishing a new hierarchy in the other direction — consistent with the project's
anti-gatekeeping framing (doc section 2, run 16 finding (b)). Only `build_prompt()`'s
prompt text was touched; no control-flow or schema changes. Verified with
`python -m py_compile src/*.py`.
