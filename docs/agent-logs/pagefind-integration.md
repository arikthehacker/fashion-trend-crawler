# Pagefind integration

Implements the deferred second half of `search-discoverability-design.md` /
`facet-filter-impl.md`: full-text search over report prose, alongside (not
replacing) the `/search` facet filters shipped last run.

## Changes

- `web/next.config.ts`: added `output: "export"`. The config previously had
  no export mode set, despite the design doc assuming "fully static export" —
  confirmed via grep that there are no route handlers, `cookies()`, `headers()`,
  or other request-time APIs in `web/app`, so static export is safe. This is
  required for Pagefind: it needs a directory of already-rendered HTML, which
  only exists at `out/` once `output: "export"` is set (default `next build`
  without it only produces `.next`, no `out/`).
- `web/package.json`: added `pagefind` (`^1.3.0`) as a devDependency, and a
  `postbuild` script: `pagefind --site out --output-subdir _pagefind`. npm
  puts `node_modules/.bin` on PATH for scripts, so no `npx` needed once
  installed. Runs automatically after `npm run build`.
- `web/app/search/SearchClient.tsx`: added a `PagefindSearch` component,
  mounted above the existing facet filters (additive — facets untouched).
  Loads `/_pagefind/pagefind-ui.css` and `/_pagefind/pagefind-ui.js` client-side
  via a native dynamic `import()` (marked `webpackIgnore` since it's a runtime
  static asset, not a bundled module) and instantiates `window.PagefindUI`
  into a `#pagefind-search` div. Wrapped in try/catch so it fails silently
  (empty mount point, no error) when the bundle doesn't exist yet — true today,
  since no build has run with `pagefind` installed.

## Confirmed

- `cd web && npx tsc --noEmit` — clean, no errors.
- Grep confirmed no dynamic/request-time route handlers exist under `web/app`
  that would break `output: "export"`.
- Read `web/app/search/page.tsx` and `SearchClient.tsx` before editing to
  check for concurrent changes from the facet-filter run — none found; edits
  here are additive only (new component + one insertion point).

## NOT confirmed — requires local verification

`npm install` was not run (network/dependency constraints in this
environment), so none of this was exercised end-to-end. A human needs to run:

1. `cd web && npm install` — pulls in `pagefind`.
2. `npm run build` — runs `next build` (now emitting to `out/` under
   `output: "export"`), then `postbuild` runs `pagefind --site out
   --output-subdir _pagefind`, writing `out/_pagefind/{pagefind-ui.js,
   pagefind-ui.css, pagefind.js, index/...}`.
3. Serve `out/` (e.g. `npx serve out`) and load `/search` — confirm the
   Pagefind UI renders and returns results across report prose, and that the
   existing facet dropdowns below it still work unchanged.

Not verified: whether `output: "export"` breaks anything else in the build
(e.g. `next/image` usage, if any, requires `unoptimized: true` under export —
grep did not find `next/image` usage in `web/app`, but this should be
double-checked during the real build, not assumed from grep alone).
