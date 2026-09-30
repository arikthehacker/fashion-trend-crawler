# Runbook: deploying migration 0004 (first-seen provenance)

Migration 0004 (`db/migrations/0004_first_seen.sql`) adds `first_seen_at`, `first_seen_basis` and `first_seen_evidence` to `items`, with triggers that stamp new rows and make the values write-once. `src/backfill_first_seen.py` fills the rows that existed before the migration.

`src/run_ingest.py` applies every pending file in `db/migrations/` at the start of each scheduled run. Creating `db/migrations/0004_first_seen.sql` is therefore the deployment, and happens only at step 5 below.

## Preconditions (all must hold, or the deployment is skipped)

1. The EXP-003A amendment is committed and CI is green.
2. `python src/test_backfill_first_seen.py` passes, and a rehearsal on a copy of the store (steps 5 to 9 against the copy) passed.
3. No ingest process is running. `schtasks /Query /TN "ARI3LLA ingest" /V /FO LIST` shows `Status: Ready`, and no `python` process has `run_ingest` in its command line.
4. At least 15 minutes remain before the next scheduled run. Runs start at 00:30, 04:30, 08:30, 12:30, 16:30 and 20:30 UTC and take about 4 minutes.

## Steps

1. **Backup.** `VACUUM INTO data/store/backups/pre-0004-first-seen-<UTC stamp>.db`. The rotation in `run_ingest.py` prunes only `ari3lla-*.db`, so this file is kept.
2. **Record** the item count, `v_events_style` count, label count and label SHA-256 (`science_counts()` in the backfill script), and the SHA-256 of the backup file.
3. **Freeze the evidence.** Copy every file in `data/store/backups/` to `data/store/first-seen-evidence-<date>/`, a folder the rotation never touches.
4. **Dry run** against the live store, read-only:
   `python src/backfill_first_seen.py --backups data/store/first-seen-evidence-<date>`
   It must report 0 invariant failures. Note the fingerprint.
5. **Install** the migration as `db/migrations/0004_first_seen.sql`. Before deployment it was kept as `design/0004_first_seen_PROPOSED.sql.txt`, outside the folder ingestion applies.
6. **Migrate** by hand: `python src/item_store.py init`. It must report `applied migrations [4]`.
7. **Backfill:**
   `python src/backfill_first_seen.py --backups data/store/first-seen-evidence-<date> --apply --expect-fingerprint <step 4>`
   It runs in one transaction and rolls back unless every post-condition holds: every planned row updated, no NULL `first_seen_at`, `published_at <= first_seen_at <= fetched_at` everywhere, planned rows `reconstructed`, any other rows `live_insert`, and science counts identical to step 2.
8. **Verify** again from a fresh connection: the same counts as step 2, and `PREREGISTRATION.md` and the EXP-003 manifests unchanged (`git status models/`).
9. **Tests and gate:** `python -m py_compile src/*.py`, every `src/test_*.py`, and `python src/validate_all_reports.py`.
10. **Commit** `db/migrations/0004_first_seen.sql` (removing the design copy) and the test update for migration 4.
11. **Observe** the next scheduled run. New rows must be `live_insert`, with `first_seen_at` equal to their original `fetched_at`.

## If something fails

- The migration and the backfill each run in a single transaction. A failure in either leaves the store as it was before that step.
- If the migration applied but the backfill failed, the store holds NULL `first_seen_at` for old rows, while new rows are stamped correctly. That state is safe for ingestion. Stop, keep the step 1 backup, and report. Do not repair the live store by hand.
- If any post-condition fails after commit, stop and report. The step 1 backup is the restore point, and restoring it is the owner's decision.

## What the reconstructed values mean

A reconstructed `first_seen_at` is the earliest surviving record that ARI3 held the item: its current `fetched_at`, a backup row matched by item ID and URL, an append-only prediction row, or a label. It can be later than the true first sighting. It is suitable for historical replay, where it can only exclude evidence ARI3 had. It is never used on its own to prove that an item arrived after a given time.

## Deployment record, 2026-09-30

- **Window:** 07:50 to 07:51 UTC. Scheduler `Ready`, no ingest process running, next run at 08:30 UTC.
- **Backup:** `data/store/backups/pre-0004-first-seen-2026-09-30T0750Z.db`, integrity `ok`, 7,955 items, SHA-256 `58013f87d5a4fcad6b37baffdf09a95fa78a132acf0dfad3c454da315221bfc5`. Local, not in git.
- **Evidence:** 15 backups copied to `data/store/first-seen-evidence-2026-09-30/`.
- **Dry run:** 7,955 rows. Winning sources: current `fetched_at` 7,738, backups 142, prediction ledgers 69, labels 6. 0 rejected, 0 invariant failures. 217 items reconstructed earlier than their current `fetched_at`. Fingerprint `8d79deafb2f46e5d2ec60ef94f30ab25da8b13673c3b1b1a16334dac6b185835`, identical to the rehearsal on a copy.
- **Migration:** `applied migrations [4]`. **Backfill:** applied with that fingerprint. Every post-condition held.
- **After:** 7,955 `reconstructed`, 0 NULL, 0 ordering violations, `integrity_check` ok. Items 7,955, style events 1,463, mentions 1,182, labels 600 (SHA-256 unchanged), prediction rows 8,215: all identical to before.
