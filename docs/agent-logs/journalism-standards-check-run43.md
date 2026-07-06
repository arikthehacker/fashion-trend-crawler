# RSS show-notes standards check — run 43

## Topic

Compared `web/app/rss.xml/route.ts` against real RSS 2.0 conventions
(rssboard.org's RSS Best Practices Profile and spec, W3C feed validator docs)
— not previously covered in `docs/agent-logs/rss-feed.md`, which only logged
the feed's initial build.

## What real conventions say

- All `<item>` elements are optional except that title or description must
  be present, but item **titles should be meaningful in an aggregator's list
  view**, not a repeated constant.
- `<category>` is a standard optional per-item element for surfacing an
  existing taxonomy so aggregators/readers can filter.
- `<guid isPermaLink="true">` is correct only when the guid *is* a
  dereferenceable URL (which it is here — `/reports/[date]`); confirmed no
  change needed there.
- `pubDate` must be RFC-822; `toRfc822()` already does this correctly.

## Gap found

Every item's `<title>` was just `report.report_date` (e.g. "2026-07-06") —
identical in shape across all items, giving a reader scanning an RSS client's
list view no signal about what a given week's report actually covers before
clicking through. No `<category>` element was emitted despite the site
already tracking a `source_sectors` taxonomy per signal.

## Fix applied

`web/app/rss.xml/route.ts`: item `<title>` now leads with the report date
followed by up to 3 top tracked signal names (e.g. "2026-07-06:
off-duty-varsity, ..."), falling back to the bare date for thin weeks with no
`top_signals`. Added a `<category>` element per unique `source_sector`
referenced by that week's signals. No changes to `<link>`, `<guid>`,
`<pubDate>`, or `<description>` — those already matched convention.

## Verification

`cd web && npx tsc --noEmit` — passes clean, no errors.

## Not done

Did not run `next build` (not required by the task instructions for this
scope) or touch `sitemap.ts`/`robots.ts`/`layout.tsx`. Not committed, per
instructions.
