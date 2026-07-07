# Run 35 research: link-rot mitigation (Wayback Machine / Perma.cc)

## Angle chosen
(a) Internet Archive's own link-rot mitigation approach, since this project cites
external style-discourse sources and calls itself an archival/preservation project.

## External findings
- Internet Archive + Automattic shipped a "Link Fixer" WordPress plugin (Feb 2026):
  it scans outbound links every 3 days, cross-references the Wayback Machine, and
  when a source page dies, redirects readers to the archived snapshot instead of a
  dead link — it also proactively snapshots a page at citation time if no archive
  exists yet, rather than waiting for it to go dead.
- Perma.cc (Harvard LIL) is the standard tool in legal/academic citation contexts:
  it captures a stable snapshot at citation time and returns a permanent redirect
  URL, precisely to prevent the citing document's own credibility from decaying when
  a cited source disappears.
- The common pattern across both: **archive the source at time of citation**, not
  after the fact — waiting until a link is already dead loses the content entirely.

## Codebase check (concrete finding)
Checked `src/report_schema.py`'s `Signal` schema and `REQUIRED_SIGNAL_KEYS`
(lines ~53-80): there is **no URL field at all** for a signal's underlying source.
`evidence` (line 80) is a free-text `str`, and `source_sectors` (line 76) is a list
of taxonomy categories (e.g. "editorial", "retail") — neither stores a citable link
to the actual article/post that was crawled. Confirmed in
`web/app/reports/[date]/page.tsx` (line 268): `{signal.evidence}` renders as prose
only, with no external `href` anywhere near a signal. `crawler.py` does fetch real
URLs during collection, but nothing carries them through to the persisted Report
schema or the rendered page.

## Recommendation
Before link-rot mitigation (Wayback save-page-now API, Perma.cc) is even relevant,
the schema needs a place to put a URL. Add an optional `source_url` (or
`source_urls: list[str]`) field to `Signal` in `src/report_schema.py`, populate it
from the crawler's already-fetched URLs in `summarize.py`, and render it as a
citation link in `reports/[date]/page.tsx`. Only once real URLs are being persisted
and shown does an archival-snapshot step (fetching a Wayback capture URL at
report-generation time) become a meaningful next step — right now there is nothing
to protect from rotting because nothing is being linked to yet.
