# Periodic full-archive audit — run 101

Read-only audit. No data/report files, taxonomy.py, or any other source file was
edited during this run. The 2026-05-07.json and 2027-06-14.json precedent
questions were explicitly out of scope (handled by a separate concurrent agent)
and were not touched or re-litigated here.

## 1. Standing script suite — full output

### `python -m py_compile src/*.py`
```
PY_COMPILE_OK
```
Compiles clean, no syntax errors across all `src/*.py` modules.

### `python src/validate_all_reports.py`
```
OK: all 93 report(s) in data/reports/ passed schema validation.
```
Note: the archive directory currently contains 94 files
(`data/reports/*.json`, confirmed via directory listing), but the validator's
own count reads 93 report(s) — consistent with one of the 94 being
`2026-05-07.json`, the report already flagged and under separate handling this
run (not re-investigated here since it's out of scope). All 93 non-flagged
reports pass schema validation cleanly.

### `python src/check_field_coverage.py`
All 35 scanned Report/Signal fields show `yes`/`yes` (typed in TS, referenced
in .tsx) except `confidence_source` (`no`/`no`), which the script's own output
explicitly calls out as an expected backend-only field, not a bug. Zero
warnings for "typed but never referenced."

### `python src/check_signal_reuse_claims.py --all`
```
Scanned 93 reports; 19 signal_id(s) appear in 2+ reports overall.
No signal-reuse-claim mismatches found in the checked report(s).
```
Zero flagged mismatches this run (even the usual handful of negation/precedent
false positives didn't trigger this time).

All four standing checks are clean.

## 2. 2027-03-01.json / 2027-03-08.json revision_history verification

Read both files directly (not trusting prior agent-log claims). Both are intact:

- **2027-03-01.json**: `revision_history` has 2 entries. The second (most recent)
  is the run-97 fix: `"reason": "Data-integrity fix (run 97): 'uraniumwaves.com' /
  'Uranium Waves' was cited as one of this signal's corroborating editorial
  sources, but it is actually an unrelated Canadian music blog/label..."`, with
  `changed_signals.modified.wales-bonner-hermes-debut: ["evidence",
  "source_corroboration_count", "source_domains"]`. `source_domains` on the live
  signal no longer contains `uraniumwaves.com` (current list: istitutomarangoni.com,
  wallpaper.com, voguescandinavia.com, wwd.com, savoirflair.com — confirmed clean).
- **2027-03-08.json**: same run-97 fix present as the second `revision_history`
  entry, same reasoning, same `changed_signals` shape. Current `source_domains`
  on `wales-bonner-hermes-debut` (istitutomarangoni.com, wallpaper.com,
  voguescandinavia.com, euronews.com, fzine.com, wwd.com) also confirmed clean of
  `uraniumwaves.com`.

Both files' revision histories are present, intact, and accurately reflect the
correction. No regression found.

## 3. Confidence-discipline spot-check (4 reports, excluding 2026-05-07 and 2027-06-14)

Read in full and checked assigned `confidence` / `confidence_source` against
`derive_confidence()`'s mechanical rule and all 16 precedents in
`docs/confidence-discipline-precedents.md`:

- **2026-09-14.json** (NYFW SS27 week-one report, 5 signals): all `high`/`medium`/`low`
  tiers are `confidence_source: "manual"` with reasoning tied to genuine
  cross-sector corroboration (institutional+editorial, designer_origin+editorial)
  or correctly held down (the media-integrity flagged forecast piece at `low`,
  single source). No mismatch.
- **2027-04-19.json** (Moschino Messina/Rizzo appointment): single signal, 3
  editorial-only sources, held at `medium` per precedent 2 (single-sector volume
  doesn't promote to high) — correctly reasoned and applied.
- **2027-09-27.json** (PFW SS28 opens + Margiela raw-edge preview): both signals
  `confidence_source: "derived"`, `high`. First signal: institutional+editorial,
  count 2, genuinely distinct mapped sectors (fhcm.paris, vogue.com) — correct.
  Second signal: `source_sectors` list is `["editorial", "editorial", "retail"]`
  (one entry per source rather than deduplicated) — `derive_confidence()`
  set-ifies this internally (`distinct_sectors = set(source_sectors)`) so the
  duplicate entry does not inflate the sector count computation; the "2 distinct
  sectors" result is correct. This is a minor data-representation quirk (a
  per-source list rather than a deduplicated sector list) worth noting but not a
  confidence-tier bug — flagging for awareness, not as an error requiring
  correction.
- **2028-02-14.json** (Proenza Schouler spiral-seam wrap coat): `derived`,
  `high`, designer_origin (house's own lookbook) + editorial (vogue.com
  independent review), count 2, two genuinely distinct sectors — explicitly
  reasoned against precedents 3 and 7 (no "unclear" domain doing the work, no
  mislabeled single-source-wearing-two-tags). Correct.

No new unexplained mechanical-vs-assigned confidence mismatches found in this
sample. All four reports' confidence reasoning is internally consistent with
the mechanical formula and the existing 16 precedents.

## 4. Domain classification re-verification (10 domains from `taxonomy.py`)

Independently re-searched (WebSearch, not trusting the code comments) 10
domains from `DOMAIN_SECTOR_MAP` to check for further uraniumwaves.com/
cafedelhomme.com/radio-station-style data artifacts:

| Domain | Mapped as | Verified as | Match? |
|---|---|---|---|
| bricksmagazine.co.uk | editorial | Independent UK fashion/music/culture magazine, queer-led, named team | Yes |
| soccerbible.com | editorial | Global football-culture publisher covering apparel/footwear/lifestyle design | Yes |
| pursuitist.com | editorial | Independent luxury lifestyle/travel magazine, named founder/EIC (Christopher Parr), founded 2008 | Yes |
| imfirenzedigest.com | editorial | Student-powered magazine of Istituto Marangoni Firenze, trend/culture/fashion content, distinct from the school's own institutional site | Yes |
| chicstylecollective.com | editorial | Named EIC (Natalie Dixon), 20+ years fashion journalism background; content is heavily shopping-listicle/"look expensive" framed — genuinely borderline against this project's own service-journalism discount (precedent 8), but sector classification (editorial vs. retail) still holds since it isn't a storefront | Yes, with a caveat |
| wardrobeoxygen.com | independent_criticism | Long-running (since 2005) single-author personal style blog by Alison Gary, independent voice | Yes |
| ecostylia.com | editorial | Independently-funded Paris outlet (Pierre-Antoine Tsady/Yoann Pantic), fashion/culture/sustainability coverage including Fashion Week reporting | Yes |
| modernluxury.com | editorial | Premier US regional luxury-lifestyle magazine publisher, 21 city titles, covers fashion among dining/design/travel | Yes |
| theimpression.com | editorial | Fashion-industry trade site, runway/backstage coverage, industry news and analysis | Yes |
| clashmusic.com | editorial | UK music magazine with a substantial, longstanding dedicated fashion vertical/biannual fashion issues | Yes |

All 10 domains checked hold up as correctly classified. No new
uraniumwaves.com/cafedelhomme.com-style fabricated-source or
wrong-business-entirely artifacts found in this sample. One soft observation:
`chicstylecollective.com`'s actual on-site content (search results are
dominated by "editor picks," "look expensive," affiliate-styled listicles)
skews closer to the commercial/service-journalism profile precedent 8 already
discounts at the confidence layer than a hard news/reviews masthead — this
doesn't make the sector tag (`editorial`) wrong, since it isn't a storefront,
but it's worth keeping in mind if this domain's content is ever cited as
confidence-relevant corroboration in a future report (apply precedent 8's
extra discount there rather than at the taxonomy layer).

## 5. Manual-sampling cadence check

`docs/manual-sampling-workflow.md` line 10-11 confirms: **last run: run 95**
(`docs/agent-logs/manual-sampling-check-run95.md`), **next due: ~run 105**.
Read directly from the doc, not inferred — this run (101) is not yet due for a
re-check under the ~10-run cadence; no action needed.

## 6. Stray file / cleanup check

Checked repo root and `src/` directory listings:

- **Repo root**: `README.md`, `TODO.md`, `data/`, `docs/`, `requirements.txt`,
  `src/`, `web/` — all expected, matches `SKILL.md`'s documented file map. No
  stray scratch files.
- **`src/`**: `__pycache__` (expected build artifact, not tracked), plus 15
  `.py`/`.sh` files, all of which are named and documented in `SKILL.md`'s file
  map (`audit_confidence.py`, `check_field_coverage.py`,
  `check_heading_patterns.py`, `check_signal_reuse_claims.py`, `crawler.py`,
  `generate_archive_manifest.py`, `manual_sample.py`, `report_schema.py`,
  `run.sh`, `server.py`, `summarize.py`, `taxonomy.py`,
  `test_crawler_timeout.py`, `test_tools.py`, `validate_all_reports.py`).
  `test_crawler_timeout.py` was read in full to confirm it's a legitimate,
  documented, self-contained localhost-only unit test (run 72/73's hard-deadline
  fix regression test), not a leftover scratch file, even though it isn't
  explicitly named in the SKILL.md file-map table (it postdates the table's
  last full update but is well-documented in its own docstring with an
  agent-log citation).

No stray/leftover scratch files found in the repo root or `src/` this run.

## Summary

All four standing scripts pass clean. The 2027-03-01/2027-03-08 revision
histories for the run-97 uraniumwaves.com fix are confirmed present, intact,
and correctly reflected in current `source_domains`. The 4-report confidence
spot-check and 10-domain taxonomy re-verification found no new unexplained
mismatches or data artifacts — only one soft observation (chicstylecollective.com's
service-journalism-leaning content, worth a confidence-layer discount if ever
cited as corroboration, not a taxonomy error). Manual-sampling cadence
confirmed at last-run-95/next-due-~105, no action needed. No stray files found.
No edits were made to any report, script, or doc as part of this audit run.
