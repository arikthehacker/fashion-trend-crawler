# Nav/link re-verification (run 45)

Scope: re-verify run 42's two fixes survived runs 43-44 (`web/lib/reports.ts`,
`web/app/page.tsx`, `web/app/reports/[date]/page.tsx`, `web/app/rss.xml/route.ts`),
plus a dedicated site-wide broken-internal-link check.

## Case-study nav (run 42 fix)

Still present and correct. `case-study/page.tsx`'s masthead `<nav>` (lines
153-186) carries the same 9-item Pattern-A array (self-link "Case Study"
omitted, 8 links shown) with identical `<Link>` style object, including
`fontFamily`, `fontSize: "0.7rem"`, `textDecoration`, and the target-size
fix (`display: "inline-block", padding: "0.65rem 0"`). Byte-for-byte
consistent with `page.tsx`'s nav block (lines 80-114) and the other four
Pattern-A pages.

## WCAG 2.2 target-size padding (run 42 fix)

Confirmed intact in all 5 files touched in run 42, including `page.tsx`
despite its runs-43/44 edits: `about`, `sources`, `taxonomy`, `glossary`,
and `page.tsx` all still have `display: "inline-block", padding: "0.65rem 0"`
on their nav `<Link>` style objects. The `page.tsx` changes in runs 43-44
(latest-report data wiring) landed above/around the nav block without
touching it — no regression.

## Site-wide broken-internal-link check (new, dedicated)

Enumerated every `<Link href>` / `<a href>` across all `.tsx` files
(static, template-literal, and dynamic hrefs). Targets: `/`, `/about`,
`/archive`, `/case-study`, `/glossary`, `/methodology`, `/search`,
`/sources`, `/taxonomy`, `/timeline`, `/reports/[date]`, `/signals/[slug]`,
plus one in-page anchor `#correction-history` in `reports/[date]/page.tsx`.
Cross-checked against `web/app/` directory listing — every static segment
(`about/`, `archive/`, `case-study/`, `glossary/`, `methodology/`,
`reports/`, `search/`, `signals/`, `sources/`, `taxonomy/`, `timeline/`,
`rss.xml/`) exists. No dead links found.

## Verification

`cd web && npx tsc --noEmit && npx eslint . && npx next build` — all clean.
Build output confirms all expected static/SSG routes generate successfully,
including `/reports/[date]` (37 paths) and `/signals/[slug]` (47 paths).

Nothing was broken; no fixes were needed this run.
