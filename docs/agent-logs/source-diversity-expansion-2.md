# Source diversity expansion, round 2 (run 19)

Follow-up to run 17/18's own caveat: nataal.com, okayafrica.com, and
fashionunited.in are diaspora- or Western-audience-adjacent, not
local-for-local. This pass targeted genuinely local-for-local outlets in
Latin America, South Asia, Middle East, and Southeast Asia. Only
`src/crawler.py` and `src/taxonomy.py` touched.

## Sources added

- **vogue.mx** (Vogue México y Latinoamérica) — Condé Nast's Mexico/LatAm
  edition, published in Spanish for a Mexican/Latin American readership, not
  a US/UK edition repackaged. Crawled cleanly: root + 8 sub-sections
  returned 6-63 headlines each; one `/search` path correctly blocked by its
  own robots.txt.
- **tribune.com.pk** (The Express Tribune, Pakistan) — Pakistani English-
  language daily newspaper (Lakson Group), `/fashion` section, written for a
  domestic Pakistani audience. Crawled cleanly: 21-110 headlines per page.
- **savoirflair.com** — Dubai-founded (2009), independently owned digital
  magazine covering Middle Eastern fashion/beauty/culture, bilingual
  Arabic/English, editorially centered on the region rather than a Western
  publisher's regional bureau. Crawled cleanly: real headlines (4-11 per
  page) from article pages; the bare homepage yielded 0 extracted headlines
  (likely a markup/extraction-pattern mismatch, not a block — `robots.txt`
  and the root page both returned normal 200s under the crawler's own UA),
  so recall from this source will lean on its article/section pages.

## Candidate rejected: vogue.ph (Vogue Philippines)

Initially added for Southeast Asia coverage (locally staffed, Filipino
editorial team, launched 2022 for a Filipino readership — genuinely
local-for-local by editorial structure). Removed after testing found it is
**not actually crawlable**: `curl` with the crawler's own UA got a normal
200, but Python's `requests` (same UA, same headers) got a `403` serving a
Cloudflare "Just a moment..." JS-challenge page. This is a different failure
mode than run 18's tokyofashion.com finding (that was a robots.txt-fetch UA
mismatch, fixable in code) — this is an active bot challenge on the content
pages themselves, which a plain `requests`-based crawler cannot pass. No
Southeast Asian replacement was substituted this round; this remains open.

## Verification

Ran `python src/crawler.py <all three URLs>` for real — all three returned
genuine, current headlines (Paris Haute Couture Week coverage, LatAm beauty
drops, Dubai culture guides), not boilerplate. `python -m py_compile
src/*.py` passes. Scratch `trends_raw.json` deleted after verification.

## What this does and doesn't fix

This adds 3 of 4 candidate regions (Latin America, South Asia, Middle East)
with outlets edited for a local/regional audience rather than diaspora or
Western readers — a real improvement on run 17's set, which was honest
about not having done this. It does **not** close the gap: Southeast Asia
is still unaddressed (best candidate found, vogue.ph, is technically
uncrawlable by this stack), all added sources remain English-or-Spanish and
still Condé-Nast/legacy-media-adjacent in two of three cases (vogue.mx,
tribune.com.pk is independent but mainstream), and BFS from these seeds
still depends on what they happen to link to in a given week. True
non-English-language extraction and smaller/independent (non-legacy-media)
local outlets remain future work, as does finding a crawlable Southeast
Asian source.
