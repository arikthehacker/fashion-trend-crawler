# EXP-008 results (2026-11-25)

The full metrics are in `runs/comparison.json`. The pre-registration and both amendments are in this folder. The reader is DeepSeek `deepseek-flash` with thinking off: 452 calls, all valid on the first attempt, estimated cost 0.45 USD. The prompt adds a taste profile written by a Claude subagent from the editor's decisions in the other six weeks, leave one week out. The comparison uses 216 signal cards, excluding the 2 decided before EXP-007's plan, which are reported separately.

## Hypotheses

| | EXP-007 (no profile) | EXP-008 (profile) | Difference, 95% bootstrap interval | Verdict |
|---|---|---|---|---|
| H1: kappa, four signal decisions | 0.079 | 0.086 | +0.006 [−0.076, +0.092] | not supported |
| H2: kappa, keep against anything else | 0.188 | 0.082 | −0.106 [−0.231, +0.016] | not supported |

## Reported beside them

| | EXP-007 | EXP-008 |
|---|---|---|
| Decision agreement (always-keep baseline 0.694) | 0.681 | 0.713 |
| Cards the AI kept, of 216 (the editor kept 150) | 202 | 212 |
| AI drops (the editor dropped 53) | 0 | 4, all also dropped by the editor |
| AI watchlist or merge choices | 14 | 0 |
| Volatility agreement on cards both kept | 0.361 (n 147) | 0.413 (n 150) |
| Duplicate cards, agreement (n 8) | 0.625 | 0.625 |
| Decisions changed by the order swap, of 226 | 26 (11.5%) | 8 (3.5%) |

- **McNemar (exact).** On the four-way decision, 7 cards went from wrong to right with the profile and none went from right to wrong (p = 0.016). That is the 4 correct drops plus 3 cards the editor kept that EXP-007 had put on the watchlist.
- **Changes by the profile.** It changed 16 of 218 decisions against EXP-007.
- **Per week.** Kappa is 0 in five of the seven weeks because the AI kept almost every card. The exception is 2026-11-08, at 0.315.

## Reading

The profile did not bring the AI's keep-or-drop judgment closer to the editor's. It made the AI drop 4 cards, all correctly, but it also stopped the AI from using the watchlist. Overall, the AI kept more cards than before. The changes the profile did make were more often right than wrong. It also made the AI's answers much less sensitive to option order, and it slightly raised volatility agreement. Neither was a pre-registered hypothesis.

## Limits

- **Small sample.** About 216 cards, and cards within a week are not independent.
- **No length-matched control.** Some of the changes could come from a longer prompt rather than from what the profile says.
- **Two weeks used second-attempt profiles** (amendment 2): 2026-10-11 and 2026-11-08. The 2026-11-08 week, which shows the highest kappa, is one of them.
