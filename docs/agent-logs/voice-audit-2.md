# Voice Audit 2

Full re-read of every `web/app/**/*.tsx` page (layout, home, archive, timeline,
signals/[slug], reports/[date], methodology, taxonomy, sources, about,
case-study) against doc §2 voice rules, following 9 loop runs of new copy.

## Findings

Nearly all pages are compliant: no first person, no "must-have"/"obsessed"/
"this season is all about," no shopping recommendations, no hype language,
uncertainty stated plainly (confidence/volatility/limitations sections), and
social signals consistently framed as high-noise-by-default rather than
upgraded by editorial co-coverage (methodology.tsx "How Social and Platform
Signals Are Handled," "How Editorial Authority Is Treated"). The newer
additions — timeline, signals/[slug], Corrections/Editorial-Independence/AI
Involvement sections on methodology and about, and the citation-line/checksum
block on reports/[date] — all use the same plain report-register phrasing
("preserved as recorded," "no ranking or trend projection implied," "not
silently edited") and read consistently with the rest of the site.

One tonal inconsistency found and fixed: `web/app/about/page.tsx`'s closing
lines — "Style should conform to how people want to live, not the other way
around." / "ARI3LLA INDEX does not tell readers how to live. It documents the
systems that try to." — were manifesto/aphorism voice, an outlier against the
plain declarative register used everywhere else on the site. Not a literal
banned-word violation, but stylistically adjacent to the "sounds like a
stylist" failure mode the rules call out. Replaced with plain register:
"ARI3LLA INDEX does not issue guidance on how readers should dress or live."
/ "It documents the sources, incentives, and language that shape style
discourse."

No other changes made.

## Verification

`cd web && npx tsc --noEmit && npx next build` — both pass clean, all 36
pages generated successfully.
