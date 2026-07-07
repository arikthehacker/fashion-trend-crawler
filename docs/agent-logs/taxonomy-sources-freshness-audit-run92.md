# Taxonomy/Sources freshness re-audit — run 92

Follow-up to run 81's fix (missing Origin Classification dimension on Taxonomy, missing
13 outlets on Sources). This run re-verifies from scratch against current source, not
trusting run 81's result still holds.

## 1. Sources page vs. `src/crawler.py` FASHION_SOURCES

Read the full `FASHION_SOURCES` list in `src/crawler.py` (lines 83-185). Current full set,
newest-first by run added:

- run 75: `voguearabia.com`
- run 74: `inexmoda.org.co`
- run 73: `ffw.com.br`
- run 54: `dieworkwear.com`
- run 39: `scmp.com`
- run 20: `dewimagazine.com`
- run 19: `vogue.mx`, `tribune.com.pk`, `savoirflair.com`
- run 17: `nataal.com`, `okayafrica.com`, `fashionunited.in`, `tokyofashion.com`
- original: `vogue.com`, `whowhatwear.com`, `hypebeast.com`

No entries newer than run 75 exist in `FASHION_SOURCES`. Runs 82-91 added no new crawled
domain. `web/app/sources/page.tsx`'s Runway/Editorial list already names all editorial
outlets above by outlet name (Vogue Runway, WWD, Vogue Mexico, The Express Tribune,
Savoir Flair, Dewi Magazine, SCMP Lifestyle, FFW (Brazil), Vogue Arabia, etc.), and
`inexmoda.org.co` (institutional, not editorial) is covered generically under
Institutional/Historical's "National fashion trade/export institutes" line, consistent
with how the page already treats CFDA/FHCM/British Fashion Council generically rather
than by name. `dieworkwear.com` is present under Independent Criticism ("Independent
critics" — the page doesn't name specific blogs there, same treatment as before run 81
for other independent-criticism entries).

Also cross-checked `src/taxonomy.py`'s `DOMAIN_SECTOR_MAP` (broader than FASHION_SOURCES,
includes classification-only domains not actively crawled) — nothing added there past
run 75 either.

**Conclusion: no staleness. Sources page remains accurate as of run 81's fix.**

## 2. Taxonomy page vs. `src/taxonomy.py` constants

Compared every table on `web/app/taxonomy/page.tsx` against the live constants:

- `CONFIDENCE_LEVELS` (low, medium, high, archival) — 4 values, page's `confidence` array
  has exactly these 4. Match.
- `VOLATILITY_LABELS` (11 values: stable, emerging, seasonal, volatile, flash,
  microtrend, recurring, revival, long_tail, saturated, declining) — page's `volatility`
  array has exactly these 11. Match.
- `SOURCE_SECTORS` (10 values, `runway` and `editorial` kept as distinct enum values) —
  page's `sourceSectors` array intentionally combines them into one "Runway/editorial"
  row (9 rows total), same as `sources/page.tsx`'s combined "Runway / Editorial"
  section. This is a pre-existing, consistent design choice across both pages, not new
  drift.
- `ORIGIN_CLASSIFICATIONS` (7 values) — page's `originClassification` array has exactly
  these 7, labels and definitions match run 81's fix. No drift since.

Also checked `src/report_schema.py` for any additional confidence/volatility/sector
constants — it imports from `taxonomy.py` rather than defining its own, so no separate
source of truth to reconcile.

**Conclusion: no staleness. Taxonomy page's four tables remain accurate as of run 81's
fix.**

## 3. Should Taxonomy reference confidence-discipline-precedents.md?

Checked whether Methodology actually added a link to
`docs/confidence-discipline-precedents.md` at run 79 — it did not add a clickable
reference (that file lives under `docs/`, not a served web route, so it can't be linked
from the deployed site). What run 79 actually did was fold the *substance* of the
precedents (manual-override discipline, the "single source spanning multiple sectors is
not independent corroboration" rule, the high-reliability-sector credit rule) into
Methodology's "How Confidence Is Assigned" prose paragraph.

Given that:
- Taxonomy's own intro states its scope explicitly: "Definitions below are applied
  consistently across reports" — it's the mechanical-vocabulary page, deliberately
  separate from Methodology's explanatory/process page.
- Methodology already covers the existence and substance of manual overrides in reader-
  facing prose.
- There's no way to link the internal `docs/confidence-discipline-precedents.md` file
  from the public site (it's not part of the Next.js app / not served), so any addition
  to Taxonomy would have to duplicate Methodology's prose rather than genuinely point
  reader anywhere new.

**Judgment: not worth adding.** Duplicating the override-discipline explanation on
Taxonomy would blur the definitional/process split between the two pages for no reader
benefit. Left Taxonomy's Confidence Levels table as pure tier definitions, matching its
stated scope.

## Validation

`cd web && npx tsc --noEmit && npx eslint . && npm run build` — all passed clean, no code
changes made this run.

## Result

No real staleness found. `web/app/sources/page.tsx` and `web/app/taxonomy/page.tsx`
remain accurate against current `src/crawler.py` and `src/taxonomy.py` as of run 92. This
is a clean re-verification, not an unverified "still fine" carry-forward.
