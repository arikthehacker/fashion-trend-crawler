// lib/editorial.ts
// The photocopy edition's rules for turning a report JSON into a page
// (design/SITE_SPEC_photocopy.md §3). Every week goes through these same
// functions, so a new report needs no design work.

import type { Report, TopSignal, EvidenceItem } from "./reports";

const MON = (iso: string) => new Date(`${iso.slice(0, 10)}T00:00:00Z`);

/** "Nov 16" or "Nov 16, 2026". */
export function fmtDay(iso: string, withYear = false): string {
  return MON(iso).toLocaleDateString("en-US", { month: "short", day: "numeric", ...(withYear ? { year: "numeric" } : {}), timeZone: "UTC" });
}

/** "Nov 16 – Nov 22, 2026". */
export function shortWindow(r: Report): string {
  return `${fmtDay(r.collection_window.start)} – ${fmtDay(r.collection_window.end, true)}`;
}

/** "November 16 – 22, 2026", with both years when the window spans two. */
export function longWindow(r: Report): string {
  const s = MON(r.collection_window.start), e = MON(r.collection_window.end);
  const o: Intl.DateTimeFormatOptions = { month: "long", day: "numeric", timeZone: "UTC" };
  if (s.getUTCFullYear() !== e.getUTCFullYear()) {
    return `${s.toLocaleDateString("en-US", { ...o, year: "numeric" })} – ${e.toLocaleDateString("en-US", { ...o, year: "numeric" })}`;
  }
  return `${s.toLocaleDateString("en-US", o)} – ${e.toLocaleDateString("en-US", { ...o, year: "numeric" })}`;
}

/** "Nov 16–22, 2026" for titles. */
export function titleWindow(r: Report): string {
  const s = MON(r.collection_window.start), e = MON(r.collection_window.end);
  const m = (d: Date) => d.toLocaleDateString("en-US", { month: "short", timeZone: "UTC" });
  if (s.getUTCFullYear() !== e.getUTCFullYear()) return `${fmtDay(r.collection_window.start, true)} – ${fmtDay(r.collection_window.end, true)}`;
  if (m(s) === m(e)) return `${m(s)} ${s.getUTCDate()}–${e.getUTCDate()}, ${e.getUTCFullYear()}`;
  return `${fmtDay(r.collection_window.start)} – ${fmtDay(r.collection_window.end, true)}`;
}

export const n = (x: number) => Number(x).toLocaleString("en-US");

/** Signals by article count, largest first; ties keep the report's order. */
export function ranked(r: Report): TopSignal[] {
  return r.top_signals
    .map((s, i) => [s, i] as const)
    .sort((a, b) => items(b[0]).length - items(a[0]).length || a[1] - b[1])
    .map(([s]) => s);
}

export const items = (s: TopSignal): EvidenceItem[] => s.evidence_items ?? [];
export const outlets = (s: TopSignal): number => s.source_domains?.length ?? new Set(items(s).map((i) => i.outlet_domain)).size;
export const slugOf = (s: TopSignal): string => s.signal_id ?? s.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

function listJoin(xs: string[]): string {
  if (xs.length <= 1) return xs.join("");
  return `${xs.slice(0, -1).join(", ")} and ${xs[xs.length - 1]}`;
}

/** The week's headline: the approved `headline` field, else the generated fallback (spec §3.2). */
export function headline(r: Report): string {
  if (r.headline && r.headline.trim()) return r.headline.trim();
  const top = ranked(r).slice(0, 3).map((s) => s.name);
  if (top.length === 0) return `The week of ${longWindow(r)}`;
  const lead = top[0].charAt(0).toUpperCase() + top[0].slice(1);
  const names = listJoin([lead, ...top.slice(1)]);
  return top.length === 1 ? `${names} was the largest signal of the week` : `${names} were the largest signals of the week`;
}

/** "4,250 items collected from 78 sources." One line under the headline (the editor's choice, 2026-11-25). */
export function standfirst(r: Report): string {
  return `${n(r.items_collected)} items collected from ${r.sources_scanned} sources${r.collection_status === "thin" ? ", a thin week" : ""}.`;
}

/** A plain description for search results and share cards, 70 to 160 characters. */
export function describe(r: Report): string {
  const top = ranked(r).slice(0, 3).map((s) => s.name).join(", ");
  const base = `Week of ${titleWindow(r)}: ${n(r.items_collected)} items from ${r.sources_scanned} sources, ${r.top_signals.length} signals kept.`;
  const full = top ? `${base} Largest: ${top}.` : base;
  return full.length <= 160 ? full : base.slice(0, 160);
}

