# Run 95: manual-sampling opportunistic check (proactive, one run early)

## Why now

`docs/manual-sampling-workflow.md`'s "Cadence tracking" section, updated at run 87,
recorded last run: run 87, next due: ~run 97. Run 94's periodic audit flagged this as
only 3 runs out and recommended handling it within 1-3 cycles to avoid repeating the
17-run silent lapse flagged at run 69. This run (95) does the check proactively, one
run before it strictly requires it.

## Method

Same as prior runs (30, 32, 41, 52, 69, 77, 87): a cheap WebSearch pass over current
Pinterest Predicts/Trends coverage and TikTok discover/fashion-trend pages, evaluated
against the workflow's two-part bar (`docs/manual-sampling-workflow.md`):

1. at least one source independent of the platform's own newsroom/PR page, AND
2. that source shows genuine editorial judgment/critique, not a repackaging of the
   platform's own press-release stats.

## Findings

**Pinterest Predicts 2026** (still the current top trend report, ~600M monthly users,
21 trends, 88%-accuracy claim over six years): search turned up the same set of outlets
as run 87 — NBC Select, Envato Elements, Yahoo Shopping, AOL Shopping, JCK Online, and
Pinterest's own newsroom/business blog. All non-Pinterest coverage restates the report's
own trend list, figures, and framing ("21 trends," "growing 4.4x faster," "trend
fatigue") without independent observation of organic search/post activity. NBC Select
and JCK Online each frame their pieces as editor-reviewed summaries of the report, not
independent measurement of the underlying trends. No outlet supplies evidence for a
trend's existence/scale that doesn't trace back to Pinterest's own report. Same
disqualifying pattern as every prior run (41, 52, 69, 77, 87).

**TikTok fashion trends, July 2026**: dominated again by WhoWhatWear's "7 Biggest TikTok
Fashion Trends of 2026" (same outlet/pattern flagged in the workflow doc itself),
TikTok's own newsroom/discover pages, and SEO/content-mill round-ups (Fash Verge, It Is
Mandy Style, INFLOW Network) covering "coastal cowgirl" evolution, multi-layered-tops
maximalism (credited to a resurgent "Rachel Green from Friends" reference), and generic
summer-outfit-transition video formats. INFLOW Network's "Entering July" piece again
describes format mechanics (rhythmic-audio transition edits) rather than sourcing claims
to TikTok's press materials, but as in run 87 it supplies no independently observed
volume/reach or hashtag data — content-marketing copy about a format, not primary
observation of trend scale. No outlet shows independent measurement of organic
post/hashtag volume distinct from what TikTok's own discover pages promote.

No candidate — on either platform — cleared the two-part bar.

## Outcome

**Honest negative**, consistent with every prior run of this check (30, 32, 41, 52, 69,
77, 87). No signal was added to `docs/manual-sampling-template.md`, no
`build_manual_signal(...)` call was made, and no `data/reports/*.json` file was created
or modified. Per the workflow's own rules, "checked, nothing cleared the bar" is a
complete, successful exercise of this step, not a gap requiring a forced entry.

## Cadence note

`docs/manual-sampling-workflow.md`'s "Cadence tracking" section has been updated in
place: last run is now run 95 (this run), next due ~run 105 (10-run interval from this
run). As before, nothing in code enforces this interval; it remains a documentation
convention that depends on some future run's periodic audit noticing and flagging it,
same structural risk noted at runs 69, 77, and 87. Doing this one run early (per run 94's
recommendation) is itself a small hedge against that risk, not a change to the
underlying mechanism.
