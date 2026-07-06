# Heading-lint automation (in response to 3x recurring styled-p-as-heading bug)

## What was added

- `web/package.json`: `eslint-plugin-jsx-a11y` added as an explicit devDependency
  (it was already present transitively via `eslint-config-next`, which registers
  the plugin under the hood — now it's a direct, visible dependency).
- `web/eslint.config.mjs`: enabled `jsx-a11y/heading-has-content` plus a few other
  jsx-a11y rules eslint-config-next doesn't turn on by default
  (`anchor-has-content`, `anchor-is-valid`, `img-redundant-alt`,
  `no-redundant-roles`, `label-has-associated-control`).
- `.github/workflows/validate-reports.yml`: added a `lint-web` job that runs
  `npm ci` + `npx eslint .` in `web/` on every push/PR, alongside the existing
  Python report-validation job.

## The honest limitation

**No ESLint rule — in jsx-a11y or otherwise — can catch the actual bug that's
recurred 3 times** (a `<p>` styled with heading-like font size/weight standing
in for a real `<h1>`–`<h6>`). ESLint operates on the AST/tag name; it has no
concept of computed visual styling, so `<p className="text-2xl font-bold">`
and `<p>tiny footer text</p>` are indistinguishable to it. `jsx-a11y` ships
exactly one heading-related rule, `heading-has-content`, and it only checks
that real `<hN>` elements aren't empty — it can't flag a `<p>` for *not* being
an `<hN>` it was never trying to be.

This was verified against the installed plugin (`eslint-plugin-jsx-a11y@6.10.2`):
`lib/rules/` contains no rule matching "heading" other than
`heading-has-content.js`. A custom rule is technically feasible (walk JSX,
flag `<p>`/`<span>`/`<div>` with heading-scale className tokens) but would be
heuristic, high false-positive-prone, and out of scope here.

## What actually catches this bug

A human/AI code-review checklist item remains the realistic fix, same as the
existing pattern in `docs/agent-logs/heading-hierarchy-fix.md` and
`accessibility-audit-run21.md`: when reviewing new page copy, check that
visually heading-shaped text uses a real `<hN>` tag and that the resulting
document outline (h1 → h2 → h3, no skipped levels) makes sense. Suggest
adding this explicitly as a checklist line in the workflow conventions
(`.claude/skills/ari3lla-index/SKILL.md` point 3, "verify before committing")
rather than relying on it being independently rediscovered a 4th time.

## Verification

`cd web && npx eslint .` — 0 errors, 1 pre-existing unrelated warning
(unused eslint-disable in `reports/[date]/page.tsx`), no new violations
across the existing codebase.

`cd web && npx tsc --noEmit && npx next build` — both pass clean, all 65
routes generated successfully.
