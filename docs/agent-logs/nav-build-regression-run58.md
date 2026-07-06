# Nav/link/build re-verification (run 58)

Scope: re-do the run-53 sweep given recurring-signals filtering, skip-link
additions (run 56/57), and the Met Gala signal-tracking fix shipped since.

## Internal links

Enumerated every `href="..."`, `href: "..."`, and `href={\`...\`}` across all
`.tsx` files in `web/app`. All static segments (`/`, `/methodology`,
`/taxonomy`, `/sources`, `/glossary`, `/timeline`, `/archive`, `/search`,
`/about`, `/case-study`) resolve against real routes under `web/app/`. The
9-item Pattern-A nav array is consistent across all 9 pages that carry it
(`page.tsx`, `not-found.tsx`, `about`, `sources`, `taxonomy`, `glossary`,
`methodology`, `case-study`), each varying only in which self-link is
dropped. Dynamic hrefs (`/reports/${date}`, `/signals/${slug}`,
`/data/reports/${date}.json` download link) all resolved during the build —
126 static paths generated with no broken-reference errors. No dead or
malformed links found.

## Skip-link consistency (post run-57)

`layout.tsx` still renders `<a href="#main-content" className="skip-link">`
site-wide, and `id="main-content"` is present in all 13 page files plus
`not-found.tsx` (14 files total, matching run-57's count). Wrote a Node
script to scan every generated file in `web/out` (not just a sample) for
both the skip link and its target: **121/121 pages pass** — skip link
present, `#main-content` target present, in the correct document order.
Consistent with run 57's result; no regression from any run-58-adjacent edit.

## Build

`npx tsc --noEmit` — clean, no errors.
`npx eslint .` — clean, no errors/warnings.
`npm run build` — succeeded: 126 static paths (47 `/reports/[date]`, 56
`/signals/[slug]`, plus fixed routes), Pagefind post-build indexed 121 pages
with no errors. The only build-time console output is expected
`[glossary] no DEFINITIONS entry for term "..."` warnings for terms without
glossary definitions yet — pre-existing, non-blocking, unrelated to this
scope.

## Verdict

Nothing broken. Links, skip-link additions, and the build are all intact
after the recurring-signals, skip-link, and Met Gala fixes. No code changes
made this run.
