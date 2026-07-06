// app/signals/[slug]/page.tsx
// longitudinal history of a single signal (by signal_id) across all dated
// reports — a plain chronological list, no forecast/trend arrow. See
// docs/agent-logs/signals-timeline-design.md for the design rationale.

import Link from "next/link";
import { notFound } from "next/navigation";
import { getAllSignalSlugs, getSignalHistory } from "../../../lib/reports";

export function generateStaticParams() {
  return getAllSignalSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return {
    title: `${slug} — ARI3LLA INDEX`,
    description: `Occurrence history for the signal "${slug}" across dated ARI3LLA INDEX reports.`,
  };
}

const labelStyle: React.CSSProperties = {
  fontFamily: "var(--font-franklin)",
  fontSize: "0.7rem",
  letterSpacing: "0.15em",
  textTransform: "uppercase",
  color: "var(--gray)",
  marginBottom: "1.5rem",
};

const sectionStyle: React.CSSProperties = {
  width: "100%",
  maxWidth: "800px",
  padding: "3.5rem 2rem",
  borderBottom: "1px solid var(--border)",
};

export default async function SignalPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const occurrences = getSignalHistory(slug);

  if (occurrences.length === 0) notFound();

  const firstSeen = occurrences[0].report_date;
  const name = occurrences[occurrences.length - 1].signal.name;

  return (
    <main style={{
      minHeight: "100vh",
      background: "var(--white)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
    }}>

      {/* header */}
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
          Signal History &nbsp;·&nbsp; Ari3lla Index
        </p>
        <h1 style={{
          fontFamily: "var(--font-instrument)",
          fontSize: "clamp(2rem, 6vw, 4rem)",
          fontWeight: "400",
          lineHeight: "1",
          letterSpacing: "-0.02em",
          color: "var(--black)",
        }}>
          {name}
        </h1>
        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.75rem",
          letterSpacing: "0.05em",
          color: "var(--gray)",
          marginTop: "1.5rem",
        }}>
          First recorded {firstSeen} &nbsp;·&nbsp; {occurrences.length} occurrence{occurrences.length === 1 ? "" : "s"} on file
        </p>
      </header>

      {/* occurrence list */}
      <section aria-label="Occurrences" style={sectionStyle}>
        <h2 style={labelStyle}>Recorded Occurrences</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
          {occurrences.map(({ report_date, signal }) => (
            <div key={report_date} style={{ borderTop: "1px solid var(--border)", paddingTop: "1.5rem" }}>
              <Link href={`/reports/${report_date}`} style={{ textDecoration: "none", color: "inherit" }}>
                <h3 style={{
                  fontFamily: "var(--font-instrument)",
                  fontSize: "1.2rem",
                  marginBottom: "0.75rem",
                  textDecoration: "underline",
                  textUnderlineOffset: "3px",
                }}>
                  {report_date}
                </h3>
              </Link>
              <div style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "0.4rem 1.5rem",
                fontFamily: "var(--font-franklin)",
                fontSize: "0.75rem",
                letterSpacing: "0.05em",
                textTransform: "uppercase",
                color: "var(--gray)",
                marginBottom: "1rem",
              }}>
                <span>Confidence: {signal.confidence}</span>
                <span>Volatility: {signal.volatility}</span>
                {signal.source_sectors?.length > 0 && (
                  <span>Sectors: {signal.source_sectors.join(", ")}</span>
                )}
              </div>
              <p style={{
                fontFamily: "var(--font-franklin)",
                fontSize: "0.95rem",
                lineHeight: "1.7",
                color: "var(--black)",
                marginBottom: "0.5rem",
              }}>
                {signal.evidence}
              </p>
              {signal.index_note && (
                <p style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.85rem",
                  lineHeight: "1.6",
                  color: "var(--gray)",
                  fontStyle: "italic",
                }}>
                  Index note: {signal.index_note}
                </p>
              )}
            </div>
          ))}
        </div>
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
        <Link href="/timeline" style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.75rem",
          letterSpacing: "0.1em",
          textTransform: "uppercase",
          color: "var(--black)",
          textDecoration: "underline",
          textUnderlineOffset: "3px",
        }}>
          Timeline
        </Link>
        <Link href="/archive" style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.75rem",
          letterSpacing: "0.1em",
          textTransform: "uppercase",
          color: "var(--black)",
          textDecoration: "underline",
          textUnderlineOffset: "3px",
        }}>
          Full archive
        </Link>
        <Link href="/" style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.75rem",
          letterSpacing: "0.1em",
          textTransform: "uppercase",
          color: "var(--black)",
          textDecoration: "underline",
          textUnderlineOffset: "3px",
        }}>
          Current report
        </Link>
      </footer>

    </main>
  );
}
