# Manual-sampling fix: platform marketing vs. organic signal (bias-audit run 18)

**Issue:** run 18's bias audit found Pinterest's self-promotional "trend report" pages get
tagged identically to organic social/UGC content in the manual-sampling workflow, with no
way to distinguish platform marketing from organic discourse. Per the recommendation, this
is a documentation-level fix, not a schema change.

**Changes made:**

- `docs/manual-sampling-template.md`: added explicit sub-guidance under the **Observer
  notes** (`human_editor_note`) field instructing samplers to state plainly when a signal
  is sourced from a platform's own official trend report / newsroom / marketing page
  rather than organic posts, hashtags, or search activity they observed directly — with
  the example phrasing "sourced from Pinterest's official trend report, not organic post
  volume." A worked example already existed in the file (the 2026-07-06 "Off-Duty Varsity"
  entry, which cites Pinterest Newsroom and already models this distinction well), so it
  was referenced rather than duplicated.
- `docs/manual-sampling-workflow.md`: added a new guardrail bullet, "Platform marketing is
  not organic signal," under **Guardrails this preserves**, cross-referencing the template
  guidance and the existing worked example, and explicitly noting this is a
  documentation/practice convention, not an enforced schema field.

**Not touched:** `src/manual_sample.py`, `src/report_schema.py` (no enforcement added, per
instructions). No commit made.
