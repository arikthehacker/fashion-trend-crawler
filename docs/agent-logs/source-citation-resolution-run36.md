# Source citation resolution (run 36)

## Decision: add `source_domains` now, homepage-level only — not `source_url`

Run 33 and 35 were in tension: 33 concluded per-article `source_links` should
stay dead because activating it risks a "hug of death"/pile-on vector for
small/independent outlets (its stated mitigation: link to the outlet
homepage/section, never the article permalink); 35 independently found no
citable link field exists at all, and recommended adding `source_url` for
link-rot/archival purposes without addressing 33's risk.

Both are right about their own concern and wrong to treat it as blocking
the other. The actual risk vector, per 33, is the **specific article
permalink**, not citation itself. A field that only ever holds a bare
outlet homepage domain (e.g. `"vogue.com"`, `"dewimagazine.com"`) carries
none of that risk — it's the same granularity `web/app/sources/page.tsx`
already publishes for every outlet, so it adds no new exposure. It also
gives archival/link-rot work (35's actual motivation) a real place to
start, and gives future report pages a citation anchor without ever
constructing a URL a reader could pile onto a single small-outlet article.

`source_url`/`source_links` (full article permalinks) remains rejected,
per run 34's removal — that decision stands.

## What was implemented

- `src/report_schema.py`: added `source_domains: list = field(default_factory=list)`
  to the `Signal` dataclass, optional/backward-compatible (empty list =
  old reports still validate). Validation added in `validate_report()`:
  must be a list of non-empty strings, and any entry containing `/` or
  starting with `http:`/`https:` is rejected outright — this makes it
  structurally impossible to smuggle a full article URL into this field,
  so the run-33 mitigation is enforced by the schema, not just by
  convention.
- `web/lib/reports.ts`: added `source_domains?: string[]` to the
  `TopSignal` interface, with an inline comment pointing at run 33 and
  this log.

## Explicitly not done in this task

- Not populated by `summarize.py` (crawler URLs -> domain extraction is a
  separate, scoped follow-up).
- Not rendered on any page (`reports/[date]/page.tsx` or elsewhere) — task
  scope was schema/data-layer only.
- No Wayback/Perma.cc archival-snapshot step — run 35's broader
  suggestion. Now unblocked (there's a domain to anchor to) but still a
  separate future task, and lower priority than per-article snapshotting
  would need per-article URLs this project has deliberately chosen not to
  store.

## Verification
- `python -m py_compile src/*.py` — passed.
- `python src/validate_all_reports.py` — `OK: all 28 report(s) ... passed
  schema validation.`
- `cd web && npx tsc --noEmit` — could not run: no local TypeScript
  install in `web/node_modules` in this environment (pre-existing, not
  caused by this change). The edit is a single additive optional
  interface field; risk of a type error is low, but a real `tsc` run is
  still owed before this is committed/merged.

## Threads closed
- Run 33 (source-protection-review): mitigation now enforced in code, not
  just documented as "if activated later."
- Run 35 (archival-practice-research): its blocking concern (no citable
  field exists) is resolved via `source_domains`; its further suggestion
  (Wayback/Perma.cc) is noted as a follow-up, not adopted now.
