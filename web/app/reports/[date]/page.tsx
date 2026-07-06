// app/reports/[date]/page.tsx
// renders a single dated ARI3LLA INDEX report

import Link from "next/link";
import { notFound } from "next/navigation";
import { getAllReportDates, getReportByDate } from "../../../lib/reports";
import { SITE_URL, SITE_NAME } from "../../../lib/site";

export function generateStaticParams() {
  return getAllReportDates().map((date) => ({ date }));
}

export async function generateMetadata({ params }: { params: Promise<{ date: string }> }) {
  const { date } = await params;
  const title = `${date} — ARI3LLA INDEX`;
  const description = `Weekly style signal report issued ${date}.`;
  return {
    title,
    description,
    alternates: { canonical: `${SITE_URL}/reports/${date}` },
    openGraph: {
      siteName: SITE_NAME,
      title,
      description,
      url: `${SITE_URL}/reports/${date}`,
      type: "article",
    },
    twitter: {
      card: "summary",
      title,
      description,
    },
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

  const headlineSource = report.executive_summary?.split(/(?<=[.!?])\s+/)[0];
  const headline = headlineSource
    ? headlineSource.slice(0, 110)
    : `Weekly style signal report — ${report.report_date}`;

  // IPTC/schema.org distinguish datePublished (original issue) from dateModified
  // (last correction) — a corrected report should not claim it was never touched.
  // Sourced from the last revision_history entry when one exists, per doc's
  // correction-history model (src/report_schema.py corrected_at).
  const lastRevision = report.revision_history?.[report.revision_history.length - 1];
  const dateModified = lastRevision?.corrected_at || report.report_date;

  // this page is both a written report (NewsArticle) and the read surface of a
  // structured dataset (each report is a dated JSON record of classified signals) —
  // schema.org recommends Dataset markup on a dataset's canonical/landing page so it
  // surfaces in dataset-aware search tooling, not just Article-style news search.
  //
  // Raw JSON download route (run 45): scripts/copy-reports.mjs copies
  // data/reports/*.json into public/data/reports/ as a prebuild step, and the
  // static export (output: "export") serves the copy as-is at
  // /data/reports/<date>.json — a real, resolving URL, so `distribution`/
  // `contentUrl` below is no longer a placeholder.
  const reportUrl = `${SITE_URL}/reports/${report.report_date}`;
  const rawDataUrl = `${SITE_URL}/data/reports/${report.report_date}.json`;
  const jsonLd = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "NewsArticle",
        "@id": `${reportUrl}#article`,
        headline,
        datePublished: report.report_date,
        dateModified,
        url: reportUrl,
        mainEntityOfPage: reportUrl,
        description: report.executive_summary,
        author: {
          "@type": "Organization",
          name: SITE_NAME,
        },
        publisher: {
          "@type": "Organization",
          name: SITE_NAME,
        },
        keywords: report.archive_tags?.join(", "),
        about: { "@id": `${reportUrl}#dataset` },
      },
      {
        "@type": "Dataset",
        "@id": `${reportUrl}#dataset`,
        name: `ARI3LLA INDEX style signal report — ${report.report_date}`,
        description: report.executive_summary,
        url: reportUrl,
        creator: {
          "@type": "Organization",
          name: SITE_NAME,
        },
        datePublished: report.report_date,
        dateModified,
        temporalCoverage: report.report_date,
        variableMeasured: Object.keys(report.source_sector_breakdown || {}),
        isBasedOn: reportUrl,
        // schema.org/license expects a URL identifying a specific license version
        // (SPDX is the recommended canonical source) rather than bare text like
        // "CC BY 4.0" — added run 46 alongside the visible license line near the
        // download link below. Covers the report's own classification/metadata
        // output only; it does not relicense the underlying source articles,
        // which remain the property of their original publishers (see
        // methodology's existing note on storing metadata/links, not full text).
        license: "https://creativecommons.org/licenses/by/4.0/",
        distribution: [
          {
            "@type": "DataDownload",
            encodingFormat: "application/json",
            contentUrl: rawDataUrl,
          },
        ],
      },
    ],
  };

  return (
    <main id="main-content" style={{
      minHeight: "100vh",
      background: "var(--white)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
    }}>

      {/* structured data for search engines — Article/NewsArticle JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

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

        {/* compact "how this report was compiled" box — Pew Research Center /
            FiveThirtyEight convention: a short, visually distinct box near the top of a
            data-driven article stating source/collection facts and linking to the
            full-length methodology page, kept separate from that long-form page itself.
            See docs/agent-logs/journalism-standards-check-run45.md */}
        <div style={{
          maxWidth: "640px",
          margin: "2rem auto 0",
          padding: "1rem 1.5rem",
          border: "1px solid var(--border)",
          textAlign: "left",
        }}>
          <p style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.7rem",
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            color: "var(--black)",
            marginBottom: "0.6rem",
          }}>
            How This Report Was Compiled
          </p>
          <div style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "0.4rem 1.75rem",
            fontFamily: "var(--font-franklin)",
            fontSize: "0.75rem",
            letterSpacing: "0.03em",
            color: "var(--gray)",
            marginBottom: "0.75rem",
          }}>
            <span>Collection window: {report.collection_window?.start}–{report.collection_window?.end}</span>
            <span>Sources scanned: {report.sources_scanned}</span>
            <span>Items collected: {report.items_collected}</span>
          </div>
          {/* byline-level AI disclosure — per-report, not just the general /about policy page.
              Research convention (Trusting News byline template; AP/BBC studies on disclosure
              credibility) recommends surfacing AI involvement at the byline, immediately next to
              authorship, rather than only in a general site-wide policy a reader may never visit.
              See docs/agent-logs/journalism-standards-check-run41.md */}
          <p style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.7rem",
            letterSpacing: "0.03em",
            color: "var(--gray)",
            margin: 0,
          }}>
            AI-assisted collection, extraction, and drafting for this report;{" "}
            {report.reviewed_by
              ? `reviewed against editorial guidelines (process: ${report.reviewed_by})`
              : "reviewed against editorial guidelines"}
            . <Link href="/methodology" style={{ color: "var(--gray)", textDecoration: "underline" }}>
              Full methodology
            </Link>
          </p>
        </div>
      </header>

      {/* pinned correction notice — corrections policy convention (AP/NYT/Reuters):
          give a correction prominence roughly equal to the original content, surfaced
          near the top rather than left only in a footer-adjacent section a reader may
          never scroll to. See docs/agent-logs/journalism-standards-check-run40.md */}
      {lastRevision && (
        <div style={{
          width: "100%",
          maxWidth: "720px",
          padding: "0.85rem 1.5rem",
          margin: "1.5rem 2rem 0",
          border: "1px solid var(--red)",
          fontFamily: "var(--font-franklin)",
          fontSize: "0.85rem",
          lineHeight: "1.6",
          color: "var(--black)",
        }}>
          <strong style={{ color: "var(--red)" }}>Corrected {lastRevision.corrected_at}: </strong>
          {lastRevision.reason}{" "}
          <a href="#correction-history" style={{ color: "var(--red)", textDecoration: "underline" }}>
            Full correction history
          </a>
        </div>
      )}

      {/* executive summary */}
      <section aria-label="Executive summary" style={sectionStyle}>
        <h2 style={labelStyle}>Executive Summary</h2>
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
          <h2 style={labelStyle}>Source Sectors</h2>
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
          <h2 style={labelStyle}>Observed Signals</h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
            {report.top_signals.map((signal, i) => {
              // per-signal deep-link anchor (run 63) — a signal's own permanent home is
              // /signals/[slug], but a reader citing "this report's third finding" had no
              // way to link to that finding's position within THIS dated report, only to
              // the whole page. Anchor ids give that a real target; scroll-margin-top in
              // globals.css keeps the anchored signal clear of the sticky-free layout.
              // See docs/agent-logs/journalism-standards-check-run63.md
              const anchorId = `signal-${signal.signal_id || i}`;
              return (
              <div key={i} id={anchorId} style={{ borderTop: "1px solid var(--border)", paddingTop: "1.5rem" }}>
                <div style={{ display: "flex", alignItems: "baseline", gap: "0.6rem", flexWrap: "wrap" }}>
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
                  <h3 style={{
                    fontFamily: "var(--font-instrument)",
                    fontSize: "1.4rem",
                    marginBottom: "0.75rem",
                  }}>
                    {i + 1}. {signal.name}
                  </h3>
                )}
                <a
                  href={`#${anchorId}`}
                  aria-label={`Permalink to signal: ${signal.name}`}
                  style={{
                    fontFamily: "var(--font-franklin)",
                    fontSize: "0.85rem",
                    color: "var(--gray)",
                    textDecoration: "none",
                    marginBottom: "0.75rem",
                  }}
                >
                  #
                </a>
                </div>
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
                  <p style={{
                    fontFamily: "var(--font-franklin)",
                    fontSize: "0.8rem",
                    lineHeight: "1.6",
                    color: "var(--gray)",
                    marginTop: "0.5rem",
                    paddingTop: "0.5rem",
                    borderTop: "1px solid var(--border)",
                  }}>
                    Editor review: {signal.human_editor_note}
                  </p>
                )}
              </div>
              );
            })}
          </div>
        </section>
      )}

      {/* repeated keywords */}
      {report.repeated_keywords?.length > 0 && (
        <section aria-label="Repeated keywords" style={sectionStyle}>
          <h2 style={labelStyle}>Repeated Keywords</h2>
          <TagList items={report.repeated_keywords} />
        </section>
      )}

      {/* garments / silhouettes / materials / colors */}
      <section aria-label="Garments, silhouettes, materials, colors" style={sectionStyle}>
        <h2 style={labelStyle}>Garments, Silhouettes, Materials, Colors</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
          {[
            ["Garments", report.garments],
            ["Silhouettes", report.silhouettes],
            ["Materials", report.materials],
            ["Colors", report.colors],
          ].map(([title, items]) => (
            (items as string[])?.length > 0 && (
              <div key={title as string}>
                <h3 style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.7rem",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  color: "var(--black)",
                  marginBottom: "0.75rem",
                }}>
                  {title}
                </h3>
                <TagList items={items as string[]} />
              </div>
            )
          ))}
        </div>
      </section>

      {/* aesthetic / cultural references */}
      {(report.aesthetic_terms?.length > 0 || report.cultural_references?.length > 0) && (
        <section aria-label="Aesthetic and cultural references" style={sectionStyle}>
          <h2 style={labelStyle}>Aesthetic &amp; Cultural References</h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "1.75rem" }}>
            {report.aesthetic_terms?.length > 0 && (
              <div>
                <h3 style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.7rem",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  color: "var(--black)",
                  marginBottom: "0.75rem",
                }}>
                  Aesthetic Terms
                </h3>
                <TagList items={report.aesthetic_terms} />
              </div>
            )}
            {report.cultural_references?.length > 0 && (
              <div>
                <h3 style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.7rem",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  color: "var(--black)",
                  marginBottom: "0.75rem",
                }}>
                  Cultural References
                </h3>
                <TagList items={report.cultural_references} />
              </div>
            )}
          </div>
        </section>
      )}

      {/* thin collection window note */}
      {report.collection_status === "thin" && (
        <section aria-label="Collection status" style={sectionStyle}>
          <h2 style={labelStyle}>Collection Status: Thin</h2>
          <p style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.9rem",
            lineHeight: "1.7",
            color: "var(--gray)",
          }}>
            {report.thin_week_note ||
              "Fewer signals met the recurrence and source-diversity thresholds than in a typical reporting period. This window is recorded as a verified low-volatility data point rather than filled to a target count."}
          </p>
        </section>
      )}

      {/* volatility / incentive / confidence notes */}
      {(report.volatility_notes || report.incentive_notes || report.confidence_notes || report.reviewed_by) && (
        <section aria-label="Methodology notes" style={sectionStyle}>
          <h2 style={labelStyle}>Notes</h2>
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
            {report.reviewed_by && (
              <p style={{ fontFamily: "var(--font-franklin)", fontSize: "0.9rem", lineHeight: "1.7", color: "var(--gray)" }}>
                <strong style={{ color: "var(--black)" }}>Review: </strong>
                {report.review_status === "draft" ? "Draft, " : "Reviewed against editorial guidelines, "}
                process: {report.reviewed_by}
              </p>
            )}
          </div>
        </section>
      )}

      {/* limitations */}
      {report.limitations?.length > 0 && (
        <section aria-label="Limitations" style={sectionStyle}>
          <h2 style={labelStyle}>Limitations</h2>
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

      {/* correction history */}
      {(report.revision_history?.length ?? 0) > 0 && (
        <section id="correction-history" aria-label="Correction history" style={sectionStyle}>
          <h2 style={labelStyle}>Correction History</h2>
          <ul style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: "1rem" }}>
            {report.revision_history?.map((revision, i) => (
              <li key={i} style={{
                fontFamily: "var(--font-franklin)",
                fontSize: "0.9rem",
                lineHeight: "1.7",
                color: "var(--gray)",
                paddingLeft: "1.25rem",
                borderLeft: "2px solid var(--border)",
              }}>
                <strong style={{ color: "var(--black)" }}>Corrected {revision.corrected_at}: </strong>
                {revision.reason}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* archive tags */}
      {report.archive_tags?.length > 0 && (
        <section aria-label="Archive tags" style={{ ...sectionStyle, borderBottom: "none" }}>
          <h2 style={labelStyle}>Archive Tags</h2>
          <TagList items={report.archive_tags} />
        </section>
      )}

      {/* footer — in-page site navigation, not part of the archival report
          record; hidden when printing/saving as PDF for citation (see
          globals.css .no-print) */}
      <footer className="no-print" style={{
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
        <Link href="/search" style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.75rem",
          letterSpacing: "0.1em",
          textTransform: "uppercase",
          color: "var(--black)",
          textDecoration: "underline",
          textUnderlineOffset: "3px",
        }}>
          Search
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
        <Link href="/methodology" style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.75rem",
          letterSpacing: "0.1em",
          textTransform: "uppercase",
          color: "var(--black)",
          textDecoration: "underline",
          textUnderlineOffset: "3px",
        }}>
          Corrections &amp; AI use
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

      {/* raw data download — human-visible counterpart to the Dataset JSON-LD's
          distribution/contentUrl above; the file itself is a plain copy of
          data/reports/<date>.json served via public/data/reports/ (run 45) */}
      <p style={{
        fontFamily: "monospace",
        fontSize: "0.65rem",
        color: "var(--gray)",
        padding: "0 2rem 0.5rem",
        textAlign: "center",
      }}>
        <a href={`/data/reports/${report.report_date}.json`} download style={{ color: "var(--gray)", textDecoration: "underline" }}>
          Download raw data (JSON)
        </a>
        {" — classification and summary metadata licensed "}
        <a href="https://creativecommons.org/licenses/by/4.0/" style={{ color: "var(--gray)", textDecoration: "underline" }}>
          CC BY 4.0
        </a>
        {"; underlying source articles remain the property of their original publishers"}
      </p>

      {/* citation line */}
      <p style={{
        fontFamily: "monospace",
        fontSize: "0.65rem",
        color: "var(--gray)",
        padding: "0 2rem 2rem",
        textAlign: "center",
      }}>
        Cite as: ARI3LLA INDEX, {report.report_date}, /reports/{report.report_date}
        {report.content_hash ? ` (checksum ${report.content_hash.slice(0, 12)})` : ""}
      </p>

      {/* formatted citation string, for readers who want a copy-pasteable reference */}
      <p style={{
        fontFamily: "monospace",
        fontSize: "0.65rem",
        color: "var(--gray)",
        padding: "0 2rem 2rem",
        textAlign: "center",
      }}>
        {SITE_NAME}. ({report.report_date}). Weekly style signal report. Retrieved from {SITE_URL}/reports/{report.report_date}
      </p>

    </main>
  );
}
