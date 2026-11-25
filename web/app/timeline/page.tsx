// app/timeline/page.tsx
// A plain chronological index of signals across all dated reports, newest first,
// as a .chron dated list. Not a graph or a dashboard.

import Link from "next/link";
import { getTimelineEntries } from "../../lib/reports";
import { fmtDay, typeLabel } from "../../lib/editorial";
import { pageMetadata } from "../../lib/site";
import { Folio } from "../components/Chrome";

export const metadata = pageMetadata("/timeline", "Timeline", "A chronological index of signals observed across dated ARI3LLA INDEX reports, newest first, with no ranking implied.");

export default function Timeline() {
  const entries = getTimelineEntries();

  const byDate = new Map<string, typeof entries>();
  for (const entry of entries) {
    const list = byDate.get(entry.report_date) ?? [];
    list.push(entry);
    byDate.set(entry.report_date, list);
  }
  const dates = Array.from(byDate.keys());

  return (
    <main id="main-content">
      <Folio
        h1
        left="Timeline"
        right={`${entries.length} signal${entries.length === 1 ? "" : "s"} across ${dates.length} report${dates.length === 1 ? "" : "s"}, newest first`}
      />
      <p className="lede-intro" style={{ marginBottom: 18 }}>
        A chronological index of signals observed across dated reports. Entries are listed as
        recorded, by report date, with no ranking or trend projection implied.
      </p>

      {dates.length === 0 ? (
        <p className="note">No reports on file.</p>
      ) : (
        <ol className="chron" aria-label="Signals by report date">
          {dates.map((date) => (
            <li key={date}>
              <span className="d">
                <Link href={`/reports/${date}`}><time dateTime={date}>{fmtDay(date, true)}</time></Link>
              </span>
              <div>
                {(byDate.get(date) ?? []).map((entry, i) => (
                  <div key={`${date}-${i}`} style={{ marginBottom: 8 }}>
                    <b>{entry.signal_id ? <Link href={`/signals/${entry.signal_id}`}>{entry.signal_name}</Link> : entry.signal_name}</b>
                    <p>{typeLabel(entry.type)} · {entry.confidence} confidence</p>
                  </div>
                ))}
              </div>
            </li>
          ))}
        </ol>
      )}
    </main>
  );
}
