// app/timeline/page.tsx
// plain chronological index of signals across all dated reports — NYT
// topic-page / Pitchfork genre-page register, not a graph or dashboard.
// See docs/agent-logs/signals-timeline-design.md for the design rationale.

import Link from "next/link";
import { getTimelineEntries } from "../../lib/reports";

export const metadata = {
  title: "Timeline — ARI3LLA INDEX",
  description: "A chronological index of signals observed across dated ARI3LLA INDEX reports.",
};

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
    <main style={{
      minHeight: "100vh",
      background: "var(--white)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
    }}>

      {/* masthead */}
      <header style={{
        width: "100%",
        borderBottom: "3px solid var(--black)",
        padding: "4rem 2rem 3rem",
        textAlign: "center",
      }}>
        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.7rem",
          letterSpacing: "0.15em",
          textTransform: "uppercase",
          color: "var(--red)",
          marginBottom: "1rem",
        }}>
          Ari3lla Index
        </p>
        <h1 style={{
          fontFamily: "var(--font-instrument)",
          fontSize: "clamp(2.5rem, 8vw, 6rem)",
          fontWeight: "400",
          lineHeight: "0.95",
          letterSpacing: "-0.02em",
          textTransform: "uppercase",
          color: "var(--black)",
        }}>
          Timeline
        </h1>
        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.95rem",
          lineHeight: "1.7",
          color: "var(--gray)",
          maxWidth: "560px",
          margin: "1.5rem auto 0",
        }}>
          A chronological index of signals observed across dated reports.
          Entries are listed as recorded, by report date, with no ranking or
          trend projection implied.
        </p>
        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.7rem",
          letterSpacing: "0.15em",
          textTransform: "uppercase",
          color: "var(--gray)",
          marginTop: "2rem",
        }}>
          {entries.length} signal{entries.length === 1 ? "" : "s"} across {dates.length} report{dates.length === 1 ? "" : "s"}
        </p>
      </header>

      {/* timeline list */}
      <section
        aria-label="Signal timeline"
        style={{
          width: "100%",
          maxWidth: "800px",
          padding: "3rem 2rem 5rem",
        }}
      >
        {dates.length === 0 ? (
          <p style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.95rem",
            color: "var(--gray)",
            textAlign: "center",
            padding: "3rem 0",
          }}>
            No reports on file yet.
          </p>
        ) : (
          dates.map((date) => (
            <div key={date} style={{ marginBottom: "3rem" }}>
              <Link
                href={`/reports/${date}`}
                style={{ textDecoration: "none", color: "inherit" }}
              >
                <h2 style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.75rem",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  color: "var(--black)",
                  borderBottom: "1px solid var(--border)",
                  paddingBottom: "0.75rem",
                  marginBottom: "0.5rem",
                }}>
                  {date}
                </h2>
              </Link>
              <div style={{ display: "flex", flexDirection: "column" }}>
                {(byDate.get(date) ?? []).map((entry, i) => (
                  <div
                    key={`${date}-${i}`}
                    style={{
                      display: "grid",
                      gridTemplateColumns: "1fr auto auto",
                      gap: "1.5rem",
                      alignItems: "start",
                      padding: "1.1rem 0",
                      borderBottom: "1px solid var(--border)",
                    }}
                  >
                    {entry.signal_id ? (
                      <Link
                        href={`/signals/${entry.signal_id}`}
                        style={{
                          fontFamily: "var(--font-franklin)",
                          fontSize: "0.95rem",
                          lineHeight: "1.5",
                          color: "var(--black)",
                          textDecoration: "underline",
                          textUnderlineOffset: "3px",
                        }}
                      >
                        {entry.signal_name}
                      </Link>
                    ) : (
                      <p style={{
                        fontFamily: "var(--font-franklin)",
                        fontSize: "0.95rem",
                        lineHeight: "1.5",
                        color: "var(--black)",
                      }}>
                        {entry.signal_name}
                      </p>
                    )}
                    <p style={{
                      fontFamily: "var(--font-franklin)",
                      fontSize: "0.7rem",
                      letterSpacing: "0.1em",
                      textTransform: "uppercase",
                      color: "var(--gray)",
                      whiteSpace: "nowrap",
                      paddingTop: "0.15rem",
                    }}>
                      {entry.type}
                    </p>
                    <p style={{
                      fontFamily: "var(--font-franklin)",
                      fontSize: "0.7rem",
                      letterSpacing: "0.1em",
                      textTransform: "uppercase",
                      color: "var(--gray)",
                      whiteSpace: "nowrap",
                      paddingTop: "0.15rem",
                    }}>
                      {entry.confidence} confidence
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </section>

      {/* footer */}
      <footer style={{
        width: "100%",
        borderTop: "1px solid var(--border)",
        padding: "2rem",
        textAlign: "center",
        display: "flex",
        justifyContent: "center",
        gap: "2rem",
      }}>
        <Link href="/archive" style={{ fontFamily: "var(--font-franklin)", fontSize: "0.75rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "var(--black)", textDecoration: "underline", textUnderlineOffset: "3px" }}>
          Full archive
        </Link>
        <Link href="/" style={{ fontFamily: "var(--font-franklin)", fontSize: "0.75rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "var(--black)", textDecoration: "underline", textUnderlineOffset: "3px" }}>
          Current report
        </Link>
      </footer>

    </main>
  );
}
