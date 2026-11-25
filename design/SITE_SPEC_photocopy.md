# ARI3LLA site spec: the photocopy edition

**Design source of truth:** `C:\Users\User\Desktop\ari3lla-redesign\site-mock.html` ("ARI3LLA INDEX, photocopy edition"; last saved 2026-11-24 19:38).

**Rejected:** the dark "research notebook" design (pink accents) on the local branch `redesign-notebook`, commit `08ec106`. Do not merge it or build on it. That branch was never pushed. The photocopy edition is built fresh from `master`. The one thing worth taking from `08ec106` is the font file `web/app/fonts/AriellaHand-Regular.woff2`.

**Goal of this spec:** every page is a template filled from data. A new week needs no design work. Once `report_finalize.py publish-file` writes `data/reports/<date>.json`, the build makes that week's report page and updates the front page, back issues, signal files and index.

---

## 1. Audit of the mock (2026-11-25)

**Checked in a browser (1280 px wide):** all 12 routes the mock links to render, with no JavaScript errors.

**Bugs to avoid in the real site:**

1. **Unknown addresses show the wrong page instead of "not found":**
   - `#/report/2026-11-22` shows the 2026-10-04 report under the 11-22 address;
   - `#/signal/burgundy` shows the sneaker file;
   - `#/ari3/exp/exp-007` shows the "Grounded retrieval" entry;
   - `#/anything` shows the front page.

   In the site, an unknown date, signal or experiment must return the 404 page.
2. **Only one report.** The 2026-10-04 report is typed into the mock by hand, so nothing in it switches between weeks.
3. **The experiment registry stops before EXP-007, EXP-008 and EXP-009.** In the site it must be read from `experiments/`, not typed in.
4. **The headline has no data source.** "Sneakers, tailoring and denim led a week of Paris and Milan show coverage" was written for the mock, and no report field holds a headline. See §3.2.
5. **The footnote markers were placed by hand inside sentences.** The notes themselves are the report's `limitations` list, which software can place. See §3.6.
6. **The byline prints the editor's full name**, and the current site does not publish it anywhere. It belongs in site settings (`web/lib/site.ts`), never in a template, and it needs the owner's yes before it goes public.

**The real data is bigger than the mock's example:**

| | Mock (2026-10-04) | The 7 new weeks (2026-10-11 to 11-22) |
|---|---|---|
| Signals per report | 12 | 19 to 27 |
| Articles per signal | 5 to 68 | 2 to 66 |
| Editor note length | long paragraphs | 28 to 114 characters (one line) |
| Longest signal name | "Sheer and lingerie-derived dressing" | "leather jacket" |

The thin 2026-05-18 report has 2 signals, one named "Resort 2027 collections shown at public sites" (44 characters). Templates must hold all of these: very short and very long names, 2 to 30 signals, 2 to 70 articles, one-line and paragraph notes.

---

## 2. Page inventory: current site to photocopy edition

| Current route | Photocopy page | Status |
|---|---|---|
| `/` | Front page | Designed |
| `/reports/[date]` | Full report | Designed (headline rule needed, §3.2) |
| `/signals/[slug]` | Signal file | Designed (multi-week history needed, §4) |
| `/archive` | Back issues | Designed |
| none | Index of signals | Designed, **new route** `/signals` |
| `/methodology` | How it works (`#/how`) | Designed. Keep the URL `/methodology` |
| `/about` | About this paper | Designed |
| `/search` | Search | Designed |
| `/ari3` | ARI3 overview | Designed |
| `/ari3/models` | Model cards | Designed |
| `/ari3/evaluation` | Evaluation | Designed |
| `/ari3/[slug]` | Experiment entry | Designed |
| `/glossary`, `/taxonomy`, `/sources`, `/ari3/claims`, `/ari3/data`, `/ari3/decisions` | none | **Not designed.** Use the Index of signals template (a lettered or grouped list) |
| `/timeline`, `/ari3/timeline` | none | **Not designed.** Use the Back issues template (a dated list) |
| `/case-study`, `/ari3/philosophy`, `/accessibility`, `/privacy`, `/terms` | none | **Not designed.** Use the About template (one column of text) |
| 404 (`not-found.tsx`) | none | **Not designed.** Masthead plus one line and links to Latest and Back issues |
| Share image (`opengraph-image.tsx`) | none | **Not designed.** Paper background, masthead, the week and the headline |
| `/rss.xml` | none | No visual design needed. Item titles use the §3.2 headline |

---

## 3. The weekly report page (`/reports/[date]`)

Every element is filled from `data/reports/<date>.json`. Elements appear in the mock's order.

