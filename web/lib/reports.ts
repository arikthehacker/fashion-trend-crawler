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
  source_links?: string[];
  confidence_notes?: string;
  volatility_notes?: string;
  incentive_notes?: string;
  human_editor_note?: string;
  content_hash?: string;
  revision_history?: RevisionEntry[];
}

export interface RevisionEntry {
  previous_content_hash: string;
  corrected_at: string;
  reason: string;
}

function reportsDir(): string {
  return path.join(process.cwd(), "..", "data", "reports");
}

/** Returns all reports, newest report_date first. */
export function getAllReports(): Report[] {
  const dir = reportsDir();
  if (!fs.existsSync(dir)) return [];

  const files = fs.readdirSync(dir).filter((f) => f.endsWith(".json"));
  const reports = files.map((f) =>
    JSON.parse(fs.readFileSync(path.join(dir, f), "utf-8")) as Report
  );

  return reports.sort((a, b) => (a.report_date < b.report_date ? 1 : -1));
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
    if ((report as { collection_status?: string }).collection_status === "thin") {
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
  highestVolatilitySector: string | null;
  overallConfidence: string | null;
}

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
  for (const r of reports) {
    if (r.aesthetic_terms && r.aesthetic_terms.length > 0) {
      dominantMood = r.aesthetic_terms[0].replace(/\s*\(carryover\)\s*/i, "").trim();
      dominantMoodSourceDate = r.report_date === latest.report_date ? undefined : r.report_date;
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
