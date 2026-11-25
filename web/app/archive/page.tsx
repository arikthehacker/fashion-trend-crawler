// Back issues: every report, newest first.

import Link from "next/link";
import { getAllReports } from "../../lib/reports";
import { headline, ranked, slugOf, shortWindow, n } from "../../lib/editorial";
import { pageMetadata } from "../../lib/site";
import { Folio } from "../components/Chrome";

export const metadata = pageMetadata("/archive", "Back issues", "Every weekly ARI3LLA INDEX report, newest first, with its headline, its largest signals and how much was collected.");

export default function Archive() {
  const R = getAllReports();
  return (
    <main id="main-content">
      <Folio h1 left="Back issues" right={<>{R.length} report{R.length === 1 ? "" : "s"}, newest first</>} />
      {R.map((r) => {
        const S = ranked(r);
        return (
          <article className="issue" key={r.report_date} aria-labelledby={`w-${r.report_date}`}>
            <p className="when" id={`w-${r.report_date}`}><Link href={`/reports/${r.report_date}`}>{shortWindow(r)}</Link></p>
            <div>
              <h2 className="what"><Link href={`/reports/${r.report_date}`}>{headline(r)}</Link></h2>
              <p className="names">
                {S.slice(0, 6).map((s, i) => <span key={slugOf(s)}>{i ? ", " : ""}<Link href={`/signals/${slugOf(s)}`}>{s.name}</Link></span>)}
                {S.length > 6 ? ` and ${S.length - 6} more` : ""}
              </p>
            </div>
            <p className="note num">
              {n(r.items_collected)} items from {r.sources_scanned} sources, {r.top_signals.length} signals.
              {r.collection_status === "thin" ? <><br />A thin week: fewer signals met the bar, and none were padded in.</> : null}
            </p>
          </article>
        );
      })}
    </main>
  );
}