### 3.1 Masthead and dates
- Nameplate: "ARI3LLA INDEX", set in the editor's hand lettering (`AriellaHand`) once approved. Until then, the mock's serif.
- Date line: "Week of September 28 – October 4, 2026", from `collection_window.start` and `.end`. When the window spans two years, both years are shown ("Week of December 28, 2026 – January 3, 2027").
- Kicker: "THE FULL REPORT".

### 3.2 Headline (decision needed)
Every week needs one. Two options:
- **A. Generated, no new field:** "Sneaker, denim and vintage were the largest signals of the week", from the three signals with the most `evidence_items`. Always factual, never interesting.
- **B. Drafted and approved (recommended):** a new optional field `headline`. It is drafted in step 3 of the weekly report under the same voice rules (no hype, no first person, no claims beyond the evidence). The editor approves it as its own card in the "Report approval" deck. When `headline` is missing, as in older reports, the site falls back to A.

### 3.3 Standfirst, byline and "Who did what"
- **Standfirst:** "4,250 items collected from 78 sources. 20 signals kept." Filled from `items_collected` (with a thousands comma), `sources_scanned` and the number of `top_signals`.
- **Byline:** "Edited by [EDITOR NAME] · compiled with ARI3". The name comes from site settings (§1, item 6).
- **Who did what**, three rows:
  - **ARI3:** fixed text, kept in site settings.
  - **AI assistant:** the AI part of `ai_assistance`.
  - **The editor:** the editor part of `ai_assistance`.

  `ai_assistance` is the fixed wording `AI_FINAL` from `report_finalize.py`. The site splits it at the sentence that begins "The editor" and never rewrites it.

### 3.4 Summary
- `executive_summary`, in two columns on desktop and one on phones, justified with hyphenation, with a drop cap on the first letter.
- Every "<signal> (N items from M outlets)" in the text links to that signal's block (`#signal-<signal_id>`). The text checks guarantee these phrases exist.

### 3.5 "Whose coverage this is"
- One horizontal bar per entry in `source_sector_breakdown`, largest first. Labels have underscores replaced by spaces, with a capital first letter. The number sits at the right.
- Caption: "Articles collected, by the kind of outlet. X% came from editorial outlets, which have their own commercial incentives." X is the editorial count divided by the total, to one decimal.

### 3.6 Notes (footnotes)
- The `limitations` list becomes numbered notes (†1, †2 …) at the end of the page, each with "back to text".
- Markers sit only at fixed places, never inside a sentence chosen by hand:
  - one marker group after the summary's "raw source records from N outlet domains" phrase, which the text checks guarantee;
  - one after the "THE SIGNALS" heading.
- The "duplicates counted once" note always goes on the "THE SIGNALS" heading.

### 3.7 The signals
- **A contents strip** comes first: every signal name in order, as links to its block. This is new, and needed because weeks now have 19 to 27 signals.
- **One block per entry of `top_signals`,** in the order given:
  - **Kicker:** "NO. n · TYPE", from `type` with underscores as spaces, in capitals.
  - **Name:** `name`, exactly as published.
  - **Count line:** "53 articles from 12 outlets · high confidence · stable". Articles is the length of `evidence_items` and outlets is the length of `source_domains`. `long_tail` shows as "long tail".
  - **Evidence:** the `evidence` paragraph.
  - **Index note:** `index_note`, in italic.
  - **Editor's note:** in the right-hand column, under the editor's name label from site settings. The text is `human_editor_note` with its leading "Editorial view: " removed. A one-line note and a paragraph both fit. The note is never shortened.
  - **Articles:** the first 4 `evidence_items` (title linked to `url`, then "outlet · Mon D"), then a fold, "All N articles", with the rest. Non-English titles show as published. When a signal has 4 or fewer articles, the fold is hidden.
- **Each block's anchor** is `signal-<signal_id>`, so any signal in a dated report can be cited.

### 3.8 Provenance
At the foot of the page:
- review status ("Reviewed by the editor");
- the evidence snapshot SHA-256 (`evidence_snapshot_sha256`, first 12 characters, with the full value on hover);
- the archive checksum (`content_hash`) when present;
- a link to the report JSON.

### 3.9 Thin weeks and old reports
- If `thin_week_note` is set, it shows as a ruled box under the standfirst.
- Fields the photocopy design does not show stay out of sight on purpose: `repeated_keywords`, `garments`, `silhouettes`, `materials`, `colors`, `aesthetic_terms` and `cultural_references`. They feed the signal index and search.
- A report without a field the page uses shows that section empty or omits it. It must never fail the build.

---

## 4. Signal file (`/signals/[slug]`)
The mock shows one week. With eight weeks of reports, a signal file is the signal's history:
- **Header:** the name, the type, and "in N of M weekly reports".
- **Week by week:** one row per report containing the signal, newest first, with:
  - the week;
  - "N articles from M outlets";
  - the volatility label;
  - confidence;
  - the editor's note;
  - a link to the block in that report.
