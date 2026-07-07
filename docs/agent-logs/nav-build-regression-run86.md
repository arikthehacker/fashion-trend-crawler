# Nav/build regression sweep — run 86

Clean-wipe regression sweep per established practice (since run 72), branch `ari3lla-index-loop-improvements`.

## 1. Stray process check
`wmic` showed one in-flight `npm run build` / `next build` / postcss.js chain (PID 25964 etc.) at
check time — a concurrent agent's build, not a straggler. It had exited on its own by the
time of the recheck seconds later. No `python.exe` processes found. Nothing killed.

## 2. `rm -rf .next out` + `npx tsc --noEmit`
Clean wipe done. `tsc --noEmit` — **PASS**, no output/errors.

## 3. `npx eslint .`
**PASS**, no output/errors.

## 4. `npm run build`
First attempt failed with "Another next build process is already running" — a concurrent
agent's build lock, not a regression. Retried ~20s later — **PASS**.
- 78 reports copied by `copy-reports.mjs`
- 191 static routes generated (7 workers), 0 build warnings
- `/reports/[date]`: 78 paths, `/signals/[slug]`: 96 paths
- Pagefind postbuild indexed 186 pages / 6115 words successfully

## 5. Built-output grep checks (against `web/out`)
Note: Next 16 export emits flat `<route>.html` files (not `<route>/index.html`) — adjusted
greps accordingly.

- Signal anchor deep-linking (`id="signal-..."`): present (e.g. `reports/2026-05-07.html`) — PASS
- Dark mode (`prefers-color-scheme` in globals.css, OS-driven, no manual toggle per project docs): PASS
- Skip-link (`#main-content`): present in `index.html` — PASS
- Open Graph meta (`og:title`, `og:description`, `og:type`): PASS
- RSS `atom:link rel="self"`: present, correct href — PASS
- RSS `<item>` count: exactly 50 — PASS
- Corrections banner: "Corrections" heading text present across report pages — PASS
- Signal titles in real `<h3>` elements: confirmed (e.g. `reports/2026-07-06.html`) — PASS
- `/signals/[slug]` recency status line (resolved / status_history text): present — PASS
- JSON-LD (`application/ld+json`): present on report pages — PASS
- Sources/Taxonomy page content (Source Sector / Confidence / Volatility): present on both pages — PASS
- Archive year-grouping headers: only `2027` and `2026` `<h2>` group headers render.

## 6. Report-page count vs. data/reports/*.json
`data/reports/*.json` = 78. Built `web/out/reports/` directories = 78. **Match — PASS.**

## 7. Real finding: archive year-boundary grouping gap (not fixed — assigned to another agent)
`data/reports/2028-01-03.json` exists (the new report mentioned as in-flight this run) and its
entry (`2028-01-03`) does appear in `archive.html`'s report list, but **no `2028` year-group
`<h2>` header renders** — only `2027` and `2026` do. This is exactly the year-boundary
archive-grouping issue this run's task brief said another agent is auditing/fixing in
`web/app/archive/page.tsx`. Per instructions, I did **not** touch `archive/page.tsx`,
`robots.ts`, or `sitemap.ts` — flagging this as a real, currently-live gap for whoever owns
that file, not something I fixed myself.

No other regressions found. No files edited except this log.
