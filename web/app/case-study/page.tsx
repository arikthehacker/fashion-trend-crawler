// page.tsx
// last edited: 09/22/2026
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
      "A public, dated record of style language: what is being named, where it first appears, and how it moves between runway, editorial, social, retail, and resale sources. Every claim links to the specific source it rests on. No shopping advice and no forecasting.",
    ],
  },
  {
    title: "What Exists",
    body: [
      "A Python crawler that respects robots.txt and enforces a hard per-request deadline. A report schema with controlled vocabularies for source sector, confidence, volatility, and origin, and a validator that runs in CI on every push. A source taxonomy mapping more than 125 outlets to sectors, including non-Anglophone publications. A static Next.js site with archive, timeline, per-signal history, search, RSS, sitemap, and structured data, linted for accessibility.",
    ],
  },
  {
    title: "Design System",
    body: [
      "Editorial tone, restrained typography, clear hierarchy, and index-like structure. Report pages carry structured data, a stable citation line, and heading markup built for accessibility rather than visual-only hierarchy.",
    ],
  },
  {
    title: "Evidence Standard",
    body: [
      "A claim is published only with a link to a specific, dated article or record. An outlet's homepage is not evidence. A report may not be dated after the day it is published. Signals are weighed by recurrence, source diversity, source incentive, visual coherence, and historical continuity, and confidence is stated plainly, including when it is low.",
    ],
  },
  {
    title: "Human and Machine",
    body: [
      "Software collects, extracts, and drafts. It does not decide what matters. Interpretation, naming, and the human-editor note on each signal belong to the editor. Social platforms are sampled through official reports and APIs or by hand, never by scraping, and runway images are linked, never rehosted.",
    ],
  },
  {
    title: "Current Limitations",
    body: [
      "The archive is empty while the collection pipeline is rebuilt. The crawler captures headlines but not publish dates or article text, so it cannot yet support dated first appearances. There is no item store yet, so evidence cannot be checked mechanically.",
    ],
  },
  {
    title: "Next",
    body: [
      "A store of dated, linked source items fed by outlet RSS feeds and archived snapshots; checks that fail any report with a future date or an unlinked claim; per-term pages showing first appearance and movement across sectors.",
    ],
  },
];

export default function CaseStudy() {
  return (
    <main id="main-content"
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

        <nav
          aria-label="Site sections"
          style={{ display: "flex", justifyContent: "center", gap: "1.5rem", marginTop: "1.5rem", flexWrap: "wrap" }}
        >
          {[
            { href: "/", label: "Report" },
            { href: "/methodology", label: "Methodology" },
            { href: "/taxonomy", label: "Taxonomy" },
            { href: "/sources", label: "Sources" },
            { href: "/glossary", label: "Glossary" },
            { href: "/timeline", label: "Timeline" },
            { href: "/archive", label: "Archive" },
            { href: "/search", label: "Search" },
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
                display: "inline-block",
                padding: "0.65rem 0",
              }}
            >
              {item.label}
            </Link>
          ))}
        </nav>
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
              <h2
                style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.75rem",
                  fontWeight: "400",
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  color: "var(--black)",
                  paddingTop: "0.2rem",
                  margin: 0,
                }}
              >
                {String(i + 1).padStart(2, "0")}&nbsp;&nbsp;{s.title}
              </h2>
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
          compiled from public, linked source material and structured for
          historical reference. No purchasing recommendation is implied.
        </p>
      </footer>
    </main>
  );
}
