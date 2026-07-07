# Run 67 check: taxonomy drift in garments/silhouettes controlled vocabulary

**Scope:** checked whether the free-text `garments`/`silhouettes` fields (part of the
report schema, populated by the LLM extraction prompt in `src/summarize.py`) had
organically drifted or lost their category boundary after 59+ reports.

## Method

Loaded every `data/reports/*.json` and tallied all `garments` and `silhouettes`
entries. Found 61 distinct garment terms and 36 distinct silhouette terms. Most
variation (e.g. "structured blazer" vs "tailored blazer" vs "deconstructed blazer")
is legitimate — these describe genuinely different garments/weeks, not drift.

One real defect found: in `data/reports/2026-07-20.json`, **"godet skirt" appears
verbatim in both `garments` and `silhouettes`** for the same report:

```
garments:    ['shirt', 'handkerchief-hem skirt', 'godet skirt', 'belt', 'soccer jersey', 'layered top']
silhouettes: ['asymmetric hem', 'godet skirt', 'relaxed suiting']
```

This is a controlled-vocabulary boundary violation, not cross-report drift: the same
term was double-counted across two fields that are supposed to be disjoint
(garment = wearable item; silhouette = shape/construction quality). Checked
`src/summarize.py`'s extraction prompt (the only place these fields are populated)
and confirmed it never defines the garments/silhouettes boundary or forbids
duplicate terms across the two lists — so the LLM had no instruction preventing
this.

Also checked (false alarm): a `Bouclé wool jacket` entry that printed as
mojibake in a raw terminal dump. Verified via `.encode('utf-8')` that the stored
JSON is correctly UTF-8-encoded (`é` escape) — display artifact only, not a
data bug. No action needed.

## Fix applied

Added one clarifying paragraph to the extraction prompt in `src/summarize.py`
(after the existing "Focus on repeated language..." line) that:
- defines "garments" as wearable items vs. "silhouettes" as shape/construction
  qualities, with examples,
- instructs that a construction detail of an already-listed garment (e.g. a godet
  insert) should not be re-listed under its own name in `silhouettes`,
- explicitly forbids placing the same term in both lists.

This is a prompt-only change (no schema/type change), so it only affects future
crawler runs — the existing 2026-07-20.json entry was left as-is (historical
record, not worth rewriting past data for one duplicate term).

No web files touched; `npx tsc --noEmit` not applicable.
