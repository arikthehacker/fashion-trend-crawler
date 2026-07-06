# Run 59 — robots.txt completeness / indexability check

**Topic:** verified `web/app/robots.ts` + `web/app/sitemap.ts` output against real
search-crawler expectations (Google Search Central robots.txt spec, sitemap protocol
0.9), not just presence of the files.

## What was checked

- `web/out/robots.txt` (built output): `User-Agent: *`, `Allow: /`, blank line, then
  `Sitemap:` directive with absolute URL — matches spec (group syntax, directive
  ordering, absolute sitemap URL are all correct; trailing newline present).
- `web/out/sitemap.xml`: valid `sitemap.org/schemas/sitemap/0.9` namespace, absolute
  `<loc>` URLs, homepage has no trailing slash (consistent with the canonical form used
  elsewhere in the site), `<lastmod>` present in ISO date form. Confirms `sitemap.ts`
  and `robots.ts` reference the same `SITE_URL` constant from `lib/site.ts` — no
  domain mismatch between the two files.
- Grepped `web/app/**` for `noindex` / robots meta overrides: none found. No page
  accidentally opts out of indexing.
- No `Disallow` rules exist at all (correctly — every route on this site is meant to be
  public/indexable; there's no admin/API surface under `web/app` that would warrant
  one).
- `dynamic = "force-static"` is set on both `robots.ts` and `sitemap.ts`, required for
  static export (`next export`/`out/`) to actually emit these files rather than 404 —
  confirmed both files exist in `web/out/`.

## Verdict

No gap found. This exact area (sitemap/robots/JSON-LD) was already built correctly in
run 5 (`docs/agent-logs/sitemap-robots-jsonld.md`) and nothing since has regressed it —
`SITE_URL` is centralized in `lib/site.ts` so there was no opportunity for the two files
to drift out of sync. No code change made this run.

## Note for next audit

`SITE_URL` still falls back to the `ari3lla-index.example.com` placeholder domain
(no production domain set yet per `lib/site.ts` comment). Once a real domain exists,
re-verify indexability against `NEXT_PUBLIC_SITE_URL` at deploy time, not just against
the placeholder build.
