# CHANGELOG — ARI3LLA INDEX rebuild

Branch: `ari3lla-index-rebuild`
Source of truth for scope: `docs/ARI3LLA INDEX.txt` (raw brainstorm transcript — section 40 has the
prioritized build list, section 41 has the JSON schema).

This file is the master **index**. Each entry below is a one-paragraph summary of a loop
run or branch-setup milestone; full detail (per-agent breakdowns, bugs found, exact file
lists) lives in its own file under `docs/changelog-entries/`. Individual per-agent working
logs are kept separately in `docs/agent-logs/*.md` for provenance (who/what changed, in the
agent's own words); the files in `docs/changelog-entries/` are the reconciled, chronological
record of what actually landed on the branch and why, just split one-file-per-run instead of
one giant file.

All timestamps are Pacific (PDT, UTC-7 — this work happened in July).

---

## Index

- **2026-07-10 ~22:15 PDT — [Loop run 93](changelog-entries/run-93.md)** — an
  86th report cleanly applies two established precedent shapes; the run-92
  flagged taxonomy gap closed with real verification, plus a useful survey of
  58 remaining editorial-domain gaps for a future run; about/case-study
  freshness re-checked 12+ runs later and remains accurate; nav/build sweep
  clean; a transient Pagefind filesystem race diagnosed and resolved without
  any code change.

- **2026-07-10 ~21:00 PDT — [Loop run 92](changelog-entries/run-92.md)** — a
  real root-cause fix for run 91's filename/date bug (the convention was
  never documented anywhere; now has an explicit docstring and a non-fatal
  validator warning that would catch a recurrence automatically); an 85th
  report immediately verifies the fix in production; taxonomy/sources pages
  re-confirmed accurate; nav/build and periodic audits both clean.

- **2026-07-10 ~19:50 PDT — [Loop run 91](changelog-entries/run-91.md)** — an
  84th report honestly logs a thin week with one factual calendar signal; a
  dormancy re-audit across the larger archive comes back clean, catching and
  discarding its own false-positive match before finalizing; the first full
  glossary voice audit since run 78 checks all 146 entries and finds zero
  violations; nav/build and periodic audits both clean.

- **2026-07-10 ~18:40 PDT — [Loop run 90](changelog-entries/run-90.md)** — an
  83rd report correctly lands the couture coverage deferred from last week;
  gh/CI check hits its official run-90 checkpoint (11th consecutive match,
  cadence to run 100); a real evidence-based review confirms the 5 precedents
  embedded in `summarize.py`'s prompt (run 89) remain the right cut — the
  other 9 have barely recurred; nav/build sweep caught and corrected its own
  false alarms before reporting; periodic audit clean.

- **2026-07-10 ~17:10 PDT — [Loop run 89](changelog-entries/run-89.md)** — an
  82nd report applies precedent 2 in both directions and respects the real
  fashion calendar (couture excluded as premature); a real structural gap
  closed — confidence discipline is now embedded directly in `summarize.py`'s
  LLM prompt, so it reaches the future automated pipeline, not just human/
  agent report-writers; gh/CI check confirmed unchanged a run early; nav/
  build and periodic audits both clean.

- **2026-07-10 ~15:50 PDT — [Loop run 88](changelog-entries/run-88.md)** — an
  81st report correctly applies precedent 2; precedent 14 (forecast/
  speculative-content exclusion) formalized after real scrutiny of a genuine
  counter-argument, backed by independent corroborating evidence from a
  report a full year earlier; a real README/live-site inconsistency found
  and fixed (README presented the off-limits `crawler.py` as routine); nav/
  build and periodic audits both clean.

- **2026-07-10 ~14:40 PDT — [Loop run 87](changelog-entries/run-87.md)** — an
  80th report correctly applies precedent 4 on its earning side; the run-86
  resale-source-seeding gap closed with a rigorous, honest "none pass" verdict
  (all 5 candidate domains confirmed JS-rendered and unreachable); the manual-
  sampling cadence ran on its due date with the same honest negative as every
  prior check; nav/build sweep explicitly re-confirms run 86's year-boundary
  fix under a truly clean build this time; periodic audit clean.

- **2026-07-10 ~13:30 PDT — [Loop run 86](changelog-entries/run-86.md)** — a
  79th report crosses into 2028 for the first time, with a careful exclusion
  of speculative forecast content; year-boundary archive rendering confirmed
  working after the coordinator caught and disproved a false-alarm regression
  report from a stale concurrent-build artifact; robots/crawl-budget audit
  confirms run 78's findings still hold; periodic audit finds a real
  structural gap (resale domains classified but not seeded as sources).

- **2026-07-10 ~12:15 PDT — [Loop run 85](changelog-entries/run-85.md)** — a
  78th report honestly logs a thin Christmas week with zero manufactured
  signals; a 13th confidence precedent formalized after real research
  (resale-platform data reflects supply/discard behavior, not demand); a
  genuinely data-driven "not yet" on an archive tag-filter, backed by real
  tag-distribution numbers; nav/build and periodic audits both clean.

- **2026-07-10 ~11:00 PDT — [Loop run 84](changelog-entries/run-84.md)** — both
  run-83 flagged confidence-precedent inconsistencies resolved as corrections
  (a directly on-point counter-example found in precedent 2's own worked
  examples, invalidating one proposed exception outright); a 77th report
  correctly leaves a genuinely novel case unforced rather than inventing a
  silent exception; run 82's `changed_signals` provenance feature exercised
  for real for the first time and confirmed working; archive year-grouping
  independently re-verified clean; nav/build and periodic audits both clean.

