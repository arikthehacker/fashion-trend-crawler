# Run 59 — Dark-mode verification against built output

Run 58 added a `prefers-color-scheme: dark` override but only verified it via
`tsc --noEmit` and token-level contrast math — never checked the actual built
CSS or how it interacts with inline styles. This run closes that gap.

## What was checked

1. Ran `npm run build` (succeeded, 124 static pages + pagefind index).
2. Inspected `web/out/_next/static/chunks/0zxdtwvheo08h.css` directly — the
   `@media (prefers-color-scheme:dark){:root{...}}` block survived
   minification intact, appears exactly once, and is scoped to `:root` only
   (no later unscoped rule overrides it). Confirmed via string search for
   `prefers-color-scheme` (1 match) and `:root{` (2 matches, light + dark).
3. Checked whether `--black`/`--white` naming is actually inverted in the
   dark block (source shows `--black: #f8f6f1` / `--white: #0a0a0a` under the
   media query, opposite of their light-mode hex values). This looked like a
   bug at first glance, but it is correct: the tokens are ink/paper roles,
   not literal colors — `body` uses `background: var(--white); color:
   var(--black)`, so swapping the two hex values under the dark query
   correctly yields a dark background with light text. No fix needed.
4. Searched all `.tsx` files under `web/app` for inline `style={{}}` color
   usage. 15 files use `var(--...)` tokens in inline styles (435 occurrences
   total) — these resolve through the cascade like any CSS custom property
   reference, so they correctly pick up the dark-mode override with no
   special handling required. Only `web/app/icon.tsx` hardcodes raw hex
   (`#000`/`#fff`) — that's the favicon/PNG icon generator (not a rendered
   page), so it's expected to be static and out of scope for theming.

## Result

No fix was needed. The dark-mode CSS block is present, correctly scoped, and
not defeated by minification or purge. Inline styles across all page
components reference the shared custom properties, so they inherit the
dark-mode swap correctly. `npx tsc --noEmit` passes with no output/errors.

## Not done (out of scope)

- No real browser/OS dark-mode screenshot was taken (build artifact
  inspection only, per task scope).
- `--red` accent contrast in dark mode still unverified (carried over from
  run 58, still low risk).
