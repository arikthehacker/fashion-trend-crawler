# Manual-sampling workflow exercised a third time (2026-07-06)

Third exercise of the compliant manual social-sampling path (doc §31) — prior
two runs (`manual-sample-exercised.md`, `-2.md`) were both Pinterest. This run
attempted TikTok diversification first.

**TikTok attempt**: re-checked TikTok's Research API eligibility
(developers.tiktok.com/doc/research-api-faq) — still gated to verified
academic/non-profit institutions with an ethics-review requirement, same
conclusion as run 8's original research, no change. Rather than falling back
to Pinterest immediately, used TikTok's own public, non-login-walled hashtag
page (`https://www.tiktok.com/tag/maxxing`) as the observation point — this is
viewing a public page, not scraping, and is a genuine (if narrow)
diversification: the primary artifact this time is a TikTok surface, not a
Pinterest newsroom page.

**Signal**: "funmaxxing" maximalist-play aesthetic (icy blue/candy pink
palettes, tassels/fringe, 80s technical sportswear), observed via the public
`#maxxing` TikTok hashtag page, with secondary dating/description from nss
magazine's ["Funmaxxing is taking over fashion, marketing and
TikTok"](https://www.nssmag.com/en/fashion/44857/funmaxxing-fashion-marketing-trend-2026).
Appended to `data/reports/2026-11-09.json` (chosen per instruction to avoid
`2026-11-16.json`, being written concurrently by another agent; 2026-11-09 had
no manually-sampled social signal yet).

Tagged `source_sectors: ["social"]`, `confidence: "low"`,
`volatility: "emerging"`, `origin_classification: "platform_native"`,
`source_corroboration_count: 1`, `signal_id: "funmaxxing-maximalist-play-aesthetic"`.

**`human_editor_note` (real judgment call)**: declines nss magazine's own
framing of funmaxxing as a sweeping generational-mood thesis ("a comprehensive
picture of the historical moment we are living through as humanity") as
trend-piece overreach, and logs only the narrower, checkable claim (a
maximalist aesthetic cluster circulating under a hashtag). Flags that, without
an approved TikTok dataset, view/post counts on the hashtag page aren't
reliably readable the way Pinterest publishes its own search-index
percentages, so volume is "unknown" rather than estimated — a real
asymmetry between the two platforms' compliant observation paths. Recommends
holding at low confidence pending a second-platform or retail/editorial
sighting.

Also updated `source_sector_breakdown` (`social: 1`), `items_collected`
(1 → 2), `sources_scanned` (11 → 12) on the report to reflect the addition.

**Verification**: `python -m py_compile src/*.py` passed.
`python src/validate_all_reports.py` passed for all 21 files in
`data/reports/` (including the concurrently-added `2026-11-16.json`, untouched
by this task) after the append and `content_hash` recomputation via
`save_report(revision_reason=..., corrected_at="2026-07-06")`.

**Sources**: [TikTok Research API FAQ](https://developers.tiktok.com/doc/research-api-faq) (confirms academic-only gate, unchanged since run 8), [TikTok #maxxing hashtag page](https://www.tiktok.com/tag/maxxing), [nss magazine: Funmaxxing is taking over fashion, marketing and TikTok](https://www.nssmag.com/en/fashion/44857/funmaxxing-fashion-marketing-trend-2026)
