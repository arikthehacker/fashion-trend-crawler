# EXP-003 INTEGRITAS: pre-registration

**Release:** ARI3 v0.0.3 INTEGRITAS, "The evidence can be trusted."
**Sub-experiments:** EXP-003A Temporal Generalization, EXP-003B Forecast Detection.
**Written:** 2026-09-26, before any EXP-003 label exists.

This file MUST NOT be edited after it is committed. A change of plan goes in a new, dated amendment file, and the results report says which plan was followed.

---

## 1. Why this experiment exists

Every evaluation of ARI3 so far has used articles collected before the model was trained. Those tests show how well the model fits the period it learned from. They cannot show how it behaves on the articles it will meet in use, because by the time the model runs, the news has moved on: new designers, new collections, new phrasing, and outlets whose coverage shifts from week to week. A model that looks accurate on its own period can still fail on the next one. The only fair test of that is data that did not exist when the model was frozen.

There is already a sign that this matters. On its test set, ARI3 v0.0.2 answered "not sure" for 25% of items. Across the whole stored corpus it answered "not sure" for 42%. Either the corpus contains harder items than the labeled sample, or the model is less at home on material it has not seen. A prospective test separates the two.

The second problem sits one step further down the pipeline. ARI3 counts style terms in articles, and later models will read those counts as evidence of what style culture is doing. An article that says a look "will be big next season" is a prediction, not an observation. Counted as a mention, it feeds the press's own forecasts back into the evidence. That is circular, and it must be fixed before any model of trends reads the counts.

Both problems ask the same question: can the evidence ARI3 produces be trusted? EXP-003A tests whether its judgments hold on new data. EXP-003B tests whether it can separate observations from predictions. Together they are INTEGRITAS.

---

## 2. Experiment at a glance

| | |
|---|---|
| Release | ARI3 v0.0.3 INTEGRITAS |
| Central question | Can the evidence ARI3 produces be trusted? |
| EXP-003A Temporal Generalization | Does frozen ARI3 v0.0.2 hold up on articles collected after it was frozen? |
| EXP-003B Forecast Detection | Can the shared perception architecture learn to tell a prediction from a report? |
| Models | ARI3 v0.0.2 `is_style_signal` head, frozen and not refit (003A). A new `is_forecast` head (003B) |
| Datasets | 150 time-holdout style labels on post-freeze items (003A). 250 `is_forecast` labels, 150 random and 100 forecast-word items (003B) |
| Hypotheses | H1 to H3 (003A), H4 and H5 (003B) |
| Deliverables | Results for all five hypotheses, a frozen and hashed `is_forecast` head, a model card, and a notebook entry in the ARI3 research notebook |

---

## 3. Terminology

- **Release:** a named, versioned state of ARI3, such as v0.0.3 INTEGRITAS. A release is frozen and hashed, and it is never changed after it is committed.
- **Experiment:** a pre-registered test with its own ID, such as EXP-003, run once and reported in full.
- **Sub-experiment:** one research question inside an experiment, such as EXP-003A. Each has its own data and hypotheses.
- **Perception Task:** one yes-or-no question ARI3 asks of an article, such as `is_style_signal` or `is_forecast`.
- **Perception Model Family:** the set of perception tasks that share one architecture (section 4).
- **Model Head:** the part trained for a single task: its logistic regression weights, temperature and conformal threshold.
- **Dataset:** a fixed set of items and labels, identified by a SHA-256 fingerprint.
- **Labeling Queue:** the list of items shown to the editor for one task, together with the question, the rule and each item's group.
- **Prediction Set:** a model's conformal output for one item: `{yes}`, `{no}`, or `{yes, no}` when it is not sure.
- **Time Holdout:** labels on items collected after a model was frozen. They are used only for testing, never for training or calibration.

---

## 4. The Perception Model Family

ARI3's perception layer is a family of independent tasks built on one shared architecture. Each task asks one yes-or-no question of an article and has its own labels, its own trained head, its own calibration and its own conformal threshold. The architecture is the same for every task:

```
Article (headline + feed excerpt, up to 1,000 characters)
  → Sentence-BERT embedding
      paraphrase-multilingual-MiniLM-L12-v2, revision e8f8c21, 384 dimensions, frozen
  → Logistic regression (L2, C = 1.0), one head per task
  → Temperature scaling on the task's calibration split
  → Split conformal prediction at α = 0.10
  → Prediction set {yes}, {no}, or {yes, no}
  → {yes} or {no}: used as the answer. {yes, no}: meant for human review
```

| Task | Question | Status |
|---|---|---|
| `is_style_signal` | Is this item about style? | Released in v0.0.1 and v0.0.2 |
| `is_forecast` | Does this item predict what will happen, instead of reporting what happened? | New in EXP-003B |

A new perception task needs only new labels and a new head. The embedding, the calibration method, the conformal step and the evaluation are inherited unchanged.

---

## 5. EXP-003A: Temporal Generalization

