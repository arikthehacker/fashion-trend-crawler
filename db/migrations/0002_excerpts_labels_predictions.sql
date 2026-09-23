-- 0002_excerpts_labels_predictions.sql
-- 1. Keep a short text excerpt per item (the feed's own summary, capped in
--    code), its language and the feed it came from, so term extraction and
--    classifiers have text to learn from. Full article text is never stored.
-- 2. Labels with full provenance, and a split fixed at labeling time so
--    test and calibration labels can never leak into training.
-- 3. Classifier predictions (label_predictions; the forecast ledger's
--    `predictions` table from 0001 is separate) that can never be edited or deleted, so the model's
--    answer before human correction is kept (disagreements are the most
--    valuable training and error-analysis data).

ALTER TABLE items ADD COLUMN text_excerpt TEXT;
ALTER TABLE items ADD COLUMN lang TEXT;
ALTER TABLE items ADD COLUMN feed_url TEXT;

CREATE TABLE labels (
  label_id       INTEGER PRIMARY KEY,
  item_id        INTEGER NOT NULL REFERENCES items(item_id),
  task           TEXT    NOT NULL,                  -- e.g. 'is_style_signal', 'is_forecast', 'term_present:quiet-luxury'
  label          TEXT    NOT NULL,
  source         TEXT    NOT NULL CHECK (source IN ('human','teacher')),
  labeler        TEXT    NOT NULL,                  -- a person's name for human labels, a model id for teacher labels
  model_version  TEXT,                              -- teacher model version (NULL for human labels)
  confidence     REAL    CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1),
  split          TEXT    NOT NULL CHECK (split IN ('train','calibration','test','time_holdout')),
  created_at     TEXT    NOT NULL,
  note           TEXT,
  UNIQUE (item_id, task, source, labeler)
) STRICT;
CREATE INDEX ix_labels_task_split ON labels(task, split);

CREATE TABLE label_predictions (
  prediction_id          INTEGER PRIMARY KEY,
  item_id                INTEGER NOT NULL REFERENCES items(item_id),
  task                   TEXT    NOT NULL,
  model_version          TEXT    NOT NULL,
  predicted_label        TEXT    NOT NULL,
  probability            REAL    CHECK (probability IS NULL OR probability BETWEEN 0 AND 1),
  calibrated_probability REAL    CHECK (calibrated_probability IS NULL OR calibrated_probability BETWEEN 0 AND 1),
  conformal_set          TEXT,                      -- JSON list of labels in the set
  created_at             TEXT    NOT NULL
) STRICT;
CREATE INDEX ix_label_predictions_item_task ON label_predictions(item_id, task);

CREATE TRIGGER trg_label_predictions_no_update BEFORE UPDATE ON label_predictions
BEGIN SELECT RAISE(ABORT, 'predictions are append-only: record a new prediction instead'); END;

CREATE TRIGGER trg_label_predictions_no_delete BEFORE DELETE ON label_predictions
BEGIN SELECT RAISE(ABORT, 'predictions are append-only and are never deleted'); END;
