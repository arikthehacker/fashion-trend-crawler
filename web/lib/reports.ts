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
