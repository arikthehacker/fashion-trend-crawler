# Manual-sampling cadence check (run 32)

**Question**: is 3 exercises across 31 runs, all bursty (runs 8, 9, 28), a problem?

**Re-read of doc §31 ("compliance/source ethics")**: it contains zero cadence language.
It's a list of compliance principles (respect robots.txt, don't bypass protections, use
official APIs, cite sources, "use manually curated samples when needed") — "when needed"
is the operative phrase, not "on a schedule." Section 31 authorizes manual sampling as a
compliant substitute for scraping; it does not mandate any frequency.

The only cadence language ("Periodically (weekly, alongside the regular crawl/report
cycle)") lives in `docs/manual-sampling-workflow.md` §"The workflow" step 1 — a doc this
project wrote itself to describe an *idealized* human-editor operating rhythm, not a
requirement traceable to the source concept doc. Nothing enforces it: it's not in
`validate_report()`, not in CI, not a schema field, not referenced by
`check_field_coverage.py`.

**Assessment: infrequent-but-present sampling is adequate as designed, not a problem.**

Reasoning:
- The workflow's own core guardrail is "human judgment stays human" — a real observer
  noticing a real recurring pattern, with a mandatory non-empty `human_editor_note`. That
  is fundamentally opportunistic, not schedulable. Forcing an entry on a fixed cadence
  regardless of whether anything genuinely observable is happening on TikTok/Pinterest
  would manufacture signal to satisfy a metric — exactly what the "no confidence
  inflation" / "platform marketing is not organic signal" guardrails are trying to
  prevent.
- All three prior exercises (runs 8, 9, 28) were genuine, well-sourced, distinctly
  documented judgment calls (two Pinterest, one TikTok hashtag page), not
  rubber-stamped repeats — quality over frequency, consistent with the doc's intent.
  Bursting around active work sessions (rather than idle weekly ticks) is exactly what
  you'd expect from a project with no live staffed editor, and doesn't contradict §31.
- Since no cadence is written into §31 and nothing downstream depends on a fixed
  interval, adding a 4th sample purely to "keep cadence alive" would be manufacturing an
  entry to satisfy an external observation about *frequency*, not a real editorial
  judgment — the opposite of what this workflow is for.

**Conclusion**: no 4th exercise added this run. No code/doc changes made. Recommend
`manual-sampling-workflow.md`'s "weekly" phrasing be softened to "opportunistically,
whenever a genuine pattern surfaces" if a future run wants to close the gap between
stated intent and actual (correct) usage — but that's a documentation-precision nit, not
a functional problem worth forcing a low-value signal over.
