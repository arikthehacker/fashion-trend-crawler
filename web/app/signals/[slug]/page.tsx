// /signals/[slug]: a signal's file. Its week-by-week history, the newest week's articles by day,
// and earlier weeks folded (design/SITE_SPEC_photocopy.md §4).

import Link from "next/link";
import { notFound } from "next/navigation";
import { getAllReports, getAllSignalSlugs, type Report, type TopSignal, type EvidenceItem } from "../../../lib/reports";
import { slugOf, typeLabel, volLabel, editorNote, items, outlets, shortWindow, fmtDay, footnotes } from "../../../lib/editorial";
import { SITE_URL, SITE_NAME, EDITOR_LABEL, pageMetadata } from "../../../lib/site";
import { Folio, Notes } from "../../components/Chrome";

export const dynamicParams = false;

export function generateStaticParams() {
  const slugs = getAllSignalSlugs();
  return slugs.length ? slugs.map((slug) => ({ slug })) : [{ slug: "none" }];
}

function historyOf(slug: string): { r: Report; s: TopSignal }[] {
  const out: { r: Report; s: TopSignal }[] = [];
  for (const r of getAllReports()) for (const s of r.top_signals) if (slugOf(s) === slug) out.push({ r, s });
  return out; // newest first, as getAllReports returns them
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const h = historyOf(slug);
  if (!h.length) return { title: "Signal not found", robots: { index: false } };
  const { s } = h[0];
  const total = getAllReports().length;
  const desc = `${s.name}: a ${typeLabel(s.type)} signal in ${h.length} of ${total} weekly reports, with every article behind it and the editor's notes, week by week.`;
  const base = pageMetadata(`/signals/${slug}`, `${s.name}, signal file`, desc.length > 160 ? `${desc.slice(0, 157)}...` : desc);
  return { ...base, alternates: { ...base.alternates, types: { "application/json": `/data/signals/${slug}.json`, "text/markdown": `/md/signals/${slug}.md` } } };
}

function byDay(list: EvidenceItem[]) {
  const days = new Map<string, EvidenceItem[]>();
  for (const it of list.slice().sort((a, b) => a.published_at.localeCompare(b.published_at))) {
    const d = it.published_at.slice(0, 10);
    days.set(d, [...(days.get(d) ?? []), it]);
  }
  return [...days.entries()];
}

function Classifieds({ s }: { s: TopSignal }) {
  return (
    <div className="classifieds">
      {byDay(items(s)).map(([d, its]) => (
        <div className="day" key={d}>
          <h3><time dateTime={d}>{fmtDay(d, true)}</time></h3>
          <ul className="srcs">
            {its.map((it, i) => <li key={`${it.url}-${i}`}><a href={it.url} rel="noopener">{it.title || it.url}</a><span>{it.outlet_domain}</span></li>)}
          </ul>
        </div>
      ))}
    </div>
  );
}

export default async function SignalPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const h = historyOf(slug);
  if (!h.length) notFound();
  const { r, s } = h[0];
  const all = getAllReports();
  const note = editorNote(s);
  const notes = footnotes(r).filter((x) => x.place === "signals");
  const url = `${SITE_URL}/signals/${slug}`;
  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      { "@type": "DefinedTerm", "@id": `${url}#term`, name: s.name, url, description: s.evidence,
        inDefinedTermSet: { "@type": "DefinedTermSet", name: `${SITE_NAME} signals`, url: `${SITE_URL}/signals` } },
      { "@type": "BreadcrumbList", itemListElement: [
        { "@type": "ListItem", position: 1, name: "Front page", item: SITE_URL },
        { "@type": "ListItem", position: 2, name: "Index of signals", item: `${SITE_URL}/signals` },
        { "@type": "ListItem", position: 3, name: s.name, item: url },
      ] },
    ],
  };
  return (
    <main id="main-content">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }} />
      <Folio left="Signal file" right={<Link href="/signals">All signals</Link>} />
      <div className="rtop">
        <div>
          <p className="kicker">{typeLabel(s.type)}</p>
          <h1 className="hed toner">{s.name}</h1>
          <p className="deck">
            {h.length === 1
              ? <>First recorded in the week of {shortWindow(r)}. It appears in 1 of {all.length} reports{r.report_date === all[0].report_date ? ", the latest one" : ""}.</>
              : <>Recorded in {h.length} of {all.length} weekly reports, most recently the week of {shortWindow(r)}.</>}
          </p>
          <div className="cols one"><p>{s.evidence}</p></div>
        </div>
        <aside>
          {note ? <blockquote className="pull"><small>{EDITOR_LABEL}, latest week</small>{note}</blockquote> : null}
          <p className="note num">
            {s.confidence.charAt(0).toUpperCase() + s.confidence.slice(1)} confidence · {volLabel(s.volatility)}. <Link href="/methodology">What these mean</Link>
          </p>
        </aside>
      </div>

      <section aria-labelledby="weeks-h">
        <h2 className="sec" id="weeks-h">Week by week</h2>
        <div className="table-wrap">
          <table className="weeks num">
            <thead>
              <tr><th scope="col">Week</th><th scope="col">Articles</th><th scope="col">Volatility</th><th scope="col">Confidence</th><th scope="col">{EDITOR_LABEL}&apos;s note</th></tr>
            </thead>
            <tbody>
              {h.map(({ r: rr, s: ss }) => (
                <tr key={rr.report_date}>
                  <td className="s"><Link href={`/reports/${rr.report_date}#signal-${slug}`}>{shortWindow(rr)}</Link></td>
                  <td>{items(ss).length} from {outlets(ss)} outlets</td>
                  <td>{volLabel(ss.volatility)}</td>
                  <td>{ss.confidence}</td>
                  <td className="q">{editorNote(ss) || "None"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section aria-labelledby="days-h">
        <h2 className="sec" id="days-h">Every article behind it, by day, week of {shortWindow(r)}</h2>
        <Classifieds s={s} />
      </section>

      {h.length > 1 ? (
        <section aria-labelledby="earlier-h">
          <h2 className="sec" id="earlier-h">Earlier weeks</h2>
          {h.slice(1).map(({ r: rr, s: ss }) => (
            <details className="more" key={rr.report_date}>
              <summary>Week of {shortWindow(rr)}: {items(ss).length} articles</summary>
              <Classifieds s={ss} />
            </details>
          ))}
        </section>
      ) : null}

      <Notes notes={notes} />

      <p className="note" style={{ marginTop: 24 }}>
        Cite as: {SITE_NAME}. &ldquo;{s.name}, signal file.&rdquo; {url} · Machine-readable: <a href={`/md/signals/${slug}.md`} type="text/markdown">Markdown</a> · <a href={`/data/signals/${slug}.json`} type="application/json">JSON</a> · <a href="/llms.txt">Guide for AI agents</a>
      </p>
    </main>
  );
}
