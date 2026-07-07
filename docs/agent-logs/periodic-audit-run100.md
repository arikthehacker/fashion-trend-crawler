# Periodic full-archive audit — run 100

Branch: `ari3lla-index-loop-improvements`. Read-only audit unless a genuine, confidently-fixable
issue was found (see part 2's disposition — no fix was applied this run).

## 1. Automated checks — full output

### `python -m py_compile src/*.py`
```
PYCOMPILE_OK
```
No syntax/compile errors across all source files.

### `python src/validate_all_reports.py`
```
OK: all 92 report(s) in data/reports/ passed schema validation.
```

### `python src/check_field_coverage.py`
```
Field coverage check (heuristic, not a CI gate)
Scanned 35 fields across Report/Signal against:
  - web\lib\reports.ts
  - 16 .tsx files under web/app/

dataclass  field                        typed in TS   referenced in .tsx
--------------------------------------------------------------------------
Report     report_date                  yes           yes
Report     collection_window            yes           yes
Report     sources_scanned              yes           yes
Report     items_collected              yes           yes
Report     source_sector_breakdown      yes           yes
Report     executive_summary            yes           yes
Report     top_signals                  yes           yes
Report     repeated_keywords            yes           yes
Report     garments                     yes           yes
Report     silhouettes                  yes           yes
Report     materials                    yes           yes
Report     colors                       yes           yes
Report     aesthetic_terms              yes           yes
Report     cultural_references          yes           yes
Report     limitations                  yes           yes
Report     archive_tags                 yes           yes
Report     content_hash                 yes           yes
Report     collection_status            yes           yes
Report     thin_week_note               yes           yes
Report     revision_history             yes           yes
Report     review_status                yes           yes
Report     reviewed_by                  yes           yes
Signal     name                         yes           yes
Signal     type                         yes           yes
Signal     source_sectors               yes           yes
Signal     confidence                   yes           yes
Signal     volatility                   yes           yes
Signal     origin_classification        yes           yes
Signal     evidence                     yes           yes
Signal     index_note                   yes           yes
Signal     source_corroboration_count   yes           yes
Signal     signal_id                    yes           yes
Signal     confidence_source            no            no
Signal     human_editor_note            yes           yes
Signal     source_domains               yes           yes

Warnings: 0 field(s) typed in TS but never referenced in any .tsx
(candidates for the same 'populated but unrendered' bug pattern -- review by hand;
 some backend-only fields are legitimate, e.g. confidence_source, content_hash)
```
`confidence_source` remains untyped/unreferenced — consistent with every prior run's
assessment that it's a legitimate backend-only provenance field, not a "populated but
unrendered" bug. No new warnings.

### `python src/check_signal_reuse_claims.py --all`
```
Signal reuse claim check (heuristic, not a CI gate)
Scanned 92 reports; 19 signal_id(s) appear in 2+ reports overall.

No signal-reuse-claim mismatches found in the checked report(s).
```

**All four checks: clean.**

## 2. Re-verification of the two run-97 uraniumwaves.com corrections

Independently opened and read both files directly (did not trust run-99's prior write-up):

- **`data/reports/2027-03-01.json`**: `revision_history` has 2 entries, both present and
  intact. Entry 2 (run 97): `previous_content_hash: "0b5df3eb913841156d61a909e6d1528c3b8029ba594ff8e215b028a6611f0535"`,
  `corrected_at: "2026-07-06"`, reason describing the uraniumwaves.com fabricated-source
  removal, `changed_signals.modified.wales-bonner-hermes-debut: ["evidence",
  "source_corroboration_count", "source_domains"]`. `source_domains` for that signal has
  5 entries (istitutomarangoni.com, wallpaper.com, voguescandinavia.com, wwd.com,
  savoirflair.com) — no `uraniumwaves.com`. Not reverted or re-edited.
- **`data/reports/2027-03-08.json`**: `revision_history` has 2 entries, both present and
  intact. Entry 2 (run 97): `previous_content_hash: "a42914f7a3b03f29fb97791f20f937a50d9405666f3217403941107acf7e6230"`,
  same reason text, same `changed_signals` shape. `source_domains` has 6 entries
  (istitutomarangoni.com, wallpaper.com, voguescandinavia.com, euronews.com, fzine.com,
  wwd.com) — no `uraniumwaves.com`. Not reverted or re-edited.

Both files pass `validate_all_reports.py` (confirmed above) and both have all required
`revision_history` fields. **No silent reversion or re-edit detected.**

## 3. `data/reports/2026-05-07.json` (docs/agent-logs/periodic-audit-run99.md's flagged item)

Independently re-derived, did not trust run 99's write-up:

- Signal `sheer-layering`: `source_corroboration_count: 2`, `source_sectors: ["editorial",
  "retail"]` (2 distinct sectors). Per `derive_confidence()` in `src/report_schema.py`
  (lines 142-192): `corroboration_count >= 2 AND len(distinct_sectors) >= 2` → returns
  `"high"`. The report assigns `confidence: "medium"`.
- Confirmed no `confidence_source` field exists anywhere in this report's signals (the
  field doesn't exist in the file at all — this report predates its introduction), and no
  override reasoning is documented for this or any other signal in this report. The report
  uses now-retired report-level fields (`confidence_notes`, `volatility_notes`,
  `incentive_notes`) instead of the per-signal `human_editor_note`/`confidence_source`
  fields the rest of the archive uses.
- The report is explicitly self-labeled: `"human_editor_note": "Placeholder example
  report used to scaffold the archive and report page templates."` and `"reviewed_by":
  "hand-authored-placeholder-run0"`.

**Disposition: documented, not fixed, matching run 99's judgment call — independently
re-confirmed rather than deferred to it.** Reasoning for not fixing:

1. This is the archive's first report, explicitly self-labeled a hand-authored
   placeholder that predates run 6's confidence-discipline system entirely (per
   `docs/confidence-discipline-precedents.md`'s own framing: "pre-run-6" is the earliest
   precedent's start point). There was never a live, in-the-moment editorial judgment
   call made about this specific mismatch to reconstruct — the report was seeded by hand
   before `derive_confidence()`, `confidence_source`, or the override convention existed.
2. Precedent 12 (structured/controlled-vocabulary fields are correctable retroactively;
   editorial prose fields are not) counsels against inventing after-the-fact reasoning in
   `human_editor_note`/prose fields to justify a historical value — doing so would
   misrepresent what was actually reasoned at authoring time, the same concern precedent
   12 raised about not rewriting `2026-07-13.json`/`2026-11-09.json`'s duplicate notes.
   Adding a `confidence_source: "manual"` field plus a retroactively-invented
   justification for why "medium" was intentional would be exactly this kind of
   fabricated-after-the-fact reasoning, since no such reasoning was ever contemporaneously
   recorded — the report's own text gives no indication the placeholder author was
   applying any of the 16 documented precedents (which didn't exist yet).
3. Correcting the value to `"high"` to match the mechanical formula is equally
   unjustified in the other direction: the placeholder's other structured data
   (`source_corroboration_count`, `source_sectors`) was itself hand-invented for
   scaffolding purposes, not derived from real crawled sources, so "matching the formula"
   on synthetic example data doesn't actually improve the archive's integrity — it would
   just be re-authoring a placeholder to look more procedurally correct without any new
   information.
4. Per the task's own framing, this is exactly the "if uncertain, leave for human
   decision" case: not uncertain about the mechanical math (that part is unambiguous), but
   uncertain that touching a self-labeled scaffold artifact from before the whole
   discipline system existed serves the archive's honesty-over-polish goal better than
   leaving it visibly flagged as a legacy artifact.

**No edit made to `data/reports/2026-05-07.json`.** Flagging again for a human/coordinator
to make the final call — options on the table: (a) leave as-is with this documentation as
the durable record, (b) add a `confidence_source`/`human_editor_note` explicitly labeling
it "legacy placeholder, predates confidence-discipline system, mismatch not corrected,"
which would at least make the exemption visible in the data itself rather than only in an
agent log.

## 4. Additional finding (independent, not previously flagged): `2027-06-14.json` Met Gala signal

While spot-checking `data/reports/2027-06-14.json` against the precedents doc (see part 5
below), found a second, distinct mechanical-vs-assigned mismatch with no documented
override reasoning, in a **live, non-placeholder report**:

- Signal `met-gala-2027-coverage-gap`: `source_corroboration_count: 1`,
  `source_sectors: ["editorial"]`, `confidence_source: "manual"`. `editorial` is in
  `HIGH_RELIABILITY_SECTORS`, so `derive_confidence()` would compute `"medium"`
  (`corroboration_count == 1 AND distinct_sectors & HIGH_RELIABILITY_SECTORS` is true).
  The report assigns `confidence: "low"`.
- The signal's `human_editor_note` ("Second occurrence of this signal_id... Consolidation
  note (run 58): a prior draft... incorrectly minted a new... archive_tag instead of
  reusing this signal_id...") documents a signal_id-reuse correction, **not** any
  reasoning for the confidence value. Neither `evidence` nor `index_note` mentions the
  confidence tier or why it was held below the mechanical result either.
- A plausible unstated rationale exists (a "coverage gap" / absence-of-evidence signal is
  a different epistemic shape than a signal backed by an actual sourced claim — the
  `source_corroboration_count: 1` here represents one search effort finding nothing, not
  one outlet asserting a fact, so treating it as equivalent to a single high-reliability
  sourced claim may overstate it), but this reasoning is **not written down anywhere** in
  the report, unlike every other manual override in the archive (all 16 documented
  precedents record their reasoning in `human_editor_note` and/or an agent-log).

**This was left undocumented-but-uncorrected, not fixed, this run** — per the task's
scope (only the 2026-05-07.json item was in-scope for a possible direct fix), and because
a `low` assignment tightening confidence below the mechanical floor is lower-risk to leave
alone than an unexplained `high`-suppression would be (it doesn't overstate the archive's
confidence in anything). Flagging for a human/future run to decide whether this pattern
(absence-of-coverage signals systematically held at `low` regardless of sector) should
become its own documented precedent (candidate 17), the same way precedents 13/14/15 each
started as an ad hoc call flagged in a report's `limitations`/`human_editor_note` before
being formalized.

## 5. Spot-check of 3 more reports against all 16 precedents in `docs/confidence-discipline-precedents.md`

Read the full doc (confirmed 16 numbered precedents, including #16 formalized at run 99)
and independently checked:

- **`data/reports/2027-06-14.json`**: two signals correctly apply precedent 3 (`unclear`
  domain-map gaps not counted as real sector diversity) — `bubble-hem-revival` (count=5,
  mechanical `high`, held `medium`, reasoning cites the `unclear` gap plus a
  commerce-adjacent-outlet discount echoing precedent 8) and `royal-purple-color-trend`
  (count=3, held `medium`, reasoning cites precedent 3's `unclear`-domain logic and
  precedent 7's "nominal sector tag mislabeling" pattern). Both `human_editor_note`s
  correctly and explicitly name the mechanical result they're overriding and why. Third
  signal, `met-gala-2027-coverage-gap`, is the mismatch documented in part 4 above.
- **`data/reports/2028-01-03.json`**: `top_signals: []`, two forecast pieces (wwd.com,
  vogue.com) correctly excluded under precedent 14 (forecast/prediction pieces are not
  evidence of a present signal) — matches the precedent doc's own worked example for this
  exact file. No confidence-tier question arises since nothing was logged as a signal.
- **`data/reports/2028-03-20.json`**: the `fw28-season-wrap-unfinished-edge-editorial-synthesis`
  signal correctly applies precedent 15's three-part gate (both antecedent signals
  pre-existing and independently sourced; neither outlet cites the other; both cite
  underlying archive facts directly) and precedent 2 (capped at `medium`, both sources
  `editorial`). `confidence_source: "derived"` is correctly used since the mechanical
  result was adopted as-is with no override — matches the precedent doc's own worked
  example for this exact file. Also correctly avoids retroactively touching the Miu Miu
  / Margiela antecedent signals per precedent 15's retroactivity clause — spot-checked
  that neither antecedent report was touched (not opened those two files this run, but
  this report's own text explicitly disclaims any such edit and its `revision_history`
  for this file is `[]`, consistent with no other file needing a companion edit).

No new precedent violations found beyond the part-4 finding above (2027-06-14.json's Met
Gala signal). All three spot-checked reports' *other* signals correctly and explicitly
tie their override reasoning to a named precedent number/logic.

## 6. Manual-sampling cadence (`docs/manual-sampling-workflow.md`)

"Cadence tracking" section currently reads: **last run: run 95**, **next due: ~run 105**.
As of this run (100), the next-due threshold has **not yet been reached** (100 < 105).
Confirmed the tracked number only, per instructions — did not run the actual
manual-sampling check.

## 7. `gh` CLI / CI-status check (SKILL.md workflow note 11: every 10th run)

Run 100 is exactly the due run for this cadence. A separate, already-completed log
(`docs/agent-logs/gh-ci-status-check-run100.md`, found already present/untracked in the
working tree when this audit started) covers this: `gh` CLI still not installed
(confirmed in both bash and PowerShell), unauthenticated GitHub API still 404s on the
repo, `.github/workflows/validate-reports.yml` exists (CI is configured) but its
pass/fail run history remains uninspectable without `gh`. No new information beyond that
log — not duplicating the check here. **Next due: run 110**, per that log's own
decision.

## Summary

- All 4 automated checks: clean pass, no failures, no new warnings.
- Both run-97 uraniumwaves.com corrections: independently re-verified intact,
  revision_history complete and un-reverted.
- `2026-05-07.json` `sheer-layering` mismatch: independently re-confirmed (mechanical
  `high` vs. assigned `medium`, no override reasoning, no `confidence_source` field at
  all). **Left undocumented-in-data / unfixed this run** — reasoned through 4 separate
  grounds above for why a retroactive fix (in either direction) would fabricate
  reasoning that was never contemporaneously made, on a report explicitly self-labeled a
  pre-discipline-system placeholder. Flagged again for a human decision between leaving
  as-is vs. adding an explicit "legacy artifact, not corrected" label to the data itself.
- **New finding**: `2027-06-14.json` signal `met-gala-2027-coverage-gap` has the same
  mechanical-vs-assigned mismatch shape (mechanical `medium`, assigned `low`) with no
  documented override reasoning, in a live (non-placeholder) report. Left uncorrected,
  flagged as a candidate for a possible 17th precedent (absence-of-coverage signals vs.
  sourced-claim signals) rather than fixed unilaterally, since it was outside this run's
  authorized fix scope and a downward-only discrepancy is lower-risk to leave open.
- Confidence spot-check across 3 more reports (2027-06-14, 2028-01-03, 2028-03-20): all
  correctly and explicitly apply named precedents, except the one new finding above.
- Manual-sampling cadence: last run 95, next due ~run 105 — not yet due.
- `gh`/CI-status check: due this run (100), already completed in a separate concurrent
  log (`gh-ci-status-check-run100.md`) — no CLI access, repo still returns 404
  unauthenticated, CI workflow exists but status uninspectable. Next due run 110.

No report files edited as part of this audit.
