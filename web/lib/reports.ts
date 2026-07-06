// lib/reports.ts
// reads dated ARI3LLA INDEX report JSON files from data/reports/ for the
// archive and per-date report pages. Separate from trends.ts (homepage data
// layer) so that file is left untouched.

import fs from "fs";
import path from "path";

export interface CollectionWindow {
  start: string;
  end: string;
}

export interface TopSignal {
  name: string;
  type: string;
  source_sectors: string[];
  confidence: string;
  volatility: string;
  origin_classification: string;
  evidence: string;
  index_note: string;
  signal_id?: string;
  source_corroboration_count?: number;
  human_editor_note?: string;
  // Outlet homepage domains (e.g. "vogue.com"), NOT per-article URLs.
  // Deliberately homepage-level only -- a per-article permalink to a small/
  // independent outlet was identified as a "hug of death"/pile-on risk (see
  // docs/agent-logs/source-protection-review-run33.md and the resolution in
  // docs/agent-logs/source-citation-resolution-run36.md). Not yet rendered
  // on any page -- schema/data-layer only for now.
  source_domains?: string[];
}

export interface Report {
  report_date: string;
  collection_window: CollectionWindow;
  sources_scanned: number;
  items_collected: number;
  source_sector_breakdown: Record<string, number>;
  executive_summary: string;
  top_signals: TopSignal[];
  repeated_keywords: string[];
  garments: string[];
  silhouettes: string[];
  materials: string[];
  colors: string[];
  aesthetic_terms: string[];
  cultural_references: string[];
  limitations: string[];
  archive_tags: string[];
  confidence_notes?: string;
  volatility_notes?: string;
  incentive_notes?: string;
  human_editor_note?: string;
  content_hash?: string;
  revision_history?: RevisionEntry[];
  collection_status?: string;
  thin_week_note?: string;
  review_status?: string;
  reviewed_by?: string;
}

export interface RevisionEntry {
  previous_content_hash: string;
  corrected_at: string;
  reason: string;
}

function reportsDir(): string {
  return path.join(process.cwd(), "..", "data", "reports");
}

// Module-level cache: every helper below calls getAllReports(), and a single
// page render can call several of those helpers (e.g. the homepage calls
// getLatestReport() and getThisWeeksIndex(); the archive page calls
// getAllReports(), getConsecutiveThinWeekCount(), and getThisWeeksIndex()).
// Without caching, one page load re-reads and re-parses every report file on
// disk once per helper call. Report files are static build-time input (this
// is a Next.js static export, not a long-running server watching for writes),
// so caching for the lifetime of the process is safe.
let allReportsCache: Report[] | null = null;

/** Returns all reports, newest report_date first. */
export function getAllReports(): Report[] {
  if (allReportsCache) return allReportsCache;

  const dir = reportsDir();
  if (!fs.existsSync(dir)) return (allReportsCache = []);

  const files = fs.readdirSync(dir).filter((f) => f.endsWith(".json"));
  const reports = files.map((f) =>
    JSON.parse(fs.readFileSync(path.join(dir, f), "utf-8")) as Report
  );

  allReportsCache = reports.sort((a, b) => (a.report_date < b.report_date ? 1 : -1));
  return allReportsCache;
}

/** Returns the most recently dated report, or null if the archive is empty. */
export function getLatestReport(): Report | null {
  const reports = getAllReports();
  return reports.length > 0 ? reports[0] : null;
}

/** Returns a single report by its report_date (YYYY-MM-DD), or null. */
export function getReportByDate(date: string): Report | null {
  const dir = reportsDir();
  const filePath = path.join(dir, `${date}.json`);
  if (!fs.existsSync(filePath)) return null;
  return JSON.parse(fs.readFileSync(filePath, "utf-8")) as Report;
}

export interface TimelineEntry {
  report_date: string;
  signal_name: string;
  type: string;
  source_sectors: string[];
  confidence: string;
  signal_id?: string;
}

/**
 * Flattens top_signals from every report into a single reverse-chronological
 * list for the /timeline page. Keys on signal name + date only — there is no
 * signal_id/slug field yet, so no cross-report identity matching is attempted
 * here.
 */
export function getTimelineEntries(): TimelineEntry[] {
  const reports = getAllReports();
  const entries: TimelineEntry[] = [];

  for (const report of reports) {
    for (const signal of report.top_signals ?? []) {
      entries.push({
        report_date: report.report_date,
        signal_name: signal.name,
        type: signal.type,
        source_sectors: signal.source_sectors,
        confidence: signal.confidence,
        signal_id: signal.signal_id,
      });
    }
  }

  return entries;
}

