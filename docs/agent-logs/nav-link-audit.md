# Nav/link coherence audit

Read all 11 pages under `web/app/**/*.tsx` and mapped every `<Link href>`.

**Broken links / typos:** none found. All static hrefs (`/`, `/archive`, `/timeline`,
`/methodology`, `/taxonomy`, `/sources`, `/about`, `/case-study`) and dynamic hrefs
(`/reports/${date}`, `/signals/${slug}`) resolve to real routes.

**Orphaned page:** `/case-study` had zero inbound links from any other page — not even
the homepage nav. It was only reachable by typing the URL directly. Fixed by adding it
to the shared nav list on the homepage and on methodology/taxonomy/sources/about.

**Inconsistent nav:** the homepage nav evolved over multiple runs to
`[methodology, taxonomy, sources, timeline, about]`, while methodology/taxonomy/sources/about
pages still used an older 4-item set (`/`, plus the other 3 of that group) that never
picked up `timeline`, `archive`, or `case-study` when those pages were added in later runs.
Result: from those four pages, timeline/archive/case-study were 0 clicks away on the
homepage but unreachable without first returning home.

Fix: unified the nav array on `page.tsx`, `methodology/page.tsx`, `taxonomy/page.tsx`,
`sources/page.tsx`, and `about/page.tsx` to include the full site section set
(`/`, methodology, taxonomy, sources, timeline, archive, about, case-study, minus self).

Archive/timeline/reports/[date]/signals/[slug] already had consistent "Timeline · Full
archive · Current report" footers from earlier runs — left as-is, no fix needed there.

Verified with `npx tsc --noEmit` (clean) and `npx next build` (clean, all 37 static/SSG
pages generated including 20 signal slugs and 5 report dates).
