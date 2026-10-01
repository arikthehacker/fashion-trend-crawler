# Corpus sufficiency: EXP-005 dev-batch-2

This is an analysis of the evidence layer. It is not a generation metric and does not change any score. EXP-004 is not modified. The corpus, excerpts, index and retriever are unchanged. The data is in `corpus_sufficiency_dev-batch-2.json`.

## Question

When a full source is relevant to a question, did the stored headline and excerpt keep the relevant part?

## Classes

| Class | Meaning |
|---|---|
| `STORED_TEXT_SUFFICIENT` | As far as the check shows, the stored headline and excerpt keep what the full source says about the question. |
| `STORED_TEXT_INSUFFICIENT` | The full source has text relevant to the question that the stored headline and excerpt leave out. |
| `SOURCE_CONTENT_UNAVAILABLE` | The relevant content cannot be assessed as text, for example because it is in images. |

## Method

Each page was fetched once on 2026-10-01 between 22:10 and 22:16 UTC. The check:
1. Removes scripts and styles and strips the tags to get the visible text.
2. Counts a case-insensitive term pattern in that text and in the stored headline plus excerpt.

The JSON records only these values:
- HTTP status;
- size;
- SHA-256;
- whether the page title matches the stored headline;
- the term counts.

No article text is stored. Pages can change, so the fingerprints identify the versions that were checked.

## Results

| Question | Items checked | Full page | Stored text | Class |
|---|---|---|---|---|
| q017 loafers, by 2026-09-15 | 278 (Die, Workwear!, 2024-11-15) | 16 "loafer" hits in 34,905 visible characters | 0 hits in a 417-character excerpt | `STORED_TEXT_INSUFFICIENT` |
| q023 ballet flats before 2020 | 2010, 2007, 2009, 2008 (i-D) | 0 "ballet" or "flat(s)" hits on all four pages | 0 hits | `STORED_TEXT_SUFFICIENT` (open to correction) |
| q031 Vogue and cowboy boots | 4586, 5654, 3484, 3242, 6892 (runway pages) | 0 "cowboy" hits. The looks are images and were not inspected. | Excerpts empty | `SOURCE_CONTENT_UNAVAILABLE` |
| q031 | 7616 (Julia Jacklin interview) | 0 "cowboy" hits. 7 mentions of boots. | Headline names boots | `STORED_TEXT_SUFFICIENT` |

**q017.** Item 278 was retrieved correctly, and its full page answers the question. The stored excerpt covers another part of the post. The model saw no loafer text and abstained. Under the context-only rule that abstention may be correct. The gap is in the evidence layer.

**q023.** The original review note reports relevant footwear discussion in at least one of the four i-D articles. The check does not reproduce it:
- All four pages returned HTTP 200.
- They are rendered on the server, and their titles match the stored headlines.
- None mentions ballet flats. The only footwear term across the four is one mention of boots, in a description of a 1990s subculture.

If the owner can name the passage, the classification will be corrected.

**q031.** Half the packet consists of runway pages with empty stored excerpts. Whether any look includes cowboy boots is visual information that neither the stored text nor the page text holds. The model could not use it, and this check could not assess it.

## Not checked

- The other nine q017 items and the other four q031 items were not fetched.
- Images were not inspected.
- Term counts miss paraphrase, for example a shoe described without the word.

## Development finding (2026-10-01)

Retrieval relevance and generation grounding depend on how each retrieved source is represented. An item can be correctly retrieved while its stored headline and excerpt leave out the information that made the full source relevant.

**Examples:**
- **Item 278 (q017).** Retrieved for loafers, and the full page discusses them. The stored excerpt does not.
- **The five q031 runway pages.** Retrieved for a Vogue cowboy-boot question with empty excerpts. Their potential relevance is visual, and none of it reaches the model.

This is a development observation from one batch of five fresh questions. It is not a headline claim and is not entered in the claim ledger.
