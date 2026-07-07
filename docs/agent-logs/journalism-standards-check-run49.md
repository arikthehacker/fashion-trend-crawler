# Journalism-standards check — run 49: print/PDF stylesheet for archival citation

**Topic:** Does the site have a `@media print` stylesheet so a researcher printing or
"Save as PDF"-ing a report page for citation gets clean archival output rather than the
full interactive site chrome?

**Research:** Standard print-CSS practice (MDN, SitePoint, and general 2025 print-CSS
guides) recommends: (1) hide in-page navigation/interactive chrome via a dedicated
`@media print` block or `.no-print` class, (2) force plain black-on-white text/links for
legibility and ink economy, (3) expand hyperlink URLs inline after link text (the classic
`a[href]:after { content: " (" attr(href) ")" }` pattern) so a printed page retains source
addresses once hyperlinks become inert on paper — directly relevant here since report pages
are full of outbound source citations, and (4) set page margins via `@page`.

**Finding:** `web/app/globals.css` had no `@media print` rules at all before this change —
confirmed via grep across `web/`. A citation printout of a report page would have carried
the full footer nav (archive/timeline/search/current-report/methodology links) with no
benefit on paper, and any expanded source-link URLs would have been silently dropped once
printed since links render as plain underlined text with no visible destination.

**Fix (small, scoped):**
- Added a `@media print` block to `web/app/globals.css`: hides `.no-print` elements, forces
  white background/black text/black links for print, expands `http(s)` link hrefs inline
  after the link text, sets a 2cm `@page` margin.
- Marked the report page's footer site-nav (`web/app/reports/[date]/page.tsx`, the
  archive/timeline/search/current-report/corrections links block) with `className="no-print"`
  — it's in-page navigation, not part of the archival report record.
- Left the methodology summary box, content_hash checksum line, and "download raw
  data"/CC BY 4.0 line untouched and printable — those are substantive citation metadata,
  not navigation chrome.

**Scope note:** Only the report detail page (the actual citable unit) was touched. The
homepage/archive/other index pages have their own inline nav but weren't in scope — they
aren't the thing a researcher cites.

**Verification:** `cd web && npx tsc --noEmit` — clean, no errors.