- **2026-07-10 ~09:50 PDT — [Loop run 83](changelog-entries/run-83.md)** — 76th
  report correctly trusts the mechanical formula where no override applies;
  archive page gets a proportionate year-grouping fix (not over-built); a
  landmark 12-precedent confidence-discipline reference is consolidated,
  surfacing two genuine unreconciled precedent departures flagged for human
  judgment rather than auto-corrected; nav/build and periodic audits both
  clean.

- **2026-07-10 ~08:10 PDT — [Loop run 82](changelog-entries/run-82.md)** — 75th
  report keeps two independently-sourced signals correctly un-merged; a
  dormancy/prolonged-silence convention audit comes back genuinely clean; a
  real provenance gap closed (revision_history now auto-records exactly which
  signals changed, not just that something did); nav/build clean; periodic
  audit finds and fixes a real doc-tracking gap in the manual-sampling
  cadence's own source-of-truth file.

- **2026-07-10 ~06:50 PDT — [Loop run 81](changelog-entries/run-81.md)** — 74th
  report continues a synthesis-signal discipline; the signal-reuse checker's
  5-item false-positive baseline eliminated via a conservative, recall-
  preserving fix (independently verified with a standalone recall test);
  taxonomy/sources pages get two real staleness fixes (missing recent
  sources, missing Origin Classification dimension); nav/build clean;
  periodic audit confirms the API-key fix holds.

- **2026-07-10 ~05:40 PDT — [Loop run 80](changelog-entries/run-80.md)** — 73rd
  report keeps a thread honestly un-padded and a new one correctly un-merged;
  gh/CI check hits its official run-80 checkpoint (9th consecutive match,
  cadence to run 90); About/case-study freshness audit clean; nav/build clean;
  periodic audit finds and fixes the actual root cause of two prior API-key
  false negatives (split shell invocations losing environment state) instead
  of just re-flagging it again.

- **2026-07-10 ~04:30 PDT — [Loop run 79](changelog-entries/run-79.md)** — 72nd
  report adds the Bogotá thread's first designer-sourced intent statement;
  gh/CI check confirmed unchanged a run early as a courtesy for run 80;
  methodology page updated with three real fixes reflecting the confidence
  and longitudinal-tracking discipline actually in force since runs 71-78;
  nav/build clean; periodic audit flags its own API-key check as now
  unreliable across two consecutive runs, to be independently re-verified
  going forward.

- **2026-07-10 ~03:20 PDT — [Loop run 78](changelog-entries/run-78.md)** — 71st
  report reasons through a mechanical-vs-intent confidence override in detail;
  a real RSS bug fixed (unbounded feed growth, now capped at 50 items per
  researched convention); sitemap/SEO audit confirms complete coverage and
  existing JSON-LD, with an explicit no-expansion judgment call; nav/build
  clean; periodic audit self-corrected an inaccurate environment claim after
  independent verification.

- **2026-07-10 ~02:10 PDT — [Loop run 77](changelog-entries/run-77.md)** — 70th
  report keeps an independent São Paulo echo distinct from its parent Bogotá
  thread; the manual-sampling cadence was run proactively before it could
  lapse again (honest negative, consistent with every prior check); the
  "Vogue" glossary gap resolved with a real definition rather than a scanner
  hack; nav/build sweep correctly distinguished concurrent-agent timing from
  a real regression; periodic audit clean.

- **2026-07-10 ~01:05 PDT — [Loop run 76](changelog-entries/run-76.md)** — 69th
  report continues the Bogotá thread on genuine new movement; a real
  accessibility bug fixed (most signal titles had no heading element at all,
  invisible to screen readers) and independently confirmed in built output; a
  quick status-read header added to `/signals/[slug]` without crossing the
  project's editorial-judgment boundary; nav/build and periodic audits both
  clean, with the manual-sampling cadence flagged as due for a proactive run
  soon.

- **2026-07-09 ~23:55 PDT — [Loop run 75](changelog-entries/run-75.md)** — 68th
  report honestly closes the 5-week Margiela thread and opens a genuinely new one
  (first real Inexmoda corroboration); Middle East source gap closed with a
  verified Vogue Arabia addition; SITE_URL audit confirms it's already correctly
  centralized, needing only a human-supplied domain; nav/build sweep found the
  prior Turbopack flake did not recur; periodic audit correctly applied last run's
  API-key-check lesson.

- **2026-07-09 ~22:50 PDT — [Loop run 74](changelog-entries/run-74.md)** — 67th
  report distinguishes single-sector confirmation from real cross-sector
  corroboration; Colombia's Inexmoda added as a verified institutional source; 50
  missing glossary definitions added, closing a persistent build-warning source;
  nav/build sweep documented a non-reproducing Turbopack flake; periodic audit
  caught and corrected its own false-negative API-key check.

- **2026-07-09 ~21:45 PDT — [Loop run 73](changelog-entries/run-73.md)** — closes
  run 72's daemon-thread leak (crawler process now exits cleanly after a timeout,
  independently re-verified); 66th report distinguishes retail adoption from
  runway/social amplification; South America source gap closed with a verified
  Brazilian editorial source (`ffw.com.br`); nav/build regression and periodic
  audit both clean.

