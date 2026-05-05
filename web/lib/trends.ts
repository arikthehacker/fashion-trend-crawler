// lib/trends.ts
// last edited: 05/04/2026
// reads and processes crawled trends data and ai summary for the frontend

import fs from "fs";
import path from "path";

export interface TrendPage {
  url: string;
  depth: number;
  titles: string[];
}

export interface Trend {
  trend: string;
  signal: string;
}

export interface TrendSummary {
  the_moment: string;
  summary: string;
  trends: Trend[];
  sources_summary: Record<string, string>;
}

export interface TrendsData {
  pages: TrendPage[];
  summary: TrendSummary | null;
  lastUpdated: string;
  totalHeadlines: number;
}

export function getTrends(): TrendsData {
  const root = path.join(process.cwd(), "..");

  // read raw crawl data
  const rawPath = path.join(root, "trends_raw.json");
  if (!fs.existsSync(rawPath)) {
    return { pages: [], summary: null, lastUpdated: "never", totalHeadlines: 0 };
  }

  const pages: TrendPage[] = JSON.parse(fs.readFileSync(rawPath, "utf-8"));
  const totalHeadlines = pages.reduce((acc, p) => acc + p.titles.length, 0);
  const stats = fs.statSync(rawPath);
  const lastUpdated = stats.mtime.toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });

  // read ai summary if it exists
  const summaryPath = path.join(root, "trends_summary.json");
  const summary: TrendSummary | null = fs.existsSync(summaryPath)
    ? JSON.parse(fs.readFileSync(summaryPath, "utf-8"))
    : null;

  return { pages, summary, lastUpdated, totalHeadlines };
}
