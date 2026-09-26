# EXP-003 amendment, 2026-09-26: EXP-003B results and later findings

This file records results and observations made after data existed. It refers to section 14 (Future findings) of `PREREGISTRATION.md` (commit `2ff1c53`, SHA-256 `fa65367d…`), which is unchanged. Nothing here alters the pre-registered design.

## EXP-003B results (run once, 2026-09-26)

- **Labels:** 250 by the editor, made 2026-09-26 22:52 to 23:09 UTC, after the pre-registration commit (22:30 UTC). 35 forecasts in total (14 of 150 random items, 21 of 100 forecast-word items). Splits by the hash rule: 161 train (18 forecasts), 38 calibration (12), 51 test (5). Label fingerprint SHA-256 `ff36351a…`.
- **Frozen head:** `models/ari3-v0.0.3/is_forecast/`, manifest SHA-256 `c39b1f60…`. Temperature 1.837, conformal threshold recorded in the manifest.

| Hypothesis | Result | Verdict |
|---|---|---|
| H4: balanced accuracy ≥ 0.75 and above the majority baseline (both groups) | 0.50, equal to the baseline | Not supported |
| H5: conformal coverage ≥ 0.90 (both groups) | 0.961 | Supported |

By group (test items): random 31 items with 3 forecasts, balanced accuracy 0.50, coverage 0.935. Forecast-word 20 items with 2 forecasts, balanced accuracy 0.50, coverage 1.00.

The head answered "not a forecast" for every test item. Accuracy was 0.902, equal to always answering "not a forecast", and it caught 0 of 5 forecasts.

**Finding without a pass criterion:** of 976 style-filtered mentions, 0 fall in items the head marks as a confident forecast. The head does not change the counts, and under section 9 it is not used in them.

**Pre-registered interpretation (section 8, H4):** headline and excerpt text, read by this architecture, is not enough to separate predictions from reports. Forecast items stay in the counts.

## Later finding: exploratory diagnostic, not pre-registered

Run after the results, on the frozen head, with no refitting.

| Split | Items | Forecasts | Ranking (AUC) | Highest probability |
|---|---|---|---|---|
| Train | 161 | 18 | 0.985 | 0.408 |
| Calibration | 38 | 12 | 0.881 | 0.373 |
| Test | 51 | 5 | 0.674 | 0.363 |

- No item scored above 0.41, so the 0.50 decision point was never reached. With forecasts at 11% of training items, the logistic regression keeps probabilities low, and temperature scaling (T = 1.84) flattened them further.
- Ranking was near perfect on training items and weak on test items. The head fit its 18 training forecasts closely and generalized poorly. The test ranking rests on 5 forecasts, so it is highly uncertain.
- The pre-registered interpretation stands. The diagnostic adds that class imbalance and a fixed 0.50 decision point contributed, which the pre-registration did not anticipate. A later experiment that changes either would be a new, separately pre-registered experiment.

## EXP-003A status

Not yet run. It needs 150 labels on items fetched after 2026-09-26 19:25:40 UTC, collected over at least 3 days. On 2026-09-26 at 23:10 UTC, 56 such items existed.
