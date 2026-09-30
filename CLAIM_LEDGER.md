# ARI3 claim ledger

Every numerical or factual claim ARI3 makes about itself, with the committed artifact that supports it. A site page, README, case study or résumé line that states a result should cite a claim ID from this file.

## Rules

- A claim enters the ledger only when a committed artifact (a manifest, a pre-registration, an amendment or a migration) supports it. Planning notes and chat transcripts do not count.
- Claim IDs are never reused, and claims are never deleted. A claim that stops being true is re-statused, with the date and the reason in its notes.
- A claim about a count that changes over time (items, feeds, labels) carries an **As of** date and is marked `historical` once a newer count replaces it.
- A result is quoted with its sample size. Values are copied from the artifact, rounded to three decimals.

## Statuses

| Status | Meaning |
|---|---|
| `measured` | A value produced by a committed run, with no pre-registered pass criterion attached |
| `supported` | A pre-registered hypothesis whose criterion was met on the run named |
| `not_supported` | A pre-registered hypothesis whose criterion was not met. It stays in the ledger |
| `superseded` | Replaced by a later claim, named in **Superseded by** |
| `historical` | True on its **As of** date and describing a past state, such as a corpus size |

## Experiments and releases

Experiment IDs (EXP-001, EXP-002, …) and ARI3 release versions (v0.0.1, v0.0.2, …) are separate sequences. A release can contain several experiments, and an experiment can exist as research or infrastructure without belonging to a release. EXP-004 (grounded retrieval) does not imply ARI3 v0.0.4.

## Index

| ID | Claim | Status | As of |
|---|---|---|---|
| C-0001 | v0.0.1 held-out accuracy 0.882 (n = 34) | measured | 2026-09-23 |
| C-0002 | EXP-002 H1: v0.0.2 decisive share 0.754 | supported | 2026-09-26 |
| C-0003 | EXP-002 H2: v0.0.2 conformal coverage 0.967 | supported | 2026-09-26 |
| C-0004 | EXP-002 H3: v0.0.2 accuracy 0.902 vs v0.0.1 0.869 on the same items | supported | 2026-09-26 |
| C-0005 | EXP-002 H4: v0.0.2 ECE after scaling 0.025 | supported | 2026-09-26 |
| C-0006 | EXP-002 H5: active-learning arm accuracy 0.898 vs random arm 0.885 | supported | 2026-09-26 |
| C-0007 | EXP-003B H4: forecast detection balanced accuracy 0.50 | not_supported | 2026-09-26 |
| C-0008 | EXP-003B H5: forecast head conformal coverage 0.961 | supported | 2026-09-26 |
| C-0009 | The pre-registered EXP-003A selector admitted 52 items stored before the freeze | measured | 2026-09-30 |

## Claims

### C-0001
- **Claim:** Frozen ARI3 v0.0.1 (`is_style_signal`) classified its held-out test items with accuracy 0.882.
- **Status:** measured
- **As of:** 2026-09-23
- **Experiment:** EXP-001
- **Artifact:** `models/ari3-v0.0.1/manifest.json`, `metrics_test.test_accuracy` (manifest SHA-256 `f9f2c44b…`)
- **Result:** 0.882 (30 of 34 correct). Conformal coverage 1.000 on the same 34 items.
- **First valid commit:** `9c296bd`
- **Limitations:** n = 34. EXP-001 had no pre-registered criterion. The same model scored 0.869 on EXP-002's 61-item test split (C-0004), a different set of items.
- **Used in:** not yet audited
- **Superseded by:** none

### C-0002
- **Claim:** EXP-002 H1: frozen v0.0.2 gave a single-label (decisive) conformal answer on at least 70% of test items.
- **Status:** supported
- **As of:** 2026-09-26
- **Experiment:** EXP-002
- **Artifact:** `models/ari3-v0.0.2/manifest.json`, `hypotheses.H1` (manifest SHA-256 `d1cad506…`)
- **Result:** 0.754 (n = 61), up from 0.574 for v0.0.1 on the same items, against a threshold of 0.70
- **First valid commit:** `ec788a0`
- **Limitations:** n = 61, a single test split. A decisive answer is a single-label conformal set, which can still be wrong.
- **Used in:** not yet audited
- **Superseded by:** none

### C-0003
- **Claim:** EXP-002 H2: frozen v0.0.2's conformal sets covered the true label on at least 90% of test items.
- **Status:** supported
- **As of:** 2026-09-26
- **Experiment:** EXP-002
- **Artifact:** `models/ari3-v0.0.2/manifest.json`, `hypotheses.H2`
- **Result:** 0.967 (n = 61), against a threshold of 0.90
- **First valid commit:** `ec788a0`
- **Limitations:** n = 61. Coverage is guaranteed only on average over exchangeable data. EXP-003A tests it on later items.
- **Used in:** not yet audited
- **Superseded by:** none

