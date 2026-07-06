# Run 66 — build/regression re-check (no changes made)

**Scope:** full build verification + spot-check of newest report pages +
internal link scan across `.tsx` files, per standing regression routine
(last checked run 64, 2 runs ago).

## Verification

`cd web && npx tsc --noEmit && npx eslint . && npm run build` — all three
clean. tsc: 0 errors. eslint: 0 errors/warnings. Build: compiled
successfully, static export generated 144 pages (up from 140 at run 64 —
archive has grown), Pagefind indexed 139 pages. Only output was the
pre-existing, expected `[glossary] no DEFINITIONS entry for term "..."`
notices for newly-added terms (2027-06-14 through 2027-08-09 reports) —
unrelated to this task, same known/expected pattern as prior runs.

## Spot-check: newest 2 report pages (`2027-08-09.html`, `2027-07-26.html`)

- **Signal-anchor permalinks:** `id="signal-ragebait-runway-casting"` /
  `id="signal-lv-waterfall-heatwave-backlash"` present, and the
  corresponding `href="#signal-ragebait-runway-casting"` permalink matches
  exactly on the 08-09 page.
- **Dark mode:** `globals.css` still has the `@media (prefers-color-scheme:
  dark)` block.
- **Skip-link:** `<a href="#main-content" class="skip-link">` and
  `id="main-content"` both present in generated HTML.
- **Open Graph:** `og:title`, `og:description`, `og:url`, `og:site_name`,
  `og:type` all present and correctly populated per report date on both
  pages.

## Internal link scan

Grepped every `href="/..."` in `web/app/**/*.tsx` — all targets
(`/methodology`, `/archive`, `/timeline`, `/search`, `/taxonomy`,
`/glossary`) correspond to real routes per the file map in SKILL.md. No
broken internal links found.

## Outcome

No regressions. Everything held — no files changed. Archive grew from 140
to 144 static pages since run 64, consistent with new reports being added
in the interim; nothing else of note.
