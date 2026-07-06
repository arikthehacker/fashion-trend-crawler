# Gap analysis — loop run 6

## 1. Cadence/burnout guidance for a solo automated publication

- **Nieman Lab** (niemanlab.org) — burnout is the dominant sustainability failure mode
  for small/solo outlets; multiple 2021-2022 pieces ("We acknowledge cohort burnout,"
  "The inevitable mental health revolution") tie unsustainable cadence directly to
  quality collapse and shutdown risk. Takeaway: a fixed weekly cadence is fine, but the
  project has no documented fallback for "no real signal this week" — the doc's own
  anti-hype rule (§2) implies an explicit "no significant movement" report state is
  needed, not silent skipping or filler.
- **Nieman Lab / general trend coverage** — sustainable solo journalism operations
  emphasize automation for repetitive collection but *manual* judgment stays on the
  interpretive step, which matches this project's existing §18/19 human-editor-note rule.
  Reinforces: don't automate signal-clustering away, but automate the crawl/save/build steps.
- Practical implication: add a defined "thin week" report state (e.g. `executive_summary`
  explicitly says signal volume was low, `limitations` field used honestly) instead of
  inventing signals to fill the schema every week.

Sources: [Nieman Lab burnout tag](https://www.niemanlab.org/tag/burnout/), [We acknowledge cohort burnout](https://www.niemanlab.org/2021/12/we-acknowledge-cohort-burnout/), [Let's talk about what sustainability really means](https://www.niemanlab.org/2021/12/lets-talk-about-what-sustainability-really-means/)

## 2. Trust-signal transparency for a small/new publication

- **The Trust Project** (thetrustproject.org) — 8 Trust Indicators: Best Practices,
  Author/Reporter Expertise, Type of Work, Citations & References, Methods, Locally
  Sourced, Diverse Voices, Actionable Feedback. Best Practices explicitly includes a
  **corrections policy**, **funding/ownership disclosure**, and **editorial independence
  guidelines**.
- **Trusting News** (trustingnews.org) — recommends disclosing sourcing method, how long
  a piece took to produce, conflicts of interest, and explicitly labeling AI involvement
  in the reporting process — directly relevant since this project's whole pipeline is
  LLM-assisted.
- **Gap found:** `web/app/methodology/page.tsx` and `web/app/about/page.tsx` contain
  **no** corrections policy, no editorial-independence statement, no funding/ownership
  disclosure, and no explicit AI-involvement disclosure (confirmed by direct grep —
  zero matches for "correction," "independence," "funding," "disclos" in either file).

Sources: [Trust Indicators Explained](https://thetrustproject.org/), [Understanding Trust Indicators](https://thetrustproject.org/trust-indicators/), [Trusting News: Daily transparency](https://trustingnews.org/trustkits/transparency/)

## 3. Section 40 status + what's still missing after 6 runs

Section 40 items 1-10 (rename, hero, prompt rewrite, schema, dated storage, archive page,
methodology page, taxonomy page, README, case study) are **all verifiably implemented** —
spot-checked `web/app/layout.tsx` (title updated), `src/report_schema.py` (schema +
validation present), `data/reports/*.json` (3 dated reports), `web/app/archive/page.tsx`,
`web/app/methodology/page.tsx`, `web/app/taxonomy/page.tsx`, README, `case-study/page.tsx`
all exist and match doc sections. Confirmed `src/run.sh` now runs crawl→summarize as one
command (this was fixed already, contrary to the skill file's stale "KNOWN STALE" note).

**Still open, concrete and prioritized:**

1. **No corrections/transparency policy on the site.** Add a short "corrections &
   transparency" block to `web/app/methodology/page.tsx` or `about/page.tsx`: how errors
   are corrected, that reports are AI-assisted with human review (§18/19), and that there
   is no advertiser/retail relationship influencing signal selection. Directly closes the
   Trust Project/Trusting News gap above.
2. **Legacy `trends_raw.json`/`trends_summary.json` migration incomplete.** Only step 1
   of 5 done (`docs/agent-logs/migration-step1.md` — `crawler.py` constant only).
   `summarize.py`'s `load_trends()` and `test_tools.py`'s `CACHE_FILE` still hardcode the
   old path; 4 legacy JSON files (root + `src/`) still present, still diverged.
3. **No real live crawl has produced a report.** All 3 `data/reports/*.json` are
   hand-authored/WebSearch-sourced, not `crawler.py` output — the core "run.sh actually
   works end-to-end against live network" claim is untested.
4. **No canonical domain / no "thin week" fallback state** in the report schema or
   `summarize.py` — every week currently assumes a full signal set; per the burnout
   research above, an honest low-signal week state should exist before cadence becomes a
   real burden.
5. **TikTok/Pinterest ingestion (doc §30/31)** still only has one exercised manual sample
   (`manual_sample.py`, one Pinterest signal) — no repeatable weekly manual-sampling
   habit/checklist has actually been run twice yet to prove it's sustainable.
