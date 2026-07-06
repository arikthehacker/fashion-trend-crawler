# Review-claim accuracy audit (run 51)

Scope: audit whether site copy overclaims genuine human review, given run 50's gap
analysis finding that `reviewed_by` values (`"loop-consolidation"`,
`"websearch-run-thin-week"`, etc.) are agent self-attribution, not a named human
editor's sign-off. Not in scope: building real human review — that remains a
flagged-for-human decision.

## Finding: yes, three places overclaimed

1. **`web/app/methodology/page.tsx`** ("AI Involvement" section) stated flatly: "A human
   reviews AI-assisted output before publication, deciding what a cluster of terms means
   culturally... " — presented as settled fact, no hedge. False in practice: the same
   automated process drafts and "reviews."
2. **`web/app/about/page.tsx`** had near-identical wording: "A human reviews that output,
   makes the interpretive classification calls..."
3. **`web/app/reports/[date]/page.tsx`** rendered the per-report byline as literally
   `human-reviewed by ${report.reviewed_by}` — e.g. "human-reviewed by
   loop-consolidation," directly asserting a human reviewer using an agent-process
   string as if it were a name. Also a second occurrence in the report's Notes section
   ("Reviewed, {reviewed_by}").

## Fix applied (copy-only, no schema/process change)

Rewrote all four spots to say the report is "reviewed against the project's editorial
guidelines" by the automated process, and explicitly disclosed that this review is
"currently performed by the same automated process that drafts the report, not by a
separate named human editor" (methodology and about pages carry the full disclosure;
the report byline/notes now show `reviewed against editorial guidelines (process:
<reviewed_by>)` instead of naming a process string as a human).

Files touched:
- `web/app/methodology/page.tsx`
- `web/app/about/page.tsx`
- `web/app/reports/[date]/page.tsx`

## Verification

`cd web && npx tsc --noEmit` — clean, no errors.

## Not touched

The underlying gap itself (no real human reviewer exists in the loop) is unchanged and
remains the human-decision item from run 50's gap analysis — this run only made the
site's own claims match that reality, it did not manufacture human oversight.
