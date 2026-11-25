# EXP-009 results (2026-11-25)

The full metrics and the taste model's weights are in `runs/comparison.json`, and the pre-registration and protocol v2 are in this folder. The test set is 185 signal cards from weeks 2 to 7, none excluded. The editor kept 130 of them. M4 made 185 DeepSeek calls, all valid on the first attempt, estimated cost 0.17 USD.

## Keep against not-keep

| Method | Agreement | Kappa | Cards kept | Kappa, terms seen before (n 170) | Kappa, new terms (n 15) |
|---|---|---|---|---|---|
| M0 always keep | 0.703 | 0.000 | 185 | 0.000 | 0.000 |
| M1 same as last time | 0.822 | 0.542 | 143 | 0.632 | 0.000 |
| M2 taste model | 0.822 | 0.515 | 153 | 0.503 | 0.500 |
| M3 DeepSeek | 0.735 | 0.182 | 173 | 0.170 | 0.186 |
| M4 DeepSeek with memory | 0.800 | 0.436 | 159 | 0.452 | 0.286 |

## Hypotheses (paired bootstrap, 10,000 resamples, 95% interval)

| | Difference in kappa | Interval | Verdict |
|---|---|---|---|
| H1: M2 taste model beats M3 DeepSeek | +0.333 | [+0.136, +0.524] | supported |
| H2: M4 DeepSeek with memory beats M3 DeepSeek | +0.254 | [+0.063, +0.440] | supported |
| H3: M2 taste model beats M1 same as last time | −0.027 | [−0.188, +0.135] | not supported |

The following differences were not hypotheses and are reported as descriptive:
- M1 beats M3: +0.360 [+0.156, +0.562].
- M1 against M4: +0.106 [−0.035, +0.248].
- M2 against M4: +0.079 [−0.067, +0.225].

## Per week (kappa)

| Week ending | M1 | M2 | M3 | M4 |
|---|---|---|---|---|
| 2026-10-18 | 0.444 | 0.129 | 0.173 | 0.468 |
| 2026-10-25 | 0.185 | 0.613 | 0.000 | 0.289 |
| 2026-11-01 | 0.247 | 0.000 | 0.058 | 0.127 |
| 2026-11-08 | 0.659 | 0.644 | 0.105 | 0.393 |
| 2026-11-15 | 0.853 | 0.775 | 0.260 | 0.693 |
| 2026-11-22 | 0.678 | 0.751 | 0.334 | 0.557 |

## The taste model

- **The first model** predicts week 2-ending 2026-10-18. It is trained on 33 cards of week 1, which have no history features. Its largest weights are on card type and baseline confidence.
- **The last model** predicts 2026-11-22 and is trained on 189 cards. Its largest weights are, in order: the share of earlier cards kept, whether the last one was kept, then item count, outlet count and days covered.

## Reading

- **The editor's own past decisions predict her next ones far better than an LLM reading the card.** Both M1 and M2 reach kappa above 0.5, while M3 reaches 0.18.
- **Memory is what the LLM was missing.** Adding the editor's earlier decisions and labels on the term more than doubles DeepSeek's kappa, from 0.18 to 0.44.
- **Even with memory, DeepSeek does not beat the plain rule** "do what she did last time" (0.54), though that difference is not significant.
- **The small learned model ties the plain rule overall.** It is the only method with clear agreement on terms the editor had never seen. That rests on 15 cards, so it is descriptive only.

## Limits

- 185 cards from six weeks, and cards within a week are not independent.
- Only 15 new terms.
- The editor's decisions were known before the design, as the pre-registration states. Every method and feature was fixed and committed before scoring.
