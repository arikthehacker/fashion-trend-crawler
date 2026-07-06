// page.tsx
// last edited: 07/06/2026
// homepage for ARI3LLA INDEX — weekly style signal report

import Link from "next/link";
import { getTrends } from "../lib/trends";

export default function Home() {
  const { pages, summary, lastUpdated, totalHeadlines } = getTrends();

  const sources = pages.reduce((acc, page) => {
    try {
      const domain = new URL(page.url).hostname.replace("www.", "");
      if (!acc[domain]) acc[domain] = [];
      acc[domain].push(...page.titles);
    } catch {}
    return acc;
  }, {} as Record<string, string[]>);

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
          Report issued {lastUpdated} &nbsp;·&nbsp; {totalHeadlines} items collected across {pages.length} sources
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
            { href: "/about", label: "About" },
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

        {/* right now — in header */}
        {summary && (
          <div style={{ marginTop: "3rem" }}>
            <p style={{
              fontFamily: "var(--font-franklin)",
              fontSize: "0.7rem",
              letterSpacing: "0.15em",
              textTransform: "uppercase",
              color: "var(--red)",
              marginBottom: "1rem",
            }}>
              Observed Signals
            </p>
            <h2 style={{
              fontFamily: "var(--font-instrument)",
              fontSize: "clamp(1.8rem, 4vw, 3rem)",
              fontWeight: "400",
              lineHeight: "1.2",
              letterSpacing: "-0.01em",
              maxWidth: "700px",
              margin: "0 auto",
            }}>
              {summary.the_moment}
            </h2>
          </div>
        )}
      </header>

      {/* summary paragraph + trends */}
      {summary && (
        <section
          aria-label="Trend summary"
          style={{
            width: "100%",
            maxWidth: "800px",
            padding: "5rem 2rem",
            textAlign: "center",
            borderBottom: "1px solid var(--border)",
          }}
        >
          <p style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "1.05rem",
            lineHeight: "1.8",
            color: "var(--gray)",
            maxWidth: "650px",
            margin: "0 auto 4rem",
          }}>
            {summary.summary}
          </p>

          {/* trend cards */}
          <div style={{
            display: "flex",
            flexDirection: "column",
            gap: "1.5rem",
            textAlign: "left",
          }}>
            {summary.trends.map((t, i) => (
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
                <p style={{
                  fontFamily: "var(--font-instrument)",
                  fontSize: "1.2rem",
                  lineHeight: "1.3",
                }}>
                  {t.trend}
                </p>
                <p style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.9rem",
                  lineHeight: "1.6",
                  color: "var(--gray)",
                }}>
                  {t.signal}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* what each source is saying */}
      {summary && (
        <section
          aria-label="Source summaries"
          style={{
            width: "100%",
            maxWidth: "800px",
            padding: "4rem 2rem",
            borderBottom: "1px solid var(--border)",
          }}
        >
          <p style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.7rem",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            color: "var(--gray)",
            marginBottom: "2rem",
            textAlign: "center",
          }}>
            Source Notes
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "0" }}>
            {Object.entries(summary.sources_summary).map(([source, desc]) => (
              <div
                key={source}
                style={{
                  display: "grid",
                  gridTemplateColumns: "160px 1fr",
                  gap: "2rem",
                  padding: "1.5rem 0",
                  borderBottom: "1px solid var(--border)",
                  alignItems: "start",
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
                  {source}
                </p>
                <p style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.95rem",
                  lineHeight: "1.6",
                  color: "var(--gray)",
                }}>
                  {desc}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* raw headlines by source */}
      <section
        aria-label="Raw headlines"
        style={{
          width: "100%",
          maxWidth: "800px",
          padding: "4rem 2rem",
          borderBottom: "1px solid var(--border)",
        }}
      >
        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.7rem",
          letterSpacing: "0.15em",
          textTransform: "uppercase",
          color: "var(--gray)",
          marginBottom: "3rem",
          textAlign: "center",
        }}>
          Collected Items
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: "3rem" }}>
          {Object.entries(sources).map(([domain, titles]) => (
            <div key={domain}>
              <p style={{
                fontFamily: "var(--font-franklin)",
                fontSize: "0.7rem",
                letterSpacing: "0.15em",
                textTransform: "uppercase",
                color: "var(--black)",
                marginBottom: "1rem",
                paddingBottom: "0.75rem",
                borderBottom: "1px solid var(--border)",
              }}>
                {domain}
              </p>
              <ul style={{ listStyle: "none", padding: 0 }}>
                {titles.slice(0, 6).map((title, i) => (
                  <li
                    key={i}
                    style={{
                      fontFamily: "var(--font-franklin)",
                      fontSize: "0.95rem",
                      lineHeight: "1.5",
                      color: "var(--black)",
                      padding: "0.75rem 0",
                      borderBottom: "1px solid var(--border)",
                    }}
                  >
                    {title}
                  </li>
                ))}
              </ul>
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