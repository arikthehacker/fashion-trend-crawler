# Run 64 — regression check on run 63's per-signal deep-linking anchors

**Scope:** confirm `npm run build` is clean and re-verify run 63's per-signal
`id="signal-..."` anchors/permalinks, plus a regression check on dark mode,
skip-link, and OG metadata (last confirmed clean run 61).

## Verification

`cd web && npx tsc --noEmit && npx eslint . && npm run build` — all three
clean, no errors/warnings beyond the pre-existing glossary "no DEFINITIONS
entry" notices (expected, unrelated to this task). Static export generated
140 pages, Pagefind indexed 135 pages successfully.

## Findings

1. **Anchor uniqueness:** `anchorId = signal-${signal.signal_id || i}` in
   `web/app/reports/[date]/page.tsx`. Wrote a script scanning every
   `data/reports/*.json` for a signal_id/fallback-index collision within the
   same report — zero collisions across the full archive. Also grepped
   generated HTML (`web/out/reports/2026-07-06.html`, 4 signals) for
   duplicate `id="..."` attributes — none found. Real bug surface (a
   signal_id literally matching another signal's numeral fallback, e.g.
   `signal_id: "2"` colliding with a missing-id entry at index 2) is
   theoretically possible but not present in any current data.
2. **Permalinks:** in the same generated page, all four
   `href="#signal-..."` anchors match their corresponding `id="signal-..."`
   targets exactly (`sheer-layering`, `soft-tailoring`,
   `1990s-minimalism-revival`, `micro-bag-styling`).
3. **Regression check (dark mode / skip-link / OG):** all intact.
   `globals.css` still has the `prefers-color-scheme: dark` block and the
   run-63 `[id^="signal-"] { scroll-margin-top: 1.5rem; }` rule. Generated
   HTML has `id="main-content"` on `<main>` and
   `<a href="#main-content" class="skip-link">`. OG tags
   (`og:title`/`og:description`/`og:site_name`/`og:type`) present and
   populated per report.

## Outcome

No regressions found across the 3 runs since the last full check (61-63).
Nothing fixed — everything held. No files changed.
