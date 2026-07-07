# Gap analysis — 60-run milestone retrospective

Fresh check against run 50's flagged finding, 10 runs later. Scope: honest accounting,
not a fix pass.

## 1. Crawler-pipeline ratio: unchanged in substance, and now worse as a proportion of new work

Still only runs 8 and 15 ever produced an archived report from a genuine `crawler.py` →
`summarize.py` execution. Reports added in runs 51-59 (2027-04-27 through 2027-06-21,
now 52 total) are WebSearch-researched, same as before. Runs 54-55's crawler work
(adding `dieworkwear.com` to `FASHION_SOURCES`, fixing the Brotli decoding bug) was
real and valuable, but it verified the crawler's *health*, not its *use* — no report was
produced by actually running it end to end and folding the output into `data/reports/`.
So the ratio has drifted from ~2/43 to ~2/52: the denominator keeps growing on the
WebSearch path while the numerator sits still. Ten runs after this was named a
significant structural finding, the underlying practice hasn't changed — only the
site's honesty *about* the practice has (run 51 rewrote the reviewed-by/methodology
copy so it no longer overclaims). That's a real, worthwhile fix, but it resolves the
transparency half of the gap, not the pipeline half. `reviewed_by` is now correctly
left blank (verified in 2027-06-07/06-14/06-21) rather than a false attribution string
— an honest downgrade, not a solve.

## 2. Self-correction ratio: trending toward more bug-fixing-of-prior-runs, not less

Reviewing changelog entries 50-59's primary items:

- Run 51: fixes run 50's overclaim (reviewed-by byline).
- Run 56: fixes a Met Gala factual error the *drafting agent itself* introduced in the
  same run, caught at consolidation.
- Run 58: fixes run 57's Met Gala signal-reuse bug (new report didn't actually reuse
  the signal_id as claimed) — a "claimed but not done" bug, the same class run 25's
  `check_field_coverage.py` was built to catch, recurring in the *process* layer
  instead of the schema layer.
- Run 59: explicitly exists to verify run 58's fix held (it did).

That's 4 of 10 runs (51, 56, 58, 59) whose primary content is correcting or verifying a
correction of a problem introduced within this same loop, in the same 10-run window —
up from essentially zero self-correction runs in the 0-50 range (per run-50's own
review, that period was dominated by net-new coverage/schema/UX work with occasional
consolidation catches, not chained fix-the-fix-the-fix sequences). Genuinely new
site-facing work in 50-59 (54's source-gap fix, 55's dark-mode/404 work, 56/57's
domain-classification and signal-tracking additions) is real, but a fifth of the last
ten runs was spent verifying that a fix from two runs prior actually stuck. Worth
naming plainly: the loop is now visibly spending part of its own throughput
self-auditing itself, which is a sign of real quality control working — but also a sign
that agent self-reports ("verified," "reused the signal_id") are not reliable without a
second agent checking the actual saved artifact, a pattern that's held since run 8's
original git-checkout incident and hasn't gone away with scale.

## 3. New structural gap beyond §40

Nothing new found against §40 (still fully closed, not the frontier, consistent with
run 50). The one genuinely new observation this run: the loop's five-subagents-per-run
structure has no persistent verification of an agent's *self-report* against the
artifact it produced, aside from ad hoc consolidation catches (which worked in 56/58,
but only because a human-authored coordination step happened to check). There's no
lightweight, repeatable check (analogous to `check_field_coverage.py` or
`validate_all_reports.py`) that diffs "what the agent's log claims it did" against
"what the file actually contains" for process claims like signal_id reuse — this is a
process gap, not a data gap, so the existing schema-validation tooling doesn't cover
it. Flagging rather than building: adding such a check is itself agent work the loop
would then need a human decision to prioritize against the still-open crawler-cadence
and SITE_URL items from run 50, which remain unresolved and are not this run's scope.

## Bottom line for the user

Nothing has moved on run 50's two headline items in 10 runs — the crawler ratio is flat
and the human-in-the-loop gap is still structurally true, only now stated honestly
instead of overclaimed. The newer development is that a growing share of the loop's own
output is spent catching mistakes the loop made two runs earlier, which is worth
watching rather than treating as normal cost of doing business.
