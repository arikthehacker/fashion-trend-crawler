// /reports/[date]: the full weekly report, photocopy edition (design/SITE_SPEC_photocopy.md §3).
// Everything on the page comes from data/reports/<date>.json through lib/editorial.ts,
// so a new week needs no design work.

import type { ReactNode } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getAllReportDates, getReportByDate, getLatestReport, type Report, type TopSignal } from "../../../lib/reports";
import {
  headline, standfirst, describe, ranked, items, outlets, slugOf, typeLabel, volLabel, editorNote, sectorLabel,
  whoDidWhat, footnotes, SUMMARY_ANCHORS, summaryParagraphs, editorialShare, titleWindow, longWindow, n, type Footnote,
} from "../../../lib/editorial";
import { SITE_URL, SITE_NAME, EDITOR_LABEL, pageMetadata } from "../../../lib/site";
import { citation } from "../../../lib/machine";
import { Folio, Dateline, Byline, Mark, Marks, Notes, SrcList } from "../../components/Chrome";

export const dynamicParams = false;

export function generateStaticParams() {
  const dates = getAllReportDates();
  // `output: "export"` refuses a dynamic route with zero params; the placeholder renders the 404 page.
  if (dates.length === 0) return [{ date: "none" }];
  return dates.map((date) => ({ date }));
}

export async function generateMetadata({ params }: { params: Promise<{ date: string }> }) {
  const { date } = await params;
  const report = getReportByDate(date);
  if (!report) return { title: "Report not found", robots: { index: false } };
  const hed = headline(report);
  const title = `Week of ${titleWindow(report)}: ${hed}`;
  const image = { url: `/reports/${date}/opengraph-image`, width: 1200, height: 630, alt: `${SITE_NAME}, week of ${longWindow(report)}: ${hed}` };
  const base = pageMetadata(`/reports/${date}`, title.length > 90 ? `Week of ${titleWindow(report)}` : title, describe(report), {
    type: "article", image, publishedTime: report.report_date,
  });
  return { ...base, alternates: { ...base.alternates, types: { "application/json": `/data/reports/${date}.json`, "text/markdown": `/md/reports/${date}.md` } } };
}

/** Insert footnote marks after the summary's guaranteed phrases, and link each "<signal> (N items from M outlets)". */
function richSummary(text: string, report: Report, notes: Footnote[], used: Set<string>): ReactNode[] {
  type Hit = { at: number; end: number; node: ReactNode; kind: "link" | "mark" };
  const hits: Hit[] = [];
  for (const place of ["summary-counts", "summary-share"] as const) {
    if (used.has(place)) continue;
    const m = SUMMARY_ANCHORS[place].exec(text);
    const marks = notes.filter((x) => x.place === place);
    if (m && marks.length) {
      used.add(place);
      const end = m.index + m[0].length;
      hits.push({ at: end, end, kind: "mark", node: <Marks key={`m-${place}`} notes={notes} place={place} /> });
    }
  }
  for (const s of report.top_signals) {
    const esc = s.name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const m = new RegExp(`\\b${esc}\\b(?= \\(\\d+ (?:items )?from \\d+)`, "i").exec(text);
    if (m) hits.push({ at: m.index, end: m.index + m[0].length, kind: "link", node: <a key={`l-${slugOf(s)}`} href={`#signal-${slugOf(s)}`}>{m[0]}</a> });
  }
  hits.sort((a, b) => a.at - b.at || (a.kind === "link" ? -1 : 1));
  const out: ReactNode[] = [];
  let pos = 0;
  for (const h of hits) {
    if (h.at < pos) continue;
    out.push(text.slice(pos, h.at), h.node);
    pos = h.end;
  }
  out.push(text.slice(pos));
  return out;
}

