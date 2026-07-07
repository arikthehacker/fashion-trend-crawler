# Download route robustness (run 46)

## Problem (from run 45)
The `/data/reports/<date>.json` copy only ran via npm's `prebuild` lifecycle
script, so a bare `npx next build` silently shipped a build missing every
report JSON file — a real risk if CI/deploy ever calls `next build` directly.

## Fix
`web/next.config.ts` now runs the copy itself, inline, in an IIFE at module
load time — before `nextConfig` is defined. Next.js evaluates `next.config.ts`
on every build invocation regardless of command (`next build`, `npm run
build`, `next build --turbopack`, etc.), so the copy now happens unconditionally.

Note: importing `scripts/copy-reports.mjs`'s exported function directly into
`next.config.ts` broke Next's config bundling (`ReferenceError: exports is
not defined` — Next transpiles the config to CJS and choked on the nested ESM
module). Working fix: duplicate the copy logic inline in `next.config.ts`
(a small, static ~10-line fs loop) instead of importing the `.mjs` script.
`copy-reports.mjs` still exists, still exports `copyReports()`, and still runs
standalone via the `prebuild` npm script — now a harmless redundant copy, not
the only copy path. Comments in both files point at each other and flag they
must be kept in sync if the copy logic ever changes.

## CI check
Read `.github/workflows/validate-reports.yml`: the `lint-web` job runs `npm
ci` + `npx eslint .` only — it does **not** run any Next.js build at all
today, so the `next build` vs `npm run build` distinction is currently moot
for CI (no gap to close there yet). If a build/deploy step is added to CI or
an external host later, the `next.config.ts` fix above makes the report copy
correct regardless of which build command that step uses.

## Verification
- `cd web && npx next build` (bare, no lifecycle scripts) — succeeded, and
  `out/data/reports/` was populated (confirms the config-level fix works
  independent of `prebuild`).
- `cd web && npm run build` — full pipeline (prebuild copy + next build +
  pagefind postbuild) succeeded; `out/data/reports/` held all 39 current
  report JSON files after this run.
- Extracted every `href="/data/reports/*.json"` from all generated
  `out/reports/*.html` files (39 links, one per dated report page) and
  confirmed each resolves to an actual file under `out/` — zero missing.
- Note: source `data/reports/` briefly showed 39 files vs. 38 copied in an
  intermediate run — traced to a concurrent agent adding
  `data/reports/2027-03-22.json` mid-session (untracked, newer mtime), not a
  bug in the copy logic. Re-running the build picked it up correctly.

## Files touched
- `web/next.config.ts` — inline copy IIFE added.
- `web/scripts/copy-reports.mjs` — comment updated to describe the new
  dual-path setup; exported `copyReports()` for potential future reuse,
  guarded its auto-run behind an `isMain` check.
