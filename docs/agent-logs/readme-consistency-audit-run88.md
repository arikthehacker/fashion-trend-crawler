# README consistency audit — run 88

Scope: cross-check `README.md` against the live site's own self-description
(`web/app/about/page.tsx`, `web/app/case-study/page.tsx`, both confirmed accurate as of
run 80's freshness audit), plus verify specific factual/setup claims. Did not touch
TODO.md, CHANGELOG.md, data/reports/*.json, or other agents' files. No commit made.

## What was cross-checked

1. **Report count / "current state" framing.** README deliberately avoids a hardcoded
   report count or date range (per doc-sync runs 18/23/24 — it points at `/archive` or
   `data/reports/` instead). Confirmed `data/reports/` currently holds 80 files, which
   matches this run's own numbering (run 88) and the about/case-study freshness audit's
   run-80 baseline. No stale number found because none is stated — consistent by
   design.
2. **Pipeline status vs. Limitations/Case Study.** README's Limitations section already
   states every report is hand-authored/WebSearch-researched, not from a live
   `crawler.py` run merged into the archive, and references the one successful-but-
   unmerged real crawl. This matches case-study's "Current Limitations" section almost
   verbatim in substance. Consistent.
3. **Roadmap.** README's roadmap correctly marks "a live crawler.py + summarize.py run
   merged into the archive" as still open (`[ ]`), consistent with case-study's "Future
   Work" listing scheduled live crawls as future work. Consistent.
4. **Ethical AI / editorial-review framing.** README's Ethical AI Statement and
   Transparency sections describe AI as an archival assistant with human interpretation
   central. About page's "Independence, Corrections, AI Use" section adds a more
   specific, more recent disclosure: that editorial review is "currently carried out by
   the same automated process that drafts the report, not by a separate named human
   editor." README does not contradict this (it never claims a separate human editor
   exists) but is less precise on this specific point. Judged not a factual
   contradiction — README speaks at a higher level of abstraction throughout and this
   is consistent with its established, more technical/less-narrative voice. Left as is.
5. **API key setup section (added run 65).** Verified against actual code:
   - `.env.example` exists at repo root, contains only a placeholder
     (`ANTHROPIC_API_KEY=your-api-key-here`), no real secret exposed or logged.
   - `src/summarize.py` line 12-13 confirms `from dotenv import load_dotenv` /
     `load_dotenv()` — matches README's claim that `.env` loads automatically via
     python-dotenv with no manual `export` required.
   - Still accurate, no changes needed.
6. **Crawler usability — the one real gap found.** README's "How to run it" section
   presented `python crawler.py` / `bash run.sh` as ordinary runnable commands with no
   caveat. TODO.md (runs 66, 67, 71, 72, 73, and the run-88 "Next up" list) documents
   that `crawler.py` caused repeated hung processes (one over an hour) during
   unattended/autonomous runs, that two hang-fixes have been implemented
   (`ThreadPoolExecutor` hard-deadline + incremental flush) but **neither has been
   proven against a real live run yet**, and that `crawler.py` "remains off-limits for
   autonomous execution pending a human-supervised live test" as of run 72, still true
   as of run 88's TODO. README made no mention of this at all — a real, concrete
   inconsistency between the repo's own operational status (tracked in TODO.md, which
   isn't public-facing) and what the README told a reader who might actually try to run
   it. Fixed: added a caveat directly under "How to run it" describing the off-limits
   status, why (unattended hangs, unverified fixes), and that the note should be
   removed once a supervised live run confirms the fix.
7. **`validate_all_reports.py` reference.** File exists at `src/validate_all_reports.py`
   and parses cleanly (`ast.parse` — did not execute, avoids any side effects). README's
   references to it (schema validation, CI) remain accurate.

## Fix applied

`README.md`, "How to run it" section: inserted a paragraph noting `crawler.py`/`run.sh`
are currently off-limits for unattended/autonomous runs pending a human-supervised live
test, citing the two implemented-but-unproven hang fixes and the prior hung-process
history, and noting the note should be removed once a supervised run confirms the fix.

## Result

One real, concrete inconsistency found and fixed (crawler runnability claim vs. actual
off-limits status tracked in TODO.md). Everything else checked — report-count framing,
pipeline-status/Limitations/roadmap consistency with case-study, Ethical AI framing, and
the run-65 API key setup section — was confirmed accurate and consistent with the live
site's self-description. No secrets were printed, logged, or exposed during this audit.
