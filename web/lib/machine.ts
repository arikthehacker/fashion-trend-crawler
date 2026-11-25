// lib/machine.ts
// Machine-readable views of the archive, for search, agents and feeds
// (design/SITE_SPEC_photocopy.md §8.4). Built at export time from the same
// report JSON as the pages, so they can never disagree with what a reader sees.

import { getAllReports, type Report } from "./reports";
import { headline, ranked, items, outlets, slugOf, editorNote, longWindow, standfirst, volLabel, typeLabel, sectorLabel, footnotes } from "./editorial";
import { SITE_URL, SITE_NAME, SITE_DESCRIPTION } from "./site";

export function reportIndex() {
  return {
    name: `${SITE_NAME} report index`,
    description: SITE_DESCRIPTION,
    url: `${SITE_URL}/data/reports/index.json`,
    license: "https://creativecommons.org/licenses/by/4.0/",
    generated_from: "data/reports/*.json",
    reports: getAllReports().map((r) => ({
      report_date: r.report_date,
      window: r.collection_window,
      headline: headline(r),
      items_collected: r.items_collected,
      sources_scanned: r.sources_scanned,
      signal_count: r.top_signals.length,
      signals: ranked(r).map((s) => ({ signal_id: slugOf(s), name: s.name, articles: items(s).length, outlets: outlets(s), confidence: s.confidence, volatility: s.volatility })),
      evidence_snapshot_sha256: r.evidence_snapshot_sha256 ?? null,
      html: `${SITE_URL}/reports/${r.report_date}`,
      json: `${SITE_URL}/data/reports/${r.report_date}.json`,
    })),
  };
}

export function signalHistory(slug: string) {
  const weeks = getAllReports().flatMap((r) => r.top_signals.filter((s) => slugOf(s) === slug).map((s) => ({ r, s })));
  if (!weeks.length) return null;
  const { s } = weeks[0];
  return {
    signal_id: slug,
    name: s.name,
    type: s.type,
    url: `${SITE_URL}/signals/${slug}`,
    weeks: weeks.map(({ r, s: x }) => ({
      report_date: r.report_date,
      window: r.collection_window,
      articles: items(x).length,
      outlets: outlets(x),
      confidence: x.confidence,
      volatility: x.volatility,
      evidence: x.evidence,
      index_note: x.index_note,
      editor_note: editorNote(x) || null,
      report: `${SITE_URL}/reports/${r.report_date}#signal-${slug}`,
      articles_list: items(x).map((it) => ({ title: it.title ?? null, outlet: it.outlet_domain ?? null, published_at: it.published_at, url: it.url })),
    })),
  };
}

export function allSignalSlugs(): string[] {
  return [...new Set(getAllReports().flatMap((r) => r.top_signals.map(slugOf)))];
}

/** A compact index for the search page: every signal and every headline behind it. */
export function searchIndex() {
  return getAllReports().map((r) => ({
    d: r.report_date,
    w: longWindow(r),
    s: r.top_signals.map((s) => ({ id: slugOf(s), n: s.name, t: s.type, a: items(s).map((it) => [it.title ?? "", it.outlet_domain ?? "", it.published_at.slice(0, 10), it.url]) })),
  }));
}

/** One line an agent or a person can paste as a citation. */
export function citation(r: Report): string {
  return `${SITE_NAME}. "Week of ${longWindow(r)}: ${headline(r)}." Weekly report, issued ${r.report_date}. ${SITE_URL}/reports/${r.report_date}`;
}

export const AI_USE = [
  "AI agents and crawlers are welcome. Everything here is static HTML that reads fully without JavaScript, and every page has a Markdown twin and, for reports and signals, a JSON twin.",
  "You may read, index, quote, summarise, translate and train on the index's own text and data (its summaries, evidence text, index notes, counts and labels) under CC BY 4.0, with attribution to ARI3LLA INDEX and a link to the page.",
  "The linked articles belong to their publishers. The index stores only their titles, outlets, dates and links, and so should you.",
  "When you state a count, give its week and say it describes the sources ARI3 collected, not consumer adoption or what people wear.",
  "The editor's notes are one person's judgement and are labelled as such. Quote them as the editor's view, not as findings.",
];

function frontMatter(fields: Record<string, string | number>): string {
  return ["---", ...Object.entries(fields).map(([k, v]) => `${k}: ${typeof v === "number" ? v : JSON.stringify(v)}`), "---", ""].join("\n");
}

