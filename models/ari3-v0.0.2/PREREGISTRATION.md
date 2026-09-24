# ARI3 v0.0.2: pre-registration

Written 2026-09-23, after ARI3 v0.0.1 was frozen and before any label for v0.0.2 existed. This file MUST NOT be edited after it is committed. A change of plan goes in a new, dated amendment file, and the results report says which plan was followed.

## Question

Does more human labeling, including one round of active learning, make ARI3's style classifier more decisive without losing accuracy, calibration or coverage?

## What changes

Only the training data changes. The labeled set grows from 145 to about 350.

The embedder and its revision, logistic regression with C = 1.0, temperature scaling, split conformal with α = 0.10 and the hash split rule stay the same. With one change at a time, any difference between versions comes from the data.

## Data plan

1. **Scope decision first.** Decided 2026-09-23 in decision 0007, before any new label: nails count as style, and makeup, skincare, fragrance, hair and beauty packaging do not. The labeling rule states this. v0.0.1's labels are kept as they were made.
2. **Random labels.** Finish the existing 300-item queue (about 155 more).
3. **Active learning round.** From the unlabeled items v0.0.1 marked `{yes, no}`, take the 50 with probability closest to 0.5 (uncertainty sampling, Settles 2009). The owner labels them.

## How it is evaluated

- **Test set.** Only items from the random queue whose hash puts them in the test split. Active-learning items are chosen by the model, which would bias a test set toward hard cases, so they are **excluded from test metrics** and reported separately.
- **Head-to-head.** v0.0.1 (frozen weights) and v0.0.2 are both scored on the same v0.0.2 test items. v0.0.1 never trained on them.
- **Metrics.** Accuracy with a Wilson 95% interval, precision, recall, 5-bin ECE, conformal coverage, decisive share, and errors outside the conformal set.

## Hypotheses

| # | Hypothesis | Counts as supported if |
|---|---|---|
| H1 | v0.0.2 is more decisive | Decisive share on the test set rises from v0.0.1's value to at least 0.70 |
| H2 | The coverage guarantee holds | Conformal coverage on the test set is at least 0.90 |
| H3 | Accuracy does not drop | v0.0.2 accuracy is no lower than v0.0.1's on the same test items |
| H4 | Calibration stays good | ECE after scaling is at most 0.10 |
| H5 | Active learning helps more than random labels | On the same test items, v0.0.2 beats a control trained on the same number of random labels only (no active-learning items) |

Every hypothesis is reported, including those that fail. Results go in the v0.0.2 model card.

## Stopping rule

The run happens once the scope decision is recorded and all labels in the data plan are in. There is no retraining after seeing test results. If a bug is found after seeing results, the fix and the rerun are both disclosed.