- **2026-07-09 ~20:30 PDT — [Loop run 72](changelog-entries/run-72.md)** — crawler
  hang fix implemented and locally proven (localhost-only test), but a real
  non-daemon-thread leak found on independent re-verification means it's still not
  clean for autonomous execution; 65th report; a retroactive-confidence review
  correctly declined an unearned edit; nav/build sweep caught and fixed a stale-
  build artifact; periodic audit added a CHANGELOG-integrity check.

- **2026-07-09 ~19:15 PDT — [Loop run 71](changelog-entries/run-71.md)** — 64th
  report resolves the NYFW SS28 scheduling thread and continues confidence
  discipline on a Margiela signal; crawler hang gets a refined diagnosis and a
  drafted (unexecuted) `ThreadPoolExecutor` fix; journalism-standards check against
  AP/Reuters conventions clean; nav/build regression and periodic audit both clean.

- **2026-07-09 ~18:00 PDT — [Loop run 70](changelog-entries/run-70.md)** — `gh`/CI
  check re-confirmed unchanged, cadence extended to run 80; two new domains
  classified (`fhcm.paris`, `laforma.club`); 63rd report continues the honest
  absence-of-evidence discipline established last run, this time for NYFW SS28's
  still-unannounced schedule; nav/build regression and periodic audit both clean.

- **2026-07-09 ~16:45 PDT — [Loop run 69](changelog-entries/run-69.md)** — 62nd report
  carefully distinguishes scheduling logistics from a real style signal; a
  colors/aesthetic_terms vocabulary audit comes back genuinely clean (unlike run 67's
  garments/silhouettes finding); a real process gap found — the manual-sampling
  ~10-run cadence had silently lapsed for 17 runs — checked and reset; nav/build
  regression and periodic audit both clean. `gh` CLI check due next run.

- **2026-07-09 ~15:30 PDT — [Loop run 68](changelog-entries/run-68.md)** — The
  historical godet-skirt vocabulary overlap gets a real, decisive fix (controlled
  taxonomy fields warrant retroactive correction, unlike editorial narrative); 61st
  report continues confidence discipline; CHANGELOG's run-13 index/detail split
  verified still holding up cleanly at 67 runs; nav/build regression and periodic
  audit both clean.

- **2026-07-09 ~14:15 PDT — [Loop run 67](changelog-entries/run-67.md)** — Made real
  progress diagnosing the crawler hang via pure static code review (no execution): a
  plausible per-read-vs-total-transfer-time timeout mismatch, corroborated by a
  delayed straggler finding that crawl output is only written once at the end,
  discarding all progress on a hang/kill. Applied a safe incremental-flush mitigation,
  verified only via py_compile. 60th report continues confidence discipline; a real
  garments/silhouettes vocabulary boundary violation found and fixed.

- **2026-07-09 ~13:00 PDT — [Loop run 66](changelog-entries/run-66.md)** — Root cause
  of three consecutive crawler-pipeline stalls (runs 62, 65, 66) finally found: not
  agent scoping, but `crawler.py` itself hanging indefinitely — two real hung
  processes found and killed during consolidation. Flagged directly for the user;
  recommend no further autonomous crawler-pipeline attempts until debugged. 59th
  report and a real RSS spec gap both shipped cleanly alongside.

- **2026-07-09 ~11:45 PDT — [Loop run 65](changelog-entries/run-65.md)** — `.env.example`
  and setup docs added, closing run 64's flagged gap; 58th report shows real
  confidence discipline against an inflated derived score; source-domain freshness
  spot-check clean. The first genuine real-pipeline (crawl→summarize→save) attempt
  stalled a second time despite tightened instructions — no secret exposure occurred,
  confirmed explicitly, but a different approach is needed for the next attempt.

- **2026-07-09 ~10:30 PDT — [Loop run 64](changelog-entries/run-64.md)** —
  Significant correction to run 63: the "missing API key" blocker on real-pipeline
  reports was wrong — a working key exists in a git-ignored `.env`, verified live
  with a real API call. The real pipeline can actually run end-to-end; the gap is
  now just missing setup docs (`.env.example`). 57th report logs a genuine
  cross-sector coverage-asymmetry judgment call; URL-persistence review and nav/build
  regression sweep both clean.

- **2026-07-09 ~09:15 PDT — [Loop run 63](changelog-entries/run-63.md)** — Retried run
  62's stalled crawler-pipeline attempt with a strict synchronous time-box; completed
  cleanly, confirmed the pipeline's real output corroborates rather than duplicates
  existing reporting. Also surfaces a more concrete blocker: `summarize.py` can't run
  without an API key set in this environment. A real per-signal deep-linking gap
  fixed; doc-sync catches a missing file reference; a leftover scratch artifact
  cleaned up during consolidation.

- **2026-07-09 ~08:00 PDT — [Loop run 62](changelog-entries/run-62.md)** —
  `check_signal_reuse_claims.py` made a standing periodic-audit step after
  cross-confirmation by 3 independent agents; reading-level accessibility quantified
  and correctly accepted as a deliberate voice-rule tradeoff; 55th report honestly
  reports mixed couture reception. One subagent stalled attempting a real
  crawler-pipeline report — noted honestly rather than re-dispatched mid-consolidation.

