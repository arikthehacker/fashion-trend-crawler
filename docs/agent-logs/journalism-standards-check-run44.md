# Structured data: Dataset schema beyond NewsArticle (run 44)

## Research
Checked against Google Search Central's Dataset structured data guidance
(https://developers.google.com/search/docs/appearance/structured-data/dataset) and
general structured-data policy. Key points: Dataset markup should go on a dataset's
canonical/landing page (not every mirror), minimum useful fields are `name` +
`description`, and Google recommends `distribution`/`contentUrl` when a downloadable
file exists, plus `creator`, `temporalCoverage`, `variableMeasured` where applicable.

## Why this, not the other candidates
- URL permalink stability: already solid — `/reports/[date]` and `/signals/[slug]`
  are static, date/slug-keyed, generated via `getAllReportDates()`/signal_id, no
  query params or pagination-dependent paths. No gap found.
- Plain-language/readability: spot-checked methodology and a report executive
  summary; dense but intentional (wire-service register per doc section 2), not
  needlessly jargon-heavy. Not a clear gap worth forcing into scope.
- Structured data beyond NewsArticle: genuinely untried per skill's covered-topics
  list, and a real gap — confirmed.

## Gap found
`web/app/reports/[date]/page.tsx` already emits `NewsArticle` JSON-LD (added a
prior run), but each report is not just an article — it's the read surface of a
dated, structured signal dataset (`data/reports/<date>.json`). Schema.org/Google
guidance treats "dataset landing page" as its own markup target, distinct from
Article/NewsArticle, and the site had none.

## Fix applied
Converted the single JSON-LD block to an `@graph` with two entities, linked via
`@id`/`about`:
- `NewsArticle` (unchanged fields, now `@id`'d as `#article`, `about` pointing to
  the dataset entity)
- `Dataset` (`@id` `#dataset`): `name`, `description`, `url`, `creator`,
  `datePublished`/`dateModified`, `temporalCoverage` (the report date), and
  `variableMeasured` (the source-sector-breakdown keys, e.g. editorial, retail,
  designer_origin, etc. — the actual measured dimensions of the dataset).

Deliberately omitted `distribution`/`contentUrl`: there is no public route serving
the raw JSON (`data/reports/*.json` lives in the repo, not on the web app), so
pointing Dataset markup at a non-resolving URL would be worse than omitting the
field. Documented this as a follow-up in the code comment rather than fabricating
a URL — consistent with the project's "claimed but not shown" anti-pattern
(SKILL.md item 9).

## Verification
`cd web && npx tsc --noEmit` — passes, no errors.

## Follow-up for TODO.md
If a raw-data download route is ever added (e.g. `/reports/[date]/data.json`),
wire `distribution: [{ "@type": "DataDownload", encodingFormat: "application/json",
contentUrl: ... }]` into the Dataset entity above.
