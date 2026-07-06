// app/archive/page.tsx
// lists all dated ARI3LLA INDEX reports as a historical record

import Link from "next/link";
import { getAllReports } from "../../lib/reports";

export const metadata = {
  title: "Archive — ARI3LLA INDEX",
  description: "Dated style signal reports issued by ARI3LLA INDEX.",
};

export default function Archive() {
  const reports = getAllReports();

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
          fontSize: "0.7rem",
          letterSpacing: "0.15em",
          textTransform: "uppercase",
          color: "var(--gray)",
          marginTop: "2rem",
        }}>
          {reports.length} report{reports.length === 1 ? "" : "s"} on file
        </p>
      </header>

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
            No reports on file yet.
          </p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column" }}>
            {reports.map((report) => (
              <Link
                key={report.report_date}
                href={`/reports/${report.report_date}`}
                style={{ textDecoration: "none", color: "inherit" }}
              >
                <div
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
                    fontSize: "0.7rem",
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
            ))}
          </div>
        )}
      </section>

      {/* footer */}
      <footer style={{
        width: "100%",
        borderTop: "1px solid var(--border)",
        padding: "2rem",
        textAlign: "center",
      }}>
        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.75rem",
          letterSpacing: "0.1em",
          textTransform: "uppercase",
          color: "var(--gray)",
        }}>
          <Link href="/" style={{ color: "var(--black)", textDecoration: "underline", textUnderlineOffset: "3px" }}>
            Current report
          </Link>
        </p>
      </footer>

    </main>
  );
}