- **2026-07-09 ~06:45 PDT — [Loop run 61](changelog-entries/run-61.md)** — Direct
  response to run 60's flagged self-report reliability gap: a real checker script
  built and honestly verified for the exact signal-reuse bug pattern seen twice;
  two independent agents converge on the same Met Gala "untracked going forward"
  transition, verified consistent; new report's agent explicitly self-verified before
  reporting; keyboard-navigability and full nav/build regression sweeps both clean.

- **2026-07-09 ~05:30 PDT — [Loop run 60](changelog-entries/run-60.md)** — 60th loop
  run milestone. `is_prolonged_silence()` fires on real accumulated data for the first
  time (Met Gala 2027, 4 occurrences); `gh`/CI check re-confirmed unchanged; internal
  citation persistence verified clean via git history. A milestone retrospective names
  a real trend — ~40% of the last 10 runs existed to fix a problem a prior run in the
  same loop introduced — flagged directly to the user, not filed as routine.

- **2026-07-09 ~04:15 PDT — [Loop run 59](changelog-entries/run-59.md)** — Run 58's
  Met Gala signal-reuse bug did not recur, confirmed independently by two agents;
  dark mode verified against real built CSS and 435 inline style usages; robots.txt/
  sitemap indexability confirmed clean since run 5; doc-sync fixes a stale
  `requirements.txt`-less install command and adds missing skip-link/dark-mode notes.

- **2026-07-09 ~03:00 PDT — [Loop run 58](changelog-entries/run-58.md)** — Found two
  real problems with the new Met Gala signal-reuse mechanism run 57 just built: the new
  report claimed to reuse the signal_id but actually minted a different tag, and run
  57's own new Signal object had reintroduced the exact incorrect "hasn't occurred yet"
  hypothesis run 56 fixed elsewhere in the same report — both caught and corrected
  before committing, with the accumulating history verified working afterward.
  Glossary warnings cleared to zero; dark mode added with real contrast-ratio
  verification; nav/build regression sweep clean.

