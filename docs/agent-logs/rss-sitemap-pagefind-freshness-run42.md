# RSS/sitemap/Pagefind freshness re-check — run 42

Re-verified after 5 new reports (runs 38-41) landed without a dedicated freshness
check since run 37.

**Result: all clean, no fixes needed.**

## Build

`cd web && npx next build` — compiled successfully, TypeScript clean, 97 static
pages (34 `/reports/[date]`, 47 `/signals/[slug]`, plus top-level static pages).
`data/reports/*.json` currently has 34 files, matching.

## RSS (`out/rss.xml`)

34 `<item>` entries, one per report — no gaps. Spot-checked `<pubDate>` sourcing
(run 36/37's fix: use last `revision_history[].corrected_at` when present, else
`report_date`):
- `2026-12-21` has two `revision_history` entries; `<pubDate>` correctly reads
  `Mon, 06 Jul 2026` from the last entry's `corrected_at`, not the report's own
  `2026-12-21` date.
- `2027-02-15` and `2027-01-11` have empty `revision_history`; `<pubDate>`
  correctly falls back to `report_date` (`15 Feb 2027`, `11 Jan 2027`).

Fix is still working correctly across the newest reports; no regression.

## Sitemap (`out/sitemap.xml`)

34 `<loc>` entries under `/reports/` and 47 under `/signals/` — matches build
output exactly (34 report routes, 47 signal routes). No gaps.

## Pagefind

Ran `npx pagefind --site out --output-subdir _pagefind` (postbuild step):
indexed 93 HTML files / 3821 words, 1 language (en). Growth is consistent and
monotonic: run 32 was 78 files/3334 words, run 35 was 81 files/3456 words
(27 reports/42 signals then), now 93 files/3821 words (34 reports/47 signals).
No errors, no stale/missing entries.

## Files touched

None — verification only, no fixes required. Not committed per instructions.
