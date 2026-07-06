# Periodic standards check — run 64: "Cool URIs don't change" URL design review

Topic not yet covered in prior periodic audits (checked list of ~35 prior topics). Reviewed
current route/URL choices against the W3C "Cool URIs Don't Change" principles (Tim
Berners-Lee, 1998; restated in the W3C "Cool URIs for the Semantic Web" note) — avoid file
extensions, avoid exposing implementation/software in the path, avoid classification
schemes that will be reorganized later, and keep identifiers stable independent of content
changes.

## What was checked

- `web/app/reports/[date]/page.tsx` — route key is the archival collection-window date
  (`YYYY-MM-DD`), which is permanent by construction (a past date never changes). Good.
- `web/app/signals/[slug]/page.tsx` — route key is `signal_id`, not a derived display name.
  Confirmed in `src/report_schema.py` (~line 423-436) that `signal_id` is schema-validated
  as a lowercase-hyphen slug (`islower()`/digit/`-`, no leading/trailing/double hyphen) at
  write time, independent of the signal's human-readable `name`. Since the URL is keyed off
  a validated stable ID rather than a mutable label, renaming a signal's display text later
  won't break existing `/signals/<slug>` links. This is already the correct pattern — no
  change needed.
- No route uses a file extension (`.html`, `.php`), a software/mechanism name (`cgi`,
  `exec`), a topic-classification path segment, or a query-string parameter as its primary
  identifier. `web/app/search/` does use client-side query state, but that's a filter UI,
  not a citable identifier — appropriate.
- `web/next.config.ts` uses `output: "export"` with no `trailingSlash` override, so Next's
  static-export default (`trailingSlash: false`) applies uniformly across all routes —
  consistent, not a mix of slash/no-slash forms that could fragment canonical URLs.
- `rss.xml/route.ts`, `sitemap.ts` — both derive links from the same date/slug identifiers
  above, so they don't introduce a second, divergent URL scheme.

## Verdict

No code change made. The site's existing route design (date-keyed reports, ID-keyed
signals, no extensions/query-params/mechanism names in paths) already matches the "Cool
URIs don't change" standard, including the specific durability property that matters most
here — a signal's citable URL is derived from a schema-validated permanent ID, not from
editable prose, so future copy edits to a signal's name/description can never break an
inbound link. Flagging as verified-compliant rather than a gap to fix.

## Sources

- https://www.w3.org/Provider/Style/URI (Tim Berners-Lee, "Cool URIs Don't Change")
- https://www.w3.org/2001/tag/2002/0607-intro
