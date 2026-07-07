# Manual-sampling policy resolution (run 52)

Run 50's gap analysis flagged the manual-sampling workflow as "acknowledged without a
defined endpoint" after only 3 exercises in 50 runs. Per run 32's precedent, forcing a
sample to hit a quota would violate the workflow's own human-judgment principle — so
this run did the real work instead of re-stating that precedent: checked for a genuine
current candidate, and then closed the actual policy gap.

**WebSearch check (this cycle):**
- Pinterest Predicts 2026 fashion trends (Glamoratti/maximalism, Poet Aesthetic,
  Explorer-inspired, brooch revival, lace, ice blue, "gimme gummy," vamp romantic):
  covered by WhoWhatWear, Axios, NBC News, The Everygirl — but all of it is wire-style
  repackaging of Pinterest's own newsroom press release (same stats, same framing, no
  independent editorial observation or critique added). This is the identical failure
  pattern run 41 found for the prior year's Pinterest Predicts report. Doesn't clear the
  bar.
- TikTok discover/hashtag pages: only SEO aggregator content (Fash Verge, Printify,
  HerFashionDaily) surfaced, generic "baddie," "academia," "coastal cowgirl" listicles
  with no independent corroboration. Doesn't clear the bar.
- **No entry added.** No report data touched.

**Policy decision (the actual ask this run):** `docs/manual-sampling-workflow.md` step 1
now states an explicit, concrete acceptance criterion instead of an open-ended
"opportunistic":
- Checked at least once per ~10 runs (a cheap WebSearch pass).
- Exercised only when a candidate has at least one source independent of the platform's
  own PR/newsroom page, AND that source shows real editorial judgment rather than
  restating the platform's press-release stats verbatim.
- A "checked, nothing cleared the bar" result (now true for runs 32, 41, 52) is defined
  as a complete, successful exercise of the step — not a debt that accumulates toward a
  forced future entry.

This replaces "no defined endpoint" with a standard future runs can actually apply:
check cadence is bounded (~10 runs), exercise cadence stays judgment-gated, and
"nothing found" is an explicit, valid terminal outcome rather than an open question.

**Verification:** `python -m py_compile src/*.py` passes. No report data was modified,
so `validate_all_reports.py` was not needed.

**Files touched:** `docs/manual-sampling-workflow.md` (policy addition only).
