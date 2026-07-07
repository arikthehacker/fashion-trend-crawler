# Bias-audit run 16 — coordinator summary

First actual bias-audit pass (prior run only identified that no such practice
existed). No code changed — audit and documentation only, logged as a dated entry in
`docs/PROMPT_CHANGELOG.md`.

Reviewed: `src/summarize.py` `build_prompt()` in full, `src/crawler.py`
`FASHION_SOURCES`, `src/taxonomy.py` (`SOURCE_SECTORS`, `DOMAIN_SECTOR_MAP`,
`classify_source()`), and `report_schema.py` `derive_confidence()` /
`HIGH_RELIABILITY_SECTORS`.

**(a) Source list skew — real finding.** All three current seeds (`vogue.com`,
`whowhatwear.com`, `hypebeast.com`) are English-language, Western editorial/retail
outlets. No non-Western regional discourse is seeded, and BFS crawling from these
seeds can't self-correct that. Recommended noting this as a documented scope
limitation and prioritizing non-Western sources in the next source-expansion pass.

**(b) Classification vocabulary — no issue.** `SOURCE_SECTORS` naming is descriptive,
not ranked, and the prompt already contains explicit anti-gatekeeping instructions
("do not treat editorial sources as neutral confirmation"). No change recommended.

**(c) `derive_confidence()` — real finding.** `HIGH_RELIABILITY_SECTORS` (editorial,
designer_origin, institutional) gives single-mention signals in those sectors a
"medium" floor that `street_ugc`/`social`/`independent_criticism`/`resale`/
`visual_archive` can never reach on one mention. This re-introduces, in the
confidence math, the same source-type hierarchy the prompt text works to avoid.
Recommended: reframe the constant's docs as a noise-rate heuristic rather than a
legitimacy ranking, and consider adding `independent_criticism` (curated,
named-author, comparable noise profile to editorial) to the single-mention gate —
its exclusion looks like an oversight, not a deliberate design choice. Left
`street_ugc`/`social`/`resale` excluded as reasonable.

Full findings with line-level detail: `docs/PROMPT_CHANGELOG.md`, "First bias-audit
pass (run 16)" section (appended, existing entries untouched).
