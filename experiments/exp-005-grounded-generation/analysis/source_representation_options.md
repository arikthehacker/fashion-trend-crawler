# Source representation: options (not adopted)

**Status:** options only. Nothing here is implemented. Ingestion, excerpts, chunking, full text, the retriever and the index are unchanged. Adopting any option needs a decision and, because it changes the evidence the model sees, a new retrieval or generation version.

**Why this exists:** dev-batch-2 showed that a correctly retrieved item can be represented by stored text that leaves out its relevant content (`corpus_sufficiency_dev-batch-2.md`).

## Options

| Option | What changes |
|---|---|
| A. Longer excerpts | Raise the stored excerpt cap (500 characters) and the serializer cap. Same items, more text per item. |
| B. Full cleaned text | Store the cleaned article body for each item. |
| C. Chunking | Split stored text into passages. Each passage keeps its item ID. |
| D. Chunk retrieval with item provenance | Retrieve passages, not items, and cite the parent item. Packets carry the matching passages. |
| E. Two-stage retrieval | Retrieve items as now, then pick the passages within each item that match the question. |
| F. Fetch on demand | Fetch a retrieved item's page at question time and extract relevant text. |

## Criteria for assessing each option later

| Criterion | Question to answer |
|---|---|
| Reproducibility | Can the same question give the same packet a month later? Option F fails this unless every fetch is cached and fingerprinted. |
| Temporal integrity | Does the text reflect what was known at `first_seen_at`? Pages are edited after publication. Text fetched later can leak later knowledge into a replay question. |
| Copyright and storage | How much third-party text is stored, where, and is any of it published? The current rule stores feed summaries capped at 500 characters and never full article text. Options B to F all change that. Publishing article text through a hosted database or API needs a separate review. |
| Retrieval quality | Does recall on the EXP-004 gold improve, measured as a new retrieval version on DEV first? |
| Provenance | Can every passage be traced to an item, a URL and a fetch time? |
| Source availability | Paywalls, deleted pages, robots rules and image-only pages such as runway galleries. Visual content stays unavailable to every text option. |
| Cache and versioning | How a stored text version is named, fingerprinted and replaced without changing old results. |
| Latency | Option F adds a network round trip per item at question time. |

## Notes

- Option A is the smallest change. On item 278 the first loafer mention comes about 2,000 visible characters after the point where the stored excerpt starts. Only a cap several times the current 500 would reach it, and a different post could put the relevant passage further in.
- Options C to E only help once text longer than the excerpt is stored, so each one depends on B or F.
- None of these options recovers runway looks, which are visual. That needs a different kind of source, such as structured look metadata, under its own terms review.
