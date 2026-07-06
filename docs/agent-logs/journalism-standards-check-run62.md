# Reading-level / plain-language accessibility check (run 62)

## Topic and why
Run 44 spot-checked readability by eye ("dense but intentional") without numbers.
This run computes actual Flesch Reading Ease / Flesch-Kincaid Grade scores to verify
that call for real, against WCAG 2.2's **3.1.5 Reading Level** success criterion
(AAA): if content requires reading ability more advanced than lower-secondary
level (~grade 9) and no simpler alternative exists, that's a documented gap.

## Method
Wrote a small standalone Flesch/Flesch-Kincaid calculator (not committed — scratch
script) and ran it against real site copy:

| Text | Flesch Ease | Grade level |
|---|---|---|
| Homepage tagline | 25.4 | 13.9 |
| Methodology intro paragraph | 41.8 | 10.7 |
| Latest report (2027-07-05) executive summary | 31.5 | 17.1 |
| Latest report limitations text | 47.1 | 10.8 |

Ease scores in the 0-50 range read as "difficult" to "very difficult" (college/
graduate level) on the standard Flesch scale; grade levels of 11-17 are well above
WCAG 3.1.5's lower-secondary (~grade 9) bar.

## Finding
This is a real, measurable gap against WCAG 3.1.5 AAA. It is not, however, an
oversight: SKILL.md's voice rules are explicit that copy must read as report/
wire-service prose — precise terminology (source-sector names, taxonomy terms,
proper nouns like "creative-director-level debuts," compound classification
language) is the point, not an accident, and dumbing it down would break the
project's core no-hype, no-influencer-voice mandate that has been enforced across
multiple prior runs (voice-audit.md, voice-audit-2.md, prompt-style-crosscheck.md).

Two mitigating facts:
1. **3.1.5 is AAA, not AA.** The site is not claiming AAA conformance anywhere in
   its accessibility-adjacent work (skip-link, heading-hierarchy, dark-mode runs
   all targeted AA-level fixes). No existing claim is contradicted.
2. The **executive_summary field itself already functions as the plain-language
   entry point** relative to the full report body (garments/silhouettes/materials/
   colors/aesthetic_terms breakdown) — it is denser than ideal but it is the
   simplification layer that exists, not raw data dumped with no summary at all.

## Decision: no code change
Forcing a simpler rewrite of the executive summary or methodology copy would
trade a real but AAA-only accessibility gap for a violation of an explicit,
repeatedly-enforced project rule (voice register). That's not a good trade for a
project whose whole differentiator is precise, non-hyped classification language.
Reporting this honestly rather than manufacturing a fix: **the site does not meet
WCAG 3.1.5 (AAA) and that is an accepted, documented tradeoff, not an unknown
gap** — logging the actual numbers here so a future run doesn't have to
re-derive them from scratch, and so if the project's voice rules ever loosen,
this is the concrete baseline to check improvement against.

## Verification
Read-only research task — no files under `web/` or `src/` were modified, so
`npx tsc --noEmit` was not run.
