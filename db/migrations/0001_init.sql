-- 0001_init.sql: ARI3LLA INDEX item store (SQLite 3.37+, STRICT tables).
-- Source: docs/MOONSHOTS_2026-09-22.md, Appendix D.1 (executed and tested
-- there on SQLite 3.45.1), plus schema_version and seeded sectors.
-- Never edit an applied migration; add 0002_*.sql instead.

CREATE TABLE schema_version (
  version     INTEGER PRIMARY KEY,
  applied_at  TEXT NOT NULL
) STRICT;

-- ---------- lookup / dimension tables ----------
CREATE TABLE sectors (
  sector_id     TEXT PRIMARY KEY,                       -- taxonomy.SOURCE_SECTORS
  coarse_group  TEXT NOT NULL CHECK (coarse_group IN
                ('designer_runway','editorial','social','retail','resale','other'))
) STRICT;

CREATE TABLE outlets (
  outlet_id  INTEGER PRIMARY KEY,
  domain     TEXT NOT NULL UNIQUE,
  region     TEXT,
  language   TEXT
) STRICT;

-- Slowly changing dimension (type 2): an outlet's sector can change over time
-- (e.g. a magazine turning into an affiliate-commerce site). Events are classified
-- by the mapping valid AT PUBLICATION TIME, not today's mapping.
CREATE TABLE outlet_sector_history (
  outlet_id   INTEGER NOT NULL REFERENCES outlets(outlet_id),
  sector_id   TEXT    NOT NULL REFERENCES sectors(sector_id),
  valid_from  TEXT    NOT NULL,
  valid_to    TEXT,                                     -- NULL = current
  rationale   TEXT    NOT NULL,
  PRIMARY KEY (outlet_id, valid_from),
  CHECK (valid_to IS NULL OR valid_to > valid_from)
) STRICT;

-- ---------- provenance: every claim must end at a row here ----------
CREATE TABLE items (
  item_id        INTEGER PRIMARY KEY,
  outlet_id      INTEGER NOT NULL REFERENCES outlets(outlet_id),
  url            TEXT    NOT NULL UNIQUE CHECK (url LIKE 'http%'),
  title          TEXT,
  published_at   TEXT    NOT NULL,
  ts_precision   TEXT    NOT NULL CHECK (ts_precision IN ('exact','day','week','snapshot_upper_bound')),
  fetched_at     TEXT    NOT NULL,
  content_hash   TEXT    NOT NULL,
  syndicated_of  INTEGER REFERENCES items(item_id),     -- NULL = original copy
  wayback_url    TEXT,
  source_method  TEXT    NOT NULL CHECK (source_method IN ('rss','wayback','commoncrawl','api','manual')),
  CHECK (published_at <= fetched_at),
  CHECK (syndicated_of IS NULL OR syndicated_of <> item_id)
) STRICT;
CREATE INDEX ix_items_outlet_pub ON items(outlet_id, published_at);
CREATE INDEX ix_items_hash       ON items(content_hash);

-- ---------- lexicon ----------
CREATE TABLE lexicon_versions (
  lexicon_version INTEGER PRIMARY KEY,
  created_at      TEXT NOT NULL,
  note            TEXT
) STRICT;

CREATE TABLE terms (
  term_id        TEXT PRIMARY KEY,                      -- slug, e.g. 'quiet-luxury'
  canonical      TEXT NOT NULL UNIQUE,
  signal_type    TEXT NOT NULL,
  merged_into    TEXT REFERENCES terms(term_id),        -- editor merges; chains allowed
  introduced_in  INTEGER NOT NULL REFERENCES lexicon_versions(lexicon_version),
  CHECK (merged_into IS NULL OR merged_into <> term_id)
) STRICT;