### C-0004
- **Claim:** EXP-002 H3: v0.0.2 was at least as accurate as v0.0.1 on the same test items.
- **Status:** supported
- **As of:** 2026-09-26
- **Experiment:** EXP-002
- **Artifact:** `models/ari3-v0.0.2/manifest.json`, `hypotheses.H3` and `results_test`
- **Result:** 0.902 vs 0.869 (n = 61). 95% intervals [0.802, 0.954] and [0.762, 0.932]
- **First valid commit:** `ec788a0`
- **Limitations:** The intervals overlap heavily. The result supports "no worse" and does not show a difference in accuracy.
- **Used in:** not yet audited
- **Superseded by:** none

### C-0005
- **Claim:** EXP-002 H4: v0.0.2's expected calibration error after temperature scaling was at most 0.10.
- **Status:** supported
- **As of:** 2026-09-26
- **Experiment:** EXP-002
- **Artifact:** `models/ari3-v0.0.2/manifest.json`, `hypotheses.H4`
- **Result:** 0.025 (n = 61), against a threshold of 0.10. Before scaling: 0.152.
- **First valid commit:** `ec788a0`
- **Limitations:** ECE on 61 items with 5 bins is noisy
- **Used in:** not yet audited
- **Superseded by:** none

### C-0006
- **Claim:** EXP-002 H5: training with active-learning labels gave higher test accuracy than an equal number of random labels.
- **Status:** supported
- **As of:** 2026-09-26
- **Experiment:** EXP-002
- **Artifact:** `models/ari3-v0.0.2/manifest.json`, `hypotheses.H5` and `h5`
- **Result:** Mean 0.898 over 20 subsets (range 0.869 to 0.918) vs 0.885 for the random arm. Arm size 194, of which 35 active-learning labels.
- **First valid commit:** `ec788a0`
- **Limitations:** A difference of 0.013 on 61 test items is less than one item. The subsets vary more than the gap between arms.
- **Used in:** not yet audited
- **Superseded by:** none

### C-0007
- **Claim:** EXP-003B H4: the `is_forecast` head reached balanced accuracy of at least 0.75 and beat the majority baseline.
- **Status:** not_supported
- **As of:** 2026-09-26
- **Experiment:** EXP-003B
- **Artifact:** `models/ari3-v0.0.3/is_forecast/manifest.json`, `hypotheses.H4` (manifest SHA-256 `c39b1f60…`). `models/ari3-v0.0.3/AMENDMENT_2026-09-26_findings.md`
- **Result:** Balanced accuracy 0.50, equal to the majority baseline (n = 51, 5 forecasts). The head labeled every test item "not a forecast".
- **First valid commit:** `bbbaaf0`
- **Limitations:** 5 positive test items
- **Used in:** not yet audited
- **Superseded by:** none

### C-0008
- **Claim:** EXP-003B H5: the `is_forecast` head's conformal sets covered the true label on at least 90% of test items.
- **Status:** supported
- **As of:** 2026-09-26
- **Experiment:** EXP-003B
- **Artifact:** `models/ari3-v0.0.3/is_forecast/manifest.json`, `hypotheses.H5`
- **Result:** 0.961 (n = 51), against a threshold of 0.90
- **First valid commit:** `bbbaaf0`
- **Limitations:** Coverage was met while the head detected no forecasts (C-0007), so this claim says nothing about forecast detection.
- **Used in:** not yet audited
- **Superseded by:** none

### C-0009
- **Claim:** The EXP-003A selector as first pre-registered (`fetched_at` after the v0.0.2 freeze) admitted 52 items that a post-freeze snapshot shows were already in the store before the freeze. The rule was amended before any EXP-003A label existed.
- **Status:** measured
- **As of:** 2026-09-30
- **Experiment:** EXP-003A
- **Artifact:** `models/ari3-v0.0.3/AMENDMENT_2026-09-30_holdout_eligibility.md`, sections 2 and 3
- **Result:** 52 of 2,270 items admitted by the original rule. The amended rule admits 2,141 items, and none appears in a surviving record dated at or before the freeze.
- **First valid commit:** `3132885`
- **Limitations:** Counted against local backups that are not in git (the snapshot's SHA-256 is in the amendment). No backup from before the freeze survives.
- **Used in:** not yet audited
- **Superseded by:** none
