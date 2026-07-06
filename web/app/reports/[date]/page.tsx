// app/reports/[date]/page.tsx
// renders a single dated ARI3LLA INDEX report

import Link from "next/link";
import { notFound } from "next/navigation";
import { getAllReportDates, getReportByDate } from "../../../lib/reports";

export function generateStaticParams() {
  return getAllReportDates().map((date) => ({ date }));
}

export async function generateMetadata({ params }: { params: Promise<{ date: string }> }) {
  const { date } = await params;
  return {
    title: `${date} — ARI3LLA INDEX`,
    description: `Weekly style signal report issued ${date}.`,
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

function TagList({ items }: { items: string[] }) {
  if (!items?.length) return null;
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.6rem" }}>
      {items.map((item, i) => (
        <span
          key={i}
          style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.8rem",
            color: "var(--black)",
            border: "1px solid var(--border)",
            padding: "0.35rem 0.75rem",
          }}
        >
          {item}
        </span>
      ))}
    </div>
  );
}

export default async function ReportPage({ params }: { params: Promise<{ date: string }> }) {
  const { date } = await params;
  const report = getReportByDate(date);

  if (!report) notFound();

  const totalSources = Object.values(report.source_sector_breakdown || {}).reduce(
    (a, b) => a + b,
    0
  );

  return (
    <main style={{
      minHeight: "100vh",
      background: "var(--white)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
    }}>

      {/* report header */}
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
          Weekly Style Signal Report &nbsp;·&nbsp; Issued by Ari3lla Index
        </p>
        <h1 style={{
          fontFamily: "var(--font-instrument)",
          fontSize: "clamp(2.2rem, 7vw, 5rem)",
          fontWeight: "400",
          lineHeight: "1",
          letterSpacing: "-0.02em",
          color: "var(--black)",
        }}>
          {report.report_date}
        </h1>

        <div style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          gap: "0.5rem 2rem",
          marginTop: "2rem",
          fontFamily: "var(--font-franklin)",
          fontSize: "0.75rem",
          letterSpacing: "0.05em",
          color: "var(--gray)",
        }}>
          <span>Collection window: {report.collection_window?.start}–{report.collection_window?.end}</span>
          <span>Sources scanned: {report.sources_scanned}</span>
          <span>Items collected: {report.items_collected}</span>
        </div>
      </header>

      {/* executive summary */}
      <section aria-label="Executive summary" style={sectionStyle}>
        <p style={labelStyle}>Executive Summary</p>
        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "1.05rem",
          lineHeight: "1.8",
          color: "var(--black)",
        }}>
          {report.executive_summary}
        </p>
      </section>

      {/* source sector breakdown */}
      {totalSources > 0 && (
        <section aria-label="Source sector breakdown" style={sectionStyle}>
          <p style={labelStyle}>Source Sectors</p>
          <div style={{ display: "flex", flexDirection: "column" }}>
            {Object.entries(report.source_sector_breakdown).map(([sector, count]) => (
              <div
                key={sector}
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr auto",
                  gap: "1rem",
                  padding: "0.75rem 0",
                  borderBottom: "1px solid var(--border)",
                  alignItems: "center",
                }}
              >
                <p style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.85rem",
                  letterSpacing: "0.05em",
                  textTransform: "uppercase",
                  color: "var(--black)",
                }}>
                  {sector.replace(/_/g, " ")}
                </p>
                <p style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.85rem",
                  color: "var(--gray)",
                }}>
                  {count}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* observed signals */}
      {report.top_signals?.length > 0 && (
        <section aria-label="Observed signals" style={sectionStyle}>
          <p style={labelStyle}>Observed Signals</p>
          <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
            {report.top_signals.map((signal, i) => (
              <div key={i} style={{ borderTop: "1px solid var(--border)", paddingTop: "1.5rem" }}>
                {signal.signal_id ? (
                  <Link
                    href={`/signals/${signal.signal_id}`}
                    style={{
                      fontFamily: "var(--font-instrument)",
                      fontSize: "1.4rem",
                      marginBottom: "0.75rem",
                      display: "block",
                      color: "var(--black)",
                      textDecoration: "underline",
                      textUnderlineOffset: "4px",
                    }}
                  >
                    {i + 1}. {signal.name}
                  </Link>
                ) : (
                  <p style={{
                    fontFamily: "var(--font-instrument)",
                    fontSize: "1.4rem",
                    marginBottom: "0.75rem",
                  }}>
                    {i + 1}. {signal.name}
                  </p>
                )}
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
                  <span>Type: {signal.type}</span>
                  <span>Confidence: {signal.confidence}</span>
                  <span>Volatility: {signal.volatility}</span>
                  <span>Origin: {signal.origin_classification}</span>
                  {signal.source_sectors?.length > 0 && (
                    <span>Sectors: {signal.source_sectors.join(", ")}</span>
                  )}
                  {(signal.source_corroboration_count ?? 1) > 1 && (
                    <span>Corroborated by {signal.source_corroboration_count} sources</span>
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
      )}

      {/* repeated keywords */}
      {report.repeated_keywords?.length > 0 && (
        <section aria-label="Repeated keywords" style={sectionStyle}>
          <p style={labelStyle}>Repeated Keywords</p>
          <TagList items={report.repeated_keywords} />
        </section>
      )}

      {/* garments / silhouettes / materials / colors */}
      <section aria-label="Garments, silhouettes, materials, colors" style={sectionStyle}>
        <p style={labelStyle}>Garments, Silhouettes, Materials, Colors</p>
        <div style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
          {[
            ["Garments", report.garments],
            ["Silhouettes", report.silhouettes],
            ["Materials", report.materials],
            ["Colors", report.colors],
          ].map(([title, items]) => (
            (items as string[])?.length > 0 && (
              <div key={title as string}>
                <p style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.7rem",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  color: "var(--black)",
                  marginBottom: "0.75rem",
                }}>
                  {title}
                </p>
                <TagList items={items as string[]} />
              </div>
            )
          ))}
        </div>
      </section>

      {/* aesthetic / cultural references */}
      {(report.aesthetic_terms?.length > 0 || report.cultural_references?.length > 0) && (
        <section aria-label="Aesthetic and cultural references" style={sectionStyle}>
          <p style={labelStyle}>Aesthetic &amp; Cultural References</p>
          <div style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
            {report.aesthetic_terms?.length > 0 && (
              <div>
                <p style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.7rem",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  color: "var(--black)",
                  marginBottom: "0.75rem",
                }}>
                  Aesthetic Terms
                </p>
                <TagList items={report.aesthetic_terms} />
              </div>
            )}
            {report.cultural_references?.length > 0 && (
              <div>
                <p style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.7rem",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  color: "var(--black)",
                  marginBottom: "0.75rem",
                }}>
                  Cultural References
                </p>
                <TagList items={report.cultural_references} />
              </div>
            )}
          </div>
        </section>
      )}

      {/* volatility / incentive / confidence notes */}
      {(report.volatility_notes || report.incentive_notes || report.confidence_notes) && (
        <section aria-label="Methodology notes" style={sectionStyle}>
          <p style={labelStyle}>Notes</p>
          <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            {report.confidence_notes && (
              <p style={{ fontFamily: "var(--font-franklin)", fontSize: "0.9rem", lineHeight: "1.7", color: "var(--gray)" }}>
                <strong style={{ color: "var(--black)" }}>Confidence: </strong>
                {report.confidence_notes}
              </p>
            )}
            {report.volatility_notes && (
              <p style={{ fontFamily: "var(--font-franklin)", fontSize: "0.9rem", lineHeight: "1.7", color: "var(--gray)" }}>
                <strong style={{ color: "var(--black)" }}>Volatility: </strong>
                {report.volatility_notes}
              </p>
            )}
            {report.incentive_notes && (
              <p style={{ fontFamily: "var(--font-franklin)", fontSize: "0.9rem", lineHeight: "1.7", color: "var(--gray)" }}>
                <strong style={{ color: "var(--black)" }}>Source incentive: </strong>
                {report.incentive_notes}
              </p>
            )}
          </div>
        </section>
      )}

      {/* limitations */}
      {report.limitations?.length > 0 && (
        <section aria-label="Limitations" style={sectionStyle}>
          <p style={labelStyle}>Limitations</p>
          <ul style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {report.limitations.map((item, i) => (
              <li key={i} style={{
                fontFamily: "var(--font-franklin)",
                fontSize: "0.9rem",
                lineHeight: "1.7",
                color: "var(--gray)",
                paddingLeft: "1.25rem",
                borderLeft: "2px solid var(--border)",
              }}>
                {item}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* archive tags */}
      {report.archive_tags?.length > 0 && (
        <section aria-label="Archive tags" style={{ ...sectionStyle, borderBottom: "none" }}>
          <p style={labelStyle}>Archive Tags</p>
          <TagList items={report.archive_tags} />
        </section>
      )}

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

      {report.content_hash && (
        <p style={{
          fontFamily: "monospace",
          fontSize: "0.65rem",
          color: "var(--gray)",
          padding: "0 2rem 1.5rem",
          textAlign: "center",
        }}>
          Archive checksum: {report.content_hash.slice(0, 12)}
        </p>
      )}

    </main>
  );
}
