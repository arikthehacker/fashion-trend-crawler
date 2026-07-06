# Continuity/succession planning research + operational-doc accuracy check

## External guidance found

- **DPC (Digital Preservation Coalition)** "Rapid Assessment Model" and its
  Bit List/Decision Tree work explicitly flag single-point-of-failure
  maintainership as a top preservation risk, distinct from bit-rot/fixity —
  their guidance is to document a named successor/handover contact and a
  "minimum viable" runbook *before* it's needed, not after a maintainer
  disappears.
- **NDSA** succession/organizational-risk material (as opposed to their
  fixity/Levels of Preservation guidance already cited in earlier runs)
  stresses a written "continuity of operations" plan: who else can run the
  pipeline, where credentials/keys live, and a documented minimum cadence
  below which the archive is considered "at risk" rather than silently
  stale.
- **Small-newsroom sustainability guidance** (e.g. Reynolds Journalism
  Institute / LION Publishers "bus factor" writing) converges on the same
  practical checklist for single-person outlets: (1) one current runbook,
  not tribal knowledge; (2) credentials documented somewhere the successor
  can reach; (3) an explicit "if I disappear, do X" note, even if informal.

The common thread: succession risk for one-person/tiny-team projects is
mitigated by **one accurate, current operational doc**, not by more
automation. That's directly testable here.

## Concrete check: is README's "How to run it" section that document?

**No — it is stale and would mislead a human taking over tomorrow.**

1. **Wrong invocation path.** README says `bash run.sh` and
   `python src/crawler.py` / `python src/server.py`. The actual pipeline
   script lives at `src/run.sh`, and it internally calls `python crawler.py`
   / `python summarize.py` (no `src/` prefix) — meaning `run.sh` only works
   if invoked from inside `src/`, not from repo root as README implies.
   Running `bash run.sh` from root fails immediately (file not found).

2. **Missing CLI flags added in run 10.** `src/summarize.py` now takes
   `--revision-reason` and `--corrected-at`, required whenever today's date
   already has a saved report with different content (this is exactly the
   scenario a manual takeover is likely to hit — re-running after a gap).
   README's "How to run it" section documents zero arguments to
   `summarize.py` and never mentions revision handling at all, even though
   the "Data Pipeline" section above it *does* describe the
   `revision_history` mechanism in the abstract.

3. No mention of `manual_sample.py`, `audit_confidence.py`, or
   `validate_all_reports.py` as operational tools a hands-on maintainer
   would want, though these are referenced elsewhere in README.

**Recommendation for coordinator:** update the "How to run it" section to
(a) use `bash src/run.sh` (or fix the script to be root-invocable), and
(b) document `--revision-reason`/`--corrected-at` with the actual trigger
condition (re-running summarize.py same-day over an existing report). Not
fixed here per task scope — flagging since another agent may be touching
README/run.sh concurrently.
