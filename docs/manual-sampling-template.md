# Manual social-signal sampling template

Fill this out weekly for any TikTok/Pinterest (or other social-platform) signal a human
observer notices. This is the compliant path for social ingestion per doc §31 — no
scraping, no automated pulls. See `docs/manual-sampling-workflow.md` for the full
rationale and `docs/agent-logs/social-ingestion-research.md` for the research behind it.

Each filled-out block below maps directly onto a `Signal` object in
`src/report_schema.py` with `source_sectors: ["social"]` (per `taxonomy.py`). Copy one
block per observed signal. Keep language descriptive and uncertain where appropriate —
no hype, no "obsessed," no shopping language (doc section 2 voice rules).

---

## Signal entry

- **Name** (`name`): short descriptive name for the signal, e.g. "balletcore ribbon
  detailing"
- **Platform(s) observed**: TikTok / Pinterest / Instagram / other — note all that apply.
  Maps into `source_sectors: ["social"]`.
- **Hashtag or trend name**: exact hashtag(s) or on-platform trend label, if any
- **Date observed** (YYYY-MM-DD): the date you personally saw/logged this, not a platform
  timestamp
- **Approximate volume/reach, if known**: view/like/post counts if visible on the public
  page — write "unknown" rather than guessing. Do not use private/authenticated-only
  data.
- **Source URL(s)**: only public, directly citable post/page URLs. If a post could
  disappear or go private, note that in observer notes. No login-walled or scraped data.
- **Observer notes** (`human_editor_note`): what you actually saw, why it seemed
  notable, any doubts. This is the human-judgment field — required, not optional (doc
  section 18/19: clustering/meaning is a human call, not automated).
- **Number of independent sources** (`source_corroboration_count`): how many separate
  posts/accounts/platforms showed this independently. Defaults to 1 if you only saw it
  once.
- **Suggested confidence** (`confidence`): one of `low`, `medium`, `high`, `archival`.
  Social-only signals should default to `low` or `medium` unless corroborated elsewhere
  — do not upgrade confidence just because it also appeared in editorial coverage (doc
  section 2).
- **Suggested volatility** (`volatility`): one of `stable`, `emerging`, `seasonal`,
  `volatile`, `flash`, `microtrend`, `recurring`, `revival`, `long_tail`, `saturated`,
  `declining`.
- **Suggested origin classification** (`origin_classification`): one of
  `designer_originated`, `editorial_amplified`, `retail_adopted`, `social_amplified`,
  `platform_native`, `archive_revival`, `unclear`. Social-sampled signals are usually
  `social_amplified` or `platform_native`.

---

### Example (filled out)

- **Name**: sheer layered slipdress over tee
- **Platform(s) observed**: TikTok
- **Hashtag or trend name**: #slipdresslayering
- **Date observed**: 2026-07-01
- **Approximate volume/reach, if known**: unknown (creator account small, <5k followers,
  but multiple similar posts seen)
- **Source URL(s)**: https://www.tiktok.com/@example/video/1234567890
- **Observer notes**: seen across three unrelated small accounts within a week, not yet
  picked up by any editorial outlet; too early to call a real signal, flagging for next
  week's re-check.
- **Number of independent sources**: 3
- **Suggested confidence**: low
- **Suggested volatility**: emerging
- **Suggested origin classification**: platform_native

---

Once filled out, hand this block to whoever assembles the week's report, or pass it
directly to `build_manual_signal(...)` in `src/manual_sample.py` to construct a valid
`Signal` object.