CREATE TABLE mentions (
  mention_id         INTEGER PRIMARY KEY,
  item_id            INTEGER NOT NULL REFERENCES items(item_id) ON DELETE RESTRICT,
  term_id            TEXT    NOT NULL REFERENCES terms(term_id),
  span_start         INTEGER NOT NULL,
  extractor_version  TEXT    NOT NULL,
  label_confidence   REAL    CHECK (label_confidence BETWEEN 0 AND 1),
  is_forecast        INTEGER NOT NULL DEFAULT 0 CHECK (is_forecast IN (0,1)),
  UNIQUE (item_id, term_id, span_start)
) STRICT;
CREATE INDEX ix_mentions_term_item ON mentions(term_id, item_id);

-- ---------- reports (the published record) ----------
CREATE TABLE reports (
  report_date        TEXT PRIMARY KEY CHECK (report_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
  window_start       TEXT NOT NULL,
  window_end         TEXT NOT NULL,
  collection_status  TEXT CHECK (collection_status IN ('normal','thin')),
  status             TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','published','quarantined')),
  CHECK (window_start <= window_end AND window_end <= report_date)
) STRICT;

-- SQLite forbids date('now') inside CHECK (non-deterministic), so the
-- "no future-dated reports" rule is a trigger. This is the rule whose absence
-- let an agent loop write 81 reports dated after today.
CREATE TRIGGER trg_reports_no_future_insert BEFORE INSERT ON reports
WHEN NEW.report_date > date('now') AND NEW.status <> 'quarantined'
BEGIN SELECT RAISE(ABORT, 'report_date is in the future'); END;

CREATE TRIGGER trg_reports_no_future_update BEFORE UPDATE OF report_date, status ON reports
WHEN NEW.report_date > date('now') AND NEW.status <> 'quarantined'
BEGIN SELECT RAISE(ABORT, 'report_date is in the future'); END;

CREATE TRIGGER trg_reports_insert_as_draft BEFORE INSERT ON reports
WHEN NEW.status = 'published'
BEGIN SELECT RAISE(ABORT, 'insert as draft, attach evidence, then publish'); END;

CREATE TABLE report_signals (
  report_date            TEXT NOT NULL REFERENCES reports(report_date) ON DELETE CASCADE,
  signal_id              TEXT NOT NULL,
  term_id                TEXT REFERENCES terms(term_id),
  name                   TEXT NOT NULL,
  confidence             TEXT NOT NULL CHECK (confidence IN ('low','medium','high','archival')),
  volatility             TEXT NOT NULL CHECK (volatility IN ('stable','emerging','seasonal','volatile',
                           'flash','microtrend','recurring','revival','long_tail','saturated','declining')),
  origin_classification  TEXT NOT NULL CHECK (origin_classification IN ('designer_originated',
                           'editorial_amplified','retail_adopted','social_amplified','platform_native',
                           'archive_revival','unclear')),
  human_editor_note      TEXT,
  PRIMARY KEY (report_date, signal_id)
) STRICT;

-- The provenance fix: a signal's evidence is a set of FK links to fetched items.
CREATE TABLE signal_evidence (
  report_date  TEXT    NOT NULL,
  signal_id    TEXT    NOT NULL,
  item_id      INTEGER NOT NULL REFERENCES items(item_id),
  PRIMARY KEY (report_date, signal_id, item_id),
  FOREIGN KEY (report_date, signal_id) REFERENCES report_signals(report_date, signal_id) ON DELETE CASCADE
) STRICT;

CREATE TRIGGER trg_publish_requires_evidence BEFORE UPDATE OF status ON reports
WHEN NEW.status = 'published' AND EXISTS (
  SELECT 1 FROM report_signals s
  WHERE s.report_date = NEW.report_date
    AND NOT EXISTS (SELECT 1 FROM signal_evidence e
                    WHERE e.report_date = s.report_date AND e.signal_id = s.signal_id))
BEGIN SELECT RAISE(ABORT, 'cannot publish: a signal has no linked evidence'); END;

-- ---------- forecast ledger (commit-reveal) ----------
CREATE TABLE prediction_batches (
  batch_hash    TEXT PRIMARY KEY CHECK (length(batch_hash) = 64),   -- sha256 hex of canonical JSON
  committed_at  TEXT NOT NULL,
  revealed_at   TEXT,
  CHECK (revealed_at IS NULL OR revealed_at > committed_at)
) STRICT;

CREATE TABLE predictions (
  batch_hash     TEXT    NOT NULL REFERENCES prediction_batches(batch_hash),
  term_id        TEXT    NOT NULL REFERENCES terms(term_id),
  horizon_end    TEXT    NOT NULL,
  p_breakout     REAL    NOT NULL CHECK (p_breakout BETWEEN 0 AND 1),
  PRIMARY KEY (batch_hash, term_id)
) STRICT;

CREATE TABLE outcomes (
  term_id      TEXT NOT NULL REFERENCES terms(term_id),
  horizon_end  TEXT NOT NULL,
  broke_out    INTEGER NOT NULL CHECK (broke_out IN (0,1)),
  PRIMARY KEY (term_id, horizon_end)
) STRICT;

-- ---------- views ----------
-- Resolve merge chains (a -> b -> c) to the final canonical term.
CREATE VIEW v_term_canonical AS
WITH RECURSIVE chain(term_id, current_id, depth) AS (
  SELECT term_id, term_id, 0 FROM terms
  UNION ALL
  SELECT c.term_id, t.merged_into, c.depth + 1
  FROM chain c JOIN terms t ON t.term_id = c.current_id
  WHERE t.merged_into IS NOT NULL AND c.depth < 20          -- cycle guard
)
SELECT c.term_id, c.current_id AS canonical_id, c.depth
FROM chain c JOIN terms t ON t.term_id = c.current_id
WHERE t.merged_into IS NULL;

-- One row per counted event: originals only, observations only, sector as of publication.
CREATE VIEW v_events AS
SELECT m.mention_id, tc.canonical_id, i.item_id, i.url, i.published_at, i.ts_precision,
       date(i.published_at, 'weekday 0', '-6 days') AS week_start,     -- Monday-start weeks
       o.domain, h.sector_id, s.coarse_group
FROM mentions m
JOIN v_term_canonical tc ON tc.term_id = m.term_id
JOIN items i   ON i.item_id = m.item_id
JOIN outlets o ON o.outlet_id = i.outlet_id
JOIN outlet_sector_history h
  ON h.outlet_id = i.outlet_id
 AND i.published_at >= h.valid_from
 AND (h.valid_to IS NULL OR i.published_at < h.valid_to)
JOIN sectors s ON s.sector_id = h.sector_id
WHERE i.syndicated_of IS NULL
  AND m.is_forecast = 0;

-- Exposure: how many original items the crawler saw per coarse sector per week.
CREATE VIEW v_exposure_weekly AS
SELECT s.coarse_group, date(i.published_at, 'weekday 0', '-6 days') AS week_start, COUNT(*) AS items
FROM items i
JOIN outlet_sector_history h
  ON h.outlet_id = i.outlet_id AND i.published_at >= h.valid_from
 AND (h.valid_to IS NULL OR i.published_at < h.valid_to)
JOIN sectors s ON s.sector_id = h.sector_id
WHERE i.syndicated_of IS NULL
GROUP BY 1, 2;

-- ---------- seed: sectors (taxonomy.SOURCE_SECTORS + 'unclear') ----------
-- coarse_group is the 5-sector view used by the models (moonshots section 3.5).
-- 'unclear' (unmapped domains) is excluded from cross-sector estimates.
INSERT INTO sectors (sector_id, coarse_group) VALUES
  ('designer_origin','designer_runway'), ('runway','designer_runway'),
  ('editorial','editorial'), ('independent_criticism','editorial'), ('trade_intelligence','editorial'),
  ('social','social'), ('street_ugc','social'),
  ('retail','retail'), ('resale','resale'),
  ('institutional','other'), ('visual_archive','other'), ('unclear','other');