/** Returns all report_date strings, for static params generation. */
export function getAllReportDates(): string[] {
  const dir = reportsDir();
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".json"))
    .map((f) => f.replace(/\.json$/, ""));
}

export interface SignalOccurrence {
  report_date: string;
  signal: TopSignal;
}

/**
 * Returns every occurrence of a given signal_id across all reports,
 * oldest first (chronological), for the /signals/[slug] history page.
 */
export function getSignalHistory(slug: string): SignalOccurrence[] {
  const reports = getAllReports();
  const occurrences: SignalOccurrence[] = [];

  for (const report of reports) {
    for (const signal of report.top_signals ?? []) {
      if (signal.signal_id === slug) {
        occurrences.push({ report_date: report.report_date, signal });
      }
    }
  }

  return occurrences.sort((a, b) => (a.report_date < b.report_date ? -1 : 1));
}

export interface RecurringSignal {
  signal_id: string;
  name: string;
  occurrence_count: number;
  first_seen: string;
  last_seen: string;
  origin_classification: string;
  is_style_aesthetic: boolean;
}

/**
 * `Signal.type` values observed across the archive that describe a genuine
 * style-aesthetic thread (a look, silhouette, material, or cultural mood
 * that could plausibly be "trending") rather than a factual/administrative
 * tracking item (an award outcome, a debut timeline, a policy, a retail-
 * calendar event, a coverage gap). Added run 48 -- see
 * docs/agent-logs/recurrence-threshold-revision-run48.md. Everything not in
 * this list (institutional_policy, designer_signal, market_behavior,
 * industry_recognition, media_integrity, industry_event,
 * retail_calendar_event, and any future/unrecognized type) is treated as
 * non-style for the retrospective-trigger threshold, since run 47 found
 * those are exactly the items recurring mechanically via carry-forward
 * rather than genuine re-emergence. Includes the two known data typos
 * ("styling behavior", "aesthetic") rather than requiring a backfill.
 */
const STYLE_AESTHETIC_TYPES = new Set([
  "styling_behavior",
  "styling behavior",
  "silhouette",
  "aesthetic_term",
  "aesthetic",
  "cultural_term",
  "color",
  "social_observation",
]);

/**
 * Returns signal_ids that appear in `minOccurrences` or more distinct
 * reports (default 4, matching the revisit threshold set in run 24's
 * retrospective-format research and re-confirmed at run 32). Used by the
 * archive page's "recurring across the archive" note -- a small, honest
 * surface of the same underlying data /signals/[slug] already tracks in
 * full, not a new retrospective/analysis feature. See
 * docs/agent-logs/recurrence-milestone-review-run47.md for the run that
 * added this and why a full quarterly/year-in-review page is still not
 * warranted.
 *
 * `options.styleOnly` (added run 48) restricts the count to signals whose
 * most recent `type` is a genuine style-aesthetic type (see
 * STYLE_AESTHETIC_TYPES above). Run 47 found the raw/unfiltered count meets
 * the "4-5 signals recurring 4+ times" retrospective-trigger threshold only
 * because factual/institutional-tracking items (CFDA fund/awards, a
 * designer-debut timeline, a coverage gap) recur mechanically via
 * carry-forward, not because a style trend is re-emerging. **The
 * retrospective trigger must be evaluated with `{ styleOnly: true }`
 * going forward** -- the raw (unfiltered) count remains available and
 * correct for the archive page's honest factual/administrative surface,
 * which is a legitimately different use of the same underlying data.
 */
export function getRecurringSignals(
  minOccurrences = 4,
  options: { styleOnly?: boolean } = {},
): RecurringSignal[] {
  const reports = getAllReports(); // newest first
  const byId = new Map<string, SignalOccurrence[]>();

  for (const report of reports) {
    for (const signal of report.top_signals ?? []) {
      if (!signal.signal_id) continue;
      const list = byId.get(signal.signal_id) ?? [];
      list.push({ report_date: report.report_date, signal });
      byId.set(signal.signal_id, list);
    }
  }

  const result: RecurringSignal[] = [];
  for (const [signal_id, occurrences] of byId) {
    if (occurrences.length < minOccurrences) continue;
    const dates = occurrences.map((o) => o.report_date).sort();
    const mostRecentType = occurrences[occurrences.length - 1].signal.type;
    const isStyleAesthetic = STYLE_AESTHETIC_TYPES.has(mostRecentType);
    if (options.styleOnly && !isStyleAesthetic) continue;
    result.push({
      signal_id,
      name: occurrences[0].signal.name,
      occurrence_count: occurrences.length,
      first_seen: dates[0],
      last_seen: dates[dates.length - 1],
      origin_classification: occurrences[0].signal.origin_classification,
      is_style_aesthetic: isStyleAesthetic,
    });
  }

  return result.sort((a, b) => b.occurrence_count - a.occurrence_count);
}

