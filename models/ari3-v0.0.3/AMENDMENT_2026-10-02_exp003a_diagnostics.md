# EXP-003 amendment, 2026-10-02: EXP-003A post-hoc diagnostics

This file records observations made after the EXP-003A result existed. It refers to section 14 (Future findings) of `PREREGISTRATION.md` (commit `2ff1c53`, SHA-256 `fa65367d…`), which is unchanged. Nothing here alters the pre-registered design, the frozen gold (`7e15f2a1…`) or the frozen result (`1c78f56`). The H2 failure stands.

**Post-hoc.** Every breakdown here was chosen after the result was known. None of it was pre-registered, and none of it is a test. With 25 errors in 150 items, most group differences rest on a handful of items.

## Method

`src/ari3_exp003a_diagnose.py` (committed in `52f0eec` before any count) does the following:
- It re-derives each item's prediction from the frozen v0.0.2 weights and the same input text. It stops unless the re-derived outputs reproduce `result.json` exactly, and they do.
- It reads the store read-only.
- It fixes its heuristics in code:
  - very short excerpt: under 80 characters;
  - 4 equal-width time bins;
  - outlet and sector groups under 10 items are pooled;
  - word lists for fashion, beauty and business wording.
- Wording is classed as "explicit" (fashion words only), "mixed" (fashion words plus beauty or business words) or "indirect" (no fashion word).
- The original v0.0.2 test is described only from its frozen records: its 61 test labels and the append-only prediction ledger of 2026-09-26 20:40 UTC. The ledger reproduces the frozen test metrics (accuracy 0.902, decisive share 0.754, coverage 0.967).

The data, with no article text, is in `exp003a/diagnostics/diagnostics.json`. A table with headlines and excerpts is kept locally only.

## Breakdown (time holdout, n = 150)

| | Count |
|---|---|
| Errors | 25: 11 false positives (16% of gold no), 14 false negatives (17% of gold yes) |
| Confident correct / confident wrong | 90 / 11 (6 false positives, 5 false negatives) |
| Not sure, correct / not sure, wrong | 35 / 14 |

| Group | Errors / n |
|---|---|
| Editorial | 20 / 71 (28%) |
| Retail | 2 / 32 |
| Other (institutional) | 2 / 31 |
| Designer and runway | 1 / 16 |
| Language tag en | 20 / 120 |
| Language tag unknown | 0 / 17 |
| Language tags fr, ja, it (pooled) | 5 / 13 |
| Items with a Lexicon v1 term | 0 / 26 |
| Items with no Lexicon v1 term | 25 / 124 |
| Very short excerpt (< 80 chars) | 5 / 46 |
| Normal excerpt | 20 / 104 |
| Explicit wording | 14 / 82 |
| Mixed wording | 2 / 6 |
| Indirect wording | 9 / 62 |

Only three outlets reach 10 items. Who What Wear has 2 errors in 32 items, NOWFASHION 0 in 18 and Fashion Week Online 1 in 10. The other 36 outlets, pooled, have 22 errors in 90 items.

The four equal-width time bins, each about 20 hours, have error rates of 4/29, 5/30, 5/44 and 11/47.

## Comparison with the original v0.0.2 test (n = 61)

| | v0.0.2 test | EXP-003A holdout |
|---|---|---|
| Gold yes share | 0.590 | 0.547 |
| Editorial share | 0.475 | 0.473 |
| Distinct outlets | 29 | 39 |
| Language tags other than en and unknown | 3% (2 items) | 9% (13 items) |
| Excerpt length, median (quartiles) | 155 (51, 233) | 155 (61, 278) |
| Very short excerpts | 31% | 31% |
| Explicit / mixed / indirect wording | 52% / 10% / 38% | 55% / 4% / 41% |
| Items with any Lexicon v1 term | 28% | 17% |
| Errors (FP / FN) | 6 (3 / 3) | 25 (11 / 14) |
| Editorial errors | 6 / 29 | 20 / 71 |
| Non-editorial errors | 0 / 32 | 5 / 79 |
| Confident errors | 2 | 11 |
| Not-sure share | 0.246 | 0.327 |

Several features are close in the two samples: sector mix, excerpt length and wording mix. Three differ:
- The holdout contained more items tagged in languages other than English (13 against 2).
- It contained fewer items with a lexicon term (17% against 28%).
- It spread across more outlets.

In both samples, errors were concentrated in editorial items. Every one of the 6 test errors was editorial.

## Reading the 25 errors

These categories come from reading the stored headline and excerpt of each error. They are post-hoc and descriptive.

- **Beauty content in a fashion setting (5 false positives, 4 confident).** Makeup or fragrance items framed by fashion-week, runway or "look" wording: an eyeshadow guide, runway beauty looks, makeup trends at a fashion week, a fashion-week backstage beauty suite, a fragrance gift set. The scope rule (decision 0007) labels beauty as not style.
- **Industry and operations in trade press (3 false positives, 1 confident false negative).** Textile recycling, a lower-carbon supply-chain coalition, a street pedestrianisation date, and a digital product passport piece the editor labeled as style.
- **Collection and fashion-week coverage the model missed (about 8 false negatives).** Several are in French, Italian or Japanese, and three of the French and Italian items carry an `en` tag. Others are review prose, show-day diaries or designer profiles with few garment words, or a short excerpt under a collection headline.
- **People and profiles (3 false negatives, all confident).** A celebrity at a brand's show, a designer profile and a jeweller interview.
- **Other.** A watch release, an essay about fashion weeks, two fashion-week interview pages and a trail-running shoe.

## Hypotheses for a future, separately pre-registered experiment

None of these is tested here. Nothing has been changed.

1. **Beauty-in-fashion-context negatives are under-represented in training.**
   - Evidence: 5 of 11 false positives, 4 of them confident, are beauty items wrapped in fashion-week or "look" wording.
   - Test: count such items among the v0.0.2 training labels, then evaluate on new labels drawn for this category.
2. **Collection coverage written as review prose, or in languages other than English, is under-predicted.**
   - Evidence:
     - About 8 false negatives are collection or fashion-week items.
     - Languages other than English: 5 errors in 13 items, against 20 in 120 for `en`.
     - The original test held 2 such items.
   - Caveat: language tags are outlet-level and can be wrong.
3. **The boundary is weakest on editorial and trade-press items, and this predates the holdout.**
   - Evidence:
     - Editorial errors: 20/71 in the holdout, 6/29 in the test.
     - Errors outside editorial: 0/32 in the test, 5/79 in the holdout.
4. **Errors fall where no tracked style term appears.**
   - Evidence: 0 errors among the 26 items with a Lexicon v1 term, and all 25 among the 124 without one. The holdout also had fewer term-bearing items than the test (17% against 28%).
   - Caveat: this is descriptive. The model does not read lexicon terms.
5. **Calibration held while point accuracy fell.**
   - Evidence: coverage 0.927 and ECE 0.049, with 14 of 25 errors inside a not-sure set. The decision boundary, not the uncertainty estimate, is where the drop shows.
6. **Label edge cases may account for some confident errors.**
   - Evidence: industry items such as the digital product passport piece, and items close to the beauty line.
   - The owner's categorisation in the deck "EXP-003A confident errors" (11 items) will separate clear model errors from edge cases. Those categories are diagnostic only and never change the gold.

The vocabulary-drift and short-excerpt hypotheses get little support. Very short excerpts had a lower error rate (5/46) than normal ones (20/104), and their share was the same in both samples. The last time bin had the most errors (11/47), but four bins of about 40 items cannot separate drift from noise.