**Question.** Does frozen ARI3 v0.0.2 hold up on articles collected after it was frozen?

**Model.** ARI3 v0.0.2 exactly as released (commit `ec788a0`). It is not refit, recalibrated or retuned.

**Data.**
- 150 items fetched after 2026-09-26 19:25:40 UTC, the moment v0.0.2 was frozen, collected over at least 3 days.
- Drawn in turn from each sector (seed 13). Items already labeled for this task are excluded.
- The editor labels them with the same `is_style_signal` question and the same scope rule (decision 0007: nails count as style, and makeup, skincare, fragrance, hair and beauty packaging do not).
- These labels get the `time_holdout` split. They are never used for training or calibration.

### Hypotheses

**H1. The coverage guarantee holds on new items.**
Supported if conformal coverage on the time holdout is at least 0.90.
*Reason:* 0.90 is the coverage target (α = 0.10) set for every ARI3 release.

**H2. Accuracy holds on new items.**
Supported if accuracy on the time holdout is at least 0.85.
*Reason:* 0.85 sits about 5 points below v0.0.2's held-out accuracy of 0.902, which allows for ordinary sampling noise on 150 items while still flagging a real drop.

**H3. The not-sure rate on new items matches the test set, not the whole corpus.**
Supported if the share of `{yes, no}` answers on the time holdout is at most 0.35.
*Reason:* 0.35 lies between v0.0.2's not-sure share on its test set (0.25) and on the whole corpus (0.42), so the result shows which of the two new data resembles.

---

## 6. EXP-003B: Forecast Detection

**Question.** Can the shared perception architecture learn to tell a prediction from a report?

**Model.** A new `is_forecast` head in the Perception Model Family (section 4), with the same architecture and settings as the style task.

**Data.**
- 250 items: 150 chosen at random (drawn in turn from each sector) and 100 whose headline or excerpt contains a forecast word (will, trend, predict, forecast, next season, 2027). Seed 11.
- Forecasts are expected to be rare. The random items alone would hold too few to learn from, so the forecast-word items enrich the sample.
- The forecast-word match is a plain text match, so it also matches words that contain these strings. It only decides which items enter the enriched group.
- The editor answers: "Does this item predict what will happen, instead of reporting what happened?" Yes: forecasts, trend predictions, "will be", "for 2027". No: reports, reviews, releases, announcements of things that exist.
- Splits are fixed by the same SHA-256 hash rule as the style task. Each label records which group its item came from.
- Test metrics are reported for both groups together and for each group separately, because the forecast-word items are not a random sample.

### Hypotheses

**H4. The model learns the task.**
Supported if balanced accuracy on the test items (both groups together) is at least 0.75, and above the majority-class baseline.
*Reason:* balanced accuracy averages the accuracy on predictions and on reports, so a rare class cannot hide behind a high overall score. 0.75 is well above the 0.50 of guessing, and below the style task's 0.90, because forecasts are rarer and phrased more subtly.

**H5. The coverage guarantee holds for the new task.**
Supported if conformal coverage on the test items is at least 0.90.
*Reason:* the new task inherits the family's coverage target of 0.90 (α = 0.10).

**Reported without a pass criterion:** the share of style-filtered mentions that fall in items the `is_forecast` model marks as forecasts. It measures how much the current counts would change, and is reported as a finding.

---

## 7. Threats to validity

Known limits, recorded before the experiment runs.

- **Labeling subjectivity.** One editor labels every item. Both tasks involve judgment, and no second labeler measures agreement.
- **Small samples.** 150 time-holdout items and about 50 `is_forecast` test items give wide intervals. A few items can move a result across a threshold.
- **Source bias.** About 87% of stored items come from editorial outlets, so small sectors contribute few items to either dataset.
- **Multilingual embedding limits.** The embedder covers many languages, but most labeled items are tagged English, so performance on other languages is barely measured.
- **Forecast-word sampling bias.** The 100 enriched items are chosen by words that forecasts often use. The model may learn those words instead of the idea of a prediction, and results on the enriched group do not describe the corpus.
- **Domain shift.** Post-freeze items differ from older items in time and possibly in topic and outlet mix. EXP-003A measures the effect of that shift. It cannot separate its causes.
- **Short time window.** Three days of post-freeze collection covers one short stretch of the news cycle, so a result may not hold for later periods.

---

## 8. Failure interpretation

Written before any result exists, to fix in advance what each outcome would mean.

