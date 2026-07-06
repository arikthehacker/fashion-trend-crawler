// app/search/page.tsx
// facet-filterable index of every signal across all dated reports. Client-side
// array filtering over a pre-built static index — no backend, no full-text
// search library. See docs/agent-logs/search-discoverability-design.md and
// docs/agent-logs/facet-filter-impl.md for scope notes (full-text search over
// report prose via Pagefind is deliberately deferred to a later run).

import Link from "next/link";
import { getSearchIndex } from "../../lib/reports";
import SearchClient from "./SearchClient";

export const metadata = {
  title: "Search — ARI3LLA INDEX",
  description: "Filter signals across dated ARI3LLA INDEX reports by source sector, confidence, and volatility.",
};

export default function Search() {
  const index = getSearchIndex();

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
        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.7rem",
          letterSpacing: "0.15em",
          textTransform: "uppercase",
          color: "var(--red)",
          marginBottom: "1rem",
        }}>
          Ari3lla Index
        </p>
        <h1 style={{
          fontFamily: "var(--font-instrument)",
          fontSize: "clamp(2.5rem, 8vw, 6rem)",
          fontWeight: "400",
          lineHeight: "0.95",
          letterSpacing: "-0.02em",
          textTransform: "uppercase",
          color: "var(--black)",
        }}>
          Search
        </h1>
        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.95rem",
          lineHeight: "1.7",
          color: "var(--gray)",
          maxWidth: "560px",
          margin: "1.5rem auto 0",
        }}>
          Filter signals across all dated reports by source sector, confidence,
          and volatility. Filtering is exact-match against the controlled
          vocabulary used for classification — no free-text or fuzzy search.
        </p>
        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.7rem",
          letterSpacing: "0.15em",
          textTransform: "uppercase",
          color: "var(--gray)",
          marginTop: "2rem",
        }}>
          {index.length} signal{index.length === 1 ? "" : "s"} on file
        </p>
      </header>

      {/* filters + results */}
      <section
        aria-label="Signal search"
        style={{
          width: "100%",
          maxWidth: "800px",
          padding: "3rem 2rem 5rem",
        }}
      >
        {index.length === 0 ? (
          <p style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "0.95rem",
            color: "var(--gray)",
            textAlign: "center",
            padding: "3rem 0",
          }}>
            No signals on file yet.
          </p>
        ) : (
          <SearchClient index={index} />
        )}
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
        <Link href="/archive" style={{ fontFamily: "var(--font-franklin)", fontSize: "0.75rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "var(--black)", textDecoration: "underline", textUnderlineOffset: "3px" }}>
          Full archive
        </Link>
        <Link href="/timeline" style={{ fontFamily: "var(--font-franklin)", fontSize: "0.75rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "var(--black)", textDecoration: "underline", textUnderlineOffset: "3px" }}>
          Timeline
        </Link>
        <Link href="/" style={{ fontFamily: "var(--font-franklin)", fontSize: "0.75rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "var(--black)", textDecoration: "underline", textUnderlineOffset: "3px" }}>
          Current report
        </Link>
      </footer>

    </main>
  );
}
