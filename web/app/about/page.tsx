// page.tsx
// about page for ARI3LLA INDEX — weekly style signal report

import Link from "next/link";

export default function About() {
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
      <header
        style={{
          width: "100%",
          borderBottom: "3px solid var(--black)",
          padding: "3rem 2rem 2rem",
          textAlign: "center",
        }}
      >
        <p
          style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.7rem",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            color: "var(--gray)",
            marginBottom: "0.75rem",
          }}
        >
          ARI3LLA INDEX
        </p>
        <h1
          style={{
            fontFamily: "var(--font-instrument)",
            fontSize: "clamp(2.5rem, 8vw, 5rem)",
            fontWeight: "400",
            lineHeight: "0.95",
            letterSpacing: "-0.02em",
            textTransform: "uppercase",
            color: "var(--black)",
          }}
        >
          About
        </h1>
        <nav
          aria-label="Site sections"
          style={{ display: "flex", justifyContent: "center", gap: "1.5rem", marginTop: "1.5rem" }}
        >
          {[
            { href: "/", label: "Report" },
            { href: "/methodology", label: "Methodology" },
            { href: "/taxonomy", label: "Taxonomy" },
            { href: "/sources", label: "Sources" },
            { href: "/timeline", label: "Timeline" },
            { href: "/archive", label: "Archive" },
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

      <section
        style={{
          width: "100%",
          maxWidth: "700px",
          padding: "4rem 2rem",
          textAlign: "center",
        }}
      >
        <p
          style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "1.05rem",
            lineHeight: "1.85",
            color: "var(--black)",
            marginBottom: "2.5rem",
          }}
        >
          ARI3LLA INDEX is a weekly style signal report. It collects public style discourse from
          across the web, classifies signals by source sector and volatility, and preserves them
          as dated reports.
        </p>

        <p
          style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "1.05rem",
            lineHeight: "1.85",
            color: "var(--black)",
            marginBottom: "2.5rem",
          }}
        >
          It does not predict what people should wear or what brands should sell. It tracks what
          style culture is naming, repeating, reviving, and absorbing, with attention to source
          incentives, platform noise, visual coherence, and historical continuity.
        </p>

        <div style={{ borderTop: "1px solid var(--border)", margin: "3rem 0", paddingTop: "2.5rem" }}>
          <p
            style={{
              fontFamily: "var(--font-franklin)",
              fontSize: "0.7rem",
              letterSpacing: "0.15em",
              textTransform: "uppercase",
              color: "var(--gray)",
              marginBottom: "1.25rem",
            }}
          >
            This Index Is Not
          </p>
          <p
            style={{
              fontFamily: "var(--font-franklin)",
              fontSize: "0.95rem",
              lineHeight: "1.8",
              color: "var(--gray)",
            }}
          >
            Trend forecasting. Fashion blogging. Shopping recommendation. Brand analytics.
            A TikTok trend recap. AI-generated taste. Influencer commentary.
          </p>
        </div>

        <div style={{ borderTop: "1px solid var(--border)", paddingTop: "2.5rem" }}>
          <p
            style={{
              fontFamily: "var(--font-franklin)",
              fontSize: "0.7rem",
              letterSpacing: "0.15em",
              textTransform: "uppercase",
              color: "var(--gray)",
              marginBottom: "1.25rem",
            }}
          >
            This Index Is
          </p>
          <p
            style={{
              fontFamily: "var(--font-franklin)",
              fontSize: "0.95rem",
              lineHeight: "1.8",
              color: "var(--gray)",
              marginBottom: "2.5rem",
            }}
          >
            Source-linked reporting. Style signal indexing. A public archive. Cultural
            documentation. Objective style discourse tracking. Human-in-the-loop research.
          </p>
        </div>

        <div style={{ borderTop: "1px solid var(--border)", margin: "3rem 0", paddingTop: "2.5rem", textAlign: "left" }}>
          <p
            style={{
              fontFamily: "var(--font-franklin)",
              fontSize: "0.7rem",
              letterSpacing: "0.15em",
              textTransform: "uppercase",
              color: "var(--gray)",
              marginBottom: "1.25rem",
            }}
          >
            Independence, Corrections, AI Use
          </p>
          <p
            style={{
              fontFamily: "var(--font-franklin)",
              fontSize: "0.95rem",
              lineHeight: "1.8",
              color: "var(--gray)",
              marginBottom: "1rem",
            }}
          >
            ARI3LLA INDEX is not sponsored by or affiliated with any brand, publication, retailer,
            or platform named in its reports. Editorial sources are cited as a source sector with
            its own commercial incentives, not treated as neutral authority.
          </p>
          <p
            style={{
              fontFamily: "var(--font-franklin)",
              fontSize: "0.95rem",
              lineHeight: "1.8",
              color: "var(--gray)",
              marginBottom: "1rem",
            }}
          >
            AI assists with crawling, extraction, and summarization. A human reviews that output,
            makes the interpretive classification calls, and records them in a human-editor note
            attached to each report.
          </p>
          <p
            style={{
              fontFamily: "var(--font-franklin)",
              fontSize: "0.95rem",
              lineHeight: "1.8",
              color: "var(--gray)",
            }}
          >
            Errors in a published report are not silently edited. A dated correction is appended
            to the affected report, and the original entry is kept intact. Full detail is on the{" "}
            <Link href="/methodology" style={{ color: "var(--black)", textDecoration: "underline" }}>
              Methodology
            </Link>{" "}
            page.
          </p>
        </div>

        <p
          style={{
            fontFamily: "var(--font-instrument)",
            fontSize: "1.6rem",
            fontWeight: "400",
            lineHeight: "1.4",
            color: "var(--black)",
            marginTop: "1rem",
          }}
        >
          ARI3LLA INDEX does not issue guidance on how readers should dress or live.
        </p>
        <p
          style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.95rem",
            lineHeight: "1.8",
            color: "var(--gray)",
            marginTop: "1.5rem",
          }}
        >
          It documents the sources, incentives, and language that shape style discourse.
        </p>
      </section>

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
            lineHeight: "1.7",
            color: "var(--gray)",
            maxWidth: "560px",
            margin: "0 auto",
          }}
        >
          ARI3LLA INDEX is an independent style signal archive. Reports are generated from public
          source material and structured for historical reference. No purchasing recommendation is
          implied.
        </p>
      </footer>
    </main>
  );
}
