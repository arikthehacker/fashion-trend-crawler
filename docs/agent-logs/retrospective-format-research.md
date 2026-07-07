# Retrospective/roundup format — research + data check (proposal, not implemented)

## How weekly-cadence outlets structure periodic roundups

Trade-press and newsletter guidance (Poynter/NiemanLab-style "best practices" pieces,
Substack's own creator guides, and journalism-org cadence advice) converges on a few
rules for monthly/quarterly recaps that avoid feeling redundant with weekly output:

1. **They synthesize, not repeat.** A good recap doesn't re-summarize each week; it
   answers a question the weekly cadence structurally can't: "what actually persisted?"
   Weekly reports are snapshots; the recap's whole value is measuring change across
   snapshots (what recurred, what died after one appearance, what accelerated).
2. **The unit of analysis shifts.** Weekly pieces are organized by signal-of-the-week;
   retrospectives are organized by trajectory (emerging -> recurring -> saturated -> faded)
   or by a small number of named threads with dated evidence trails.
3. **Threshold-gated, not calendar-gated.** The strongest guidance (seen in newsletter
   ops playbooks) is that a recap should only ship when there's enough repeated signal to
   report on — publishing a "quarterly" just because a quarter elapsed, with nothing new
   to say, is the exact redundancy risk being warned against.
4. **They cite the underlying weekly editions**, not replace them — recaps link back to
   the dated reports that first flagged each thread, preserving the archive's
   source-linked provenance model this project already relies on.

## Data check: does the archive support a real retrospective yet?

Ran a recurrence count of `signal_id` across all 16 files in `data/reports/*.json`
(2026-05-07 through 2026-10-12):

- 36 unique signal_ids total across the archive.
- Only **10** recur in 2+ reports; **none** recur in more than **3**.
- The top recurrences: `sheer-layering` and `soft-tailoring` (3 reports each, but with a
  ~2-month gap between appearances: 05-07 -> 07-06 -> 08-03 — not sustained weekly
  recurrence, more like the same theme resurfacing), `off-duty-varsity` and
  `peplum-waist-revival` (3 consecutive weekly reports each — the strongest real
  recurrence in the archive), plus six pairs that appeared in only 2 reports, several of
  which are fashion-week logistics items (NYFW scheduling, LFW eligibility rules, Versace/
  Armani leadership transitions) rather than style signals at all.

## Assessment

**Premature.** A quarterly retrospective needs multiple signals with sustained,
multi-cycle recurrence to justify a "what persisted" narrative distinct from the weekly
reports. Right now the strongest case is two signals recurring across 3 consecutive
weeks each — genuinely useful for a signal detail page (which `signals/[slug]/page.tsx`
already handles) but too thin to fill an entire retrospective report type without
padding it with one-off items, which is precisely the redundancy the research above
warns against.

**Recommendation:** don't build a quarterly/monthly report type yet. Instead, set a
concrete threshold to revisit this: once at least 4-5 signal_ids each show recurrence
across **4+ non-adjacent reports** (not just 3 consecutive weeks), there's enough
trajectory data for a genuine "signals that persisted through fashion month" piece
scoped to Sept 8 - Oct 6, 2026 (the NYFW/LFW/MFW/PFW window already logged in the
fashion-week-calendar note), since that's the only stretch dense enough with real
editorial activity to have multi-week corroboration. Re-run this same recurrence count
after a few more archive runs before committing to the format.
