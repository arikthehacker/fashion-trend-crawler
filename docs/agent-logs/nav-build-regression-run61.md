# Nav/link/build re-verification (run 61)

Scope: re-check `npm run build` cleanliness, dark mode/skip-link/OG metadata
in built output, and internal link integrity, given dark mode, several new
reports, and the Met Gala threshold-crossing shipped since run 58.

## TypeScript / ESLint

`npx tsc --noEmit` — clean, no errors.
`npx eslint .` — clean, no errors/warnings.

## Build

`npm run build` succeeded: 53 reports copied, 134 static paths generated
(51 `/reports/[date]` including new 2027-06-28/06-21/06-14 tenniscore/Wimbledon
reports, 64 `/signals/[slug]` including `met-gala-2027-coverage-gap`, plus
fixed routes), zero build errors. Pagefind post-build indexed 129 pages
cleanly. Only console output was the expected non-blocking
`[glossary] no DEFINITIONS entry for term "..."` warnings for newly-added
terms (tenniscore, Wimbledon 2027, blokecore, etc.) — pre-existing pattern,
not a regression.

## Output spot-check (web/out, 3 pages)

Checked `index.html`, `reports/2027-06-28.html` (most recent report), and
`archive.html` for `og:title`/`og:description`/`og:type`, the site-wide
skip-link (`<a href="#main-content" class="skip-link">`), and its target
(`id="main-content"`). All three present and correctly rendered on all three
pages, matching run-57/58 findings — no regression. Dark-mode CSS
(`prefers-color-scheme`) confirmed present in the compiled stylesheet
(`_next/static/chunks/0zxdtwvheo08h.css`).

## Internal links

Enumerated every `href=` across all `.tsx` files in `web/app`. All static
nav hrefs (`/`, `/methodology`, `/taxonomy`, `/sources`, `/glossary`,
`/timeline`, `/archive`, `/search`, `/about`, `/case-study`) resolve to real
routes; nav arrays in `page.tsx`, `not-found.tsx`, `methodology`, `sources`
match run-58's pattern. Dynamic hrefs (`/reports/${date}`,
`/signals/${slug}`, JSON download link) all resolved during build with no
errors. No dead or malformed links found.

## Verdict

No regressions. Build, dark mode, skip-link, OG metadata, and internal links
all hold after the dark-mode, new-report, and Met Gala changes. No code
changes made this run.