export interface SearchableSignal {
  name: string;
  signal_id?: string;
  report_date: string;
  source_sectors: string[];
  confidence: string;
  volatility: string;
  origin_classification: string;
  evidence: string;
  index_note: string;
}

/**
 * Flattens every signal across all reports into a single searchable/filterable
 * array for the /search page's client-side facet filters. One entry per
 * signal occurrence (not deduped by signal_id) — a signal recurring across
 * weeks is meaningful history, per /signals/[slug]'s existing model.
 */
export function getSearchIndex(): SearchableSignal[] {
  const reports = getAllReports();
  const index: SearchableSignal[] = [];

  for (const report of reports) {
    for (const signal of report.top_signals ?? []) {
      index.push({
        name: signal.name,
        signal_id: signal.signal_id,
        report_date: report.report_date,
        source_sectors: signal.source_sectors,
        confidence: signal.confidence,
        volatility: signal.volatility,
        origin_classification: signal.origin_classification,
        evidence: signal.evidence,
        index_note: signal.index_note,
      });
    }
  }

  return index;
}

/**
 * Counts how many of the most recent consecutive reports (by report_date,
 * newest first) have collection_status === "thin". Stops at the first
 * non-thin report. Used to surface a repeated-thin-week pattern explicitly
 * rather than letting each report restate "quiet period" in isolation.
 */
export function getConsecutiveThinWeekCount(): number {
  const reports = getAllReports(); // newest first
  let count = 0;

  for (const report of reports) {
    if (report.collection_status === "thin") {
      count++;
    } else {
      break;
    }
  }

  return count;
}

export interface ThisWeeksIndex {
  reportDate: string;
  sourcesScanned: number;
  itemsCollected: number;
  topSignal: string | null;
  risingTerm: string | null;
  recurringMaterial: string | null;
  dominantMood: string | null;
  /** Set when dominantMood was carried forward from an earlier report because
   *  the latest one had no aesthetic_terms of its own (e.g. a fashion-week
   *  logistics-heavy window) — surfaced so the UI can be transparent about it
   *  rather than presenting a stale mood as current. */
  dominantMoodSourceDate?: string;
  /** Set when a mood term exists somewhere in the archive but only past the
   *  staleness cutoff (MOOD_STALENESS_CUTOFF_DAYS) — the UI should show an
   *  explicit "no distinct mood signal in recent weeks" state instead of
   *  silently carrying forward an arbitrarily old term indefinitely. */
  dominantMoodTooStale?: boolean;
  highestVolatilitySector: string | null;
  overallConfidence: string | null;
}

// Beyond this many days, a carried-forward dominant mood is no longer
// disclosed as a (very old) current value — it's treated as "no distinct
// signal in recent weeks" instead. ~12 weeks, per run 43's flagged
// observation that a 24-week-old carry-forward reads as meaningless even
// though it's honestly disclosed. Chosen to match the site's existing
// "thin week" honesty conventions rather than hiding the gap silently.
const MOOD_STALENESS_CUTOFF_DAYS = 84;

/**
 * Derives the "THIS WEEK'S INDEX" glanceable metrics module (doc §27/§28) from
 * the latest report plus recent archive history. Every field is computed from
 * real report data — nothing here is hardcoded or invented:
 *
 * - topSignal: the latest report's highest-ranked top_signal (list order is
 *   the report's own prioritization).
 * - risingTerm: a repeated_keyword present in the latest report that was NOT
 *   present in the immediately prior report — i.e. genuinely new this window,
 *   not a subjective "trending" call. Falls back to the first keyword when
 *   there is no prior report to diff against.
 * - recurringMaterial: a material appearing in more than one of the last five
 *   reports (including the latest), i.e. actually recurring across the
 *   archive rather than a one-off mention.
 * - dominantMood: the latest report's first aesthetic_term. Some windows
 *   (e.g. fashion-week logistics weeks) report no aesthetic_terms at all; in
 *   that case this walks backward to the most recent report that had one and
 *   flags dominantMoodSourceDate so the caller can disclose it's carried
 *   forward rather than presenting it as this week's finding.
 * - highestVolatilitySector: the source sector attached to the most
 *   volatility-weighted top_signals this window (flash/emerging weighted
 *   highest, stable/dormant weighted zero). Null if no signal this window
 *   carries meaningful volatility.
 * - overallConfidence: the most common confidence level across this window's
 *   top_signals (mode), not an average or a guess.
 */
