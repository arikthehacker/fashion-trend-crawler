# Gap analysis — 50-run / ~43-report milestone

Fresh read of doc §40 (priority list), §2 (voice), §18/19 (human-in-loop) against current
state. Excludes items already correctly declined with documented reasoning (quarterly
retrospective, TikTok Research API, contact form, Wayback auto-snapshot, etc.).

## §40 status: fully closed, not the active frontier anymore

All 10 original priority items were done by run 6 and remain done. §40 has not been the
real constraint for ~44 runs. Continuing to frame future work against it is no longer
useful — the punch list below is the actual open frontier.

## Real, still-open gaps (prioritized)

1. **The described crawler pipeline is not what actually produces the archive.** Doc §1/§42
   promise a report that "collects public style discourse from across the web" via
   `crawler.py`. In practice, of ~42 reports, only two runs (8, 15) ever executed the real
   crawler; every other report is a WebSearch-researched or hand-authored reconstruction
   presented as a dated collection window. This is the single largest gap between the
   concept doc and reality, and it has never been named as an open item in `TODO.md` —
   only the now-resolved sub-symptoms (stale example data, thin weeks, migration) were
   tracked. Worth deciding explicitly: either commit to running the real pipeline on
   cadence, or honestly document in methodology that "collection" currently means
   editorial WebSearch research, not automated crawling — the current silence on this
   distinction is itself a transparency gap given how much the site's trust language
   leans on "collected," "scanned," "sources_scanned" counts.

2. **"Human-in-the-loop" (§18/19) has no actual human in it.** `reviewed_by` values are
   agent self-attribution strings (`"loop-consolidation"`, `"websearch-run-thin-week"`),
   not a named editor's sign-off. §18/19's core claim — "the methodology should decide
   what matters, not the model" — is structurally unmet: an autonomous LLM loop has
   authored, classified, and "human-reviewed" all 43 reports end to end with no external
   human checkpoint ever exercised. This isn't a voice-copy issue (the copy correctly says
   "AI-assisted, human-reviewed") — it's that the process the copy describes has never
   actually happened. Distinct from, and deeper than, the earlier "populated but
   unrendered" bug class (runs 21/23/24) — this is "claimed but never true."

3. **`SITE_URL` is still `ari3lla-index.example.com`** (`web/lib/site.ts`). Blocks: real
   Wayback/Save-Page-Now self-archival (parked since run 43), a genuine "citable" URL for
   the citation-format work (run 30), and JSON-LD/sitemap correctness against a real
   domain. This has been a standing precondition for multiple features for 7+ runs without
   being escalated as its own line item — it's a human decision (buy/point a domain,
   choose a host), not something an agent loop can resolve, and should be flagged as
   blocked-on-human rather than silently re-deferred.

4. **`gh` CLI unavailable — CI pass/fail has never been confirmed once in 16+ consecutive
   checks.** Each run re-notes this identically instead of trying an alternative
   verification path (e.g., checking `.github/workflows` run status via the GitHub REST
   API with a token, or asking the human operator directly). Restating the same unresolved
   fact 16 times without escalating or trying a different method is itself a process gap.

5. **Manual social-sampling (§30/31) remains thin relative to the original vision.** Only
   3 manual samples have ever been exercised across 43 reports (run 3, 9, 28), despite
   social platforms being one of doc's five named source sectors. The cadence was
   correctly softened from "weekly" to "opportunistic" (run 32) to avoid forcing
   low-quality entries, but the practical effect is that "social" is now the
   thinnest-populated sector in the taxonomy by a wide margin — worth an honest note on
   `/methodology`/`/taxonomy` acknowledging this imbalance rather than presenting all five
   sectors as equally exercised.

6. **Geographic/language coverage is still materially Western/English-skewed** despite
   6+ runs of incremental additions (dewimagazine.com, SCMP, The National, Nataal,
   OkayAfrica, etc.) — no source from Latin America outside Mexico, nothing from mainland
   China, Korea, or continental Europe beyond English-language coverage. This has been
   repeatedly acknowledged as a "real, documented scope limitation" but never given an
   endpoint or explicit acceptance — it's treated as perpetually "in progress" without
   ever being declared either resolved-enough or a permanently-disclosed limitation.

## §2 (voice) and §18/19 drift check

No new banned-phrase violations found (grep for "must-have," "obsessed," "this season is
all about," "you need," "everyone is wearing" across `web/app/**/*.tsx`: zero matches),
consistent with the clean audits at runs 25, 40. Voice itself has not drifted further.
The real drift is structural, not lexical: §18/19 is a *process* claim (a human decides
what clusters mean), and the process described no longer matches what's actually
happening (see #2 above) even though every sentence on the site is worded correctly.
Voice audits that only check word choice will keep passing while this gap persists —
future audits should explicitly ask "who is the *actual* editor" as well as "does the
copy sound editorial."

## Not re-litigated here (already tracked, correctly not urgent)
run-19 confidence-gate (untested, benign), CFDA prolonged-silence signals (working as
designed), source_domains/citation design (settled run 39), retrospective feature
(correctly deferred, styleOnly threshold not yet met).
