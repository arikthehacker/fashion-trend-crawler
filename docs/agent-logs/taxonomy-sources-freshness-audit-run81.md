# Taxonomy / Sources freshness audit (run 81)

## Scope

Read `web/app/taxonomy/page.tsx` and `web/app/sources/page.tsx` in full.
Cross-checked field-by-field against `src/taxonomy.py` (`SOURCE_SECTORS`,
`CONFIDENCE_LEVELS`, `VOLATILITY_LABELS`, `ORIGIN_CLASSIFICATIONS`,
`DOMAIN_SECTOR_MAP`), `src/crawler.py`'s `FASHION_SOURCES` (the actual crawl
seed list), `docs/ARI3LLA INDEX.txt` section 12 (origin classification
definitions), and prior precedent `docs/agent-logs/methodology-freshness-audit-run79.md`
(which last touched both these pages).

## Findings

**1. Taxonomy page was missing the entire Origin Classification dimension —
real gap, fixed.**

`taxonomy.py` defines four controlled vocabularies (source sectors, confidence,
volatility, origin classification — doc sections 11/14/15/12 respectively).
`ORIGIN_CLASSIFICATIONS` (`designer_originated`, `editorial_amplified`,
`retail_adopted`, `social_amplified`, `platform_native`, `archive_revival`,
`unclear`) is a live, populated field — `origin_classification` appears in
every report JSON in `data/reports/`, is typed and read in `web/lib/reports.ts`,
and is rendered directly on every signal card in
`web/app/reports/[date]/page.tsx` (`Origin: {signal.origin_classification}`).
Despite that, the Taxonomy page — the page whose job is specifically to define
this vocabulary — only had sections for Signal Types, Source Sectors,
Volatility, and Confidence. Origin classification was never documented there
at all. This contradicts run 79's log, which claimed "confidence/volatility/
origin-classification tables match ... exactly" — that claim was checked
against this file and found not to hold: there is no origin-classification
table on the current page, so run 79 either mis-stated or the section was
since removed; either way it's real, currently-live drift.

Fixed: added an "Origin Classification" section with all seven values, using
definitions drawn from doc section 12's own framing ("what a designer made,
what editors said it meant, what retailers sold it as, what a platform
renamed it") rather than inventing new prose. Also updated the page's intro
sentence from "four dimensions" to "five dimensions."

**2. Sources page's Runway/Editorial outlet list was frozen at the pre-run-17
seed set — real gap, fixed.**

The Sources page is the one page in the site that names specific outlets
(all other sectors list content-type categories, not named sources). Its
Runway/Editorial item list — Vogue Runway, WWD, Business of Fashion, GQ
Style, Harper's Bazaar, Elle, i-D, Dazed, Highsnobiety, Hypebeast, The Cut,
New York Times Style — maps to the *original* `DOMAIN_SECTOR_MAP` editorial
entries, most of which (wwd.com, businessoffashion.com, gq.com,
harpersbazaar.com, elle.com, i-d.co, dazeddigital.com, thecut.com,
nytimes.com) were never actually in `FASHION_SOURCES` to begin with — they're
classification vocabulary, not crawl seeds, which is a fine and intentional
distinction for this page (it documents source *types*, not a literal crawl
manifest). But the list also completely omitted every geographic-diversity
addition from runs 17-75, all of which **are** in `FASHION_SOURCES` and
`DOMAIN_SECTOR_MAP` as `editorial`: Nataal, OkayAfrica, FashionUnited India,
Tokyo Fashion (run 17), Vogue Mexico, The Express Tribune Pakistan, Savoir
Flair (run 19), Dewi Magazine (run 20), SCMP Lifestyle (run 39), RUNWAY
Magazine, Style Rave (run 56), FFW Brazil (run 73), Vogue Arabia (run 75).
That's 13 real, currently-crawled editorial sources — including the three
runs 73/75/78 specifically flagged for this audit (`ffw.com.br`,
`voguearabia.com`) — with zero representation on the one page whose purpose
is to name sources. This is exactly the English-language-Western-editorial
bias pattern the project's own run-16/17 bias audit found and fixed in the
crawl seed list, just never propagated to this page's copy.

Fixed: added all 13 outlets to the Runway/Editorial items list, and added one
clause to the sector definition noting the list's geographic broadening
(without over-claiming — phrased as description of the existing list, not a
new promise).

**3. Institutional/Historical item list skewed entirely toward archive/museum
framing, omitting governing bodies and trade institutes that make up more
than half of `DOMAIN_SECTOR_MAP`'s actual institutional entries — real gap,
fixed.**

