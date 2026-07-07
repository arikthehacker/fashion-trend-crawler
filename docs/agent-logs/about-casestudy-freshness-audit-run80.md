# About / Case-study freshness audit (run 80)

## Scope

Read `web/app/about/page.tsx` and `web/app/case-study/page.tsx` in full, and
`docs/ARI3LLA INDEX.txt` sections 33 (case-study framing), 37 (product
distinctions), and 38 (philosophical stance). Cross-checked against current
repo state: `data/reports/` report count (72, confirmed via build log:
"copy-reports: copied 72 report(s)"), and the crawler-off-limits /
hand-authored-reports status from runs 65-73 / 68+.

## Findings

**No stale concrete claims found on either page. Clean result.**

1. **Report/source counts** — About page makes no numeric claims about report
   count, source count, or archive size at all ("preserves them as dated
   reports" is the only framing). Nothing to go stale here.

2. **"Early"/"prototype" framing** — Neither page uses developmental-stage
   language ("early," "prototype," "experimental," "in progress" as a
   disclaimer). About page's tone already reads as an established,
   operating archive. No change needed.

3. **Case-study automation framing — already accurate, not overstated.**
   The "Technical System" section says a crawler "collects public source
   material" and LLMs "summarize and structure," which could read as
   fully-automated in isolation, but the page immediately follows with a
   dedicated **"Current Limitations"** section stating explicitly: "Every
   report in the archive is hand-authored or research-assembled rather than
   produced by a live crawl merged into the archive; a real crawl-and-
   summarize run has succeeded once but its output was not merged, pending a
   deliberate resolution of a same-date collision. Migration off the legacy
   cache-file pipeline is nearly, not fully, complete." This precisely
   matches the runs 65-73/68+ reality (crawler.py off-limits pending
   supervised live test, reports hand-authored since run 68) and is not
   overstated. The page's `last edited: 07/06/2026` comment and the
   `Current Limitations`/`Future Work` sections show this exact gap was
   already closed in a prior pass — nothing new to fix.

4. **Source-doc comparison (`ARI3LLA INDEX.txt` §33)** — The original spec's
   "My Role" case-study section (crawler/MCP/taxonomy/frontend authorship)
   was dropped from the live page in favor of a "Design System" section;
   this is an intentional editorial choice already reflected in the current
   page, not staleness (a case-study page doesn't need to itemize authorship
   the way an internal planning doc does).

5. **§37/§38 product-distinction and philosophical-stance language** ("not
   trend forecasting," "human-in-the-loop research," "style should conform
   to how people want to live, not the other way around") is reproduced
   near-verbatim in About's "This Index Is / Is Not" blocks and closing
   pull-quote. Matches source doc and current framing exactly.

6. **AI-involvement/independence/corrections claims** on About were already
   cross-checked in run 79 against `report_schema.py`'s revision-history
   mechanism and confirmed accurate; re-read in this pass, still consistent
   — no new drift found.

## Fix applied

None. No edits made to `about/page.tsx` or `case-study/page.tsx` — both
pages' concrete factual claims (report authorship status, automation
framing, product-distinction language) hold up against current system
behavior. This is a valid clean audit result, not a missed check: the
crawler-automation nuance that this audit was specifically watching for was
already addressed by a prior edit (page timestamped same day as this audit).

## Validation

```
cd web && npx tsc --noEmit   # clean
npx eslint .                 # clean
npm run build                # succeeded, 176 pages incl. 72 reports, 87 /signals/[slug] paths, pagefind indexed 171 pages
```

No `.env` or secret values were read, logged, or printed during this audit.
