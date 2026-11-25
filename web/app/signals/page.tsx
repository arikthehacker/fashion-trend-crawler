// Index of signals: every signal across every report, A to Z, with the weeks it appeared.

import Link from "next/link";
import { getAllReports, type Report, type TopSignal } from "../../lib/reports";
import { slugOf, typeLabel, fmtDay } from "../../lib/editorial";
import { pageMetadata } from "../../lib/site";
import { Folio } from "../components/Chrome";

export const metadata = pageMetadata("/signals", "Index of signals", "Every style signal the ARI3LLA INDEX has recorded, A to Z, with each weekly report it appeared in.");

export default function SignalsIndex() {
  const seen = new Map<string, { s: TopSignal; reports: Report[] }>();
  for (const r of getAllReports().slice().reverse()) {
    for (const s of r.top_signals) {
      const id = slugOf(s);
      const e = seen.get(id) ?? { s, reports: [] };
      e.s = s; // keep the newest name
      e.reports.push(r);
      seen.set(id, e);
    }
  }
  const all = [...seen.entries()].sort((a, b) => a[1].s.name.localeCompare(b[1].s.name, "en", { sensitivity: "base" }));
  const groups = new Map<string, typeof all>();
  for (const x of all) {
    const L = x[1].s.name.charAt(0).toUpperCase();
    groups.set(L, [...(groups.get(L) ?? []), x]);
  }
  return (
    <main id="main-content">
      <Folio h1 left="Index of signals" right={<>{all.length} signals, A to Z, with every week each appeared</>} />
      <div className="bindex">
        {[...groups.entries()].map(([L, xs]) => (
          <section className="letter" key={L} aria-labelledby={`l-${L}`}>
            <h2 id={`l-${L}`}>{L}</h2>
            {xs.map(([id, { s, reports }]) => (
              <p key={id}>
                <Link className="n" href={`/signals/${id}`}>{s.name}</Link> <span>{typeLabel(s.type)} · {reports.length} week{reports.length === 1 ? "" : "s"}</span>
                <br />
                {reports.slice().reverse().map((r, i) => (
                  <span key={r.report_date} style={{ color: "inherit" }}>{i ? ", " : ""}<Link href={`/reports/${r.report_date}#signal-${id}`}>{fmtDay(r.collection_window.end, true)}</Link></span>
                ))}
              </p>
            ))}
          </section>
        ))}
      </div>
    </main>
  );
}
