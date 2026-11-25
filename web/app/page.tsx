// The front page: the newest report's headline and story, and its index of signals.

import Link from "next/link";
import { getLatestReport } from "../lib/reports";
import { headline, ranked, items, slugOf, sentences, standfirst, plusFinds } from "../lib/editorial";
import { SITE_URL, SITE_NAME, SITE_DESCRIPTION, pageMetadata } from "../lib/site";
import { Dateline, Byline, Folio } from "./components/Chrome";

export function generateMetadata() {
  const r = getLatestReport();
  const desc = r ? `The front page of a weekly, source-linked record of style language. This week: ${headline(r)}.` : SITE_DESCRIPTION;
  const base = pageMetadata("/", r ? headline(r) : "A weekly, source-linked record of style language", desc.length > 160 ? SITE_DESCRIPTION : desc);
  return { ...base, title: { absolute: `${SITE_NAME}: a weekly, source-linked record of style language` } };
}

export default function Home() {
  const r = getLatestReport();
  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      { "@type": "WebSite", "@id": `${SITE_URL}#website`, name: SITE_NAME, url: SITE_URL, description: SITE_DESCRIPTION, inLanguage: "en",
        potentialAction: { "@type": "SearchAction", target: `${SITE_URL}/search?q={search_term_string}`, "query-input": "required name=search_term_string" } },
      { "@type": "Organization", "@id": `${SITE_URL}#org`, name: SITE_NAME, url: SITE_URL, logo: `${SITE_URL}/icon` },
    ],
  };
  if (!r) {
    return (
      <main id="main-content">
        <Folio h1 left="No report yet" />
        <p className="lede-intro">The first weekly report has not been published yet.</p>
      </main>
    );
  }
  const S = ranked(r);
  const ss = sentences(r.executive_summary);
  const body = ss.length > 5 ? [ss.slice(3, 5).join(" "), ss.slice(5, 8).join(" ")] : [ss.join(" ")];
  return (
    <main id="main-content">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\u003c") }} />
      <Dateline report={r} />
      <div className="front">
        <article>
          <h1 className="hed toner">{headline(r)}</h1>
          {plusFinds(r).length ? (
            <p className="deck">Plus: {plusFinds(r).map((s, i, all) => (
              <span key={slugOf(s)}>{i ? (i === all.length - 1 ? " and " : ", ") : ""}<Link href={`/signals/${slugOf(s)}`}>{s.name}</Link></span>
            ))}.</p>
          ) : <p className="deck">{standfirst(r)}</p>}
          <Byline />
          <div className="cols drop">{body.filter(Boolean).map((p, i) => <p key={i}>{p}</p>)}</div>
          <nav className="inside" aria-label="Inside">
            <b>Inside</b>
            <Link href={`/reports/${r.report_date}`}>The full report</Link>
            <Link href="/archive">Back issues</Link>
            <Link href="/signals">Every signal</Link>
            <Link href="/methodology">How the index works</Link>
          </nav>
        </article>
        <aside className="side" aria-labelledby="idx-h">
          <h2 id="idx-h">Latest index <span>articles</span></h2>
          <ol>
            {S.map((s, i) => (
              <li key={slugOf(s)}>
                <Link href={`/signals/${slugOf(s)}`}><span className="w">{i + 1}. {s.name}</span><span className="c num">{items(s).length}</span></Link>
              </li>
            ))}
          </ol>
        </aside>
      </div>
    </main>
  );
}