function SignalBlock({ s, i }: { s: TopSignal; i: number }) {
  const id = slugOf(s);
  const note = editorNote(s);
  return (
    <article className="sig" id={`signal-${id}`} aria-labelledby={`h-${id}`}>
      <div>
        <p className="kicker">No. {i + 1} · {typeLabel(s.type)}</p>
        <h3 id={`h-${id}`}><Link className="toner-lite" href={`/signals/${id}`}>{s.name}</Link></h3>
        <p className="facts num">
          {items(s).length} article{items(s).length === 1 ? "" : "s"} from {outlets(s)} outlet{outlets(s) === 1 ? "" : "s"} · {s.confidence} confidence · {volLabel(s.volatility)}
        </p>
        <div className="body">
          <p>{s.evidence}</p>
          {s.index_note ? <p className="inote">{s.index_note}</p> : null}
        </div>
      </div>
      <div>
        {note ? <blockquote className="pull"><small>{EDITOR_LABEL}</small>{note}</blockquote> : null}
        <SrcList items={items(s)} show={4} />
      </div>
    </article>
  );
}

export default async function ReportPage({ params }: { params: Promise<{ date: string }> }) {
  const { date } = await params;
  const report = getReportByDate(date);
  if (!report) notFound();

  const latest = getLatestReport();
  const S = ranked(report);
  const notes = footnotes(report);
  const who = whoDidWhat(report.ai_assistance);
  const sectors = Object.entries(report.source_sector_breakdown ?? {}).sort((a, b) => b[1] - a[1]);
  const top = sectors[0]?.[1] ?? 0;
  const share = editorialShare(report);
  const hed = headline(report);
  const used = new Set<string>();
  const paras = summaryParagraphs(report).map((p) => richSummary(p, report, notes, used));
  const leftover = notes.filter((x) => (x.place === "summary-counts" || x.place === "summary-share") && !used.has(x.place));

  const lastRevision = report.revision_history?.[report.revision_history.length - 1];
  const dateModified = lastRevision?.corrected_at || report.report_date;
  const url = `${SITE_URL}/reports/${report.report_date}`;
  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "NewsArticle", "@id": `${url}#article`, headline: hed, description: describe(report),
        datePublished: report.report_date, dateModified, url, mainEntityOfPage: url, inLanguage: "en", isAccessibleForFree: true,
        image: [`${url}/opengraph-image`],
        author: { "@type": "Organization", name: SITE_NAME, url: SITE_URL },
        publisher: { "@type": "Organization", name: SITE_NAME, url: SITE_URL },
        isBasedOn: { "@id": `${url}#dataset` },
        about: S.map((s) => ({ "@type": "DefinedTerm", name: s.name, url: `${SITE_URL}/signals/${slugOf(s)}`, inDefinedTermSet: `${SITE_URL}/signals` })),
      },
      {
        "@type": "Dataset", "@id": `${url}#dataset`, name: `${SITE_NAME} weekly report, week of ${longWindow(report)}`,
        description: `${standfirst(report)} Signals, counts, source sectors and the dated articles behind each signal, as JSON.`,
        url, creator: { "@type": "Organization", name: SITE_NAME, url: SITE_URL }, datePublished: report.report_date, dateModified,
        temporalCoverage: `${report.collection_window.start}/${report.collection_window.end}`, isAccessibleForFree: true,
        license: "https://creativecommons.org/licenses/by/4.0/", measurementTechnique: `${SITE_URL}/methodology`,
        variableMeasured: ["signal", "article count", "outlet count", "confidence", "volatility", "source sector"],
        distribution: [{ "@type": "DataDownload", encodingFormat: "application/json", contentUrl: `${SITE_URL}/data/reports/${report.report_date}.json` }],
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: "Front page", item: SITE_URL },
          { "@type": "ListItem", position: 2, name: "Back issues", item: `${SITE_URL}/archive` },
          { "@type": "ListItem", position: 3, name: `Week of ${longWindow(report)}`, item: url },
        ],
      },
    ],
  };

  return (
    <main id="main-content">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }} />
      <Dateline report={report} />
      <Folio left="The full report" right={latest && latest.report_date !== report.report_date ? <Link href="/">Latest report</Link> : <Link href="/archive">Back issues</Link>} />

      <article>
        <div className="rtop">
          <div>
            <h1 className="hed rp toner">{hed}</h1>
            <p className="deck">{standfirst(report)}</p>
            <Byline><Marks notes={notes} place="byline" /></Byline>
            {report.thin_week_note ? <div className="box"><h2>A thin week</h2><p>{report.thin_week_note}</p></div> : null}
          </div>
          <aside className="who" aria-labelledby="who-h">
            <h2 id="who-h">Who did what</h2>
            {who ? (
              <dl>{who.map((r) => <div key={r.who} style={{ display: "contents" }}><dt>{r.who}</dt><dd>{r.did}</dd></div>)}</dl>
            ) : (
              <p className="note">{report.ai_assistance ?? "AI-assistance details for this report were not recorded."}</p>
            )}
          </aside>
        </div>

        <section aria-labelledby="summary-h">
          <h2 className="sec" id="summary-h">Summary</h2>
          <div className="cols three drop">
            {paras.map((p, i) => <p key={i}>{p}{i === paras.length - 1 ? leftover.map((x) => <Mark key={x.n} n={x.n} />) : null}</p>)}
          </div>
          {report.evidence_items?.length ? <div style={{ marginTop: 8 }}><SrcList items={report.evidence_items} show={3} /></div> : null}
        </section>

        {sectors.length ? (
          <section aria-labelledby="sectors-h">
            <h2 className="sec" id="sectors-h">Whose coverage this is<Marks notes={notes} place="sectors" /></h2>
            <div className="bars num" role="list">
              {sectors.map(([k, v], i) => (
                <div key={k} role="listitem" style={{ display: "contents" }}>
                  <span>{sectorLabel(k)}</span>
                  <span className="track" aria-hidden="true"><span className={i === 0 ? "fill lead" : "fill"} style={{ width: `${Math.max(0.8, (v / top) * 100)}%` }} /></span>
                  <span className="v">{n(v)}</span>
                </div>
              ))}
            </div>
            {share ? <p className="caption">Articles collected, by the kind of outlet. {share.pct}% came from {share.label} outlets, which have their own commercial incentives.</p> : null}
          </section>
        ) : null}

        <section aria-labelledby="signals-h">
          <h2 className="sec" id="signals-h">The signals<Marks notes={notes} place="signals" /></h2>
          {S.length > 1 ? (
            <nav aria-label="Signals in this report">
              <p className="contents">
                {S.map((s) => <a key={slugOf(s)} href={`#signal-${slugOf(s)}`}>{s.name}<span className="num">{items(s).length}</span></a>)}
              </p>
            </nav>
          ) : null}
          {S.map((s, i) => <SignalBlock key={slugOf(s)} s={s} i={i} />)}
        </section>

        {report.revision_history?.length ? (
          <section aria-labelledby="corrections-h">
            <h2 className="sec" id="corrections-h">Corrections</h2>
            <ol className="chron">
              {report.revision_history.map((rv, i) => (
                <li key={i}><span className="d"><time dateTime={rv.corrected_at}>{rv.corrected_at.slice(0, 10)}</time></span><div><b>Corrected</b><p>{rv.reason}</p></div></li>
              ))}
            </ol>
          </section>
        ) : null}

        <Notes notes={notes} />

        <section aria-labelledby="prov-h">
          <h2 className="sec" id="prov-h">The record</h2>
          <dl className="prov">
            <dt>Issued</dt><dd><time dateTime={report.report_date}>{report.report_date}</time>{dateModified !== report.report_date ? `, corrected ${dateModified.slice(0, 10)}` : ""}</dd>
            <dt>Review</dt><dd>{report.review_status === "reviewed" ? "Reviewed and approved by the editor" : report.review_status ?? "Not recorded"}</dd>
            {report.evidence_snapshot_sha256 ? <><dt>Evidence snapshot</dt><dd className="num" title={report.evidence_snapshot_sha256}>SHA-256 {report.evidence_snapshot_sha256}</dd></> : null}
            {report.content_hash ? <><dt>Archive checksum</dt><dd className="num">{report.content_hash}</dd></> : null}
            <dt>Cite as</dt><dd>{citation(report)}</dd>
            <dt>Machine-readable</dt><dd><a href={`/md/reports/${report.report_date}.md`} type="text/markdown">Markdown</a> · <a href={`/data/reports/${report.report_date}.json`} type="application/json">JSON</a> · <a href="/llms.txt">Guide for AI agents</a></dd>
            <dt>License</dt><dd>The index&apos;s own text and data: CC BY 4.0, with attribution and a link. The linked articles belong to their publishers.</dd>
          </dl>
        </section>
      </article>
    </main>
  );
}