- **2026-07-09 ~01:30 PDT — [Loop run 57](changelog-entries/run-57.md)** — 50th report;
  Met Gala 2027 finally given a real tracked signal (with an honest caveat about what
  it does and doesn't fix); a second, independently-found dormancy gap closed in the
  same file; skip-link and heading-hierarchy checks both verified clean against real
  built output; a stuck build traced to leftover server processes from a prior agent's
  verification step, cleared and rebuilt.

- **2026-07-09 ~00:15 PDT — [Loop run 56](changelog-entries/run-56.md)** — 49th report's
  drafted Met Gala reasoning contradicted the archive's own established finding about
  the event's date; caught and corrected before committing. Two domains classified,
  a real skip-link accessibility gap fixed across all 13 pages, a thorough post-Brotli
  crawler health check confirms only one source was affected, and a structural gap
  found (Met Gala 2027 has no real tracked signal_id).

- **2026-07-08 ~23:00 PDT — [Loop run 55](changelog-entries/run-55.md)** — Run 54's
  independent-criticism source fix was actually broken under the real crawl path
  (Brotli decoding); found via real-pipeline testing and fixed by adding `brotli` as
  a genuine dependency plus the repo's first `requirements.txt`, verified with 10 real
  headlines returned; a real 404 page added; doc-sync fixes a missing favicon
  reference; 48th report shows careful confidence discipline; periodic audit clean.

- **2026-07-08 ~21:45 PDT — [Loop run 54](changelog-entries/run-54.md)** — Solves a
  30+ run mystery: the run-19 confidence-gate fix was untested because the
  `independent_criticism` sector was structurally unreachable (no source in
  `FASHION_SOURCES`), not because the fix was wrong — added a real, verified
  independent-criticism source; 47th report exercises a genuine high-confidence
  override case; Rich Results and font-loading checks both return clean, honest
  compliance results; periodic audit clean.

- **2026-07-08 ~20:30 PDT — [Loop run 53](changelog-entries/run-53.md)** — 46th report
  finds a genuinely notable Met Gala coverage silence; the `gh` CLI question is
  resolved thoroughly via a real alternative-verification attempt (confirmed the repo
  is private, not just re-checking) and its cadence downgraded; a favicon gap found
  and fixed; nav/link/build regression sweep clean; a real static-export build break
  from the new favicon route caught and fixed during consolidation.

- **2026-07-08 ~19:15 PDT — [Loop run 52](changelog-entries/run-52.md)** — 45th report
  ends the thin-week streak with a genuine Chanel Cruise signal; the manual-sampling
  ambiguity flagged in run 50 gets a concrete acceptance policy instead of open-ended
  acknowledgment; Open Graph/social-card metadata added; a follow-up check finds and
  fixes real methodology-page overclaims run 51 missed; `gh` CLI unavailability hits a
  20-consecutive-check milestone.

- **2026-07-08 ~18:00 PDT — [Loop run 51](changelog-entries/run-51.md)** — Responds to
  run 50's flagged human-in-the-loop finding by fixing three real overclaims in the
  site's own copy (a byline literally read "human-reviewed by loop-consolidation"),
  without attempting to resolve the underlying process gap itself; confirms the real
  crawler pipeline is infrastructurally healthy; adds operator-transparency disclosure;
  44th report handles a thin week honestly; periodic audit clean.

- **2026-07-08 ~16:45 PDT — [Loop run 50](changelog-entries/run-50.md)** — 50th loop
  run, 43rd report. A milestone gap analysis surfaces a significant structural finding:
  the loop's own process doesn't fully satisfy the site's stated human-in-the-loop
  principle (flagged directly for a human decision, not filed as routine TODO); a real
  redundant full-archive read regression fixed in the glossary page; sitemap `lastMod`
  gap fixed; periodic audit clean.

- **2026-07-08 ~15:30 PDT — [Loop run 49](changelog-entries/run-49.md)** — 42nd report
  catches a real false-resolution trap (a 2025-cycle CFDA announcement mistaken for the
  tracked 2026 question) and honestly revises a saturated signal's volatility; all 27
  source domains verified live; a genuine `human_editor_note` copy-paste gap found and
  fixed at the prompt level; a print stylesheet added for archival citation use;
  periodic audit clean.

- **2026-07-08 ~14:15 PDT — [Loop run 48](changelog-entries/run-48.md)** — 41st report
  avoids a false recurrence claim; the run-47-flagged recurrence threshold gets a real
  `styleOnly` filter instead of another deferral; the external correction-request
  channel question is finally closed with a real GitHub Issues link; an AP-style
  headline-case check returns an honest compliance result; periodic audit clean.

- **2026-07-08 ~13:00 PDT — [Loop run 47](changelog-entries/run-47.md)** — Archive
  crosses 40 reports. The run-24 recurrence threshold is finally met, but composed of
  unresolved-question signals, not style trends — built a minimal honest addition
  instead of the previously-declined narrative retrospective; Trust Project audit finds
  and honestly discloses a real corrections-channel gap; full-archive coherence review
  fixes real doc gaps at the milestone; periodic audit clean.

- **2026-07-08 ~11:30 PDT — [Loop run 46](changelog-entries/run-46.md)** — 39th report
  correctly separates retrospective trend-roundup commentary from new in-window
  reporting; Feb-March RTW fashion month added to the editorial calendar; a CC BY 4.0
  license added for the new public JSON download; the download route hardened against
  `next build` vs `npm run build` invocation differences; periodic audit clean.

- **2026-07-08 ~10:15 PDT — [Loop run 45](changelog-entries/run-45.md)** — 38th report
  finds a previously-undocumented Feb-March RTW fashion month underway; a public
  raw-JSON download route closes run 44's flagged Dataset-schema gap; a methodology
  transparency box added per Pew/FiveThirtyEight convention; nav/link audit and
  periodic audit both clean.

- **2026-07-08 ~09:00 PDT — [Loop run 44](changelog-entries/run-44.md)** — 37th report
  finally makes the Wales Bonner "untracked going forward" transition decision at its
  planned checkpoint; homepage dominant-mood metric gets an honest 12-week staleness
  cutoff; report pages gain Dataset structured data alongside NewsArticle; a slug audit
  renames 4 over-length slugs with a full prose sweep done upfront; a real cross-run
  slug collision caught and fixed during consolidation.

- **2026-07-08 ~07:45 PDT — [Loop run 43](changelog-entries/run-43.md)** — 36th report
  carefully avoids conflating tracked signals with unrelated real-world events; the
  long-carried self-archival question finally resolved with a concrete manifest tool
  and trigger condition instead of another deferral; RSS item titles/categories
  improved per RSS 2.0 best practices; homepage index module verified fresh against
  15+ new reports; periodic audit clean.

- **2026-07-08 ~06:30 PDT — [Loop run 42](changelog-entries/run-42.md)** — 35th report
  holds the revisit plan on the Wales Bonner prolonged-silence question; a real WCAG 2.2
  target-size violation found and fixed across 5 nav instances; a genuine prompt-drift
  bug (stale sector list) found and fixed 11 runs after the last clean audit; RSS/
  sitemap/Pagefind freshness clean; doc-sync/nav audit fixes `/case-study`'s missing nav
  and a skill-doc file-map gap.

- **2026-07-08 ~05:15 PDT — [Loop run 41](changelog-entries/run-41.md)** — 34th report
  carefully judges the Wales Bonner prolonged-silence question rather than forcing a
  state transition; `thenationalnews.com` removed after a real decision (client-side
  rendered, no fix worth the complexity); byline-level AI disclosure added per
  Trusting News/AP research; manual-sampling check returns an honest negative;
  periodic audit clean.

- **2026-07-08 ~04:00 PDT — [Loop run 40](changelog-entries/run-40.md)** — 33rd report
  crosses the prolonged-silence threshold for the Wales Bonner/Hermès debut for the
  first time; glossary build warnings curated down to zero; a real crawl-path test finds
  one new source is client-side rendered and yields no headlines; correction notices
  brought in line with AP/NYT placement standards; full-archive coherence review clean.

- **2026-07-08 ~02:45 PDT — [Loop run 39](changelog-entries/run-39.md)** — 32nd report
  honestly reports 3 consecutive windows with no post-show coverage; glossary
  build-warning noise cut 130 → 19 with a term-plausibility filter; two new
  geographically-diverse sources added (Hong Kong, UAE); the run-35 archival/link-rot
  question closed for good with a documented permanent design decision; periodic audit
  clean.

- **2026-07-08 ~01:30 PDT — [Loop run 38](changelog-entries/run-38.md)** — Dedicated
  slug-reference audit finds 17 more stale prose mentions run 37 missed; 31st report
  re-checks and correctly does not force a correction; build-time warning added for
  undefined glossary terms; editorial calendar gains a January menswear/couture window;
  `source_domains` extended to the per-signal history page.

- **2026-07-08 ~00:15 PDT — [Loop run 37](changelog-entries/run-37.md)** — `source_domains`
  fully wired end-to-end; 30th report catches a false lead; the report-page
  dateModified fix extended to RSS; a new glossary failure mode found (undefined terms
  silently dropped); periodic audit catches a real regression from last run's slug
  rename.

- **2026-07-07 ~23:00 PDT — [Loop run 36](changelog-entries/run-36.md)** — Resolves the
  source-citation tension with a real decision (`source_domains`, homepage-only,
  schema-enforced); completes the dedicated slug-curation pass (12 renames); IPTC check
  finds and fixes a real `dateModified` bug; fresh CI environment verification clean.

- **2026-07-07 ~21:30 PDT — [Loop run 35](changelog-entries/run-35.md)** — All 5 tasks
  tightly scoped, no stalls. 28th report exercises the "untracked going forward"
  convention for real; slug-quality check correctly stops at its scope boundary;
  archival research finds a real citation gap in tension with a prior run's removal;
  quality spot-check and Pagefind regression check both clean.

- **2026-07-07 ~20:15 PDT — [Loop run 34](changelog-entries/run-34.md)** — 27th report;
  editorial calendar addition retried successfully after last run's stall; `source_links`
  removed with real reasoning; a genuinely new honest "untracked going forward" state
  designed for factual questions that never resolve; homepage index-module concern
  verified as a non-issue.

- **2026-07-07 ~18:45 PDT — [Loop run 33](changelog-entries/run-33.md)** — CFDA Fashion
  Awards crosses the prolonged-silence threshold for real, validating the run-29 tool;
  doc-sync finds and fixes real drift (missing tool scripts, stale sample-count claims);
  source-protection research finds no real risk but flags dead TS typing; a 4th instance
  of the populated-but-unrendered bug found and fixed on the signal history page.

- **2026-07-07 ~17:00 PDT — [Loop run 32](changelog-entries/run-32.md)** — 25th report
  avoids conflating two similarly-named award shows; periodic audit closes out 2 more
  overdue dormant signals; year-end review research correctly declines an unsupported
  feature; search facets confirmed fully dynamic; manual-sampling cadence check declines
  to manufacture a signal just to hit a quota.

- **2026-07-07 ~15:30 PDT — [Loop run 31](changelog-entries/run-31.md)** — Confirms
  `human_editor_note` was the one real "populated by convention, not schema-enforced"
  gap; 24th report; resort/cruise calendar research added; full-year coherence review
  clean across 23 reports; performance check fixes a real redundant-call issue.

- **2026-07-07 ~13:50 PDT — [Loop run 30](changelog-entries/run-30.md)** — Built a
  heading-bug heuristic (honest negative result); 23rd report finds a real signal that
  was only ever tracked in prose, never as a real `signal_id`; conservative prompt audit
  correctly declines a rewrite; citation format improved; manual-sampling check finds
  `human_editor_note` was never actually a schema field — fixed properly.

- **2026-07-07 ~12:30 PDT — [Loop run 29](changelog-entries/run-29.md)** — Resolved
  prolonged-silence handling with a minimal helper, not a new field; 22nd report adds a
  genuine Black Friday signal; skill doc codifies the "documented ≠ working" lesson;
  forecast-calibration check honestly finds one concerning miscalibration; accessibility
  audit fixes a 4th instance of the recurring heading bug.

- **2026-07-07 ~11:10 PDT — [Loop run 28](changelog-entries/run-28.md)** — 21st report
  handles a 4th-window open question with a named explanation instead of repetition;
  manual sampling diversified beyond Pinterest for the first time (TikTok, compliant);
  a documented-but-never-fixed garment drift finally corrected; continuity research
  found README's run instructions were actually broken and fixed them; RSS/sitemap
  verification found and fixed a real missing-routes bug.

- **2026-07-07 ~09:50 PDT — [Loop run 27](changelog-entries/run-27.md)** — Closed out
  layered-tops-styling's 13-window dormancy; 20th report correctly avoids conflating a
  similarly-named UK award with the still-open CFDA question; added non-English source
  translation-transparency to the prompt; archive-milestone research correctly declined
  an unnecessary feature; signal-link integrity fully verified clean.

- **2026-07-07 ~08:30 PDT — [Loop run 26](changelog-entries/run-26.md)** — Resolved
  review_status/reviewed_by (rendered, real data); 19th report; periodic audit flags
  layered-tops-styling as 13-windows dormant; genuine Southeast Asian source progress
  (first local-language outlet added); fixed a real UX gap — corrections/AI-disclosure
  content had no pointer from report pages, the actual reader entry point.

- **2026-07-07 ~07:10 PDT — [Loop run 25](changelog-entries/run-25.md)** — Built a
  structural fix (`check_field_coverage.py`) for the 3-times-recurring unrendered-field
  bug; 18th report honestly logs an unresolved signal instead of fabricating; first full
  voice audit since run 10 finds nothing wrong across 14 runs of additions; fashion
  archive research validates current schema design; confidence-gate fix verification is
  an honest "still untested" result.

- **2026-07-07 ~05:50 PDT — [Loop run 24](changelog-entries/run-24.md)** — Systematic
  transparency sweep finds a third instance of the "claimed but not shown" bug pattern
  (`thin_week_note`) — fixed; de-staled README/PROJECT_STRUCTURE's report-count claims
  for good; 17th report closes out a stale signal; retrospective-format research
  correctly deferred a premature feature; CI verification honestly notes it's never
  been confirmed against real GitHub Actions.

- **2026-07-07 ~04:30 PDT — [Loop run 23](changelog-entries/run-23.md)** — 16th report
  genuinely confirms the post-fashion-month volume drop (not assumed); fixed real nav
  gaps (`/search`/`Glossary` missing from primary nav); found and fixed the corrections-
  transparency claim was actually false on the live site; confidence/dormancy review
  clean; doc-sync fixed README/PROJECT_STRUCTURE staleness again.

- **2026-07-07 ~03:10 PDT — [Loop run 22](changelog-entries/run-22.md)** — Investigated
  automating the heading-hierarchy check (honestly concluded ESLint can't catch it,
  documented a manual checklist instead); added glossary/taxonomy cross-link; 15th report
  closes out fashion month; made a real placement decision keeping the index module
  homepage-only; cross-report audit of all 5 fashion-month reports found and fixed one
  real gap.

- **2026-07-07 ~01:50 PDT — [Loop run 21](changelog-entries/run-21.md)** — Formalized the
  garment-terminology practice; a third doc re-read found `human_editor_note` was never
  rendered anywhere despite substantive data — fixed; 14th report caught a real
  sourcing-integrity issue; index module stress-tested clean; accessibility audit found
  the run-5 heading bug recurring in brand-new pages — fixed again.

- **2026-07-07 ~00:30 PDT — [Loop run 20](changelog-entries/run-20.md)** — Shipped the
  two doc-central gaps run 19 found: "THIS WEEK'S INDEX" (real derived metrics on the
  homepage) and `/glossary` (terms extracted from the actual archive). Also fixed real
  nav drift, researched Costume Core vocabulary standards (concluded not worth adopting
  yet), and added a 13th report.

- **2026-07-06 ~23:50 PDT — [Loop run 19](changelog-entries/run-19.md)** — Tuned the
  confidence-conservatism prompt; added manual-sampling marketing-vs-organic guidance; a
  12th report proved the busy-week fixes hold under real fashion-week volume; source
  diversity narrowed further; a full re-read of the original doc found two genuine
  18-run-old gaps: an unbuilt glossary page and the "THIS WEEK'S INDEX" metrics module.

- **2026-07-06 ~22:45 PDT — [Loop run 18](changelog-entries/run-18.md)** — Found and fixed
  a real crawler bug (Cloudflare 403 on robots.txt false-blocking a source); proactively
  raised `max_tokens` ahead of fashion month; added an 11th report; second bias-audit pass
  confirmed a real confidence-conservatism pattern with production data; doc-sync found
  README/PROJECT_STRUCTURE undercounting reports by more than half.

- **2026-07-06 ~21:30 PDT — [Loop run 17](changelog-entries/run-17.md)** — Expanded
  source diversity (partial fix, honestly caveated); added homepage thin-week framing;
  10th report ends the 5-week thin streak with an earned "normal" status and catches a
  likely reversed-causality claim; refreshed docs, added a reusable editorial-calendar
  reference.

- **2026-07-06 ~20:15 PDT — [Loop run 16](changelog-entries/run-16.md)** — Added a 9th
  report (5th consecutive thin week); closed out 3 dormant signals; added low-volatility
  methodology framing; first real bias audit found and fixed an inconsistent confidence
  gate; backfilled meaningful `reviewed_by` provenance; confirmed fashion month
  (~Sept 8 – Oct 6, 2026) should end the quiet stretch structurally.

- **2026-07-06 ~19:00 PDT — [Loop run 15](changelog-entries/run-15.md)** — Ran a real
  crawl to test whether the 4-thin-week streak was a WebSearch artifact — confirmed it's a
  genuine quiet period. Added soft review-status metadata; created `PROMPT_CHANGELOG.md`;
  verified Pagefind search fully works end-to-end via a real `npm install`/build;
  confidence/dormancy review found nothing new.

- **2026-07-06 ~17:45 PDT — [Loop run 14](changelog-entries/run-14.md)** — Fixed static
  export properly (real `out/` output confirmed); added `/rss.xml`; added an 8th report,
  now the 4th consecutive thin week, explicitly flagged as a streak; fixed stale
  README/PROJECT_STRUCTURE/skill-doc references; AI-journalism-standards research found
  real gaps (auditable review records, prompt versioning, bias audits).

- **2026-07-06 ~16:45 PDT — Loop run 13 homepage rewrite (approved)** — User approved
  retiring `web/lib/trends.ts`; homepage rebuilt as a masthead + latest-report teaser via
  `getLatestReport()`; deleted the 4 legacy `trends_raw.json`/`trends_summary.json` files —
  **migration step 5/5 complete**, closing the 6-run-old legacy-migration plan.

- **2026-07-06 ~16:30 PDT — [Loop run 12](changelog-entries/run-12.md)** — Shipped `/search`
  with client-side facet filtering; built a signal-dormancy history helper instead of a
  static status field; expanded taxonomy outlet coverage; added a 7th report (Copenhagen
  Fashion Week, correctly logged as pre-show forecast); a 12-run health-check audit flagged
  `off-duty-varsity`'s unresolved dormancy and a "3 thin reports in a row" pattern worth
  watching. All checks clean.

- **2026-07-06 ~15:15 PDT — [Loop run 11](changelog-entries/run-11.md)** — Proposed (not yet
  executed, needs sign-off) retiring `web/lib/trends.ts` since the homepage renders a stale
  crawl snapshot; fixed real nav-coherence drift across 5 pages; designed (not built)
  Pagefind + facet search; added a 6th report with two signals correctly downgraded on
  dormancy.

- **2026-07-06 ~14:00 PDT — [Loop run 10](changelog-entries/run-10.md)** — Wired
  `revision_reason`/`corrected_at` through `summarize.py`; found a real migration blocker —
  `web/lib/trends.ts` still reads legacy cache files, missed by every prior migration step;
  fixed a tonal voice slip on the about page; added a 5th report that honestly used
  `collection_status: "thin"` instead of padding; refreshed README/case-study to match
  actual shipped state.

- **2026-07-06 ~12:45 PDT — [Loop run 9](changelog-entries/run-09.md)** — Implemented the
  `revision_history` mechanism on `save_report()`; completed migration step 4/5
  (`test_tools.py`); exercised manual sampling a second time (Poetcore signal); added an
  explicit git-safety guardrail to the skill doc after run 8's coordination bug — no work
  lost this run.

- **2026-07-06 ~11:30 PDT — [Loop run 8](changelog-entries/run-08.md)** — Biggest-finding
  run: a live `crawler.py` + `summarize.py` run against real network/API succeeded and
  surfaced a real bug (`max_tokens=2000` truncating responses, fixed to 4000); a
  coordination bug was also found and fixed, where one agent's broad git revert silently
  wiped two other agents' concurrent work (redone from their logs). Retention/versioning
  design proposed, not implemented.

- **2026-07-06 ~10:10 PDT — [Loop run 7](changelog-entries/run-07.md)** — Added
  Corrections/Editorial-Independence/AI-Involvement disclosure sections; migration step
  2/5; added `collection_status`/`thin_week_note` schema fields for honest thin-week
  reporting; refreshed the stale skill doc; audited all signals and flagged one
  (Resale/secondhand) with confidence overstated relative to corroboration, for human
  review.

- **2026-07-06 ~09:00 PDT — [Loop run 6](changelog-entries/run-06.md)** — Implemented
  `derive_confidence()` (opt-in); migration step 1/5; curated overly long signal slugs;
  added a 4th report; fixed a cross-run consistency bug where a concurrent slug-curation
  and new-report agent produced mismatched slugs; gap analysis found no
  corrections/transparency disclosure existed anywhere on-site.

- **2026-07-06 ~07:50 PDT — [Loop run 5](changelog-entries/run-05.md)** — Fixed WCAG heading
  hierarchy; added sitemap/robots/JSON-LD SEO; added an archival "Cite as" citation line;
  wrote a detailed (unexecuted) legacy-migration plan, noting `server.py` is a real MCP
  server contract; researched confidence-scoring frameworks for run 6. Three agents
  concurrently edited the same report page file and merged cleanly.

- **2026-07-06 ~06:40 PDT — [Loop run 4](changelog-entries/run-04.md)** — Added CI
  (`validate_all_reports.py` + GitHub Actions workflow, failure path actually tested);
  exercised `manual_sample.py` for the first time (Off-Duty Varsity signal); shipped
  `/signals/[slug]` and fixity-field UI display; researched (not yet implemented)
  accessibility/SEO fixes for run 5.

- **2026-07-06 ~05:30 PDT — [Loop run 3](changelog-entries/run-03.md)** — Added
  `Signal.signal_id` slugs and backfilled them across reports; found and fixed a
  pre-existing hand-authored report that silently failed schema validation; built
  `/timeline`; tightened the summarizer prompt against Reuters attribution norms; designed
  (not yet exercised) the manual-sampling workflow.

- **2026-07-06 ~04:20 PDT — [Loop run 2](changelog-entries/run-02.md)** — Added
  fixity/corroboration schema fields; fixed missing source sectors on taxonomy/sources
  pages; corrected run 1's plan — `trends_raw.json` is live-used, not dead, so removal
  needs a real migration; researched (not implemented) signal timeline design and
  compliant social-sourcing options.

- **2026-07-06 ~03:15 PDT — [Loop run 1](changelog-entries/run-01.md)** — First loop run:
  added `TODO.md`; fixed `run.sh`'s broken crawl→summarize wiring; added the first
  WebSearch-researched dated report; fixed a first-person voice slip; folded in
  journalism/archival research; hygiene scan found no sensitive data.

- **2026-07-06 02:04–02:10 PDT — [Branch setup and overnight build](changelog-entries/run-00-branch-setup.md)** —
  Created the `ari3lla-index-rebuild` branch, removed a stray nested `.git`; dispatched 5
  parallel subagents (data pipeline/schema, frontend archive, frontend static pages +
  rebrand, README + case study, repo hygiene) that built the structural core of the
  project from scratch; consolidation pass fixed stale branding and verified full build.
  Known gaps and deliberate overnight scope cuts are listed at the end of that file.

---

For the currently open items, see `TODO.md` at the repo root (updated every loop run) —
it is the authoritative, current punch list; this file is a historical record only.