const SECTOR_LABELS: Record<string, string> = {
  editorial: "Editorial", trade_intelligence: "Trade press", retail: "Retail", visual_archive: "Visual archive",
  runway: "Runway", designer_origin: "Designer", institutional: "Institutional", independent_criticism: "Independent critics",
  resale: "Resale", social: "Social", street_ugc: "Street and user-made",
};
export const sectorLabel = (k: string) => SECTOR_LABELS[k] ?? (k.charAt(0).toUpperCase() + k.slice(1).replace(/_/g, " "));
export const typeLabel = (t: string) => t.replace(/_/g, " ");
export const volLabel = (v: string) => v.replace(/_/g, " ");

/** The editor's note without the "Editorial view:" prefix. Never shortened. */
export const editorNote = (s: TopSignal): string => (s.human_editor_note ?? "").replace(/^\s*Editorial view:\s*/i, "").trim();

export const sentences = (t: string) => t.split(/(?<=[.!?])\s+/).filter(Boolean);

/** "How this report was made", split into who did what. Null when the wording is not the standard one. */
export function whoDidWhat(ai?: string): { who: string; did: string }[] | null {
  if (!ai) return null;
  const WHO: [RegExp, string][] = [[/^ARI3[’']s deterministic pipeline\s+/i, "ARI3"], [/^An AI assistant\s+/i, "AI assistant"], [/^The editor\s+/i, "Editor"]];
  const rows = sentences(ai).map((s) => {
    for (const [re, who] of WHO) if (re.test(s)) { const d = s.replace(re, ""); return { who, did: d.charAt(0).toUpperCase() + d.slice(1) }; }
    return null;
  });
  return rows.every(Boolean) ? (rows as { who: string; did: string }[]) : null;
}

/** Where each limitation's marker sits (spec §3.6): fixed places, chosen by what the note is about. */
export type NotePlace = "byline" | "summary-counts" | "summary-share" | "sectors" | "signals";
export type Footnote = { n: number; text: string; place: NotePlace };
const PLACE_ORDER: NotePlace[] = ["byline", "summary-counts", "summary-share", "sectors", "signals"];

function placeFor(text: string): NotePlace {
  const t = text.toLowerCase();
  if (/one editor/.test(t)) return "byline";
  if (/classifier|not-sure|not sure|first-seen|reconstructed/.test(t)) return "summary-counts";
  if (/editorial sector|editorial group|% of collected items/.test(t)) return "summary-share";
  if (/social platform|resale|sector/.test(t)) return "sectors";
  return "signals";
}

export function footnotes(r: Report): Footnote[] {
  return (r.limitations ?? [])
    .map((text, i) => ({ text, place: placeFor(text), i }))
    .sort((a, b) => PLACE_ORDER.indexOf(a.place) - PLACE_ORDER.indexOf(b.place) || a.i - b.i)
    .map((x, k) => ({ n: k + 1, text: x.text, place: x.place }));
}

/** Phrases the drafting rules guarantee in every summary; a place's markers go right after its phrase. */
export const SUMMARY_ANCHORS: Record<"summary-counts" | "summary-share", RegExp> = {
  "summary-counts": /raw source records from \d+ outlet domains/,
  "summary-share": /\d+(\.\d+)?% editorial in this window/,
};

/** Split the summary into paragraphs of three sentences, as the mock does. */
export function summaryParagraphs(r: Report): string[] {
  const parts = r.executive_summary.split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean);
  if (parts.length > 1) return parts;
  const ss = sentences(r.executive_summary);
  const out: string[] = [];
  for (let i = 0; i < ss.length; i += 3) out.push(ss.slice(i, i + 3).join(" "));
  return out;
}

export const editorialShare = (r: Report): { label: string; pct: number } | null => {
  const entries = Object.entries(r.source_sector_breakdown ?? {}).sort((a, b) => b[1] - a[1]);
  const total = entries.reduce((a, [, v]) => a + v, 0);
  if (!entries.length || !total) return null;
  return { label: sectorLabel(entries[0][0]).toLowerCase(), pct: Math.round((entries[0][1] / total) * 1000) / 10 };
};
