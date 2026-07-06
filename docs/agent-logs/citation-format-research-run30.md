# Citation format research (run 30)

## Research

Checked standard web-citation conventions (Purdue OWL, APA Style 7th ed., Scribbr) for
citing a web page/dataset with a version/access date. Consensus elements: author/organization,
publication or access date, page title, site/publisher name, and URL — with "Retrieved from"
required specifically for non-archived, content-designed-to-change pages (a stable/archived
page doesn't strictly need a retrieval date, but including one is harmless and common in
digital-humanities archive practice).

## What the existing "Cite as" block had

`web/app/reports/[date]/page.tsx` (added run 5, `docs/agent-logs/citation-line.md`) renders:

```
Cite as: ARI3LLA INDEX, {report.report_date}, /reports/{report.report_date} (checksum ...)
```

This has organization, date, and a stable identifier (checksum) — but two gaps vs. standard
convention: (1) no page/report title, and (2) the URL was site-relative, not a resolvable
absolute URL, so it isn't actually copy-pasteable as a citation outside the site. Run 5's log
noted no canonical domain existed at the time; that's since been fixed — `lib/site.ts` now
exports `SITE_URL`/`SITE_NAME` (used elsewhere in this same file for JSON-LD), so the original
blocker is gone.

## Change made

Added one additive line beneath the existing "Cite as" line — a formatted, copy-pasteable
citation string using the now-available `SITE_URL`/`SITE_NAME`:

```
ARI3LLA INDEX. ({report.report_date}). Weekly style signal report. Retrieved from {SITE_URL}/reports/{report.report_date}
```

Kept as a plain `<p>` (not a heading — matches the existing citation line's tag/styling, no
heading semantics needed for a caption-style footer line). No other JSX changed.

## Verification

`cd web && npx tsc --noEmit && npx next build` — both passed clean, all 77 static pages
generated including the report date routes.

Not committed, per instructions.
