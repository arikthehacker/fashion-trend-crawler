// app/search/page.tsx
// facet-filterable index of every signal across all dated reports. Client-side
// array filtering over a pre-built static index — no backend, no full-text
// search library. See docs/agent-logs/search-discoverability-design.md and
// docs/agent-logs/facet-filter-impl.md for scope notes (full-text search over
// report prose via Pagefind is deliberately deferred to a later run).

import { getSearchIndex } from "../../lib/reports";
import SearchClient from "./SearchClient";
import { pageMetadata } from "../../lib/site";

export const metadata = pageMetadata("/search", "Search", "Filter signals across dated ARI3LLA INDEX reports by source sector, confidence and volatility.");


export default function Search() {
  const index = getSearchIndex();

  return (
    <main id="main-content" style={{
      flex: 1,
      background: "var(--white)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
    }}>

      {/* masthead */}
      <header className="page-masthead">
        <h1 className="page-title">
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
          Search the full text of every page, or filter signals by source sector,
          confidence and volatility.
        </p>
        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.75rem",
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
            No signals on file.
          </p>
        ) : (
          <SearchClient index={index} />
        )}
      </section>


    </main>
  );
}
