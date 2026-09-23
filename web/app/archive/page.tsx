// app/archive/page.tsx
// lists all dated ARI3LLA INDEX reports as a historical record

import Link from "next/link";
import { getAllReports, getConsecutiveThinWeekCount, getThisWeeksIndex, getRecurringSignals } from "../../lib/reports";
import { pageMetadata } from "../../lib/site";

export const metadata = pageMetadata("/archive", "Archive", "Every dated ARI3LLA INDEX report, preserved as issued.");


export default function Archive() {
  const reports = getAllReports();
  const thinStreak = getConsecutiveThinWeekCount();
  const thisWeek = getThisWeeksIndex();
  const recurringSignals = getRecurringSignals(4);

  return (
    <main id="main-content" style={{
      flex: 1,
      background: "var(--white)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
    }}>

      {/* masthead */}
      <header className="page-masthead">
        <h1 className="page-title">
          Archive
        </h1>
        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.95rem",
          lineHeight: "1.7",
          color: "var(--gray)",
          maxWidth: "560px",
          margin: "1.5rem auto 0",
        }}>
          A historical record of weekly style signal reports. Each entry reflects
          the source material collected during its stated window and is preserved
          as issued.
        </p>
        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.75rem",
          letterSpacing: "0.15em",
          textTransform: "uppercase",
          color: "var(--gray)",
          marginTop: "2rem",
        }}>
          {reports.length} report{reports.length === 1 ? "" : "s"} on file
        </p>
        {thinStreak >= 2 && (
          <p style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.85rem",
            lineHeight: "1.6",
            color: "var(--gray)",
            maxWidth: "560px",
            margin: "1.5rem auto 0",
            borderTop: "1px solid var(--border)",
            paddingTop: "1.5rem",
          }}>
            The archive&apos;s {thinStreak} most recent reporting windows were
            classified thin, reflecting limited genuine signal volume rather
            than a change in collection method.
          </p>
        )}
      </header>

      {/* pointer to the live current-week snapshot, not a duplicate of it —
          this page is the frozen historical record; THIS WEEK'S INDEX is a
          live "check it now" module and belongs on the homepage only */}
      {thisWeek && (
        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.8rem",
          letterSpacing: "0.02em",
          color: "var(--gray)",
          textAlign: "center",
          maxWidth: "560px",
          padding: "1.5rem 2rem 0",
        }}>
          Looking for the current snapshot rather than the historical record?
          See{" "}
          <Link href="/" style={{ color: "var(--black)", textDecoration: "underline", textUnderlineOffset: "3px" }}>
            THIS WEEK&apos;S INDEX
          </Link>{" "}
          on the homepage.
        </p>
      )}

      {/* report list */}
      <section
        aria-label="Dated reports"
        style={{
          width: "100%",
          maxWidth: "800px",
          padding: "3rem 2rem 5rem",
        }}
      >
        {reports.length === 0 ? (
          <p style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.95rem",
            color: "var(--gray)",
            textAlign: "center",
            padding: "3rem 0",
          }}>
            No reports on file.
          </p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column" }}>
            {reports.map((report, i) => {
              const year = report.report_date.slice(0, 4);
              const prevYear = i > 0 ? reports[i - 1].report_date.slice(0, 4) : null;
              const isNewYear = year !== prevYear;
              return (
                <div key={report.report_date}>
                  {isNewYear && (
                    <h2
                      style={{
                        fontFamily: "var(--font-franklin)",
                        fontSize: "0.75rem",
                        letterSpacing: "0.15em",
                        textTransform: "uppercase",
                        color: "var(--red)",
                        margin: i === 0 ? "0 0 0.5rem" : "2.5rem 0 0.5rem",
                        paddingTop: i === 0 ? 0 : "1rem",
                        borderTop: i === 0 ? "none" : "1px solid var(--border)",
                      }}
                    >
                      {year}
                    </h2>
                  )}
                  <Link
                    href={`/reports/${report.report_date}`}
                    style={{ textDecoration: "none", color: "inherit" }}
                  >
                    <div className="stack-sm"
                      style={{
                        display: "grid",
                        gridTemplateColumns: "160px 1fr auto",
                        gap: "2rem",
                        alignItems: "start",
                        padding: "1.75rem 0",
                        borderBottom: "1px solid var(--border)",
                      }}
                    >
                      <p style={{
                        fontFamily: "var(--font-franklin)",
                        fontSize: "0.75rem",
                        letterSpacing: "0.1em",
                        textTransform: "uppercase",
                        color: "var(--black)",
                        paddingTop: "0.2rem",
                      }}>
                        {report.report_date}
                      </p>
                      <p style={{
                        fontFamily: "var(--font-franklin)",
                        fontSize: "0.95rem",
                        lineHeight: "1.6",
                        color: "var(--gray)",
                      }}>
                        {report.top_signals?.[0]?.name
                          ? `Top signal: ${report.top_signals[0].name}`
                          : "Report on file"}
                      </p>
                      <p style={{
                        fontFamily: "var(--font-franklin)",
                        fontSize: "0.75rem",
                        letterSpacing: "0.1em",
                        textTransform: "uppercase",
                        color: "var(--gray)",
                        whiteSpace: "nowrap",
                        paddingTop: "0.2rem",
                      }}>
                        {report.sources_scanned} sources
                      </p>
                    </div>
                  </Link>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* recurring-across-the-archive note -- deliberately small. Run 24 set a
          revisit threshold of 4-5 signals recurring 4+ times before building
          any retrospective/year-in-review feature; run 32 re-checked and it
          still wasn't met. Run 47 found it numerically met (4 signals) but
          all four are unresolved factual/administrative tracking items
          (award-winner status, a coverage gap), not recurring style
          aesthetics -- the kind of recurrence the threshold assumed. That's
          a reason to surface it plainly, not a reason to build a narrative
          retrospective page. See docs/agent-logs/recurrence-milestone-review-run47.md */}
      {recurringSignals.length > 0 && (
        <section
          aria-label="Recurring across the archive"
          style={{
            width: "100%",
            maxWidth: "800px",
            padding: "0 2rem 3rem",
          }}
        >
          <h2 style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.75rem",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            color: "var(--gray)",
            borderTop: "1px solid var(--border)",
            paddingTop: "2rem",
            marginBottom: "1rem",
          }}>
            Recurring across the archive
          </h2>
          <p style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.85rem",
            lineHeight: "1.6",
            color: "var(--gray)",
            marginBottom: "1.25rem",
          }}>
            Signals appearing in four or more separate reporting windows.
            All entries currently in this list are unresolved factual or
            institutional tracking items rather than recurring style
            aesthetics -- a distinction the archive continues to track
            separately rather than treat as equivalent.
          </p>
          <div style={{ display: "flex", flexDirection: "column" }}>
            {recurringSignals.map((s) => (
              <Link
                key={s.signal_id}
                href={`/signals/${s.signal_id}`}
                style={{ textDecoration: "none", color: "inherit" }}
              >
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr auto",
                    gap: "1rem",
                    alignItems: "baseline",
                    padding: "0.85rem 0",
                    borderBottom: "1px solid var(--border)",
                  }}
                >
                  <p style={{
                    fontFamily: "var(--font-franklin)",
                    fontSize: "0.9rem",
                    color: "var(--black)",
                  }}>
                    {s.name}
                  </p>
                  <p style={{
                    fontFamily: "var(--font-franklin)",
                    fontSize: "0.75rem",
                    letterSpacing: "0.08em",
                    textTransform: "uppercase",
                    color: "var(--gray)",
                    whiteSpace: "nowrap",
                  }}>
                    {s.occurrence_count} reports &middot; {s.first_seen} &ndash; {s.last_seen}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}


    </main>
  );
}