export function getThisWeeksIndex(): ThisWeeksIndex | null {
  const reports = getAllReports(); // newest first
  if (reports.length === 0) return null;

  const latest = reports[0];
  const previous = reports[1] ?? null;

  const topSignal = latest.top_signals?.[0]?.name ?? null;

  // Rising term: a repeated_keyword this week that wasn't present last week.
  let risingTerm: string | null = null;
  if (previous) {
    const prevKeywords = new Set(previous.repeated_keywords ?? []);
    risingTerm =
      (latest.repeated_keywords ?? []).find((k) => !prevKeywords.has(k)) ?? null;
  } else {
    risingTerm = latest.repeated_keywords?.[0] ?? null;
  }

  // Recurring material: appears in more than one of the last five reports.
  const recentWindow = reports.slice(0, 5);
  const materialCounts = new Map<string, number>();
  for (const r of recentWindow) {
    for (const m of new Set(r.materials ?? [])) {
      materialCounts.set(m, (materialCounts.get(m) ?? 0) + 1);
    }
  }
  let recurringMaterial: string | null = null;
  let bestMaterialCount = 1;
  for (const [m, c] of materialCounts) {
    if (c > bestMaterialCount) {
      bestMaterialCount = c;
      recurringMaterial = m;
    }
  }

  // Dominant mood: latest report's first aesthetic_term, else the most
  // recent earlier report that has one (disclosed via dominantMoodSourceDate).
  let dominantMood: string | null = null;
  let dominantMoodSourceDate: string | undefined;
  let dominantMoodTooStale = false;
  for (const r of reports) {
    if (r.aesthetic_terms && r.aesthetic_terms.length > 0) {
      const isCarryForward = r.report_date !== latest.report_date;
      if (isCarryForward) {
        const daysOld =
          (Date.parse(latest.report_date) - Date.parse(r.report_date)) / 86_400_000;
        if (daysOld > MOOD_STALENESS_CUTOFF_DAYS) {
          dominantMoodTooStale = true;
          break;
        }
      }
      dominantMood = r.aesthetic_terms[0].replace(/\s*\(carryover\)\s*/i, "").trim();
      dominantMoodSourceDate = isCarryForward ? r.report_date : undefined;
      break;
    }
  }

  // Highest volatility sector: sum a volatility weight across each signal's
  // source_sectors, take the sector with the highest total this window.
  const volatilityWeight: Record<string, number> = {
    flash: 3,
    emerging: 2,
    seasonal: 2,
    recurring: 1,
    declining: 1,
    stable: 0,
    dormant: 0,
  };
  const sectorScores = new Map<string, number>();
  for (const s of latest.top_signals ?? []) {
    const weight = volatilityWeight[s.volatility] ?? 0;
    for (const sector of s.source_sectors ?? []) {
      sectorScores.set(sector, (sectorScores.get(sector) ?? 0) + weight);
    }
  }
  let highestVolatilitySector: string | null = null;
  let bestSectorScore = 0;
  for (const [sector, score] of sectorScores) {
    if (score > bestSectorScore) {
      bestSectorScore = score;
      highestVolatilitySector = sector;
    }
  }

  // Overall confidence: mode of this window's top_signal confidence values.
  const confidenceCounts = new Map<string, number>();
  for (const s of latest.top_signals ?? []) {
    confidenceCounts.set(s.confidence, (confidenceCounts.get(s.confidence) ?? 0) + 1);
  }
  let overallConfidence: string | null = null;
  let bestConfidenceCount = 0;
  for (const [c, count] of confidenceCounts) {
    if (count > bestConfidenceCount) {
      bestConfidenceCount = count;
      overallConfidence = c;
    }
  }

  return {
    reportDate: latest.report_date,
    sourcesScanned: latest.sources_scanned,
    itemsCollected: latest.items_collected,
    topSignal,
    risingTerm,
    recurringMaterial,
    dominantMood,
    dominantMoodSourceDate,
    dominantMoodTooStale,
    highestVolatilitySector,
    overallConfidence,
  };
}

/** Returns all distinct non-empty signal_id values across all reports. */
export function getAllSignalSlugs(): string[] {
  const reports = getAllReports();
  const slugs = new Set<string>();

  for (const report of reports) {
    for (const signal of report.top_signals ?? []) {
      if (signal.signal_id) slugs.add(signal.signal_id);
    }
  }

  return Array.from(slugs);
}
