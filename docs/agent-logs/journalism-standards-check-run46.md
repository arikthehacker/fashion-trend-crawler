# Journalism standards check — run 46: open data licensing

## Topic
Open data licensing conventions for a publicly downloadable dataset — not previously
covered (checked existing agent-log topics: AI-journalism-standards, forecast-calibration,
IPTC-metadata, archival-permanence, bias-audit, retention-versioning, ICD-203,
Costume-Core/Getty-AAT, correction-notice-placement, byline-AI-disclosure, WCAG 2.2,
RSS-2.0, schema.org Dataset, Pew methodology-box).

Run 45 added a real, resolving raw-JSON download route
(`/data/reports/<date>.json`) and a `Dataset`/`DataDownload` JSON-LD block on each
report page. That's exactly the situation where a stated license becomes necessary:
once a dataset is actually downloadable, "reuse terms unstated" is itself a gap, not
neutral.

## Research
- schema.org's `license` property expects a URL identifying a specific license
  version — SPDX is the recommended canonical source — not bare text like "CC BY 4.0".
- CC-BY-4.0 is the standard default for openly published research/data (used across
  GBIF, World Bank Data Catalog, data.world): permits reuse including commercial use,
  requires attribution and change-notice.
- Sources: [schema.org/license](https://schema.org/license), [CC BY 4.0 / SPDX](https://spdx.org/licenses/CC-BY-4.0.html), [GBIF IPT licensing guide](https://ipt.gbif.org/manual/en/ipt/latest/applying-license).

## Gap found and fixed
Before this run, nothing on the site stated reuse terms for the downloadable JSON —
no `license` field in the Dataset JSON-LD, no visible license line near the download
link, no mention in methodology (which does note the site stores metadata/links
rather than full copyrighted article text — that framing stays true and unchanged).

Fixed in `web/app/reports/[date]/page.tsx`:
1. Added `license: "https://creativecommons.org/licenses/by/4.0/"` to the Dataset
   JSON-LD object (per schema.org's URL-not-text convention).
2. Added a visible line next to the "Download raw data (JSON)" link: classification/
   summary metadata is CC BY 4.0, underlying source articles remain the property of
   their original publishers — scoping the license correctly to what the site
   actually produces vs. what it merely links to.

## Verification
`cd web && npx tsc --noEmit` — clean, no errors.

## Not done / left open
Did not touch methodology/about page prose — the existing "stores metadata and
source links rather than reproducing copyrighted content" note already covers the
distinction; a future run could cross-link it to the new license line if desired.
