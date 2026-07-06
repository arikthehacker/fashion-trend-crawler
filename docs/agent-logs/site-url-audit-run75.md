# SITE_URL placeholder audit — run 75

## Task

Investigate the long-standing carried-forward TODO ("SITE_URL remains a placeholder
domain, blocking self-archival/citation correctness — still awaiting a human decision",
flagged run 50, still open at run 74). Scope: inventory every dependency on the
placeholder, consolidate if scattered, and confirm the actual domain decision correctly
stays deferred to a human.

## Finding: already centralized (no scattering found)

`web/lib/site.ts` already defines a single source of truth:

```ts
// lib/site.ts
export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL || "https://ari3lla-index.example.com";

export const SITE_NAME = "ARI3LLA INDEX";
```

It reads `NEXT_PUBLIC_SITE_URL` at build time and falls back to the placeholder
`https://ari3lla-index.example.com` so dev/build never breaks. This matches the
SKILL.md file-map description ("lib/site.ts: shared SITE_URL/SITE_NAME constants for
metadata/sitemap/robots/JSON-LD") — a previous run had already done the consolidation
work described in this task's step 3. No refactor was needed.

## Full inventory of consumers (every file/line depending on SITE_URL)

All 6 files that reference the placeholder import `SITE_URL` (and/or `SITE_NAME`) from
`web/lib/site.ts` — none hardcode the literal domain string themselves:

- `web/lib/site.ts:7` — the single definition (env var + fallback literal lives here,
  and only here)
- `web/app/layout.tsx:4,27,36,39` — `metadataBase`, Open Graph `siteName`/`url`
- `web/app/robots.ts:5,15` — `sitemap: \`${SITE_URL}/sitemap.xml\``
- `web/app/sitemap.ts:6,45,54,64` — route URLs, per-report URLs, per-signal URLs
- `web/app/rss.xml/route.ts:7,30,83,84,85` — RSS `<link>`, `<atom:link href>`,
  per-item URLs, feed title (`SITE_NAME`)
- `web/app/reports/[date]/page.tsx:7,20,25,107,108,123,127,140,761` — canonical link,
  Open Graph `url`, JSON-LD `Dataset`/`CreativeWork` identifiers, raw-data download URL,
  citation string ("Retrieved from {SITE_URL}/reports/...")

**Total: 6 files, ~23 reference sites, all funneling through the one constant.**

## Checked and ruled out as unrelated

Grepped `web/app/**/*.tsx` for other hardcoded `https://*.com|org|net` literals to make
sure no second placeholder domain was hiding elsewhere. Found only:
- `about/page.tsx:246` — GitHub issues link (real, permanent, not a placeholder)
- `reports/[date]/page.tsx:110` — `https://schema.org` (JSON-LD context URI, correct)
- `reports/[date]/page.tsx:154,735` — Creative Commons license URL (real, permanent)

None of these are placeholder-domain dependencies; no further consolidation needed.

## Conclusion

- The scatter problem described as "fixable" in the task did not exist at inspection
  time — it was already fixed in a prior run. No code changes made this run.
- When a human supplies the real production domain, the fix is genuinely one line:
  set `NEXT_PUBLIC_SITE_URL` in the deploy environment (or edit the fallback literal in
  `web/lib/site.ts:7`). No find-and-replace across files is required.
- The human-decision item itself — *what the real production domain is* — remains
  correctly unresolved and deferred. This run did not invent or guess a domain.

## Validation

Run from `web/`:

```
npx tsc --noEmit      -> clean, no output/errors
npx eslint .          -> clean, no output/errors
npm run build         -> succeeded, 164 pages generated, Pagefind postbuild indexed
                          159 pages / 5695 words, no errors
```

No files changed in this run other than this log.
