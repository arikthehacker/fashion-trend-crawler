# Glossary definitions curated (run 40)

Follow-up to run 39, which cut the build-time "no DEFINITIONS entry" warning
count from ~130 to 19 by filtering out narrative sentences before the
`DEFINITIONS` lookup. This run wrote real definitions for those remaining 19
warnings (14 unique terms; some repeated across multiple report dates) in
`web/app/glossary/page.tsx`'s `DEFINITIONS` object only. No extraction/filter
logic was touched.

## Terms added

- 1990s minimalism revival
- 1970s 'boho' revival styling
- Resale/secondhand retail growth
- Coastal-cowgirl styling evolution
- 2026 FIFA World Cup
- Oversized 'bug-eye' sunglasses
- Utility-detailed belts
- Copenhagen Fashion Week SS27
- Collina Strada international guest slot
- CFDA September 2026 NYFW schedule
- Pre-fashion-week anticipation
- CFDA fur-free policy
- CFDA/Vogue Fashion Fund 2026
- Rachel Comey 25th anniversary
- Conner Ives NYFW debut
- Magda Butrym NYFW debut

Each entry is a factual, wire-service-voice description of what the term
refers to (event, policy, market trend, or styling pattern) rather than
commentary on its significance — e.g. "CFDA fur-free policy" describes it as
a policy position on fur use from the CFDA, not an editorial judgment about
it.

## Verification

`npx tsc --noEmit`: no errors.

`npx next build`: exit 0; `grep -i "no DEFINITIONS entry"` on the build
output returned zero lines — all 19 warnings present at the start of this
run are resolved. (Per the task instructions, any new warnings from reports
added concurrently by other agents after this run started would be
acceptable to remain, but none appeared.)
