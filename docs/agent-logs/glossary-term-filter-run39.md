# Glossary term filter (run 39)

Follow-up to run 38, which added the build-time `console.warn()` for
undefined glossary terms and found ~130 hits, mostly long narrative
`top_signals[].name` sentences (e.g. tracking notes with embedded
parentheticals/dates) rather than genuine short vocabulary.

## Change

`web/app/glossary/page.tsx` only — added `isPlausibleGlossaryTerm()`, applied
right after `normalize()` and before the `DEFINITIONS` lookup in
`loadGlossaryTerms()`. A candidate is rejected if it:

- exceeds 40 characters,
- has more than 5 whitespace-separated words,
- contains parentheses, or `,`/`;`/`:`,
- contains a dash-as-aside (`--`, em/en dash), or
- ends in terminal sentence punctuation (`.`/`!`/`?`).

This runs before the `DEFINITIONS[key]` check, so narrative sentences never
reach (and never trigger a warning against) the definitions dict. No changes
to `DEFINITIONS` itself or to the matching/dedupe logic for terms that pass
the filter.

Thresholds were checked against all 29 existing `DEFINITIONS` keys — the
longest (`"uneven and handkerchief-hem silhouettes"`, 39 chars/4 words;
`"peplum / exaggerated-waistline revival"`, 38 chars/4 words) both clear the
40-char/5-word limits, so no legitimate curated term is filtered out.

## Verification

`npx tsc --noEmit`: no output/errors.

`npx next build`: exit 0, all 93 static pages generated (glossary page
included).

Warning count: **~130 before -> 19 after** (counted via `grep -c "no
DEFINITIONS entry"` on the build log). Remaining warnings are short
title-case phrases (e.g. "CFDA fur-free policy", "Conner Ives NYFW debut",
"Copenhagen Fashion Week SS27") — a genuinely small, curatable set, not
narrative sentences.

Rendered glossary output: confirmed 26 `<dt>` entries in the built
`/glossary` HTML (out of 29 curated `DEFINITIONS`), so real terms still
render correctly and the page did not collapse toward zero.
