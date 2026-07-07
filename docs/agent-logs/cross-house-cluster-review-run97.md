# Run 97 — cross-house "raw/unfinished edge" cluster review

## Flag under review

Run 96's `real-report-2028-03-13.md` flagged, without asserting a conclusion, that
`miumiu-fw28-raw-hem-bias-slip-skirt` (2028-03-13) "echoes the closed-out Margiela
raw-edge thread (2027-10-18) in surface description" and asked a future agent to check
whether a genuine cross-house "unfinished edge" construction cluster is forming.

## Method

Grepped `data/reports/*.json` for `raw-edge|raw edge|deconstruct|frayed|unfinished|raw hem`
across all 89 archived reports (28 files matched, mostly the same Margiela thread carried
forward week to week via `archive_tags`) and read every distinct signal/aesthetic-term hit
in full, not just the two named in the flag.

## What the full history actually contains

1. **The Margiela thread** (`margiela-raw-edge-tailoring-preview` ->
   `margiela-raw-edge-critical-reception` / `margiela-raw-edge-retail-buy` ->
   `margiela-raw-edge-editorial-close-out`, 2027-09-20 through close-out 2027-10-18,
   carried in `archive_tags` through 2028-03-13): this is a **single-house** thread about
   Maison Margiela's own raw-edge tailoring, sourced from the house's own atelier release
   plus editorial/retail follow-through. It is explicitly Margiela's house-codes language,
   reinforced by the separate `martens-margiela-debut` signal (2027-08-23), which is about
   a designer deliberately invoking *Margiela's own* deconstructivist/"unfinished seams"
   vocabulary — not a different house converging on it independently.
2. **`antwerp-lineage-raw-edge-wider-claim`** (2027-10-11, `confidence: low`,
   `origin_classification: unclear`): the one place in the archive that gestured at a
   *wider* claim beyond Margiela itself. Explicitly logged as resting on "a single,
   unnamed-designer social post" with "no editorial, runway, or retail corroboration,"
   retained as a distinct low-confidence claim shape rather than treated as trend
   confirmation. It never gained corroboration in any later window and was never named to
   a specific second house.
3. **`miumiu-fw28-raw-hem-bias-slip-skirt`** (2028-03-13): a single-house, single-window
   signal — Miu Miu's own lookbook + one independent editorial review. No other house's
   signal co-occurs with it in this or adjacent windows.
4. **One unrelated stray hit**: `2027-06-07.json` lists "deconstructed blazer" as an
   aesthetic term under `sleepwear-as-outerwear-relaxed-tailoring` (editorial_amplified,
   relaxed tailoring + sleepwear-coded pieces). This is a generic use of "deconstructed"
   describing a loose/relaxed silhouette, unconnected to raw/unfinished-edge construction
   and five months earlier than the Margiela thread even starts — not related.

## Doc check

`docs/ARI3LLA INDEX.txt` and this project's standing convention (`SKILL.md` designer
intent vs. editorial interpretation vs. retail adoption vs. social amplification) require
that a cross-house "convergent trend" claim rest on **multiple named houses, independently
corroborated, in the same season** — not on two houses sharing a generic English adjective
("raw," "unfinished," "deconstructed") that fashion criticism applies constantly and
loosely across unrelated techniques and eras. No section of the doc or any existing report
treats vocabulary overlap alone as sufficient; every existing convergence-shaped signal in
the archive (e.g. the Bogota resort-tailoring institutional signal) is grounded in an
actual named plurality of designers from one corroborated source, not an inferred
similarity across otherwise-unconnected single-house threads.

## Conclusion: closing as a non-issue, not a genuine convergent trend

The evidence does not support naming a cross-house "unfinished edge" aesthetic trend:

- Only two houses ever appear (Margiela, Miu Miu), five months apart, with the
  Margiela thread already closed out on dropped discourse volume before the Miu Miu
  signal existed — no temporal overlap, no shared season, no co-occurring editorial
  coverage treating them as one story.
- The one candidate for an actual multi-designer claim (`antwerp-lineage-raw-edge-wider-claim`)
  was single-source, unnamed-designer, and never corroborated in any of the ~20 subsequent
  windows it could have appeared in — it is dead, not dormant.
- The garment categories, construction techniques, and design lineages are genuinely
  different: Margiela's raw-edge tailoring is decades-old house-codes deconstructivism
  applied to structured tailoring; Miu Miu's raw hem is a bias-cut slip-skirt finishing
  detail in an entirely different silhouette register. "Raw"/"unfinished edge" is doing
  the work of a shared adjective, not a shared construction technique or shared design
  intent.

No new signal is being added, and no existing report is being edited. This closes the
run-96 flag as **checked and resolved: not a genuine convergent trend, correctly kept as
two independent single-house signals.** No report data was touched by this review, so
`validate_all_reports.py` was not re-run (nothing to validate).
