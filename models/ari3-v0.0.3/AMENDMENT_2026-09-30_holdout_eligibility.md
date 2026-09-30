# EXP-003 amendment, 2026-09-30: EXP-003A eligibility rule, changed before labeling

This file amends the EXP-003A selection rule in section 5 of `PREREGISTRATION.md` (commit `2ff1c53`, SHA-256 `fa65367d…` of the committed file). That file is unchanged.

The 2026-09-26 amendment recorded results. Unlike that one, this amendment changes part of the pre-registered design. The problem was found before the EXP-003A labeling queue was created and before any `time_holdout` label existed. As of 2026-09-30 07:19 UTC, the item store (`data/store/ari3lla.db`) held 0 labels with the `time_holdout` split. That check counted rows and read no labels or outcomes.

## 1. The original rule and what it assumed

Section 5 selects "150 items fetched after 2026-09-26 19:25:40 UTC, the moment v0.0.2 was frozen." `make_holdout_queue` in `src/label_tool.py` implements this as `fetched_at > '2026-09-26T19:25:40Z'`. The protocol treated `fetched_at` as the time an item was first acquired by the store.

## 2. What inspection found

`upsert_item` in `src/item_store.py` overwrites `fetched_at` whenever a re-fetched item's title or summary has changed. The ingest log records 492 such updates across 39 runs up to 2026-09-30 04:33 UTC. So `fetched_at > '2026-09-26T19:25:40Z'` does not show that an item was first observed after the freeze. An item first stored before the freeze can carry a later `fetched_at`.

At 2026-09-30 07:19 UTC, the original rule admitted 2,270 items. For 52 of them, a store snapshot taken after the freeze (section 3) shows a `fetched_at` at or before the freeze, so those 52 items were in the store before v0.0.2 was frozen. None had an `is_style_signal` label, because the queue excludes labeled items. They still belong to the period the model was built in, which the time holdout exists to exclude. Their `published_at` values run from 2026-09-11 to 2026-09-26 13:30 UTC.

The eligibility rule is therefore amended here, before the queue is built and before any outcome label exists.

## 3. Snapshot check

No complete snapshot of the store exists from at or before 19:25:40 UTC. The scheduled backups keep only the newest 14, and the oldest surviving one is from 2026-09-27 12:30 UTC.

The nearest complete snapshot is `data/store/backups/pre-lexicon-v1-2026-09-26.db`, written at 2026-09-26 20:38:46 UTC, 73 minutes after the freeze and just before migration 0003. It holds 5,709 items. SHA-256 `11a99e1c9d4c82597509f10e57b1db7a713afb4b61e98a218fc1eb6068cd6b16`. The file is local and not in git.

Between the freeze and the snapshot, the ingest log records one run, 20:30:02 to 20:33:14 UTC, with 54 inserts and 2 updates. The snapshot has exactly 56 rows with a `fetched_at` after the freeze.

A second, independent record gives the same item set. At 2026-09-26 20:40:23 UTC, v0.0.2 wrote a prediction for every item then in the store to `label_predictions`, a table whose triggers block updates and deletes. The 5,709 item IDs in that write are identical to the snapshot's.

## 4. The amended rule

An item is eligible for EXP-003A only if all of the following hold:

1. **`published_at` is after 2026-09-26T19:25:40Z.** The database requires `published_at <= fetched_at` when a row is written, and no code path updates `published_at`. A row whose `published_at` is after the freeze was therefore first stored after the freeze.
2. **The section 5 filters still hold.** The item has a stored summary, is not a syndicated copy, and has no `is_style_signal` label.
3. **Once `first_seen_at` exists (migration 0004),** every selected item must also have a `first_seen_at` after the freeze. Any exception stops deck construction. A reconstructed `first_seen_at` can be later than the true first sighting, so it is never used on its own to establish eligibility.

The post-freeze snapshot and the append-only prediction ledger are used as independent contamination checks. They are not used to exclude items merely because the frozen model scored them after the freeze. Before the deck is built, every eligible item is checked against each record that carries a timestamp at or before the freeze: rows in any surviving backup with `fetched_at` at or before the freeze (matched by item ID and by URL), prediction-ledger rows written before the freeze, and labels created before the freeze. If any record shows that an eligible item already existed before the freeze, deck construction stops. The v0.0.2 prediction write at 20:40:23 UTC comes after the freeze, so it cannot show pre-freeze existence on its own. It is used to confirm that the snapshot's item set is complete.

All other parts of section 5 and the evaluation procedure are unchanged: the sample size of 150, the draw in turn from each sector with seed 13, the `is_style_signal` question and scope rule, the `time_holdout` split, hypotheses H1 to H3 and their thresholds, and the single run.

At 2026-09-30 07:40 UTC, 2,141 items met the amended rule. They come from 80 outlets and were published from 2026-09-26 19:27:57 to 2026-09-30 04:30 UTC. That spans 3.4 days, so the section 5 condition of at least 3 days of collection holds. The contamination check found no eligible item in any record from before the freeze. 9 eligible items were scored by v0.0.2 at 20:40:23 UTC. The snapshot shows them first stored between 20:30:30 and 20:33:12 UTC, after the freeze, and they remain eligible.

The pool grows with every ingest. The deck is drawn from the pool as it stands when the deck is built, and the EXP-003A manifest records the item list and its SHA-256.

## 5. Limitations of the amended rule

- `published_at` is the time the feed reports, and a feed can report it wrongly or change it upstream. Some feeds report an update time instead of a first-publication time, so an older article re-dated by its feed would pass rule 1. The rule does not guarantee that the article first appeared online after the freeze.
- 80 item IDs at or below 5,789 have no row in either the snapshot or the current store, so those items were removed before the freeze. If one of their URLs were collected again with a feed date after the freeze, it would receive a new ID and pass rule 1. The contamination check matches backup rows by URL as well as by ID, but it can see only the surviving backups, and no backup file was written before the freeze.
- The amended pool excludes 129 items the original rule admits (6%), all published at or before the freeze. The domain-shift threat in section 7 applies to the amended pool as written.

## 6. Code change

The commit that adds this file also changes `make_holdout_queue` in `src/label_tool.py` to apply rules 1 to 3 and the contamination check. The selector refuses to build the deck until `first_seen_at` exists, so rule 3 always applies.