- **"Every article behind it, by day":** the newest week open, grouped by day. Earlier weeks are folded.
- **Notes:** as in §3.6, from the newest report.
- An unknown slug returns 404.

## 5. Other designed pages
- **Front page:** shows the newest report: masthead, date line, headline (§3.2), standfirst, the first summary paragraph, then "Latest index" (each signal name with its article count, linked). It updates itself when a report is added.
- **Back issues:** every report, newest first: the week, the headline, "N signals · N items", a link.
- **Index of signals:** every signal across all reports, A to Z under letter headings, each with the number of weeks it appeared, linked to its signal file.
- **Experiment registry** (`/ari3`, `/ari3/[slug]`): read from `experiments/*/PREREGISTRATION.md` and `RESULTS.md`, so EXP-007 to EXP-009 appear without hand edits.

## 6. Adding a new week: what has to happen
1. The weekly report flow runs as now and ends with `publish-file`.
2. The build makes the new pages. Nobody designs anything.
3. These checks must pass before the push (run them in a throwaway copy with the unpublished week, as done on 2026-11-25):
   - `npx eslint .` and `npx next build` pass;
   - `/reports/<date>` exists and shows the right week, headline and count of signal blocks;
   - every signal block has its editor's note;
   - the summary's links all resolve;
   - the front page shows the new week, and back issues lists it;
   - every signal file for that week includes it;
   - an unknown date returns 404;
   - the sharing, search and agent checks in §8.6 pass. The week has its own share image, description, structured data, a JSON link and entries in `llms.txt` and `/data/reports/index.json`.

## 7. Decisions (the owner, 2026-11-25)
1. **Headline:** B, drafted and approved. `headline` is a report field. `report_finalize.py text` requires it (one sentence, at most 100 characters, no full stop, same voice rules as the summary), and the "Report approval" deck has a "Headline" card. Reports without one fall back to A.
2. **Byline:** no personal name anywhere. The byline and note label read "Editor" (`EDITOR_LABEL` in `web/lib/site.ts`).
3. **Lettering:** no hand lettering anywhere. Only Hedvig Letters Serif and Funnel Sans, self-hosted through `next/font`.
4. **The pink branch:** deleted. `master` before the redesign is saved as `save/master-pre-photocopy-2026-11-25` on GitHub.
5. **AI crawlers:** all allowed and named in `robots.txt`. Every page has Markdown and, for reports and signals, JSON twins (§8.4).
6. **Social handle:** none yet. `twitter:site` is left out until there is one.

---

## 8. Sharing, search and agents

### 8.1 What the live site does today (checked 2026-11-25)

**Works:**
- titles, descriptions and canonical URLs on `www.ari3lla.com`;
- the home page's large share card (`summary_large_image`, 1200 × 630, with alt text);
- `robots.txt`, `sitemap.xml` and `rss.xml`;
- report JSON at `/data/reports/<date>.json`;
- `NewsArticle` structured data on reports;
- a real 404 status for unknown report dates.

**Gaps:**
1. **A shared report link shows no picture.** The report pages have no `og:image`, and their card type is the small `summary`.
2. **Report descriptions are generic** ("Weekly style signal report issued 2026-10-04."), and the structured-data headline is the summary's first sentence ("In the window from …").
3. **`/opengraph-image` is served as `application/octet-stream`.** The tag says `image/png`, but some link previewers (LinkedIn, Slack, iMessage) check the real type and drop the image.
4. **No `/llms.txt`,** no machine-readable index of reports and no `rel="alternate"` link from a report page to its JSON.
5. **`ari3lla.com` redirects to `www` with a temporary 307.** Search engines prefer a permanent 308 or 301 (a setting in Vercel's domain panel; the owner's action).

### 8.2 Every page
- **`<title>`:** the page's own title plus " | ARI3LLA INDEX", 60 characters or fewer before the suffix.
- **`<meta name="description">`:** written for that page, 70 to 160 characters, and never shared by two pages.
- **Canonical URL:** `https://www.ari3lla.com/...` with no trailing slash, the same URL the sitemap lists.
- **Share card:** `og:title`, `og:description`, `og:url`, `og:type`, `og:site_name`, `og:image` (absolute URL, 1200 × 630, PNG, with `og:image:alt`), `twitter:card = summary_large_image` and `twitter:image`.
- **Page setup:** `<html lang="en">`, the viewport meta and `theme-color` matching the paper background.
- **Semantic HTML:** one `<h1>` per page, headings in order, `<article>` for reports, `<time datetime>` on every date and descriptive link text (never "click here").
- **No content only after JavaScript runs.** Folded content (`<details>`) is in the HTML, so crawlers and agents read it.

