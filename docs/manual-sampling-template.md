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
  - **If the signal is sourced from a platform's own official "trend report," newsroom
    post, or other marketing/PR page — rather than organic user posts, hashtag activity,
    or search volume you observed directly — say so explicitly in this field.** For
    example: "sourced from Pinterest's official trend report, not organic post volume."
    A platform publishing its own trend report is self-promotional content with its own
    incentives (driving ad sales, press coverage, platform relevance), not a neutral
    measurement of organic discourse — the same caution the workflow already applies to
    editorial coverage. There is no separate schema field for this distinction (this is
    a documentation-level fix, not a schema change); it belongs in this free-text note so
    future editors and readers know the evidentiary basis for the entry.
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

### Filled entry — 2026-07-06

- **Name**: "Off-Duty Varsity" sports-luxe summer uniform (jerseys + cargo bottoms)
- **Platform(s) observed**: Pinterest (official platform search-trend data, not a
  scraped video feed)
- **Hashtag or trend name**: no single hashtag; Pinterest's named trend label is
  "Off-Duty Varsity," tracked via search terms including "World Cup jerseys,"
  "cargo jeans," "denim jorts outfit," and "Brazil jersey outfit women"
- **Date observed**: 2026-07-06 (report reviewed/cited on this date; Pinterest's
  underlying report is dated May 26, 2026 and explicitly frames itself as a Summer
  2026 forecast, i.e. covering the season currently underway)
- **Approximate volume/reach, if known**: Pinterest-reported year-on-year search
  growth: "World Cup jerseys" +840%, "cargo jeans" +366%, "cargo pants for women"
  +363%, "denim jorts outfit" +330%, "Brazil jersey outfits" +302%, "bedazzled
  jorts" +212%. These are Pinterest's own aggregate search-index figures (600M+
  monthly active users cited), not independently verified by this project, and not
  a proxy for TikTok video volume.
- **Source URL(s)**: https://newsroom.pinterest.com/news/summer-trend-report-2026/
  (Pinterest Newsroom, official trend-report page — public, citable, not a private
  or login-walled endpoint)
- **Observer notes**: This reads less like an organic styling movement and more
  like search behavior tracking a live external event (the 2026 World Cup) —
  people searching for jersey-outfit inspiration during the tournament window
  isn't the same claim as a durable "sports-luxe" aesthetic shift. Pinterest's
  own framing ("comfort with bite") leans promotional/forecast-branding language,
  which this entry deliberately does not adopt. Single-platform, single-source
  data (one Pinterest report) with no corroborating editorial, retail, or
  designer-origin sightings collected yet, so this stays low/medium rather than
  being upgraded on the strength of the large percentage figures alone — a huge
  percentage jump can still be a small base number, and Pinterest doesn't publish
  absolute search volume. Flagging for a re-check after the tournament ends to see
  whether jersey-as-daily-top interest persists past the news-event window (which
  would indicate a genuine style shift) or collapses immediately (which would mean
  it was event-driven search noise, not a fashion trend).
- **Number of independent sources**: 1
- **Suggested confidence**: low
- **Suggested volatility**: flash
- **Suggested origin classification**: platform_native

---

Once filled out, hand this block to whoever assembles the week's report, or pass it
directly to `build_manual_signal(...)` in `src/manual_sample.py` to construct a valid
`Signal` object.
