// app/signals/[slug]/page.tsx
// longitudinal history of a single signal (by signal_id) across all dated
// reports — a plain chronological list, no forecast/trend arrow. See
// docs/agent-logs/signals-timeline-design.md for the design rationale.

import Link from "next/link";
import { notFound } from "next/navigation";
import { SITE_URL } from "../../../lib/site";
import { getAllSignalSlugs, getSignalHistory, getSignalRecencyStatus } from "../../../lib/reports";

export function generateStaticParams() {
  const slugs = getAllSignalSlugs();
  // `output: "export"` refuses to build a dynamic route with zero params. While
  // the archive is empty, emit one placeholder that renders the 404 page below.
  if (slugs.length === 0) return [{ slug: "none" }];
  return slugs.map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return {
    title: `Signal: ${slug}`,
    alternates: { canonical: `${SITE_URL}/signals/${slug}` },
    description: `Occurrence history for the signal "${slug}" across dated ARI3LLA INDEX reports.`,
  };
}

const labelStyle: React.CSSProperties = {
  fontFamily: "var(--font-franklin)",
  fontSize: "0.75rem",
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
  const recency = getSignalRecencyStatus(slug);

  return (
    <main id="main-content" style={{
      flex: 1,
      background: "var(--white)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
    }}>

      {/* header */}
      <header className="page-masthead">
        <p className="page-eyebrow">Signal History</p>
        <h1 className="page-title page-title--plain">
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
        {recency && (
          <p style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.75rem",
            letterSpacing: "0.05em",
            color: "var(--gray)",
            marginTop: "0.5rem",
          }}>
            {recency.isMostRecentReport
              ? "Appeared in the most recently published report."
              : `Last appeared ${recency.lastSeen}. Not recorded in the ${recency.reportsSinceLastSeen === 1 ? "report" : `${recency.reportsSinceLastSeen} reports`} published since.`}
          </p>
        )}
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
                {signal.source_domains && signal.source_domains.length > 0 && (
                  <span>Sources: {signal.source_domains.join(", ")}</span>
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
              {signal.human_editor_note && (
                <div style={{ marginTop: "1rem" }}>
                  <h4 style={{
                    fontFamily: "var(--font-franklin)",
                    fontSize: "0.75rem",
                    letterSpacing: "0.1em",
                    textTransform: "uppercase",
                    color: "var(--red)",
                    marginBottom: "0.4rem",
                  }}>
                    Editorial Close-Out
                  </h4>
                  <p style={{
                    fontFamily: "var(--font-franklin)",
                    fontSize: "0.85rem",
                    lineHeight: "1.6",
                    color: "var(--black)",
                  }}>
                    {signal.human_editor_note}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>


    </main>
  );
}
