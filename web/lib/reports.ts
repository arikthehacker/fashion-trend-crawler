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

/** Returns a single report by its report_date (YYYY-MM-DD), or null. */
export function getReportByDate(date: string): Report | null {
  const dir = reportsDir();
  const filePath = path.join(dir, `${date}.json`);
  if (!fs.existsSync(filePath)) return null;
  return JSON.parse(fs.readFileSync(filePath, "utf-8")) as Report;
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
