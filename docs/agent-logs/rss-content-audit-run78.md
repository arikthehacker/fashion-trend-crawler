# RSS content audit — run 78

## Research
- WebSearch on RSS item-limit conventions: no universal standard, but real-world
  guidance is that RSS is for recent updates, not an archive substitute; feeds
  are commonly kept lightweight; podcast feeds are the documented exception
  (full back-catalog expected in-feed).
- WebFetch of rssboard.org RSS 2.0 spec: RSS 0.91 hard-capped feeds at 15
  `<item>`s; RSS 2.0/rssboard removed the hard limit but leaves item-count
  policy to the publisher. pubDate must be RFC 822 (e.g. `Sat, 07 Sep 2002
  00:00:01 GMT`). `<guid>` uniqueness/format is entirely up to the feed
  source — no mandated syntax, only that it identifies the item; `isPermaLink`
  defaults to true and, when true, the guid should be a clickable permalink.

## Audit of web/app/rss.xml/route.ts (before fix)
1. **Item limit — real bug found.** `getAllReports()` was used unbounded: all
   70 reports (data/reports/, growing weekly) were emitted as `<item>`s. Per
   research above, this is real feed bloat for a text-report feed (not the
   podcast exception) — fixed by capping to the 50 most recent reports
   (`MAX_FEED_ITEMS = 50`), consistent with the common ~20-50 recent-item
   convention. Full archive remains available at /archive and per-date pages;
   the feed doesn't need to duplicate it.
2. **pubDate — correct, no bug.** `toRfc822()` derives from `lastUpdated`
   (`report.revision_history[...].corrected_at ?? report.report_date`), a
   real content-derived date, not file mtime or build time. `toUTCString()`
   output format matches RFC 822 as required by spec.
3. **guid — correct, no bug.** `guid isPermaLink="true"` is built from
   `${SITE_URL}/reports/${report.report_date}` — deterministic from a
   permanent identifier (the report's own date), so it is unique per item and
   stable across repeated builds (verified: rebuilding the site does not
   change the input report_date, so the guid string doesn't change).
4. **Title/description — correct, no bug.** Title is built from real
   `top_signals[].name` (or falls back to the date for a genuinely thin
   week); description is `report.executive_summary`, both read live from
   data/reports/ JSON — no hardcoded/placeholder text found.
5. **External validator cross-check** — rssboard.org RSS 2.0 spec (linked
   from the W3C Feed Validator's own docs page) confirms above; W3C
   validator page itself is just a landing page, not spec text, so rssboard's
   canonical spec was used instead.

## Fix applied
- `web/app/rss.xml/route.ts`: added `MAX_FEED_ITEMS = 50` constant and
  `.slice(0, MAX_FEED_ITEMS)` on `getAllReports()` in the `GET()` handler,
  with an inline comment citing the research rationale.

## Verification
- `npx tsc --noEmit` — clean.
- `npx eslint .` — clean.
- `npm run build` — succeeded (166 pages, Pagefind index built).
- Inspected `web/out/rss.xml` directly: `grep -c '<item>'` → 50 (was
  unbounded/70 before the fix). Spot-checked the first item: real
  `pubDate` (`Mon, 01 Nov 2027 00:00:00 GMT`), real title/description text
  matching the actual report content, `guid` matching the item's permalink.

## Result
One real bug found and fixed (unbounded feed item count → capped at 50).
pubDate, guid, and title/description were all already correct against RFC
822 / rssboard spec conventions — no changes needed there. Not committed per
instructions.