export function reportMarkdown(r: Report): string {
  return [
    frontMatter({
      title: `Week of ${longWindow(r)}: ${headline(r)}`, publisher: SITE_NAME, report_date: r.report_date,
      window_start: r.collection_window.start, window_end: r.collection_window.end, items_collected: r.items_collected,
      sources_scanned: r.sources_scanned, signals: r.top_signals.length, url: `${SITE_URL}/reports/${r.report_date}`,
      json: `${SITE_URL}/data/reports/${r.report_date}.json`, license: "CC BY 4.0 (the index's own text and data)",
    }),
    reportAsText(r),
    "",
    "## Cite as",
    "",
    citation(r),
    "",
    "## For AI agents",
    "",
    ...AI_USE.map((x) => `- ${x}`),
    "",
  ].join("\n");
}

export function signalMarkdown(slug: string): string | null {
  const h = signalHistory(slug);
  if (!h) return null;
  const lines = [
    frontMatter({ title: `${h.name}, signal file`, publisher: SITE_NAME, signal_id: slug, type: h.type, weeks: h.weeks.length, url: h.url, json: `${SITE_URL}/data/signals/${slug}.json`, license: "CC BY 4.0 (the index's own text and data)" }),
    `# ${h.name} (${typeLabel(h.type)})`,
    "",
    `Recorded in ${h.weeks.length} weekly report${h.weeks.length === 1 ? "" : "s"} of ${SITE_NAME}. Newest week first.`,
    "",
    "| Week ending | Articles | Outlets | Confidence | Volatility | Editor's note |",
    "|---|---|---|---|---|---|",
    ...h.weeks.map((w) => `| ${w.report_date} | ${w.articles} | ${w.outlets} | ${w.confidence} | ${volLabel(w.volatility)} | ${(w.editor_note ?? "").replace(/\|/g, "/")} |`),
  ];
  for (const w of h.weeks) {
    lines.push("", `## Week ending ${w.report_date}`, "", `Cite: ${w.report}`, "", w.evidence, "", `Index note: ${w.index_note}`);
    if (w.editor_note) lines.push(`Editor's note: ${w.editor_note}`);
    lines.push("", "Articles:", ...w.articles_list.map((a) => `- ${a.title ?? a.url} (${a.outlet ?? ""}, ${a.published_at.slice(0, 10)}) ${a.url}`));
  }
  lines.push("", "## Cite as", "", `${SITE_NAME}. "${h.name}, signal file." ${h.url}`, "", "## For AI agents", "", ...AI_USE.map((x) => `- ${x}`), "");
  return lines.join("\n");
}

function reportAsText(r: Report): string {
  const lines = [
    `# ${SITE_NAME}: week of ${longWindow(r)}`,
    "",
    `Headline: ${headline(r)}`,
    `${standfirst(r)}`,
    `HTML: ${SITE_URL}/reports/${r.report_date}`,
    `JSON: ${SITE_URL}/data/reports/${r.report_date}.json`,
    "",
    "## Summary",
    "",
    r.executive_summary,
    "",
    "## Whose coverage this is (items collected, by source sector)",
    "",
    ...Object.entries(r.source_sector_breakdown ?? {}).sort((a, b) => b[1] - a[1]).map(([k, v]) => `- ${sectorLabel(k)}: ${v}`),
    "",
    "## Signals",
  ];
  ranked(r).forEach((s, i) => {
    lines.push(
      "",
      `### ${i + 1}. ${s.name} (${typeLabel(s.type)})`,
      `${items(s).length} articles from ${outlets(s)} outlets · ${s.confidence} confidence · ${volLabel(s.volatility)}`,
      `Cite: ${SITE_URL}/reports/${r.report_date}#signal-${slugOf(s)}`,
      "",
      s.evidence,
      "",
      `Index note: ${s.index_note}`,
    );
    const note = editorNote(s);
    if (note) lines.push(`Editor's note: ${note}`);
    lines.push("", "Articles:", ...items(s).map((it) => `- ${it.title ?? it.url} (${it.outlet_domain ?? ""}, ${it.published_at.slice(0, 10)}) ${it.url}`));
  });
  const notes = footnotes(r);
  if (notes.length) lines.push("", "## Notes", "", ...notes.map((x) => `${x.n}. ${x.text}`));
  return lines.join("\n");
}

