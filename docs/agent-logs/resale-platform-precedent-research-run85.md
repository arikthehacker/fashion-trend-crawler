# Resale-platform corroboration precedent research (run 85)

## Trigger

Run 84's new-report agent (`docs/agent-logs/real-report-2027-12-20.md`) hit
`bogota-waist-tailoring-resale-holiday-demand`: a single `therealreal.com` source,
`corroboration_count=1`, mechanically `low` (resale is not in
`HIGH_RELIABILITY_SECTORS`). The agent correctly left the mechanical output alone and
flagged "resale-platform corroboration reliability" as a candidate for future
precedent formalization rather than inventing a silent exception. This log is that
follow-up.

## Current code state (checked before researching)

- `src/taxonomy.py`: `SOURCE_SECTORS` already includes `"resale"` (line 30). The
  `DOMAIN_SECTOR_MAP` already maps `therealreal.com`, `thereal-real.com`,
  `depop.com`, `vestiairecollective.com`, `grailed.com`, and `poshmark.com` to
  `"resale"` (lines 147-153).
- `src/report_schema.py`: `HIGH_RELIABILITY_SECTORS` (per
  `confidence-discipline-precedents.md`) is `editorial`, `designer_origin`,
  `institutional`, `independent_criticism` — `resale` is deliberately absent, so a
  single resale source can only ever reach `low`, never `medium`, under the current
  formula. That part is not new; it already works as intended.

## Research question

Is resale-platform sourcing (The RealReal, Vestiaire Collective, Depop, ThredUp) a
leading or lagging indicator of demand in how it's actually treated by fashion trade
journalism/forecasting, and does it carry a known bias worth naming explicitly (the
way this project already names Pinterest Predicts' self-promotional bias in
`docs/manual-sampling-workflow.md`)?

## Findings

**Split evidence on leading vs. lagging.** Resale-analytics vendors and some market
reports market resale listing/pricing data as a leading indicator — e.g. commercial
tools claiming resale price/volume moves can predict primary-market silhouette trends
weeks ahead (found via businesswire/market-report and vendor-tool search results).
This is real but should be read skeptically: it's the vendors' own marketing claim for
their own analytics product, i.e. the same kind of self-interested framing this
project already discounts elsewhere.

**Separately, and more load-bearing for this project's purposes: resale volume is a
supply-side signal, not a clean demand signal.** Consumer-behavior research (Nature
Scientific Reports 2025; Yale News coverage of resale-market carbon-footprint
research) found: (1) secondhand purchasing correlates positively with, rather than
substituting for, primary-market purchasing — people who buy resale are not simply
diverting spend away from new goods; (2) frequent secondhand buyers discard garments
faster than average, chasing novelty, meaning a given item appearing on a resale
platform in volume can reflect owners moving on from a look as easily as it can
reflect rising demand for it. This directly supports treating resale listing/sell-
through volume as ambiguous between "people want this" and "people are done with
this" rather than a clean demand proxy.

**Self-promotional "trending" framing.** No direct case study was found of a resale
platform's own trend report being independently audited for spin the way Pinterest
Predicts has been discussed in this project's own docs, but the structural argument
carries over directly: a platform's own "what's trending in resale" categorization is
produced by a party with a commercial interest in generating press coverage and
driving traffic to specific categories, exactly the reasoning already codified for
Pinterest in `docs/manual-sampling-workflow.md`'s "platform marketing is not organic
signal" rule. Applying the same skepticism to a resale platform's self-reported
"trending" claims is a direct extension of an existing, already-accepted project rule,
not a new leap.

## Decision

**Formalized as precedent 13** in `docs/confidence-discipline-precedents.md`. This is
genuinely generalizable, not a one-off, because:

- The single-source `low` case (this run's trigger) was already handled correctly by
  the existing formula — no override was needed there. The precedent is what
  actually needed writing: a real *future* case is not equally well covered — if a
  resale-sector signal ever reaches `corroboration_count >= 2` from a single sector,
  the formula mechanically computes `medium` (same "single sector, count>=2" rule as
  precedent 2/8), and without this precedent a future agent could reasonably assume
  volume of resale listings validates demand the way volume of editorial coverage at
  least partially does. Precedent 13 pre-empts that by stating explicitly that
  resale-sector volume should be discounted for the supply/discard reason above even
  at that tier, not just at `low`.
- It ties an existing, already-accepted rule (Pinterest platform-marketing
  skepticism) to a second platform type (resale) that wasn't previously covered by
  that language, closing a real gap rather than restating something already written
  down.

No code change was made — `resale`'s exclusion from `HIGH_RELIABILITY_SECTORS` was
already correct and remains unchanged. This is purely an editorial-judgment precedent,
consistent with how all 12 prior precedents work.

## Verification

`python -m py_compile src/*.py` — PASS, no output (no code touched, checked to confirm
nothing was accidentally broken by doc edits alone).
