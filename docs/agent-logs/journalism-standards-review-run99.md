# Journalism-standards benchmarking review — run 99

Research task, not a code-editing task. Read `docs/ARI3LLA INDEX.txt` (§2 voice rules, §22
methodology), `docs/confidence-discipline-precedents.md`, `web/app/methodology/page.tsx`,
and `docs/manual-sampling-workflow.md` first. Then checked prior coverage: this project has
already run a `journalism-standards-check-run*.md` pass at runs 40, 41, 46, 71, plus
`ai-journalism-standards-research.md` (run 14), `journalism-research.md` (early), and
`archival-standards-audit-run82.md`. Those already resolved: correction-notice placement
(top-of-page pinned notice, run 40), byline-adjacent AI disclosure (run 41), open-data
licensing (run 46), Reuters sourcing-hierarchy spot-check + AP corrections-visibility
re-check (run 71, found clean), and structural per-signal correction diffing against IPTC
News Architecture provenance guidance (run 82). This run's job was to find what's still
genuinely uncovered, not repeat those.

## Sources actually found via WebSearch (real URLs, not fabricated)

- [AP Stylebook - quotations/corrections guidance summary](https://en.wikipedia.org/wiki/AP_Stylebook) — general reference; AP guidance on not altering quotes and using editor's notes for unusual quoted material. **Not directly applicable**: this project never quotes named individuals verbatim, it summarizes source material, so the quote-alteration rule has no analog here. Checked and correctly set aside rather than forced into a finding.
- [IFCN Code of Principles — The Commitments](https://ifcncodeofprinciples.poynter.org/the-commitments) — five commitments: nonpartisanship/fairness, transparency of sources and funding, transparency of methodology, a published corrections policy followed scrupulously, and **reader verification** ("provide all sources in enough detail that readers can replicate their work").
- [Reuters Handbook of Journalism (PDF)](https://www.mediareform.org.uk/wp-content/uploads/2015/12/Reuters_Handbook_of_Journalism.pdf) — anonymous sources are the weakest sources; Reuters should "never... cite sources in the plural when only one source exists."
- [ONA Ethics — Corrections](https://ethics.journalists.org/topics/corrections/) and [Removing material from your archives](https://ethics.journalists.org/topics/removing-material-from-your-archives/) — archives should be corrected/updated in place rather than content removed, with a note describing what changed if more than a typo was fixed.
- [IPTC Digital Source Type NewsCodes vocabulary](https://cv.iptc.org/newscodes/digitalsourcetype/) and [schema.org's IPTCDigitalSourceEnumeration](https://schema.org/IPTCDigitalSourceEnumeration) — a structured `digitalSourceType` property (values like `TrainedAlgorithmicMediaDigitalSource`) that Google now actively parses to disclose AI involvement in content, distinct from prose disclosure. Confirmed current via [IPTC's technical guidance release](https://iptc.org/news/iptc-releases-technical-guidance-for-creating-and-editing-metadata-including-digitalsourcetype/) and [IPTC's synthetic-media metadata guidance](https://iptc.org/news/iptc-publishes-metadata-guidance-for-ai-generated-%22synthetic-media%22/).

## Where the project already meets the bar (no fabricated gaps)

- **ONA's archive-correction standard** (correct in place, note what changed, don't erase
  the record) is already met and then some — `revision_history` preserves the prior
  content hash, states the reason, and (since run 82) structurally diffs added/removed/
  modified signal_ids and fields, which exceeds ONA's baseline of "a note describing what
  changed."
- **Reuters' plural-sourcing rule was already being followed in practice** (confirmed at
  run 71's spot-check of two reports) — see the codification below; this is a
  documentation gap, not a behavior gap.
- **IFCN's "transparency of methodology" and "published corrections policy, followed
  scrupulously" commitments** are both substantively met by the existing methodology page
  and `revision_history` mechanism.

## Gaps found and what was done about each

### 1. Reuters' singular/plural sourcing rule existed only as a one-off audit finding, not a durable rule (fixed — doc only)

Run 71 spot-checked two reports against this Reuters convention and found them compliant,
but the rule itself was never written into either the living precedents doc or the
methodology page — it existed only in that one `journalism-standards-check-run71.md` log.
That is exactly this project's own recurring "documented once, not carried into the
durable ruleset" bug pattern (SKILL.md workflow convention #9), applied to a prose
convention instead of a schema field: a future report-writing agent has no way to know
this rule exists unless it happens to re-read that specific old log.

**Fixed:** added precedent 16 to `docs/confidence-discipline-precedents.md` (cites the
Reuters Handbook directly) and a line to `web/app/methodology/page.tsx`'s "How Citations
Work" section, so the rule is now checkable against the actual written record going
forward rather than needing re-verification each time.

### 2. IFCN's reader-verification principle vs. domain-level-only citation was an unnamed tension (fixed — doc only)

The project deliberately cites signals at the outlet-domain level rather than
per-article, for a real, previously-decided reason (protecting small/independent outlets
from disproportionate traffic spikes — see run 33/39's design decision, already documented
in methodology's "How Citations Work"). That reasoning is sound and this review is not
recommending a change to it. But the trade-off was never named against the specific
external standard it deviates from: IFCN's Code of Principles states signatories should
"provide all sources in enough detail that readers can replicate their work," and
domain-level citation does not fully satisfy that bar (a reader can confirm the outlet and
sector, not reconstruct the specific article without an independent search).

**Fixed:** added a sentence to the same methodology section naming this explicitly as a
known, deliberate departure from IFCN's reader-verification standard, rather than leaving
the trade-off implicit. This doesn't change behavior — it makes an existing honest
trade-off legible against the specific standard it diverges from, consistent with how the
"AI Involvement" section already names limitations as limitations rather than omitting
them.

### 3. No structured AI-disclosure metadata (`digitalSourceType`) — real gap, NOT fixed, flagged for a future code run

Current AI disclosure is prose-only: `web/app/methodology/page.tsx`'s "AI Involvement"
section and the report page's byline-adjacent line (added run 41). Neither the
`NewsArticle` nor the `Dataset` JSON-LD block in `web/app/reports/[date]/page.tsx`
(lines ~109-164) includes a `digitalSourceType` value. This is a structured-metadata
standard, not a prose one, and it's recent enough (IPTC's technical guidance and Google's
active support for the property are both current as of 2026) that it plausibly wasn't in
scope for any prior journalism-standards pass in this project — a check of every prior
`docs/agent-logs/journalism-standards-check-*.md` and `iptc-metadata-check-run36.md`
confirms none of them covered structured AI-source disclosure specifically (run 36's IPTC
check was about `dateModified`, a different property).

Concretely, `report.report_date`'s `NewsArticle` entry could carry
`"digitalSourceType": "https://cv.iptc.org/newscodes/digitalsourcetype/compositeWithTrainedAlgorithmicMedia"`
(or the closest matching IPTC NewsCodes value for AI-assisted-but-human-reviewed content —
picking the exact value correctly needs a real editorial decision, not a guess) so that
search engines and any downstream aggregator parsing this project's structured data get
the same AI-involvement disclosure a human reader gets from the prose, machine-readably.

**Not implemented, per this task's scope** (this is a code change to a `.tsx` file's
JSON-LD object, not a prose/doc edit) — documented here and should be added as a TODO
item for a future run that can also make the correct editorial call on which specific
IPTC NewsCodes value accurately represents this project's actual AI-involvement pattern
(AI drafts and reviews under the same automated process — see "AI Involvement" — which
doesn't map cleanly onto any single existing IPTC enum value without a real judgment
call, the same kind of "don't force a taxonomy fit" discipline precedent 14 already
applies to `origin_classification`).

## Files changed

- `docs/confidence-discipline-precedents.md` — added precedent 16 (singular/plural
  sourcing rule, cites Reuters Handbook).
- `web/app/methodology/page.tsx` — "How Citations Work" section gained two sentences:
  the IFCN reader-verification trade-off, and the singular/plural sourcing rule.
- This file (`docs/agent-logs/journalism-standards-review-run99.md`) — new.

No `data/reports/*.json`, `TODO.md`, or `CHANGELOG.md` files were touched. `cd web && npx
tsc --noEmit` run after the methodology edit — passes clean, no errors. No git commit was
made, per instructions.

## Recommendation for the coordinator / TODO.md

Add a TODO item: evaluate adding a `digitalSourceType` value to the `NewsArticle`/`Dataset`
JSON-LD in `web/app/reports/[date]/page.tsx` per the IPTC/schema.org structured AI-disclosure
standard described above — requires an editorial decision on which specific NewsCodes value
fits this project's actual AI-involvement pattern, not just a mechanical code add.
