# Forecast calibration check (run 29)

Question: do this project's own confidence/volatility calls track what actually
happened to a signal later? Never checked before.

## What calibration research says

Tetlock's Good Judgment Project frames calibration precisely: a forecaster is
well-calibrated if events called "70% likely" happen ~70% of the time — accuracy
is scored via Brier scores, not by whether any single call felt right in
hindsight. Superforecasters do many small probability updates rather than one
confident call and stick to it, and they're distinguished less by raw
confidence than by track record over many resolved cases
([Good Judgment Project overview](https://goodjudgment.com/philip-tetlocks-10-commandments-of-superforecasting/),
[AI Impacts summary](https://aiimpacts.org/evidence-on-good-forecasting-practices-from-the-good-judgment-project/)).
That bar — many resolved cases, scored systematically — is the honest
comparison point for what follows; this project has neither yet.

Industry fashion forecasting is a cautionary tale on self-reported accuracy:
platforms like WGSN/Heuritech claim 90%+ accuracy, but independent academic
work (Clothing and Textiles Research Journal) found data-driven forecasts
matched professional trend calls only ~8% of the time, and critics note
forecasts can become self-fulfilling once retailers act on them in lockstep —
which erases the independence a real accuracy check needs
([Style3D AI summary](https://www.style3d.ai/blog/how-accurate-are-ai-fashion-trend-prediction-tools-in-2026/)).
Lesson: claimed accuracy without an independent, resolved-outcome check is not
evidence of calibration, it's marketing.

## What this project's own data shows (n is very small — read as anecdote, not proof)

Used `get_signal_status_history()` against every `data/reports/*.json`.

- **sheer-layering** (05-07: medium/recurring) → 07-06 medium/seasonal →
  08-03 dropped to low/declining. Confidence fell in step with the fade — no
  contradiction, but also no case where "medium" predicted anything before the
  fade was already visible in the data.
- **soft-tailoring** (05-07: medium/seasonal) → 07-06 rose to **high/stable**
  → 08-03 fell to low/declining just one window later. This is the most
  interesting case against calibration: a "high confidence, stable" call did
  not anticipate the very next report's collapse — the label described the
  present, not the near future.
- **archival-romanticism** (05-07: medium/emerging) never reappeared —
  1 appearance only, so "emerging" was never actually tested against
  recurrence.
- **layered-tops-styling** (low/volatile → low/declining) and
  **off-duty-varsity** (low/flash → declining → declining) and
  **peplum-waist-revival** (low/emerging → declining → declining): all three
  low-confidence, volatile/flash-labeled signals did fade as labeled — the
  cleanest matches between label and outcome in the archive.
- **cfda-vogue-fashion-fund-2026-winner**: stuck at "low/emerging" across 4
  consecutive reports (10-26 through 11-16) without resolving, despite being
  about a factual award outcome that should eventually resolve one way. This
  looks less like a volatility miscall and more like the "prolonged silence"
  pattern the schema already names — the label isn't being updated as new
  information should have arrived.

## Honest takeaway

Low-confidence/volatile-labeled signals fading is the one pattern with
multiple corroborating cases (3) in this dataset. The high-confidence case
(soft-tailoring) is a single, mildly concerning data point where "stable"
preceded a collapse rather than protecting against it — not disqualifying on
n=1, but worth re-checking the next time a "stable"/"high" signal appears
early in its life. Overall: too few signals have enough history (most appear
only once or twice) to say anything about calibration with real confidence.
This isn't a case for a schema change — it's a case for periodically re-running
this exact check as the archive grows, the way `audit_confidence.py` already
does for confidence vs. `derive_confidence()`.
