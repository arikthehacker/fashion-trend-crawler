# Archival permanence follow-up (run 39)

## Question
Run 35 flagged link-rot mitigation as premature (no citable field existed). Run 36
resolved that by adding `source_domains` (bare homepage domains, not article
permalinks — deliberate, per run 33's source-protection mitigation). `source_domains`
is now populated and rendered on both report pages and signal pages (runs 36-38).
Does domain-level citation close the run-35 concern, or is there a real remaining gap?

## External research
Standard archival-journalism practice (Perma.cc/Harvard LIL, Internet Archive) is to
snapshot a cited source *at citation time*, producing a permanent redirect so the
citing document's credibility survives even if the source dies. But Columbia
Journalism Review's "A Public Record at Risk" report raises a distinct, more relevant
risk: newsrooms are leaning on the Internet Archive to preserve **their own published
content**, and the Wayback Machine's coverage is incomplete/non-guaranteed (one study
found ~72.6% retrieval) — a false sense of security if treated as a real backup.

## Reconciliation
The run-35 gap ("nothing to protect from rotting because nothing is being linked to")
is **adequately closed** for its original scope: `source_domains` gives every signal
a stable citation anchor (a homepage domain effectively never disappears the way an
article permalink does), with no per-article link-rot surface to mitigate and no
new pile-on risk. Per-article Wayback/Perma.cc snapshotting remains correctly
rejected — there's no permalink to snapshot, by design.

But CJR's finding surfaces a **different, real gap this project does have**: this
site's own dated report pages (`data/reports/<date>.json`, rendered at
`/reports/[date]`) are the actual permanent record being promised to readers, and
there is currently no self-archival step for them at all — if this site goes down
or a report file is lost, nothing preserves it. This is not urgent (git history is
itself a backup), but it's the more honest framing of "archival permanence" risk
than per-article link rot ever was.

## Recommendation
1. Treat domain-level citation as the **permanent design choice** — do not revisit
   per-article permalinks or Wayback-per-article snapshotting again absent a change
   to the source-protection stance.
2. Documented a short note in `web/app/methodology/page.tsx` (see diff) clarifying
   that citations are homepage-level by design (source protection), not a
   placeholder for future per-article links, so future agents don't reopen run 35's
   question from scratch.
3. Deferred, non-speculative future item (added to TODO.md candidates, not built):
   periodic Wayback "Save Page Now" snapshot of each published `/reports/[date]`
   page at publish time — protects the *site's own* record per CJR's actual finding,
   is low-effort (one URL per report, no per-article risk), and is a different
   problem from the one runs 35/36 debated.

## Sources
- CJR, "A Public Record at Risk: The Dire State of News Archiving in the Digital Age"
- American Bar Association, "Best Practices for Citing Online Content and Avoiding Link Rot"
