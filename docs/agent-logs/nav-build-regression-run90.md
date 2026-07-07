# Nav/Build Regression Sweep — Run 90

Branch: `ari3lla-index-loop-improvements`. Clean wipe per practice since run 72.

## Steps

1. **Stray processes**: `wmic` checks for node.exe/python.exe returned "No Instance(s) Available" — nothing to kill.
2. **Clean wipe + typecheck**: `rm -rf .next out && npx tsc --noEmit` — clean, no output/errors.
3. **ESLint**: `npx eslint .` — clean, no output/errors.
4. **Build**: `npm run build` — completed fully. 82 reports copied by prebuild script, Next.js 16.2.4 (Turbopack) compiled successfully, 198 static pages generated (0/198 → 198/198), no warnings. Postbuild pagefind indexed 193 HTML files / 6195 words successfully.
5. **Report count check**: `data/reports/*.json` = 82, `web/out/reports/*.html` = 82. Match.
6. **Built-output verification** (all confirmed intact, accounting for static-export `<route>.html` shape, not `<route>/index.html`):
   - Signal deep-link anchors: live on **report** pages (`reports/2026-07-06.html` has `id="signal-sheer-layering"` etc. + matching `href="#signal-..."`), not on signal detail pages — correct per source (`app/reports/[date]/page.tsx:356`).
   - Dark mode: CSS `@media (prefers-color-scheme: dark)` in `app/globals.css` — no JS toggle by design; confirmed present in source.
   - Skip-link: present in `index.html` ("Skip to" text + `skip-link` class).
   - Open Graph meta tags: present in `index.html` (og:title/description/url/type).
   - RSS: `atom:link` self-reference present, exactly 50 `<item>` elements in `rss.xml`.
   - Corrections banner: renders on affected pages (e.g. `signals/peplum-waist-revival.html`, `reports/2026-05-07.html`, `reports/2026-07-20.html`).
   - Signal titles: wrapped in real `<h3>` elements (confirmed on signal detail page).
   - `/signals/[slug]` recency line: conditional on `getSignalRecencyStatus`; renders "Last appeared ... since, with no further occurrence on file." on applicable signals (e.g. `1990s-minimalism-revival.html`); null/absent correctly for signals without a recency gap (e.g. `lv-fw28-menswear-dropped-shoulder-overcoat.html`).
   - JSON-LD structured data: present on `reports/[date]` and `glossary` pages (by design, per source) — confirmed in `reports/2026-07-06.html`.
   - Sources/Taxonomy pages: `<h1>` content present ("Sources", "Taxonomy").
   - Archive year-grouping headers: 2026, 2027, 2028 all present in `archive.html`.

## Outcome

No regressions found. All initial zero-hit greps during investigation were due to checking the wrong page/pattern (e.g. expecting signal anchors on signal-detail pages instead of report pages, or expecting a JS dark-mode toggle instead of the CSS-media-query implementation) — not actual code defects. No fixes needed, no files modified other than this log.
