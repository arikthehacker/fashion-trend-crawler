# Heading-pattern heuristic tool (run 22 follow-up)

## What was added

`src/check_heading_patterns.py` — a standalone, dependency-free heuristic
scanner (regex-based, not a real JS/TS parser) over `web/app/**/*.tsx`. Run
manually: `python src/check_heading_patterns.py`. Not wired into CI, same
non-blocking spirit as `audit_confidence.py` / `check_field_coverage.py`.

It flags `<p style={{...}}>` tags whose inline style matches this codebase's
two observed heading-shaped conventions (confirmed by grep before writing
the script):

1. `fontFamily: "var(--font-instrument)"` — the site's dedicated
   display/heading font, used inside real `<h1>`-`<h3>` everywhere except
   one case checked.
2. Uppercase + `letterSpacing` + short text — the actual run-29 bug
   signature (`case-study/page.tsx`'s numbered section labels used
   `--font-franklin`, not `--font-instrument`; the display-font check alone
   would have missed it entirely). Score also considers word count and
   whether a real `<hN>` tag sits immediately adjacent (legitimate kickers
   next to a real `<h1>` get a score penalty).

## Validation against a known-bad pattern

Copied `web/app/case-study/page.tsx` to a scratch file outside the repo
(`.../scratchpad/page_scratch.tsx`), reverted the run-29 fix (`<h2>` section
label back to `<p>`, the pre-fix state), and re-ran the scorer against it in
isolation. **It caught the reverted instance** at the same threshold (score
4) used for everything else. Scratch file deleted afterward; no repo files
touched by the validation step.

## Honest result against the current (already-fixed) codebase

Run against the real `web/app` tree: **17 candidates flagged, 0 of which are
real bugs.** Every flagged instance is a legitimate kicker/eyebrow label or
a result-count line ("X report on file", "Timeline", "confidence" facet
label, etc.) that intentionally uses the uppercase+letterSpacing convention
without being a smuggled heading.

So the honest detection profile from this one test case is: 1/1 true
positive caught, but with a roughly 17:1 false-positive-to-clean-codebase
ratio at the threshold that catches the true positive. Raising the
threshold to cut noise would also risk losing the true positive, since the
real bug scores identically to the false positives (both are short,
uppercase, letterSpaced). This heuristic **cannot cleanly separate
"legitimate label" from "smuggled heading" on styling alone** — the
distinguishing signal is really structural (does this text function as the
title of the content block that follows it?), which a regex-based scanner
over raw source text can't reliably determine. The adjacency-to-real-heading
penalty helps a little (it's why `case-study/page.tsx`'s "Case Study"
masthead kicker and "ARI3LLA INDEX" footer label still show up, though, since
neither sits directly next to an `<hN>` in a way the 200-char window
catches).

## Conclusion

Useful as a narrow-focus checklist prompt ("here are N candidates, go look")
rather than a trustworthy pass/fail signal. It does not replace the manual
visual/structural read called for in `SKILL.md` workflow convention #3 — it
supplements it by giving a starting candidate list instead of requiring a
cold grep through every `<p>` in the app.

## Verification

`python -m py_compile src/*.py` — passes clean.
