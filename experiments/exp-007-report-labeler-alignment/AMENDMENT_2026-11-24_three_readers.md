# Amendment 2026-11-24: three readers

**When:** written after protocol v1 was frozen (`2775bd1`) and before any AI answer existed. The only run attempt under v1 got no answer back: every request was refused for an invalid key (`ABORTED_2026-11-24_invalid_key.md`). The editor had not decided any backlog card. `PREREGISTRATION.md` and `protocol_v1.json` are unchanged. Everything not changed here holds as written there.

**Decided by:** the owner, 2026-11-24.

## The change

The same cards get three readers instead of two:

| Reader | What it is | Orders |
|---|---|---|
| Editor | Her decisions in ARI3 Review. She also records one video per week, talking through her decisions. | app order |
| AI, thinking off | As in v1: `deepseek-flash`, thinking disabled, max_tokens 1000 | app order and reversed |
| AI, thinking on | The same model, prompt and definitions, with thinking mode on. Its reasoning text is kept. | app order only |

This follows the chain-of-thought question in Lee et al. (ICML 2024): does letting the labeler reason first change its agreement with the human?

## The thinking-on reader

- **Request:** `{"thinking": {"type": "enabled"}}`, through a new adapter (`src/llm_deepseek_thinking.py`). The adapter EXP-005 froze is untouched.
- **Saved per attempt:** the reasoning text (`reasoning_content`) and its token count. Both are sealed with the answers.
- **Settings:** max_tokens 16000. The docs do not say whether reasoning counts against max_tokens, so the limit leaves room. Temperature has no effect in thinking mode. top_p stays 1.0. The DeepSeek docs were read on 2026-11-24.
- **Prompt and retry:** the same prompt (`protocol/prompt_v1.md`) and the same one-retry rule. Reasoning text is never sent back.
- **Budget:** a worst-case estimate at the full output limit (about 10 USD) is not a useful gate. Instead the run stops once its running estimated cost reaches 3.00 USD. It also does not start if the account balance is below 3.00 USD. The stop and the counts are recorded.

## Run order

1. Thinking off runs first, then is sealed, committed and pushed.
2. Thinking on runs only after that.
3. Each runs once.

A run stops at once on an authentication or balance error (HTTP 401 or 402), so a bad key cannot produce a run of failures.

## The editor's backlog

She may start deciding cards once this amendment and `protocol_v2.json` are committed and pushed, even while an AI reader is running. No AI reader ever reads her decision log (tested).

**Videos:** one per week. They stay on her PC and follow the same rules as the app:
- She does not open evidence links.
- If she looks something up, she says so and writes `[looked up]` in that card's thoughts.

## Comparisons

Each comparison uses the metrics of `PREREGISTRATION.md`:

1. **Editor against thinking off.** Position bias is measured here from the reversed run.
2. **Editor against thinking on.**
3. **Thinking off against thinking on.** Both readers' app-order answers are used, like for like: decision agreement and kappa overall and per week, volatility on both kept, duplicates, kept-set overlap, and the number of decisions thinking changed.

Comparison 3 stays sealed with the rest until the editor's backlog is done and her logs are fingerprinted.

The local detail file lists every card where any two readers differ, with the editor's thoughts, both AI readers' thoughts and the thinking reader's reasoning. It is the source for the three-way video.
