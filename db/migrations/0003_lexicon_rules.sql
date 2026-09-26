-- 0003: lexicon variants and editor rules.
-- terms (0001) holds one canonical name per term. A term is matched through its
-- surface variants, and the editor's usage note travels with the term.

CREATE TABLE term_variants (
  term_id          TEXT    NOT NULL REFERENCES terms(term_id),
  variant          TEXT    NOT NULL CHECK (length(trim(variant)) > 0),
  lexicon_version  INTEGER NOT NULL REFERENCES lexicon_versions(lexicon_version),
  PRIMARY KEY (term_id, variant)
) STRICT;

CREATE TABLE term_rules (
  term_id            TEXT    PRIMARY KEY REFERENCES terms(term_id),
  editor_note        TEXT,
  needs_sense_check  INTEGER NOT NULL DEFAULT 0 CHECK (needs_sense_check IN (0,1)),
  decided_at         TEXT    NOT NULL
) STRICT;

-- Counted events limited to items the style classifier did not rule out, and to
-- terms that need no sense check. model_version picks which classifier's
-- predictions to use, so the view is read with a WHERE on it.
CREATE VIEW v_events_style AS
SELECT e.*, p.model_version, p.calibrated_probability, p.conformal_set
FROM v_events e
JOIN label_predictions p ON p.item_id = e.item_id AND p.task = 'is_style_signal'
JOIN term_rules r ON r.term_id = e.canonical_id
WHERE r.needs_sense_check = 0
  AND p.conformal_set LIKE '%"yes"%';