`DOMAIN_SECTOR_MAP`'s `institutional` sector has six domains:
`fitnyc.edu`, `metmuseum.org`, `vam.ac.uk` (archive/museum/academic — matches
the page's existing items), plus `cfda.com`, `kci.or.jp`,
`britishfashioncouncil.co.uk`, `fhcm.paris` (added run 70), and
`inexmoda.org.co` (added run 74) — governing bodies and trade/export
institutes that coordinate fashion weeks and publish industry trend
research, a materially different thing from a museum collection or academic
paper. `inexmoda.org.co` (flagged for this audit) falls squarely in this
second, undocumented category. The page's item list ("FIT resources, Museum
collections, Fashion archives, Costume history databases, Academic papers,
Old runway archives, Library collections") had no entry that would describe
CFDA, the British Fashion Council, FHCM, or Inexmoda at all.

Fixed: added "Fashion week governing bodies" and "National fashion
trade/export institutes" to the item list, and broadened the sector
definition sentence to mention them alongside the existing archival/academic
framing.

## Checked and found accurate / not changed

- **Confidence Levels table** (`taxonomy/page.tsx`): Low/Medium/High/Archival
  with the "single noisy source" / "two or more source types" / "multiple
  distinct sectors" / "recurring across time periods" definitions match
  `CONFIDENCE_LEVELS = ["low", "medium", "high", "archival"]` exactly. No
  drift, no change.
- **Volatility Labels table**: all 11 labels (Stable, Emerging, Seasonal,
  Volatile, Flash, Microtrend, Recurring, Revival, Long-tail, Saturated,
  Declining) match `VOLATILITY_LABELS` exactly, same order, same count. No
  drift, no change.
- **Source Sectors table on Taxonomy page**: nine listed sectors
  (Designer-origin, Runway/editorial combined, Retail/commerce,
  Social/platform, Visual archive/search, Independent criticism,
  Institutional/historical, Street/user-generated, Resale/secondhand) match
  `SOURCE_SECTORS`'s ten entries with `runway`+`editorial` intentionally
  combined into one row — same longstanding abstraction run 79 already
  confirmed, re-verified here and still correct. No change.
- **Sources page's sector list**: same nine sectors, same intentional
  runway/editorial combination, consistent with the Taxonomy page. No change.
- **Sources page's Retail/Commerce, Social/Platform, Visual Archive/Search,
  Independent Criticism, Street/User-Generated, Resale/Secondhand
  sections**: these list generic content-type categories rather than named
  outlets/domains (e.g. "Product titles," "TikTok captions," "Reverse image
  and visual search platforms"), so there was no specific-domain claim to go
  stale — no drift found, no change made.
- **Signal Types list** (`taxonomy/page.tsx`): cross-checked against
  `report_schema.py` — there is no coded `SIGNAL_TYPE` enum in the schema
  (signal type is free text in practice), so this list is prose-level
  taxonomy documentation with nothing in source code to drift against. Left
  as-is.

## Fix applied

Edited `web/app/taxonomy/page.tsx`:
- Added a new `originClassification` array (7 entries: Designer-originated,
  Editorial-amplified, Retail-adopted, Social-amplified, Platform-native,
  Archive revival, Unclear) with definitions drawn from doc section 12.
- Added a new "Origin Classification" section (with a short framing
  paragraph) after "Confidence Levels."
- Changed the intro paragraph from "four dimensions" to "five dimensions."

Edited `web/app/sources/page.tsx`:
- Added 13 outlet names (Nataal, OkayAfrica, FashionUnited India, Tokyo
  Fashion, Vogue Mexico, The Express Tribune (Pakistan), Savoir Flair, Dewi
  Magazine, SCMP Lifestyle, RUNWAY Magazine, Style Rave, FFW (Brazil), Vogue
  Arabia) to the Runway/Editorial items list; added one clause to that
  sector's definition.
- Added "Fashion week governing bodies" and "National fashion trade/export
  institutes" to the Institutional/Historical items list; broadened that
  sector's definition sentence accordingly.

No changes to `methodology/page.tsx`, `about/page.tsx`, `case-study/page.tsx`,
`src/taxonomy.py`, `src/report_schema.py`, `TODO.md`, `CHANGELOG.md`, or any
`data/reports/*.json` file.

## Validation

```
cd web && npx tsc --noEmit   # clean
npx eslint .                 # clean
npm run build                # succeeded, 176 pages incl. 74 reports, 87 /signals/[slug] paths, pagefind indexed 176 pages
```

No `.env` or secret values were read, logged, or printed during this audit.
