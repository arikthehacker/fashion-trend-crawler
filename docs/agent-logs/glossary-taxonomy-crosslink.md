# Glossary/Taxonomy cross-link

Run 21's doc re-read flagged that `/glossary` deliberately excludes "recurring
classifications" (volatility/confidence tiers), deferring that content to
`/taxonomy`, but the split wasn't cross-linked with any specificity.

## Changes

- `web/app/glossary/page.tsx`: extended the intro paragraph with one sentence
  naming what's excluded (source sectors, confidence/volatility labels like
  flash/microtrend/revival) and a direct link to `/taxonomy`.
- `web/app/taxonomy/page.tsx`: extended the intro paragraph with a reciprocal
  sentence naming what taxonomy doesn't cover (style/aesthetic terminology,
  e.g. quiet luxury, Y2K nostalgia) and a direct link to `/glossary`.

Both pages already had a loose prose mention of the other page; this makes the
split and the reason for it explicit and adds an inline `<Link>` rather than
just naming the page. No content duplicated — purely navigational.

Only `web/app/glossary/page.tsx` and `web/app/taxonomy/page.tsx` touched.

## Verification

`cd web && npx tsc --noEmit && npx next build` — both clean, all 65 routes
generated including `/glossary` and `/taxonomy`.
