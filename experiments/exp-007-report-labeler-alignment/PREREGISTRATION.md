# EXP-007: AI labeler alignment on weekly report decisions

**Status:** pre-registered 2026-11-24, before any provider call and before the editor's backlog decisions. The frozen details (fingerprints of the decks, the definitions, the code and this file) are in `protocol/protocol_v1.json`. The runner is `src/exp007.py`.

## Question

Can an LLM stand in for the editor on ARI3LLA's weekly report decisions? This adapts the "AI labeler alignment" measure of Lee et al. (ICML 2024, RLAIF vs RLHF) from pairwise preferences to the editor's categorical decisions.

## Cards

All 226 required cards in the seven prepared weeks, report dates 2026-10-11 to 2026-11-22:
- 218 signal cards, each decided keep / drop / merge / watchlist;
- 8 duplicate cards, each decided collapse yes / no.

The 7 optional report-thoughts cards are not used. The 2 cards the editor decided in the 2026-10-11 week before this plan existed (`signal:sneaker`, `signal:denim`) are included and flagged. The AI never reads them.

## The AI labeler

- **Model:** DeepSeek `deepseek-flash`, with the frozen settings already used in EXP-005: temperature 0, top_p 1, max_tokens 1000, thinking disabled, JSON output. One retry only if the answer cannot be saved: it does not parse, or the app's own save rules (`report_review.payload_errors`) reject it. The reasons are shown on the retry.
- **What it sees:** exactly the title, card text, form fields and option lists the app shows, word for word, filled in from the frozen deck files. That includes the merge list of the week's other candidates by name, and the editor's definitions file (`editorial/report_definitions.md`), word for word, as the app shows it beside every card. Two things are added: a short opening paragraph and the JSON output format. The prompt is specified in `protocol/prompt_v1.md`, with every part marked [APP] or [ADDED].

  It opens no URLs and gets no article text, images, outside search, earlier weeks, examples or editor decisions.
- **What it returns:** the same fields the editor fills in. For signal cards: decision, merge target, type, confidence, volatility, origin, name, items to remove and thoughts. For duplicate cards: collapse yes or no, and thoughts.
- **Arm:** zero-shot only (the owner's choice, 2026-11-24). The prompt holds the task, the options and the card. It has no worked examples of the editor's decisions. A few-shot arm, which would teach it her taste from examples, would be a separate experiment.
- **Order swap (position-bias check):** every card runs a second time, with every option list reversed, including the merge list.

## Same view for both labelers

- **Definitions:** the editor writes every definition herself, in the ARI3 Review deck "Report definitions (your words)". Every save goes to an append-only log, and `editorial/report_definitions.md` is rebuilt from it with her text exactly as typed. Claude then proposes a minimal copyedit of each one (spelling, punctuation and broken sentences only, nothing added, unclear passages flagged rather than guessed). In the deck "Report definitions approval", she chooses the copyedit, her original or her own rewrite for every card. Only her choices reach the file. Her raw text stays in the log. Software never writes a definition. Both the app and the prompt read that file. The file stays on the editor's PC and is never committed. Only its SHA-256 is published, in `protocol/protocol_v1.json`. Nothing runs while any line is unwritten or unapproved. The editor approved all 35 on 2026-11-24.
- **No links:** the editor does not open evidence URLs while deciding the experiment's cards, because the AI cannot. She also does not look the stories up elsewhere. If she does, she writes `[looked up]` in that card's thoughts, and the card is reported separately.
- **The 2 cards decided before this plan** were decided without the definitions panel. They are flagged and reported separately.

## Blinding and sealing

- AI outputs go to `data/store/blind/exp007/` (local, never committed, never printed).
- A committed manifest records their SHA-256, so they cannot change afterwards.
- The code never opens `reports-editing/app/`. A test enforces this.
- Until unsealing, status reports give counts only: calls, schema validity, cost.
- **Unsealing** happens only after the editor says the backlog is done. Her decision logs are fingerprinted, and the fingerprints committed, first.

## Metrics (no pass criteria; this is a measurement)

On cards both labelers decided, in the original order:

1. **Decision agreement and Cohen's kappa** on the 4 signal decisions, overall and per week, with the majority-class baseline beside them. Per-week kappa rests on about 30 cards and is reported as noisy.
2. **Include agreement:** keep against anything else, with agreement and kappa.
3. **Volatility agreement** (exact match) on cards both kept.
4. **Merge target agreement** on cards both merged.
5. **Duplicate cards:** collapse agreement on 8 cards, descriptive.
6. **Kept-set overlap per week:** Jaccard index of the kept signal sets.
7. **Position bias:** the share of cards whose decision changes under the order swap.

Cards the editor leaves undecided, and cards the AI could not answer validly after its one retry, are excluded and counted. The two sets of thoughts are compared side by side, qualitatively only. The metrics are committed in `runs/comparison.json`. Thoughts and the side-by-side detail stay local.

## Outputs

- A per-week comparison table.
- The disagreement list, with both sets of thoughts.
- For each week, two signal tables (kept signals with counts, volatility and confidence): one from the editor's decisions, one from the AI's.

The AI version is a local comparison artifact. It has no editor notes (rule 6), and it is never published.

## Cost gate

The worst case is computed before any call: every input character counted as a token, two attempts per call, full output, peak prices. The run stops if that exceeds the authorized cap.

| What runs | Calls | Worst-case estimate |
|---|---|---|
| Zero-shot with order swap | 452 | 3.81 USD, under the 5 USD gate |

Actual cost in earlier runs was about a fifteenth of the worst case.
