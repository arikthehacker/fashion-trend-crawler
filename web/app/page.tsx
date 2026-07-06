// page.tsx
// last edited: 08/10/2026
// homepage for ARI3LLA INDEX — weekly style signal report.
// Rewritten to pull from the archived-report data layer (reports.ts) instead of
// the retired live-crawl view (trends.ts), which rendered a stale, un-versioned
// crawl snapshot inconsistent with every other page. See
// docs/agent-logs/trends-ts-fate-proposal.md and docs/agent-logs/homepage-rewrite.md.

import Link from "next/link";
import { getLatestReport, getThisWeeksIndex } from "../lib/reports";

export default function Home() {
  const latest = getLatestReport();
  const index = getThisWeeksIndex();

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
        <h1 style={{
          fontFamily: "var(--font-instrument)",
          fontSize: "clamp(3rem, 12vw, 10rem)",
          fontWeight: "400",
          lineHeight: "0.9",
          letterSpacing: "-0.03em",
          textTransform: "uppercase",
          color: "var(--black)",
        }}>
          ARI3LLA<br />Index
        </h1>

        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.85rem",
          letterSpacing: "0.15em",
          textTransform: "uppercase",
          color: "var(--black)",
          marginTop: "1.5rem",
        }}>
          Weekly Style Signal Report
        </p>

        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "1rem",
          lineHeight: "1.7",
          color: "var(--gray)",
          maxWidth: "560px",
          margin: "1.5rem auto 0",
        }}>
          A source-linked index tracking recurring style language, silhouettes, materials, aesthetics, and cultural signals across the web.
        </p>

        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.7rem",
          color: "var(--gray)",
          marginTop: "2.5rem",
          letterSpacing: "0.15em",
          textTransform: "uppercase",
        }}>
          {latest
            ? <>Latest report issued {latest.report_date} &nbsp;·&nbsp; {latest.items_collected} items collected across {latest.sources_scanned} sources</>
            : "No reports archived yet."}
        </p>

        {/* nav */}
        <nav
          aria-label="Site sections"
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "1.5rem",
            marginTop: "1.25rem",
          }}
        >
          {[
            { href: "/methodology", label: "Methodology" },
            { href: "/taxonomy", label: "Taxonomy" },
            { href: "/sources", label: "Sources" },
            { href: "/timeline", label: "Timeline" },
            { href: "/archive", label: "Archive" },
            { href: "/about", label: "About" },
            { href: "/case-study", label: "Case Study" },
          ].map((item) => (
            <Link
              key={item.href}
              href={item.href}
              style={{
                fontFamily: "var(--font-franklin)",
                fontSize: "0.7rem",
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                color: "var(--black)",
                textDecoration: "underline",
                textUnderlineOffset: "3px",
              }}
            >
              {item.label}
            </Link>
          ))}
        </nav>

      </header>

      {/* this week's index — condensed metrics module, doc section 27/28 */}
      {index && (
        <section
          aria-label="This week's index"
          style={{
            width: "100%",
            maxWidth: "800px",
            padding: "2.5rem 2rem",
            borderBottom: "1px solid var(--border)",
          }}
        >
          <h2 style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.7rem",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            color: "var(--black)",
            marginBottom: "1.25rem",
            textAlign: "center",
          }}>
            This Week&rsquo;s Index — {index.reportDate}
          </h2>

          <dl style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "1.25rem 2rem",
            margin: 0,
          }}>
            {[
              { label: "Sources scanned", value: String(index.sourcesScanned) },
              { label: "Items collected", value: String(index.itemsCollected) },
              { label: "Top signal", value: index.topSignal ?? "None logged this window" },
              {
                label: "Rising term (new since last report)",
                value: index.risingTerm ?? "No new term this window",
              },
              {
                label: "Recurring material",
                value: index.recurringMaterial ?? "No material recurring across recent reports",
              },
              {
                label: "Dominant mood",
                value: index.dominantMood
                  ? index.dominantMoodSourceDate
                    ? `${index.dominantMood} (carried from ${index.dominantMoodSourceDate}; none logged this window)`
                    : index.dominantMood
                  : "None logged this window",
              },
              {
                label: "Highest-volatility sector",
                value: index.highestVolatilitySector ?? "No sector showing elevated volatility this window",
              },
              { label: "Overall confidence", value: index.overallConfidence ?? "Not enough signals to score" },
            ].map((row) => (
              <div key={row.label}>
                <dt style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.65rem",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  color: "var(--gray)",
                  marginBottom: "0.35rem",
                }}>
                  {row.label}
                </dt>
                <dd style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.9rem",
                  lineHeight: "1.5",
                  color: "var(--black)",
                  margin: 0,
                }}>
                  {row.value}
                </dd>
              </div>
            ))}
          </dl>
        </section>
      )}

      {/* latest report teaser */}
      {latest && (
        <section
          aria-label="Latest report"
          style={{
            width: "100%",
            maxWidth: "800px",
            padding: "5rem 2rem",
            textAlign: "center",
            borderBottom: "1px solid var(--border)",
          }}
        >
          <h2 style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.7rem",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            color: "var(--red)",
            marginBottom: "1rem",
          }}>
            Latest Report — {latest.report_date}
          </h2>

          <p style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "1.05rem",
            lineHeight: "1.8",
            color: "var(--gray)",
            maxWidth: "650px",
            margin: "0 auto 4rem",
          }}>
            {latest.executive_summary}
          </p>

          {(latest as unknown as { collection_status?: string }).collection_status === "thin" && (
            <p style={{
              fontFamily: "var(--font-franklin)",
              fontSize: "0.75rem",
              lineHeight: "1.7",
              color: "var(--gray)",
              maxWidth: "650px",
              margin: "-2.5rem auto 4rem",
              borderTop: "1px solid var(--border)",
              paddingTop: "1.5rem",
            }}>
              This window is classified thin. Low-volatility periods are recorded as a
              verified data point rather than filled to a target count — see{" "}
              <Link
                href="/methodology"
                style={{ color: "var(--gray)", textDecoration: "underline", textUnderlineOffset: "3px" }}
              >
                methodology
              </Link>.
            </p>
          )}

          {/* top signal cards */}
          <div style={{
            display: "flex",
            flexDirection: "column",
            gap: "1.5rem",
            textAlign: "left",
          }}>
            {latest.top_signals.slice(0, 5).map((s, i) => (
              <div
                key={i}
                role="article"
                style={{
                  padding: "1.5rem",
                  border: "1px solid var(--border)",
                  display: "grid",
                  gridTemplateColumns: "1fr 2fr",
                  gap: "1.5rem",
                  alignItems: "start",
                }}
              >
                <h3 style={{
                  fontFamily: "var(--font-instrument)",
                  fontSize: "1.2rem",
                  fontWeight: "400",
                  lineHeight: "1.3",
                  margin: 0,
                }}>
                  {s.name}
                </h3>
                <p style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.9rem",
                  lineHeight: "1.6",
                  color: "var(--gray)",
                }}>
                  {s.evidence}
                </p>
              </div>
            ))}
          </div>

          <p style={{ marginTop: "3rem" }}>
            <Link
              href={`/reports/${latest.report_date}`}
              style={{
                fontFamily: "var(--font-franklin)",
                fontSize: "0.7rem",
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                color: "var(--black)",
                textDecoration: "underline",
                textUnderlineOffset: "3px",
              }}
            >
              Read the full report
            </Link>
          </p>
        </section>
      )}

      {/* footer */}
      <footer style={{
        width: "100%",
        borderTop: "1px solid var(--border)",
        padding: "2rem",
        textAlign: "center",
      }}>
        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.85rem",
          lineHeight: "1.7",
          color: "var(--gray)",
          maxWidth: "560px",
          margin: "0 auto 0.75rem",
        }}>
          ARI3LLA INDEX is an independent style signal archive. Reports are generated from public source material and structured for historical reference. No purchasing recommendation is implied.
        </p>
        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.7rem",
          letterSpacing: "0.15em",
          textTransform: "uppercase",
          color: "var(--gray)",
        }}>
          Issued weekly
        </p>
      </footer>

    </main>
  );
}