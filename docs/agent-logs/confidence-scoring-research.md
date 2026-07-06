# Confidence-scoring research (run 6 candidate)

Research only — no code changed. Question: how do professional forecasting/intel
disciplines assign confidence to a claim, and can that inform a less-subjective rule
for `summarize.py`/`report_schema.py`?

## 1. ICD 203 / Words of Estimative Probability (US intelligence community)

Sherman Kent's 1964 framework, formalized in Intelligence Community Directive 203
(2007), separates two axes that ARI3LLA INDEX currently conflates into one field:

- **Likelihood** ("almost-certain," "likely," "roughly-even-chance," "unlikely," etc.,
  each mapped to a rough percentage band).
- **Confidence in the judgment itself** (low/moderate/high), which is explicitly a
  function of source quality, source diversity/corroboration, and how much analytic
  reasoning was required to connect the dots — not of how strongly worded the
  conclusion is. ICD 203 forbids blending the two ("high confidence this is likely")
  in one unsupported phrase; confidence must be justified separately from the
  probability language.
- Sources: [ICD 203 reference (GitHub)](https://github.com/wesinator/ICD203-intel-analysis), [Words of estimative probability overview](https://grokipedia.com/page/Words_of_estimative_probability), [FIRST.org CTI SIG — Communicating Uncertainties](https://www.first.org/global/sigs/cti/curriculum/cti-reporting)

Relevance: this project's `confidence` field is doing the ICD 203 "confidence in the
judgment" job, and `volatility` is closer to the "likelihood of persistence" job. They
should stay separate axes, as ICD 203 insists — good validation of the existing schema
split, but a signal here that confidence should be *evidence-derived*, not
prompt-vibes-derived.

## 2. Cyber threat intelligence (CTI) adaptation of ICD 203

CTI analysts (a domain that, like this project, aggregates open-source claims of
uneven reliability) have adapted ICD 203 into scoring tables that explicitly gate
confidence tiers on **number of independent sources + diversity of source type**, not
just source count — two reports from the same outlet family don't earn the same
confidence bump as two reports from different sectors. Source:
[Communicating Uncertainties: Estimative Language and Confidence Levels in CTI Reporting](https://medium.com/@orojcik/the-shades-of-doubt-a-guide-to-estimative-language-and-confidence-levels-in-cti-reporting-1545233f7470)

## 3. WGSN / commercial fashion forecasting

WGSN's public methodology description (marketing-level detail, no published rubric)
says its "TrendCurve AI" combines multi-sector inputs — social, search, retail,
runway, consumer sentiment — with analyst review, and that academic comparison
against EDITED found forecasts converged most reliably when corroborated across
multiple independent data streams, less reliably on any single-sector signal (e.g.
runway-only). Source:
[WGSN Trend Forecasting](https://www.wgsn.com/en/what-we-do/trend-forecasting), [Traditional vs. big-data fashion trend forecasting: WGSN and EDITED (UDSpace)](https://udspace.udel.edu/server/api/core/bitstreams/2565859a-a82a-4d49-ad8e-887879e3e5f7/content)

Relevance: commercial forecasting practice independently converges on the same
principle as ICD 203/CTI — cross-sector corroboration is the real confidence signal,
not raw mention count.

## Recommendation (not implemented — flagged for run 6)

`report_schema.py` already tracks `source_corroboration_count` per signal, and
`taxonomy.py` already assigns a `source_sector` per source. Currently `summarize.py`'s
prompt asks Claude to assign `confidence` subjectively alongside everything else. All
three frameworks above converge on: **gate the confidence tier on corroboration count
AND source-sector diversity, not corroboration count alone.**

Concrete rule to implement in a future run: add a validation/derivation step (either
in `report_schema.py`'s `validate_report()` or as a post-processing pass after
`summarize.py`'s LLM call) that computes confidence deterministically rather than
letting the model assign it freely:

- `confidence = "high"` only if `source_corroboration_count >= 2` AND those sources
  span `>= 2` distinct `source_sector` values.
- `confidence = "medium"` if corroborated (`count >= 2`) but all from one sector, or
  `count == 1` from a high-reliability sector (e.g. designer-origin, institutional
  archive).
- `confidence = "low"` for single-source, non-institutional signals (the current
  default for most social-only mentions).
- `confidence = "archival"` remains a distinct, manually-flagged tier (per existing
  taxonomy) rather than something the corroboration formula should ever output.

This turns confidence into a checkable, re-derivable value instead of an LLM
judgment call — the prompt could still narrate *why*, but the tier itself would be
computed, closing the "somewhat subjective" gap named in this task.
