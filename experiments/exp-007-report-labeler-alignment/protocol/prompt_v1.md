# EXP-007 prompt v1

Every part of the prompt is marked as one of two kinds:
- **[APP]:** copied word for word from what ARI3 Review shows on the card. It comes from `report_review.card_text` and the form in `ari3_review.pyw`, filled in from the frozen deck file.
- **[ADDED]:** not shown in the app. It is kept to the minimum the model needs to do the task at all.

## Signal card

```
[ADDED, sent as the system message]
You are filling in one card of the "Report decisions" deck in ARI3 Review, for a weekly report of the ARI3LLA INDEX. Below is exactly what the card shows: its title, its text and its form fields with their options, followed by the editor's definitions. Use only what is shown. Return one JSON object with the keys decision, merge_into, type, confidence, volatility, origin, name, remove_item_ids and thoughts. Write every value exactly as one of the options shown. Use null for a field left empty, and an empty list for remove_item_ids if none.

[APP, sent as the user message]
Report decisions {window start} to {window end}

{card name}

{card text: "N style-positive items from M outlets | type ... | baseline confidence ...",
 Sectors, Dates, Weaknesses, then EVIDENCE: item ID | date | outlet | sector, and the headline}

Decision: keep / drop / merge / watchlist
Merge into (only for merge): {the names of the week's other candidates, as in the app's list}
Type: aesthetic_term / color_print / commerce_language / footwear / garment_silhouette / material   (preset: {card type})
Confidence: baseline ({baseline}) / low / medium / high   (preset: baseline)
Volatility (needed to keep): stable / emerging / seasonal / volatile / flash / microtrend / recurring / revival / long_tail / saturated / declining
Origin: designer_originated / editorial_amplified / retail_adopted / social_amplified / platform_native / archive_revival / unclear   (preset: unclear)
Name as published: (preset: {card name})
Item IDs to remove (comma-separated)
Your thoughts (for a kept signal they become your editor note)

DEFINITIONS (your words)

{editorial/report_definitions.md, word for word, exactly as the panel beside the card shows it}

The app will not save if:
a kept signal needs a volatility label
a kept signal needs the editor's thoughts (they become the editor note)
choose which signal this merges into
```

## Duplicate card

```
[ADDED, sent as the system message]
You are filling in one card of the "Report decisions" deck in ARI3 Review, for a weekly report of the ARI3LLA INDEX. Below is exactly what the card shows: its title, its text and its form fields with their options, followed by the editor's definitions. Use only what is shown. Return one JSON object with the keys collapse (true for "one story: count once", false for "separate pieces: count each") and thoughts.

[APP, sent as the user message]
Report decisions {window start} to {window end}

Possible duplicates

{card text: Why flagged, "Are these the same underlying story (count once) or separate
 pieces?", then item ID | outlet | date | in: signals, and the headline}

Decision: one story: count once / separate pieces: count each
Your thoughts (optional)

DEFINITIONS (your words)

{editorial/report_definitions.md, word for word}
```

## Left out on purpose

- The progress line ("Card 5 of 33 | 2 of 33 decided"). It carries no information about the card.
- Anything not on the card or in the definitions file: no examples, no earlier weeks, no editor decisions.

## Definitions

`editorial/report_definitions.md` is written by the editor only. The app shows it beside every report-decision card, and the prompt includes the same file. No call runs while any line is unwritten. Its SHA-256 is frozen in the pre-registration.

## Order swap (second run)

The same prompt with every option list reversed, including the merge list. The definitions file is not reordered. Nothing else changes.

## Retry

If the answer does not parse, or the app's own save rules reject it, one more message is sent: "The app could not save that answer: {reasons}. Return only the JSON object." Nothing else is ever sent.

The exact rendering is `exp007.render` in `src/exp007.py`, fingerprinted in `protocol_v1.json`.
