# Pagefind regression check (run 35)

**Result: pass — no gap found, no fix needed.**

Ran `cd web && npm run build` after the `source_links` removal (run 34) and
other recent frontend changes.

- Next.js build (Turbopack) compiled successfully, TypeScript check clean,
  85 pages generated across all routes (27 `/reports/[date]`, 42
  `/signals/[slug]`, plus static top-level pages).
- Pagefind postbuild step ran automatically and succeeded: indexed 81 HTML
  files, 1 language (en), 3456 words. (Up slightly from run 32's 78 files /
  3334 words, consistent with archive growth since then.)
- No errors or warnings from either the Next.js build or the Pagefind index
  step.

Conclusion: the `source_links` removal and other recent frontend changes did
not break the build or the Pagefind indexing pipeline. No further action
needed.

## Files touched

None — verification only.