- **If H1 fails** (coverage below 0.90 on new items): the conformal guarantee depends on new data resembling the calibration data, and this result would mean it does not. Calibration on old data would not be enough, and later work would need calibration that adapts as the news changes.
- **If H2 fails** (accuracy below 0.85): the boundary v0.0.2 learned would be tied to the period it was trained on. Later work would need labels drawn from newer periods and a regular check of accuracy on fresh items.
- **If H3 fails** (not-sure share above 0.35): new articles would be harder for v0.0.2 than its test set, and the 42% corpus rate would reflect the model's unfamiliarity rather than harder items in the corpus. Human review load would grow over time unless the model is refreshed.
- **If H4 fails** (balanced accuracy below 0.75): headline and excerpt text, read by this architecture, would not be enough to separate predictions from reports. Forecast detection would need more labels, more context from the article, or a different kind of model, and forecast items would stay in the counts until then.
- **If H5 fails** (coverage below 0.90 for `is_forecast`): the new head's uncertainty would not be reliable enough to decide which items need human review, and its predictions could not be used to filter counts.
- **If every hypothesis is supported:** v0.0.2 would be shown to hold on data it could not have seen, and the counts could begin excluding forecasts in a later release.

---

## 9. Release criteria

Release criteria decide when v0.0.3 is complete. They are separate from the hypotheses: a release is complete when the work is done and reported, whatever the results.

v0.0.3 INTEGRITAS is complete when all of the following are true:

1. This pre-registration is committed before any EXP-003 label exists, and its committed text is unchanged when results are published.
2. EXP-003A has been run once on 150 time-holdout labels, with frozen v0.0.2.
3. EXP-003B has been run once on 250 `is_forecast` labels, and the new head is frozen and hashed.
4. All five hypotheses are reported with their values and verdicts, including any that fail.
5. The results are published in the ARI3 research notebook, with any analysis choice not written here listed as such.
6. `is_forecast` does not change any count until those results are published.

---

## 10. What is frozen

Once this pre-registration is committed, the following cannot change without a dated amendment:

- the hypotheses H1 to H5 and their wording
- the thresholds: 0.90 coverage, 0.85 accuracy, 0.35 not-sure share, 0.75 balanced accuracy
- the datasets: 150 time-holdout items and 250 `is_forecast` items, with the selection rules above
- the splits: `time_holdout` for EXP-003A, and the SHA-256 hash rule for EXP-003B
- the seeds: 13 for EXP-003A, 11 for EXP-003B
- the labeling rules: both questions and the style scope rule (decision 0007)
- the model architecture in section 4, including α = 0.10
- the evaluation metrics: coverage, accuracy, not-sure share, balanced accuracy, and the per-group reporting for EXP-003B
- the release criteria in section 9

---

## 11. Reproducibility checklist

| Artifact | Status |
|---|---|
| Pre-registration commit | Planned: the commit that adds this file |
| ARI3 v0.0.2 release commit | Available: `ec788a0` |
| ARI3 v0.0.3 release commit | Planned |
| Dataset fingerprints | Available for v0.0.2 labels: SHA-256 `20ca8e4a…`. Planned for both EXP-003 datasets, recorded in the release manifest |
| Model hashes | Available for v0.0.2 weights: SHA-256 `f6b25eb4…`. Planned for the `is_forecast` head |
| Manifest hashes | Available for v0.0.2: `d1cad506…`. Planned for v0.0.3 |
| Random seeds | 13 (EXP-003A queue), 11 (EXP-003B queue). Model fitting is deterministic |
| Software versions | Tracked for the evaluation charts (Python 3.13.2, numpy 2.5.0, scikit-learn 1.9.1). Planned for the v0.0.3 manifest, with runtime |
| Model card | Available for v0.0.2. Planned for the `is_forecast` head |
| Results notebook | Planned: an EXP-003 entry in the ARI3 research notebook |
| Labeling queue definitions | Available in code: `make-holdout-queue` and `make-forecast-queue` in `src/label_tool.py`. The item lists are kept locally. Planned: their fingerprints in the release manifest |

---

## 12. Architecture evolution

**v0.0.2**

```
RSS feeds
  → Perception: is_style_signal
  → Style-filtered items
  → Mentions of lexicon terms
```

**v0.0.3**

```
RSS feeds
  → Perception Model Family (shared embedding, calibration, conformal)
      ├── is_style_signal   frozen v0.0.2, tested on post-freeze items (EXP-003A)
      └── is_forecast       new head (EXP-003B)
  → Shared output: items that are about style and are not predictions
  → Mentions of lexicon terms
  → Future temporal models (Style R₀, latent salience)
```


v0.0.3 introduces ARI3's first multi-task perception architecture, with style perception and forecast perception side by side. Later perception tasks reuse the shared embedding, calibration and conformal step, and add only their own labels and model head.

---

## 13. Stopping rule

EXP-003A runs once the 150 time-holdout labels are in. EXP-003B runs once the 250 `is_forecast` labels are in. Each runs once. There is no retraining after seeing test results. A bug found after seeing results is fixed, and both the fix and the rerun are disclosed.

---

## 14. Future findings

Observations made after results exist belong here, separate from the pre-registered hypotheses, so that a later finding is never mistaken for a commitment made in advance. Because this file is never edited after it is committed, findings are recorded in a dated amendment file that refers to this section.

In the committed file, this section is empty.
