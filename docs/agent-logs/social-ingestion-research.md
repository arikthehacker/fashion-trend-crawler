# Social ingestion research (TikTok/Pinterest) — compliant paths only

Per doc §31: no aggressive/ToS-violating scraping. Options researched below.

## 1. TikTok Research API
Official endpoint: [TikTok Research Tools](https://developers.tiktok.com/products/research-api/), [FAQ](https://developers.tiktok.com/doc/research-api-faq). Restricted to verified academic/non-profit institutions in the US, EEA, UK, Switzerland, and Brazil under DSA vetting; requires a formal research proposal, ethics review evidence, and institutional affiliation. Approval takes ~30 days. **Commercial use is explicitly prohibited.** Rate limit: 1,000 requests/day, up to 100,000 records/day. Exposes hashtag/topic performance and video metadata, not full scraping. Sourced also via [SAGE eval of TikTok Research API bias](https://journals.sagepub.com/doi/10.1177/08944393251413277).
- **Verdict**: Not viable for this project — no institutional academic affiliation, and it's a personal archival project, not a university research program.

## 2. Pinterest official API
[Pinterest Trends API docs](https://developers.pinterest.com/docs/api-features/trends/), [trending keywords endpoint](https://developers.pinterest.com/docs/api/v5/trending_keywords-list/). Free/dev-tier access via standard Pinterest API app registration. Limitations: max 50 results per query, **today's date only** (no historical backfill), scoped by region/category filters.
- **Verdict**: Usable but thin — good for a lightweight "today's trending keywords" snapshot, not deep historical trend data. Reasonable low-effort integration later.

## 3. Approved third-party datasets
- **DeepFashion** (academic, image/attribute focused, not live trend signal) — [Innovatiana overview](https://www.innovatiana.com/en/datasets/deepfashion).
- **StreetStyle (Instagram-derived academic dataset)** and similar (Lookbook, Insta NYFW-19) referenced in [arXiv fashion trend forecasting survey](https://arxiv.org/pdf/2105.03299).
- **Heuritech** — commercial licensed data provider (~500M Instagram/Weibo posts), paid enterprise product — [heuritech.com/fashion-data](https://heuritech.com/fashion-data/).
- Broader catalog: [Datarade fashion datasets](https://datarade.ai/search/products/fashion-datasets).
- **Verdict**: Academic datasets are static/historical, not live signal feeds — good for methodology validation, not ongoing archival. Heuritech-style providers are commercial-grade and priced for brands, out of scope for a small project.

## 4. Manual sampling (fallback, no API)
WGSN's public [methodology page](https://www.wgsn.com/en/methodology) describes triangulating ~2,800 third-party sources (institutional, NGO, media) with expert human review rather than raw scraping — i.e., curated observation + citation, not automated pulls. No documented "manual sampling script," but the pattern validates a human-curated-links approach as a legitimate industry practice, not just a stopgap.
- **Verdict**: This is the actual precedent for doc §31's "manually curated samples" principle.

## Recommendation
1. **Immediate**: manual sampling — a human (or a lightweight intake form) logs specific TikTok/Pinterest post URLs + observed metadata (caption, hashtags, approx. engagement, date) as source citations. Zero API risk, matches WGSN-style precedent, matches project scale.
2. **Later**: integrate Pinterest's official Trends API for a daily trending-keywords snapshot (free, simple, no academic gate) — accept the "today only" limitation by storing a daily archive ourselves.
3. **Not pursued**: TikTok Research API (blocked by academic-institution requirement) and commercial datasets (Heuritech, cost-prohibitive for this project's scale).
