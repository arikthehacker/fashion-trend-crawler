# Bias audit — run 18 (second pass)

Analytical only, no code changes. Full findings logged in `docs/PROMPT_CHANGELOG.md`
under "Second bias-audit pass (run 18)." Deliberately covered different angles than
run 16 (source-list skew, `HIGH_RELIABILITY_SECTORS` gate).

**(a) Taxonomy value-loading (`VOLATILITY_LABELS`/`ORIGIN_CLASSIFICATIONS`).** No
issue found. `archive_revival` and `designer_originated` are unranked, orthogonal to
`confidence`, and untouched by `derive_confidence()` or `build_prompt()`. Suggested
(not made) a one-line clarifying note on the taxonomy page so future editors don't
start reading the list as a legitimacy hierarchy.

**(b) Sector-level confidence patterns in the 10 real reports (real finding).**
Grouped every signal in `data/reports/*.json` by `source_sectors` x
`source_corroboration_count` x `confidence`. At equal corroboration count (2),
`independent_criticism` lands at `low` 75% of the time vs. `editorial` 40% and
`retail` 0%. This is the same root cause as run 16's `HIGH_RELIABILITY_SECTORS`
finding (`independent_criticism` excluded from the single-mention medium floor), now
confirmed as a pattern visible in actual assigned data, not just latent in the
formula. Reinforces run 16's recommendation to extend the gate to
`independent_criticism` — flagging as the top candidate for the next code-touching
run.

**(c) Manual-sampling platform balance (real finding, reshaped).** Both real exercises
of the compliant social-sampling workflow ("Off-Duty Varsity," "Poetcore") sampled
Pinterest exclusively — zero TikTok signals logged. Root cause is compliance friction
(TikTok's Research API is academic-gated; Pinterest publishes an easy public "trend
report" page), not editorial preference, and the taxonomy/domain map itself doesn't
favor Pinterest over other social platforms. The sharper issue: both logged signals
came from Pinterest's own self-promotional "trend report" pages (marketing/forecast
content), not organic user posts, yet get tagged identically
(`source_sectors: ["social"]`, `origin_classification: "platform_native"`) to
grassroots UGC — `taxonomy.py` has no vocabulary distinction between platform-marketing
content and organic discourse within the `social` sector. Recommended a
documentation-level distinction in `manual-sampling-template.md`, not a new controlled
vocabulary value (sample size is only 2, too small to justify a schema change).

**Method for (b):** ad hoc script aggregating `confidence`/`source_corroboration_count`/
`source_sectors` across all 10 files in `data/reports/`, grouped by corroboration count
to compare sectors on equal footing — a finer cut than `audit_confidence.py`'s existing
per-signal mismatch check, which doesn't group by sector.

No code changes made. All three findings written to `docs/PROMPT_CHANGELOG.md`
("Second bias-audit pass (run 18)") per the periodic-review practice TODO.md asked
for after run 16. Recommend `TODO.md` be updated to note (b) as the next concrete
code candidate (extend `HIGH_RELIABILITY_SECTORS`-adjacent gate to
`independent_criticism`) and (c) as a documentation-only follow-up.
