# Raw JSON download route (run 45)

## What was implemented
Run 44 added Dataset JSON-LD to `web/app/reports/[date]/page.tsx` but omitted
`distribution`/`contentUrl` because no public route served the raw
`data/reports/<date>.json` files. This run adds that route.

- `web/scripts/copy-reports.mjs`: copies every `data/reports/*.json` into
  `web/public/data/reports/` at build time.
- `web/package.json`: added a `prebuild` script running the copy script before
  `next build` (npm lifecycle hook — triggers on `npm run build`, not on a bare
  `npx next build`).
- Since `next.config.ts` has `output: "export"`, anything under `public/` is
  copied verbatim into `out/`, so each report becomes fetchable at
  `/data/reports/<date>.json`.
- `web/app/reports/[date]/page.tsx`: added `distribution: [{ "@type":
  "DataDownload", encodingFormat: "application/json", contentUrl: rawDataUrl }]`
  to the Dataset JSON-LD entity, and a visible "Download raw data (JSON)" link
  just above the existing "Cite as" citation block, for human discoverability.

## Sensitive-data check
Spot-checked `data/reports/2026-07-06.json`: contains only report metadata
(dates, source-sector counts, signal names/evidence/confidence, garment/color
terms, aesthetic terms, content hash, reviewer tag). No PII, credentials, or
anything not already implied by the rendered report page. Safe to serve as-is.

## Verification
- `cd web && npx tsc --noEmit` — passes.
- `cd web && npx next build` — succeeds, but a bare `next build` does NOT run
  npm's `prebuild` lifecycle script (that's an `npm run build` convention), so
  the copy doesn't happen under that invocation alone.
- `cd web && npm run build` — runs `prebuild` (copy script) then `next build`
  then `postbuild` (pagefind), confirmed correct end-to-end.
- Confirmed 37 files present at `web/out/data/reports/*.json` after
  `npm run build`, content matches source JSON.
- Confirmed `out/reports/2026-07-06.html` contains both the `distribution`
  JSON-LD field and the rendered "Download raw data (JSON)" link.

## Note for whoever runs CI/deploy
Deploy scripts must invoke `npm run build` (not `next build` directly) for the
report JSON to be copied into the static output. If CI currently calls
`next build` directly, that's now a real gap to close as a follow-up.
