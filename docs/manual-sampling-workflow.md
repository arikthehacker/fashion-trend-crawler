# Manual social-signal sampling workflow

## Why this exists

Doc §31 rules out aggressive/ToS-violating scraping of TikTok and Pinterest. The
research in `docs/agent-logs/social-ingestion-research.md` evaluated the compliant
alternatives — TikTok's Research API (blocked: academic-institution gate only),
Pinterest's Trends API (usable later, but "today only," no historical backfill), and
approved third-party datasets (static/historical, not live signal, or commercial-priced
out of reach) — and concluded manual sampling is the correct near-term path. This
mirrors WGSN's own published methodology of curated human observation + citation rather
than raw automated pulls.

## The workflow

1. **Observe.** Opportunistically, not on a fixed schedule (per doc §31 this is a
   compliant substitute for scraping used "when needed," not a weekly quota — see
   `docs/agent-logs/manual-sampling-cadence-check-run32.md`), a human notices a recurring
   hashtag, trend name, or aesthetic pattern on TikTok, Pinterest, or
   another social platform, using only publicly visible pages — no login-walled scraping,
   no automated pulls.

   **Concrete acceptance criterion for "opportunistic" (set run 52, replacing the
   open-ended "no defined endpoint" status flagged by run 50's gap analysis):**
   "opportunistic" means *checked* at least once every ~10 runs (a cheap WebSearch pass
   over current Pinterest Predicts/Trends and TikTok discover/hashtag pages), but
   *exercised* — i.e. an entry actually added — only when a candidate clears this bar:

   - at least one source independent of the platform's own newsroom/PR page, AND
   - that independent source shows actual editorial judgment/critique/observation, not
     a repackaging of the platform's press-release stats and copy (a real-world
     recurring failure mode: outlets like WhoWhatWear, Axios, or SEO content mills that
     simply restate Pinterest's "X search up N%" figures verbatim do not count — see
     runs 41 and 52, both of which found only this pattern for that cycle's Pinterest
     Predicts report).

   A "checked, nothing cleared the bar" outcome (runs 32, 41, 52 so far) is a complete,
   successful exercise of this step — it is not a gap, does not need a "resolution," and
   does not accumulate into a debt that must eventually be paid off with a forced entry.
   The workflow's endpoint is the check itself, not a guaranteed signal at the end of it.
2. **Log it.** For each observed signal, fill out one block of
   `docs/manual-sampling-template.md`: name, platform(s), hashtag/trend name, date
   observed, approximate volume/reach (or "unknown" — never guessed), public source
   URL(s), observer notes, and a rough guess at confidence/volatility/origin
   classification.
3. **Transcribe.** Pass the filled-out fields to `build_manual_signal(...)` in
   `src/manual_sample.py`, which validates them against the controlled vocabularies in
   `taxonomy.py` and returns a `Signal` object with `source_sectors=["social"]`. This can
   be done by hand at report-assembly time — it's a small pure function, not a pipeline
   stage.
4. **Fold into the report.** The resulting `Signal` gets appended to a report's
   `top_signals` list alongside crawler/summarize-derived signals, then validated as
   normal via `validate_report()` before `save_report()`.

## Guardrails this preserves

- **No scraping.** Every field in the template traces back to something a human directly
  observed on a public page — nothing here fetches or stores data via an API call or
  scraper.
- **Human judgment stays human.** `build_manual_signal()` requires a non-empty
  `human_editor_note` and raises `ValueError` if it's missing — a manually sampled signal
  with no observer judgment isn't a valid entry (doc §18/19: clustering/meaning is a
  human call, not something to automate away).
- **No confidence inflation.** The template explicitly tells the observer not to upgrade
  confidence just because a signal also shows up in editorial coverage — editorial is a
  separate source sector with its own incentives, not corroboration by default (voice
  rules, doc section 2).
- **Corroboration is explicit.** `source_corroboration_count` defaults to 1 (matching the
  schema's existing single-source default) and only rises if the observer actually saw
  the signal independently in multiple places.
- **Platform marketing is not organic signal.** A platform's own official "trend report,"
  newsroom post, or PR page (e.g. Pinterest's published trend reports) is self-promotional
  content, not a neutral measurement of organic user activity, and should not be logged
  the same way as directly observed posts/hashtag activity without saying so. When a
  signal's evidentiary basis is a platform's own marketing/trend-report page rather than
  organic posts you personally observed, the observer must state that explicitly in
  `human_editor_note` (e.g. "sourced from Pinterest's official trend report, not organic
  post volume") — see the template's Observer notes guidance and the worked example dated
  2026-07-06. This is a documentation/practice convention, not a new schema field or
  enforced check.

## What this does not do

This workflow does not attempt live volume/reach numbers, does not integrate any
platform API, and is not a replacement for the crawler pipeline — it is a narrow,
compliant intake path specifically for the two platforms (TikTok, Pinterest) that doc §31
blocks from automated ingestion. The Pinterest Trends API integration recommended as a
"later" step in the ingestion research remains a separate, not-yet-built follow-up.
