# Run 60 — internal citation/link-rot check (signal_id cross-references)

**Topic:** not previously covered in agent-logs. Checked whether report prose
(`evidence`/`index_note`/`human_editor_note`) ever references a `signal_id` by name that
no longer exists after a rename, and whether the `/reports/[date]` and `/signals/[slug]`
URL scheme has drifted across its history.

## Method

1. `git log --follow` on `web/app/reports/[date]/page.tsx` and
   `web/app/signals/[slug]/page.tsx`, plus a rename-summary log scoped to both route
   directories. No renames found since the routes shipped (run 3-4): `720b372` (reports)
   and `88f44ee` (signals) are still the original paths.
2. Checked how `/signals/${slug}` hrefs are generated in `archive/page.tsx`,
   `reports/[date]/page.tsx`, `search/SearchClient.tsx`, `timeline/page.tsx`, and
   `sitemap.ts` — all five build the href directly from a live `signal.signal_id` field
   read off `data/reports/*.json` at build time, not from any hardcoded string. There is
   no separate slugify step to drift out of sync.
3. Parsed all 20+ files under `data/reports/*.json`, collected the full set of 63 distinct
   `signal_id` values ever used, then scanned every prose field for kebab-case tokens that
   look like a signal reference but aren't in that set. All matches were false positives
   (dates like `2026-08-24`, descriptive phrases like `back-to-school`, `year-over-year`,
   `no-forward-fill`) — not signal_id-shaped mentions of an actual retired signal.

## Finding

**No link rot exists, and the architecture is structurally immune to it**: signal links
are never hardcoded in prose — every `/signals/[slug]` href on every page is generated
live from the same `signal_id` field that `signals/[slug]/page.tsx`'s
`generateStaticParams` also reads. A signal can't go stale in one place without going
stale everywhere, because there's only one source of truth for the id. The
`/reports/[date]` and `/signals/[slug]` route paths themselves have also been stable
since they were introduced (runs 3-4), confirmed via `git log --follow` with zero renames
across the ~55 subsequent runs.

## Outcome

No code change made — genuinely verified as already meeting the standard. No TODO item
added.