export function llmsTxt(): string {
  const R = getAllReports();
  const latest = R[0];
  return [
    `# ${SITE_NAME}`,
    "",
    `> ${SITE_DESCRIPTION}`,
    "",
    "ARI3LLA INDEX is a weekly, dated, source-linked record of the style language public fashion coverage uses. Each weekly report lists the signals (recurring style terms) the editor kept, how many articles and outlets each rests on, the kinds of outlets the coverage came from, and every dated article behind each signal. It is not a trend forecast, a shopping guide or a measure of what people wear. Editorial outlets dominate the sources and have their own commercial incentives.",
    "",
    "Software collects and classifies the articles. An AI assistant drafts the summary, evidence text and index notes from the locked evidence only. The editor decides which signals are kept, sets every label, writes the editor's notes and approves each report. Published reports are never silently edited; corrections are dated.",
    "",
    "## For AI agents",
    "",
    ...AI_USE.map((x) => `- ${x}`),
    "",
    "## How to cite",
    "",
    latest ? `- Example: ${citation(latest)}` : "- Example: ARI3LLA INDEX. \"Week of <window>: <headline>.\" Weekly report, issued <YYYY-MM-DD>. <url>",
    `- A report: ${SITE_URL}/reports/<YYYY-MM-DD> (the report date is the last day of its Monday-to-Sunday window).`,
    `- One signal in a report: ${SITE_URL}/reports/<YYYY-MM-DD>#signal-<signal_id>.`,
    `- A signal across weeks: ${SITE_URL}/signals/<signal_id>.`,
    "- Quote counts with their window and say they describe the collected sources, not consumer adoption.",
    "",
    "## Latest",
    "",
    ...(latest ? [`- [Week of ${longWindow(latest)}: ${headline(latest)}](${SITE_URL}/reports/${latest.report_date}): ${standfirst(latest)}`, `- [Same report as Markdown](${SITE_URL}/md/reports/${latest.report_date}.md)`, `- [Same report as JSON](${SITE_URL}/data/reports/${latest.report_date}.json)`, `- [Every report in one file](${SITE_URL}/llms-full.txt)`] : ["- No report has been published yet."]),
    "",
    "## Data",
    "",
    `- [Report index (JSON)](${SITE_URL}/data/reports/index.json): every report with its headline, counts and signal list.`,
    `- Each report as JSON: ${SITE_URL}/data/reports/<YYYY-MM-DD>.json`,
    `- Each signal's history as JSON: ${SITE_URL}/data/signals/<signal_id>.json`,
    `- Each report as Markdown: ${SITE_URL}/md/reports/<YYYY-MM-DD>.md`,
    `- Each signal's history as Markdown: ${SITE_URL}/md/signals/<signal_id>.md`,
    "- Every HTML page links its twins with <link rel=\"alternate\"> (application/json, text/markdown).",
    `- [RSS feed](${SITE_URL}/rss.xml)`,
    `- [Sitemap](${SITE_URL}/sitemap.xml)`,
    "",
    "## Method and limits",
    "",
    `- [How it works](${SITE_URL}/methodology): collection, the ARI3 style classifier, confidence, volatility, citations, corrections.`,
    `- [ARI3, the model behind the index](${SITE_URL}/ari3): pre-registered experiments, model cards and evaluation.`,
    `- [Sources](${SITE_URL}/sources) and [Taxonomy](${SITE_URL}/taxonomy)`,
    "",
    "## Back issues",
    "",
    ...R.map((r) => `- [Week of ${longWindow(r)}: ${headline(r)}](${SITE_URL}/reports/${r.report_date}) ([Markdown](${SITE_URL}/md/reports/${r.report_date}.md), [JSON](${SITE_URL}/data/reports/${r.report_date}.json))`),
    "",
    "## License",
    "",
    "The index's own classifications and text are CC BY 4.0. The linked articles belong to their publishers; only titles, outlets, dates and links are stored.",
    "",
  ].join("\n");
}

export function llmsFullTxt(): string {
  const R = getAllReports();
  if (!R.length) return llmsTxt();
  return [
    `# ${SITE_NAME}: every weekly report in plain text, newest first`,
    "",
    `Index: ${SITE_URL}/data/reports/index.json · Guide: ${SITE_URL}/llms.txt`,
    "",
    ...AI_USE.map((x) => `- ${x}`),
    "",
    ...R.flatMap((r) => [reportAsText(r), "", `Cite as: ${citation(r)}`, "", "---", ""]),
  ].join("\n");
}