### 8.3 Weekly report pages, generated per week
- **Title:** "Week of Nov 16–22, 2026: <headline> | ARI3LLA INDEX". When the headline is long, the title keeps the week and shortens the headline.
- **Description:** the standfirst plus the three largest signals, for example "4,250 items from 78 sources, 20 signals kept. Largest: sneaker, denim, vintage."
- **Share image, one per week:** generated at build by `app/reports/[date]/opengraph-image.tsx` in the photocopy style. It shows the nameplate, the week, the headline, the three largest signals with their counts and "ari3lla.com". The `alt` text says the same in words. No runway images, only type.
- **Structured data (JSON-LD), one `@graph` per page:**
  - **`NewsArticle`:**
    - `headline` (§3.2) and `description`;
    - `datePublished` = `report_date` and `dateModified`;
    - `author` and `publisher` (§7, item 2);
    - `isAccessibleForFree: true`, `inLanguage: "en"` and `image` (the week's share image);
    - `isBasedOn`, pointing to the `Dataset` below;
    - `about`: the signal names as `DefinedTerm`s.
  - **`Dataset`:** the report JSON:
    - `name`, `description` and `temporalCoverage` ("2026-11-16/2026-11-22");
    - `distribution` (`DataDownload`, `encodingFormat: application/json`, `contentUrl` = `/data/reports/<date>.json`);
    - `license` and `creator`;
    - `measurementTechnique`, a short line linking `/methodology`.
    - This makes each week eligible for Google Dataset Search.
  - **`BreadcrumbList`:** Home › Back issues › Week of ….
- **Machine-readable link:** `<link rel="alternate" type="application/json" href="/data/reports/<date>.json">`.
- **Feeds:** RSS items use the headline as title and the description as summary. Every page's `<head>` carries `<link rel="alternate" type="application/rss+xml">`.

### 8.4 Agents and AI tools
- **`/llms.txt`,** generated at build. Plain Markdown: what the index is and is not, how to cite a report and a signal (anchor URLs), and links to the latest report (HTML and JSON), the report index, methodology, limitations and voice rules, license and contact.
- **`/llms-full.txt`:** the latest report as plain text (summary, every signal with counts, evidence text, index note and editor's note, and the notes), plus a link to the archive index.
- **`/data/reports/index.json`:** every report with its date, window, headline, counts, the signal list, `evidence_snapshot_sha256`, and HTML and JSON URLs. Newest first.
- **`/data/signals/<slug>.json`:** a signal's week-by-week history (§4), for agents that ask "how did X move?".
- **`robots.txt`:** allows all crawlers, names the sitemap, and lists the AI crawlers explicitly so the choice is on record:
  - search and answer bots: `OAI-SearchBot`, `ChatGPT-User`, `Claude-User`, `Claude-SearchBot` and `PerplexityBot`;
  - training bots: `GPTBot`, `ClaudeBot`, `Google-Extended`, `CCBot` and `Applebot-Extended`.

  Allowing all is recommended for a public citation archive. Blocking only the training bots is the alternative (§7, item 5).
- **Stable URLs:** report dates and signal anchors never change. A corrected report keeps its URL and records the correction in the report.
- **Citations agents can follow:** every evidence item keeps its original outlet URL. Runway images are never rehosted.

### 8.5 Speed and accessibility (both count for search)
- Static pages, no client-side data fetching for content.
- Fonts self-hosted with `font-display: swap`, and the hand font preloaded only where it is used.
- No layout shift from fonts or folds.
- Text contrast at least 4.5:1 on the paper background, visible focus outlines, and skip-to-content.
- **Lighthouse targets on the report page and the front page:** Performance ≥ 90, and Accessibility, Best Practices and SEO ≥ 95.

### 8.6 Checks, automated for every new week
`web/scripts/check-seo.mjs`, run after `next build` in CI, reads the built HTML of every report and the front page, and fails the build if any of these is missing or wrong:
- title length;
- description length and uniqueness;
- the canonical URL matching the sitemap;
- `og:image` present and its file existing;
- `twitter:card = summary_large_image`;
- the JSON-LD parsing, with `NewsArticle.headline` not starting "In the window";
- the JSON alternate link resolving;
- `llms.txt` and `index.json` listing the new week.

`vercel.json` serves every `opengraph-image` path with `Content-Type: image/png`.

**Checked by hand before launch, then once a month:**
- Google Rich Results Test and the Schema.org validator on one report;
- a share-card preview (opengraph.xyz, LinkedIn Post Inspector, the Facebook Sharing Debugger);
- a real paste into iMessage and Slack;
- Lighthouse.

**The owner's account steps:**
- set the apex redirect to permanent (308) in Vercel;
- verify the site in Google Search Console and Bing Webmaster Tools;
- submit `sitemap.xml` in both.
