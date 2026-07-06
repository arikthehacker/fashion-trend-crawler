// page.tsx
// last edited: 07/06/2026
// case study — ARI3LLA INDEX: Building a Weekly Style Signal Report

import Link from "next/link";

const sections: { title: string; body: string[] }[] = [
  {
    title: "Problem",
    body: [
      "Style discourse moves quickly across platforms, editorial media, retail copy, and brand campaigns. Signals are often flattened into trends without source context, historical memory, or incentive analysis.",
    ],
  },
  {
    title: "Goal",
    body: [
      "Build a recurring report that tracks what style culture is saying without turning it into shopping advice or brand forecasting.",
    ],
  },
  {
    title: "Scope",
    body: [
      "Covers the crawler, MCP workflow, report structure, style taxonomy, frontend interface, and editorial/product direction.",
    ],
  },
  {
    title: "Technical System",
    body: [
      "A crawler collects public source material. MCP tools expose extracted data. Language models summarize and structure recurring signals. Reports are saved as dated JSON files and rendered in a Next.js frontend.",
    ],
  },
  {
    title: "Design System",
    body: [
      "The interface uses an editorial/reporting tone, restrained typography, clear hierarchy, source transparency, and index-like structure.",
    ],
  },
  {
    title: "Methodology",
    body: [
      "Signals are evaluated by recurrence, source diversity, source type, incentive context, visual coherence, volatility, and historical continuity.",
    ],
  },
  {
    title: "Ethical AI Stance",
    body: [
      "AI is used for extraction and organization, not taste authority. Human interpretation and source transparency remain central.",
    ],
  },
  {
    title: "Future Work",
    body: [
      "Archive, signal timelines, source-sector comparison, volatility scoring, Pinterest/manual visual signal tracking, a TikTok/compliant social signal layer, and a historical style glossary.",
    ],
  },
];

export default function CaseStudy() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background: "var(--white)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      {/* masthead */}
      <header
        style={{
          width: "100%",
          borderBottom: "3px solid var(--black)",
          padding: "4rem 2rem 3rem",
          textAlign: "center",
        }}
      >
        <p
          style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.7rem",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            color: "var(--red)",
            marginBottom: "1.5rem",
          }}
        >
          Case Study
        </p>
        <h1
          style={{
            fontFamily: "var(--font-instrument)",
            fontSize: "clamp(2.5rem, 9vw, 6.5rem)",
            fontWeight: "400",
            lineHeight: "0.95",
            letterSpacing: "-0.03em",
            textTransform: "uppercase",
            color: "var(--black)",
          }}
        >
          Building a Weekly<br />Style Signal Report
        </h1>

        <p
          style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "1rem",
            lineHeight: "1.7",
            color: "var(--gray)",
            maxWidth: "600px",
            margin: "2rem auto 0",
          }}
        >
          A source-linked archive that tracks style language, aesthetics,
          materials, silhouettes, and cultural signals across the web.
        </p>

        <p
          style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.7rem",
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            color: "var(--gray)",
            marginTop: "2rem",
          }}
        >
          <Link
            href="/"
            style={{
              color: "var(--black)",
              textDecoration: "underline",
              textUnderlineOffset: "3px",
            }}
          >
            ARI3LLA INDEX
          </Link>
          {" — weekly style signal report"}
        </p>
      </header>

      {/* case study sections */}
      <section
        aria-label="Case study"
        style={{
          width: "100%",
          maxWidth: "800px",
          padding: "5rem 2rem",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: "0" }}>
          {sections.map((s, i) => (
            <div
              key={s.title}
              style={{
                display: "grid",
                gridTemplateColumns: "160px 1fr",
                gap: "2rem",
                padding: "2.5rem 0",
                borderBottom:
                  i === sections.length - 1
                    ? "none"
                    : "1px solid var(--border)",
                alignItems: "start",
              }}
            >
              <p
                style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.75rem",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  color: "var(--black)",
                  paddingTop: "0.2rem",
                }}
              >
                {String(i + 1).padStart(2, "0")}&nbsp;&nbsp;{s.title}
              </p>
              <div>
                {s.body.map((p, j) => (
                  <p
                    key={j}
                    style={{
                      fontFamily: "var(--font-franklin)",
                      fontSize: "1rem",
                      lineHeight: "1.8",
                      color: "var(--gray)",
                      marginBottom: j === s.body.length - 1 ? 0 : "1rem",
                    }}
                  >
                    {p}
                  </p>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* footer */}
      <footer
        style={{
          width: "100%",
          borderTop: "1px solid var(--border)",
          padding: "2rem",
          textAlign: "center",
        }}
      >
        <p
          style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.85rem",
            lineHeight: "1.6",
            color: "var(--gray)",
            maxWidth: "500px",
            margin: "0 auto",
          }}
        >
          ARI3LLA INDEX is an independent style signal archive. Reports are
          generated from public source material and structured for
          historical reference. No purchasing recommendation is implied.
        </p>
      </footer>
    </main>
  );
}
