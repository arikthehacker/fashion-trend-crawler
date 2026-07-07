# Glossary voice audit — run 91

## Scope
Full read-through of every entry in the `DEFINITIONS` map in
`web/app/glossary/page.tsx` (146 entries total, from `1970s boho` through
`bias-cut column dress`), checked against doc section 2's voice rules: no
first person, no hype language ("must-have," "obsessed," "iconic,"
"stunning," etc.), no shopping-recommendation phrasing, wire-service/
encyclopedic tone throughout. This is the first full-map audit since run 78's
periodic check; roughly 15+ entries have been added since then (designer
transitions, tennis/Wimbledon cluster, resort 2028 silhouette cluster,
Haute Couture SS28 entries, etc.).

## Method
Read all 146 entries line by line. Checked each for:
- First-person language — none found.
- Hype/superlative adjectives (must-have, obsessed, iconic, stunning, must,
  can't-miss, essential, chic in a prescriptive sense, etc.) — none found.
- Shopping-recommendation phrasing ("shop the look," "add to cart," "worth
  buying," "invest in") — none found.
- Subtler enthusiast/fan-blog tone (rhetorical excitement, unearned
  certainty, marketing-adjacent framing even without a red-flag word) —
  checked each entry's verbs and framing; all use neutral observational
  verbs ("cited as," "observed," "tracked as," "associated with,"
  "distinct from," "referenced when") consistent with the rest of the
  glossary's established register.

## Result
No violations found. All 146 entries — including the newer designer-
transition entries (Demna/Gucci, Glenn Martens/Margiela, Matthieu
Blazy/Chanel), the tennis/Wimbledon cluster, the resort 2028 silhouette
cluster (obi-sash cocoon coat, puffer-shell skirt, etc.), and the Haute
Couture SS28 entries (bias-cut column dress) — read in clean wire-service/
encyclopedic voice consistent with the rest of the glossary.

This is a genuine clean result, not a forced one: per the project's own
audit history (e.g. run 62's check_signal_reuse_claims sweep), a clean
full-archive pass is a valid and expected outcome, not evidence the check
wasn't thorough.

## Changes made
None. `web/app/glossary/page.tsx` was not modified. No other files touched.

## Validation
No code changes were made, so `tsc`/`eslint`/`next build` were not required
to re-verify a diff. Not run for this audit since there is nothing to
validate.
