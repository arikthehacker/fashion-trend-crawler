# Confidence audit: derive_confidence() vs assigned confidence

Read-only audit via `src/audit_confidence.py`. 22 signals across all 4 reports in
`data/reports/`; 14 mismatches (64%). No files mutated.

## Mismatches

**Formula says higher than assigned (11 cases)** — LLM/editor was more conservative
than the formula: `Sheer layering` (05-07, 07-06), `Soft tailoring`, `Archival
romanticism`, `1990s minimalism revival`, `Saturated purple`, `Uneven and
handkerchief-hem silhouettes`, `Oversized 'bug-eye' sunglasses` — all 2-3
cross-sector-corroborated signals marked "medium"/"low" when the formula says
"high". Not concerning: cross-sector corroboration is a reasonable proxy but
editorial judgment can legitimately discount it (e.g. `1990s minimalism revival`
assigned "low" despite 2 sectors — plausibly because the editor judged the
signal itself as thin/speculative, a dimension the formula can't see).

**Formula says lower than assigned (1 case) — genuinely concerning:**
`Resale/secondhand retail growth` (2026-07-13) was assigned **"high"** confidence
with `source_corroboration_count=1` (source_sectors: retail, editorial,
institutional — but only one *count*, so likely one aggregated source spanning
sectors, not independent corroboration). Formula derives "medium". This is
exactly the failure mode the formula was built to catch: a single-source signal
promoted to "high" on the strength of institutional/editorial framing rather
than independent corroboration.

**Formula says medium, assigned low (3 cases)** — `Coastal-cowgirl styling
evolution`, `Textured maximalist layering`, `Utility-detailed belts`, `Layered
tops styling`, `"Off-Duty Varsity" jersey styling` (07-13, 07-20): single-source
signals paired with an editorial mention, downgraded to "low" by the human/LLM
despite the formula's high-reliability-sector allowance. Reasonable — these read
like social-origin signals where an editorial write-up doesn't yet establish
real corroboration; the human judgment here is arguably *better calibrated*
than the formula on social-adjacent signals, consistent with the project's
voice rule that social signals shouldn't be upgraded just because editorial
also covered them.

## Recommendation

1. Wire `derive_confidence()` into `summarize.py` or `validate_report()` as a
   **non-blocking warning**, not an auto-override: flag any signal where
   assigned confidence is "high" but derived is "medium"/"low" (the
   `Resale/secondhand` pattern) for editor re-review before publishing.
2. Don't auto-adopt derive_confidence() where it says higher than assigned —
   the audit shows the human/LLM's downgrades on social-adjacent signals are
   defensible and the formula lacks that nuance.
3. Consider tightening the formula, not the LLM: distinguish "3 sectors, 1
   corroboration count" from genuine multi-source corroboration, since a single
   article citing multiple sectors isn't independent confirmation.
