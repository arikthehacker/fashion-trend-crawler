# EXP-009: what predicts the editor's report decisions best?

**Status:** pre-registered 2026-11-25, before any score is computed and before any new model call. The frozen details (fingerprints of this file, the code, the decks, the definitions, the editor's fingerprinted decision logs and EXP-007's sealed outputs) are in `protocol/protocol_v2.json`. It supersedes `protocol_v1.json`, under which nothing ran, because v1's freeze check refused the run on a type mismatch. The runner is `src/exp009.py`.

## Question

EXP-007 and EXP-008 found that an LLM reading a card does not track the editor's keep-or-drop decisions (kappa 0.08 and 0.09, against the editor's 216 decided cards), with or without an AI-written profile of her taste. EXP-009 asks which kind of predictor does best: the editor's own past decisions, a small model trained on them, or the LLM, with and without a memory of her earlier calls on the same term. In RLHF terms (Christiano et al., 2017; Ouyang et al., 2022), M2 below is a first reward model learned from one human's labels. The paper being presented, Lee et al. (ICML 2024), asks whether AI feedback can replace that human signal.

## Cards and the walk-forward split

- **Target cards:** the 185 signal cards of weeks 2 to 7 (report dates 2026-10-18 to 2026-11-22).
- **Week 1 (2026-10-11)** is used only as history and training data, never as a target.
- **Excluded:** duplicate cards (8 in all weeks). EXP-007's exclusion rules (cards decided before its plan, or marked `[looked up]`) apply too. On the target weeks they remove nothing.
- **The split:** each method guesses a card in week k using only what was known before week k. This is a walk-forward evaluation, also called time-series cross-validation. The editor's decisions are already known to the owner and to Claude, so this is not a blind test like EXP-007. What keeps it honest is that every method, feature, rule and threshold below is fixed and committed before any score is computed.

## The five methods

| | Method | How it decides a card in week k |
|---|---|---|
| M0 | Always keep | Every card is kept |
| M1 | Same as last time | The editor's decision on the same term (same `signal_id`) in the most recent earlier week with a card for it. A term with no earlier card is kept |
| M2 | Taste model | A logistic regression (Cox, 1958), fitted on every decided signal card of weeks 1 to k−1. It predicts keep when its probability is at least 0.5 |
| M3 | DeepSeek | EXP-007's sealed thinking-off answers in the app's option order. No new calls |
| M4 | DeepSeek with memory | EXP-007's prompt and settings, app order only, with one addition after the definitions: the editor's decision, volatility and any confidence she set on the same term in every earlier week. Decisions and labels only, no thoughts (the owner's choice, 2026-11-25). A term with no earlier card gets "None. This term has no card in an earlier week." |

**M2's model, fixed in advance:**
- **Target:** keep (1) against drop, watchlist or merge (0).
- **Card features:** log(1 + items), log(1 + outlets), number of sectors, number of days covered, number of weaknesses, baseline confidence (low 0, medium 1, high 2), and the card type as six 0/1 indicators.
- **History features, from earlier weeks only:** seen before (0/1), last decision was keep (0/1), share of earlier cards kept, number of earlier cards.
- **Fitting:** features standardized on the training rows, with L2 penalty 0.1. Batch gradient descent, learning rate 0.5, 2,000 iterations, starting from zero, so it is deterministic. Pure Python.
- **Records:** each target week's fitted weights are reported, so the model is readable.

## Hypotheses (keep against not-keep, Cohen's kappa)

The primary measure is kappa on keep against not-keep, the decision a report depends on. Each hypothesis is tested with a paired bootstrap over cards of the kappa difference (10,000 resamples, seed 9009, 95% percentile interval):
- a lower bound above 0 means **supported**;
- an interval containing 0 means **not supported**;
- an upper bound below 0 means **reversed**.

- **H1:** M2 (taste model) beats M3 (DeepSeek).
- **H2:** M4 (DeepSeek with memory) beats M3 (DeepSeek).
- **H3:** M2 (taste model) beats M1 (same as last time).

**Reported beside them, with no pass criteria:**
- each method's keep-against-not agreement and kappa, beside the always-keep baseline. M0's kappa is 0 by definition.
- four-way agreement and kappa for M0, M1, M3 and M4 (M2 predicts keep or not only);
- the number of cards each method keeps;
- per-week kappa;
- kappa on terms seen before against new terms;
- every pairwise kappa difference with its interval, descriptive.

The metrics and M2's weights are committed in `runs/comparison.json`. The card-by-card predictions stay local.

## Known limits, stated before the results

- **Small sample.** 185 cards. Cards within a week are not independent, so the intervals are optimistic.
- **Little training data early.** M2 for week 2 learns from about 31 cards of week 1, which has no history features. Its early weeks are expected to be weak.
- **Recurring terms.** Most terms recur, so M1 and the history features may do much of the work. The split by seen-before and new terms shows this.
- **Already-seen decisions.** The editor's decisions were seen before this design, as stated above. The design was fixed in conversation before any of these methods was scored.

## Cost

M4 makes 185 first calls, with at most one retry each. The expected cost is about 0.08 USD off-peak and about 0.15 USD at peak, scaled from EXP-007's actual cost per call. The worst case is 1.60 USD: every character a token, two attempts, full output, peak prices. The run stops itself once its running estimated cost reaches 0.50 USD. M0 to M3 make no calls.

## Order of work

1. Commit and push this file, the code, its tests and the frozen protocol.
2. Run M4, seal its outputs, commit and push the manifest.
3. Compare all five methods, commit and push the metrics.
