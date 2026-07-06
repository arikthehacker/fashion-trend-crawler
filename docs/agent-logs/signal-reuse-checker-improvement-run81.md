# Run 81: signal-reuse-claim checker false-positive reduction

## Task

`src/check_signal_reuse_claims.py` is a heuristic (non-gating) checker that flags
when a report's prose names a prior `signal_id` in a way that reads like a
reuse/continuation claim, but that `signal_id` doesn't actually appear in the
report's own `top_signals`. It had accumulated 5 confirmed false positives:
2026-09-14, 2026-09-28, 2026-10-05, 2027-06-28, 2027-10-11.

## Investigation

Ran `python src/check_signal_reuse_claims.py --all` (before change) and pulled
the full text of all 5 flagged prose fields directly from the report JSONs
(read-only, no secrets involved). All 5 follow the same shape: a
`reuse`/`continu*`-matching word appears somewhere in the field, and a known
long-running `signal_id` is named elsewhere in the *same field*, but the two
are unrelated -- the sid is named either (a) to explicitly say it is *not*
being carried forward this window, or (b) as precedent/context for an
unrelated origin-classification or transition decision. The root cause is
that the original check only required "reuse word anywhere in field" AND
"known sid anywhere in same field" with no proximity/negation check at all.

Specific phrases found immediately adjacent to the named sid in each case:
- 2026-09-14: "...is **not carried forward** this window..."
- 2026-09-28 / 2026-10-05: "...so it is **not re-asserted**..."
- 2027-06-28: "...the **precedent set for** wales-bonner-hermes-debut..."
- 2027-10-11: "...**rather than merged into** margiela-raw-edge-tailoring-preview's evidence field..."

Sentence-level proximity alone (splitting on `.`) does *not* separate all 5
cases from the reuse-word match, since several are single run-on sentences
containing both the reuse word and the negation clause. What reliably
distinguishes all 5 is a short, literal negation/precedent phrase occurring
within a small character window around the named sid.

## Change made

Added `NEGATION_EXCLUSION_PHRASES` (a short literal tuple: "not carried
forward", "not re-asserted", "not reused", "not being reused", "precedent
set for", "rather than merged into", "not merged into") and a
`NEGATION_PROXIMITY_WINDOW` (220 chars) in `src/check_signal_reuse_claims.py`.
When a named sid is found in a reuse-flagged field, the checker now looks at
the text within 220 characters before/after that sid mention; if one of the
exclusion phrases appears in that window, the mismatch is treated as an
explained non-reuse/precedent reference and not flagged. If no exclusion
phrase is nearby, the mismatch is still flagged exactly as before -- this is
intentionally a narrow, literal, proximity-scoped list, not general negation
detection, to avoid masking a real future bug.

## Validation

- Before: `python src/check_signal_reuse_claims.py --all` -> 5 warnings
  (the 5 known false positives listed above, verified by hand against the
  report JSON text).
- After: `python src/check_signal_reuse_claims.py --all` -> 0 warnings.
  Manually re-read all 5 previously-flagged texts against the new exclusion
  logic -- each is excluded via the phrase adjacent to the named sid, not by
  any accidental over-broad match.
- Recall check: simulated the original run-57/58-style bug (prose says
  "Reuses the signal_id X from the prior report without changes" with no
  negation phrase nearby, X not in top_signals) against `check_report()`
  directly -- still correctly flagged. Confirms the exclusion is scoped
  tightly enough to not hide a genuine reuse-claim/artifact mismatch.

## Decision

Change applied: added proximity-scoped negation-phrase exclusion list to
`src/check_signal_reuse_claims.py`. No other files touched. Exit code
behavior (always 0, informational) and CLI usage (`--all` flag) unchanged.
