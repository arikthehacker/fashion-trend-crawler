-- 0004: immutable first-seen provenance for items.
--   published_at   when the outside world published the item (feed-reported)
--   first_seen_at  when ARI3 first acquired the item (set once, never changed)
--   fetched_at     when ARI3 last fetched a changed version of the item
-- Invariant, enforced below: published_at <= first_seen_at <= fetched_at.
--
-- first_seen_basis:
--   live_insert    stamped by the database from fetched_at at the moment the row
--                  was inserted. Exact to the ingest run's timestamp.
--   reconstructed  written once by src/backfill_first_seen.py for rows that existed
--                  before this migration. It is the earliest surviving evidence that
--                  ARI3 held the item, an upper bound on the true first sighting.
--                  It does not show that ARI3 had not seen the item earlier.
-- first_seen_evidence: NULL for live_insert. For reconstructed rows, the record
--   that supplied the value, e.g. 'current_fetched_at',
--   'backup:ari3lla-2026-09-27T1230Z.db', 'prediction_ledger:ari3-v0.0.2',
--   'label:is_style_signal'.

ALTER TABLE items ADD COLUMN first_seen_at TEXT;
ALTER TABLE items ADD COLUMN first_seen_basis TEXT
  CHECK (first_seen_basis IS NULL OR first_seen_basis IN ('live_insert', 'reconstructed'));
ALTER TABLE items ADD COLUMN first_seen_evidence TEXT;

-- A writer cannot choose a new row's first-seen values. The database sets them.
CREATE TRIGGER trg_items_first_seen_not_supplied BEFORE INSERT ON items
WHEN NEW.first_seen_at IS NOT NULL OR NEW.first_seen_basis IS NOT NULL OR NEW.first_seen_evidence IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'first_seen_* is set by the database, not by the writer'); END;

-- Every new row is stamped at insert time from the fetched_at it was written with.
-- An upsert that takes the ON CONFLICT DO UPDATE path is an UPDATE and does not fire this.
CREATE TRIGGER trg_items_first_seen_stamp AFTER INSERT ON items
BEGIN
  UPDATE items SET first_seen_at = NEW.fetched_at, first_seen_basis = 'live_insert'
  WHERE item_id = NEW.item_id;
END;

-- Write-once: the three columns can be set only while first_seen_at is NULL, which is
-- the stamp above or the one-time backfill. Setting them back to NULL is also blocked.
CREATE TRIGGER trg_items_first_seen_write_once
BEFORE UPDATE OF first_seen_at, first_seen_basis, first_seen_evidence ON items
WHEN OLD.first_seen_at IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'first_seen_* is write-once'); END;

-- Shape and ordering, checked on every update of a row that has a first-seen value,
-- including later fetched_at changes from the ingest upsert.
CREATE TRIGGER trg_items_first_seen_valid BEFORE UPDATE ON items
WHEN NEW.first_seen_at IS NOT NULL AND (
       NEW.first_seen_at NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z'
    OR NEW.first_seen_at < NEW.published_at
    OR NEW.first_seen_at > NEW.fetched_at
    OR NEW.first_seen_basis IS NULL
    OR (NEW.first_seen_basis = 'live_insert'   AND NEW.first_seen_evidence IS NOT NULL)
    OR (NEW.first_seen_basis = 'reconstructed' AND NEW.first_seen_evidence IS NULL))
BEGIN SELECT RAISE(ABORT, 'first_seen_* violates published_at <= first_seen_at <= fetched_at or its basis rules'); END;

-- A row can be missing first-seen values only if it was inserted before this migration
-- and the backfill has not run yet. The runbook runs the backfill in the same window
-- and then asserts: SELECT COUNT(*) FROM items WHERE first_seen_at IS NULL  ->  0.
