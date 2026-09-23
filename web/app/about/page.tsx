// page.tsx
// about page for ARI3LLA INDEX — weekly style signal report

import Link from "next/link";
import { pageMetadata } from "../../lib/site";

export const metadata = pageMetadata("/about", "About", "What ARI3LLA INDEX is and is not: an independent, source-linked archive of style language, its editorial independence, AI use and corrections policy.");


export default function About() {
  return (
    <main id="main-content"
      style={{
        flex: 1,
        background: "var(--white)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <header className="page-masthead">
        <h1 className="page-title">
          About
        </h1>
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
              fontSize: "0.75rem",
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
              fontSize: "0.75rem",
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
            documentation. Style discourse tracked by source and incentive. Human-edited research.
          </p>
        </div>

        <div style={{ borderTop: "1px solid var(--border)", margin: "3rem 0", paddingTop: "2.5rem", textAlign: "left" }}>
          <p
            style={{
              fontFamily: "var(--font-franklin)",
              fontSize: "0.75rem",
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
            ARI3LLA INDEX is an independently operated research and reporting project, not a
            staffed newsroom or a commercial publication. It is built and maintained by a single
            researcher-developer, with source code published on the project&apos;s public
            repository; there is no separate editorial board, ownership structure, or funding
            source to disclose beyond that.
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
            AI assists with collection, extraction, and first drafts. It does not decide what
            matters. Every claim in a report links to a specific, dated source, and a report is
            published only after human review. The human-editor note on each signal is written by
            the editor, never by software. See{" "}
            <Link href="/methodology" style={{ color: "var(--gray)" }}>methodology</Link> for the
            full process.
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
            page. A suspected error can be reported by{" "}
            <a
              href="https://github.com/arikthehacker/fashion-trend-crawler/issues"
              rel="noopener noreferrer"
              style={{ color: "var(--black)", textDecoration: "underline" }}
            >
              opening an issue on the project&apos;s public repository
            </a>
            . This is not a staffed inbox, but it is a real channel, not a placeholder.
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

    </main>
  );
}
