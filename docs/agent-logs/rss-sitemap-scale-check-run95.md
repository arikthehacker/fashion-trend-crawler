# RSS + Sitemap Scale Re-Verification (Run 95)

Follow-up to Run 86 (robots/crawl-budget audit) and Run 78 (RSS 50-item cap). Archive has grown
to 87 reports since Run 86; re-verifying both systems hold at the larger scale.

## 1. Fresh build

No concurrent node processes were running. Ran:

```
cd web && rm -rf .next out && npm run build
```

Build succeeded. Static page generation log reported **210 total generated paths** in the
build's route table:

- 10 static routes (`/`, `/archive`, `/methodology`, `/taxonomy`, `/sources`, `/about`,
  `/case-study`, `/timeline`, `/glossary`, `/search`)
- 87 `/reports/[date]` pages
- 106 `/signals/[slug]` pages
- Plus non-sitemap utility routes: `/_not-found`, `/icon`, `/robots.txt`, `/rss.xml`,
  `/sitemap.xml` (7 extra, non-content routes not expected in the sitemap)

Pagefind postbuild indexed 205 HTML files (210 routes minus the 5 non-HTML/utility
outputs — robots.txt, rss.xml, sitemap.xml, icon, and one other non-indexable route).

## 2. Sitemap completeness check

Counted actual `<loc>` entries in the built `out/sitemap.xml` and cross-checked against
source data, not just "it built without errors":

| Check | Count |
|---|---|
| `<loc>` entries in sitemap.xml | 203 |
| Static routes in sitemap | 10 |
| `/reports/*` URLs in sitemap (unique) | 87 |
| `data/reports/*.json` files on disk | 87 |
| `/signals/*` URLs in sitemap (unique) | 106 |
| Unique `signal_id` values across all 87 report JSON files (computed directly, not via `getAllSignalSlugs()`) | 106 |

10 + 87 + 106 = 203, matching the sitemap exactly. Every report and every distinct signal_id
has a corresponding sitemap entry — no missing pages, no stale/orphaned entries either.
`web/app/sitemap.ts` logic (static + `getAllReportDates()` + `getAllSignalSlugs()`) is confirmed
correct at current scale.

## 3. RSS feed check

- `<item>` count in `out/rss.xml`: **50** (cap from Run 78 is still holding exactly, not "50 or
  more" — confirmed via exact grep count, not an inequality check).
- pubDate format: RFC-822 as required by the RSS spec, e.g.
  `Mon, 28 Feb 2028 00:00:00 GMT` — well-formed on all sampled entries.
- Spot-checked the 3 most recent items against source data:

  | RSS item link | report JSON | report_date field | pubDate |
  |---|---|---|---|
  | /reports/2028-02-28 | 2028-02-28.json | 2028-02-28 | Mon, 28 Feb 2028 |
  | /reports/2028-02-21 | 2028-02-21.json | 2028-02-21 | Mon, 21 Feb 2028 |
  | /reports/2028-02-14 | 2028-02-14.json | 2028-02-14 | Mon, 14 Feb 2028 |

  All three pubDate values trace directly to the real `report_date` field in the
  corresponding report JSON — no drift, no hardcoded/stale dates.

## 4. Crawl-budget / sitemap-size sanity math

Run 86 already established the relevant thresholds; this is just a scale re-check of the same
math, not new research:

- Google's single-sitemap limit: 50,000 URLs / 50MB uncompressed.
- Current sitemap: 203 URLs — **~0.4% of the 50k limit**.
- Total build routes: 210 — trivial for any crawler's budget; no pagination/sitemap-index
  needed at this scale, and won't be needed for a very long time (archive would need to grow
  ~250x from here to approach the single-sitemap limit).

## Conclusion

Both systems remain healthy at current scale (87 reports / 210 routes / 203 sitemap URLs):

- Sitemap: complete, every report and every unique signal represented, verified by direct count
  cross-check against source JSON rather than trusting a clean build.
- RSS: cap holds at exactly 50 items, pubDate values are well-formed RFC-822 and correctly
  derived from real `report_date` fields on all spot-checked entries.
- Crawl-budget math from Run 86 still comfortably holds; no action needed.

No gaps found. No code changes made.
