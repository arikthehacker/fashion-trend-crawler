# Full regression sweep — run 87

Branch: `ari3lla-index-loop-improvements`. Clean-wipe practice (since run 72) followed
throughout: killed/verified no stray processes, `rm -rf .next out`, then a single
fully-completed `npm run build` from scratch — no partial/interrupted output was
inspected at any point (this is the exact failure mode that produced run 86's false
"missing 2028 header" alarm).

## Process check
`wmic process where "name='node.exe'"` and `...python.exe...` both returned "No
Instance(s) Available." — nothing to kill.

## Checks
- `npx tsc --noEmit` — **PASS**, no output.
- `npx eslint .` — **PASS**, no output.
- `npm run build` (from wiped `.next`/`out`) — **PASS**, ran to full completion
  (prebuild copy-reports → Turbopack build → 192 static pages generated → Pagefind
  postbuild indexing 187 pages/6136 words). No warnings emitted anywhere in the log.
  Route summary: 79 `/reports/[date]` pages, 96 `/signals/[slug]` pages, plus the
  fixed top-level routes (home, about, archive, case-study, glossary, methodology,
  search, sources, taxonomy, timeline, sitemap.xml, robots.txt, rss.xml, icon).

## Report count
`data/reports/*.json` = 79. Built `web/out/reports/` = 79 date subdirectories
(plus matching `.html`/`.txt` flat files per date). **Exact match — PASS.**

## Regression-fix spot checks (grepped against the real built `web/out` output, all on
first-run clean artifacts)
- Signal-anchor deep-linking permalinks (`id="signal-..."` in report pages) — PASS
- Dark mode (`prefers-color-scheme` present in built CSS) — PASS
- Skip-link (`#main-content` present, x2, in report page) — PASS
- Open Graph meta tags (`og:title`, `og:description`, `og:type`, `og:url`) — PASS
- RSS `atom:link rel="self"` self-reference — PASS; `<item>` count = exactly 50 — PASS
- Corrections banner (`correction-history` class/text found in reports with
  corrections, e.g. 2026-07-20) — PASS
- Signal titles as real `<h3>` elements in report pages — PASS
- `/signals/[slug]` recency status line — PASS (verified exact text: "Last appeared
  2027-12-20 — 2 published reports since, with no further occurrence on file." on
  `resort-2028-puffer-shell-skirt`)
- JSON-LD structured data (`application/ld+json`) present in report pages — PASS
- Sources/Taxonomy pages — PASS, non-trivial content present (single-line minified
  HTML, ~65KB/~70KB respectively; `wc -l` reads 0 because there's no trailing
  newline, this is not missing content — confirmed via byte count + text grep)
- **Archive year-grouping headers, including 2028** — PASS. Confirmed directly against
  this run's own from-scratch build: `archive.html` contains an `<h2>2028</h2>`
  header alongside `2027` and `2026`. This is the exact item run 86 misreported as
  missing due to inspecting a stale/partial build during a concurrent build-lock
  collision. This run's build had no lock conflict and ran start-to-finish before any
  grep was performed.

## Regression found / fixed
None. No real regression found in already-committed code. All prior fixes remain
intact in a genuinely clean, fully-completed build. Run 86's "missing 2028 header"
report is reconfirmed as a false alarm — not reproduced here.

## Concurrent work note
No frontend-affecting changes from other concurrent agents (crawler.py/taxonomy.py
domain additions, manual-sampling cadence check, docs-only report work) were visible
in this build — those are Python/docs-only per the task brief and did not appear in
the `web/` diff surface checked here (tsc/eslint/build all ran against `web/` only).
No files were edited by this sweep; nothing committed.
