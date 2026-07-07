# Rich Results validation against Google's documented requirements (run 54)

Checked the `@graph` (NewsArticle + Dataset) in `web/app/reports/[date]/page.tsx` against
Google's actual search-central docs (developers.google.com/search/docs/appearance/structured-data),
not third-party summaries — this markup had only ever been checked for JSON validity/field
coverage before, never the real eligibility bar.

**Method:** ran `cd web && npm run build`, then extracted the real generated JSON-LD from
`out/reports/2026-05-07.html` (grepped the `application/ld+json` script tag) and read it against
Google's documented required/recommended property lists for both types.

**NewsArticle/Article — Google's docs state there are no strictly required properties** ("add the
properties that apply to your content"); everything listed is recommended: `headline`,
`datePublished`, `dateModified`, `author` (name/url), `image`. The generated output has headline,
datePublished, dateModified, author.name, url, description — all present. The only recommended gap
is `image` (no ImageObject/URL), which Google explicitly treats as recommended, not required — a
report page with no representative image genuinely has none to offer, so this is a legitimate,
not-necessarily-fixable gap, noted rather than patched.

**Dataset — Google's docs list exactly two required properties: `name` and `description`,** with
`description` required to be 50–5,000 characters. Both present in the generated output: `name`
("ARI3LLA INDEX style signal report — 2026-05-07") and `description` (~330 characters, pulled from
`executive_summary`), comfortably inside range. All recommended extras Google lists
(`creator`, `license`, `temporalCoverage`, `variableMeasured`, `url`, `isAccessibleForFree`, etc.)
are already present except `isAccessibleForFree` and `citation`/`funder` (not applicable to this
project).

**Result: no genuinely required property was missing from either type. No code change was made.**
This is a clean result given how much prior JSON-LD work (runs 5, 36, 37, 44, 46) already went into
this block — it was over-built relative to Google's actual (low) required bar, not under-built.
Verified with `npx tsc --noEmit` (no errors) and a full `npm run build` (succeeded, 112 pages,
Pagefind index built). Not committed per instructions.

Optional, non-required follow-up if ever prioritized: add an `image` property to NewsArticle if/when
a representative image exists for a report (currently text-only reports have none to offer, so this
is not a bug — see doc's photo-free-by-design principle for report pages).
