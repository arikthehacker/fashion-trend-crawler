"use client";
// app/search/SearchClient.tsx
// client-side facet filtering over the pre-built search index. No backend,
// no full-text search library — plain array filtering in the browser, per
// docs/agent-logs/search-discoverability-design.md's "simpler half" scope.
// Full-text search over report prose (Pagefind) is deliberately deferred.

import { useMemo, useState } from "react";
import Link from "next/link";
import type { SearchableSignal } from "../../lib/reports";

const labelStyle: React.CSSProperties = {
  fontFamily: "var(--font-franklin)",
  fontSize: "0.7rem",
  letterSpacing: "0.1em",
  textTransform: "uppercase",
  color: "var(--gray)",
  display: "block",
  marginBottom: "0.5rem",
};

const selectStyle: React.CSSProperties = {
  fontFamily: "var(--font-franklin)",
  fontSize: "0.85rem",
  color: "var(--black)",
  background: "var(--white)",
  border: "1px solid var(--border)",
  padding: "0.5rem 0.75rem",
  width: "100%",
};

function uniqueSorted(values: string[]): string[] {
  return Array.from(new Set(values.filter(Boolean))).sort();
}

export default function SearchClient({ index }: { index: SearchableSignal[] }) {
  const sectorOptions = useMemo(
    () => uniqueSorted(index.flatMap((s) => s.source_sectors ?? [])),
    [index]
  );
  const confidenceOptions = useMemo(
    () => uniqueSorted(index.map((s) => s.confidence)),
    [index]
  );
  const volatilityOptions = useMemo(
    () => uniqueSorted(index.map((s) => s.volatility)),
    [index]
  );

  const [sector, setSector] = useState("");
  const [confidence, setConfidence] = useState("");
  const [volatility, setVolatility] = useState("");

  const filtered = useMemo(() => {
    return index.filter((s) => {
      if (sector && !(s.source_sectors ?? []).includes(sector)) return false;
      if (confidence && s.confidence !== confidence) return false;
      if (volatility && s.volatility !== volatility) return false;
      return true;
    });
  }, [index, sector, confidence, volatility]);

  return (
    <>
      {/* facet controls */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "1.5rem",
          marginBottom: "3rem",
          paddingBottom: "2rem",
          borderBottom: "1px solid var(--border)",
        }}
      >
        <div>
          <label style={labelStyle} htmlFor="filter-sector">Source sector</label>
          <select
            id="filter-sector"
            style={selectStyle}
            value={sector}
            onChange={(e) => setSector(e.target.value)}
          >
            <option value="">All sectors</option>
            {sectorOptions.map((opt) => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        </div>
        <div>
          <label style={labelStyle} htmlFor="filter-confidence">Confidence</label>
          <select
            id="filter-confidence"
            style={selectStyle}
            value={confidence}
            onChange={(e) => setConfidence(e.target.value)}
          >
            <option value="">All confidence levels</option>
            {confidenceOptions.map((opt) => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        </div>
        <div>
          <label style={labelStyle} htmlFor="filter-volatility">Volatility</label>
          <select
            id="filter-volatility"
            style={selectStyle}
            value={volatility}
            onChange={(e) => setVolatility(e.target.value)}
          >
            <option value="">All volatility levels</option>
            {volatilityOptions.map((opt) => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        </div>
      </div>

      <p style={{
        fontFamily: "var(--font-franklin)",
        fontSize: "0.7rem",
        letterSpacing: "0.1em",
        textTransform: "uppercase",
        color: "var(--gray)",
        marginBottom: "1.5rem",
      }}>
        {filtered.length} signal{filtered.length === 1 ? "" : "s"} matching current filters
      </p>

      {/* results */}
      {filtered.length === 0 ? (
        <p style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.95rem",
          color: "var(--gray)",
          textAlign: "center",
          padding: "3rem 0",
        }}>
          No signals on file match this combination of filters.
        </p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column" }}>
          {filtered.map((s, i) => (
            <div
              key={`${s.report_date}-${s.signal_id ?? s.name}-${i}`}
              style={{
                display: "grid",
                gridTemplateColumns: "120px 1fr auto auto",
                gap: "1.5rem",
                alignItems: "start",
                padding: "1.1rem 0",
                borderBottom: "1px solid var(--border)",
              }}
            >
              <p style={{
                fontFamily: "var(--font-franklin)",
                fontSize: "0.75rem",
                letterSpacing: "0.05em",
                color: "var(--gray)",
                paddingTop: "0.15rem",
              }}>
                {s.report_date}
              </p>
              {s.signal_id ? (
                <Link
                  href={`/signals/${s.signal_id}`}
                  style={{
                    fontFamily: "var(--font-franklin)",
                    fontSize: "0.95rem",
                    lineHeight: "1.5",
                    color: "var(--black)",
                    textDecoration: "underline",
                    textUnderlineOffset: "3px",
                  }}
                >
                  {s.name}
                </Link>
              ) : (
                <p style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.95rem",
                  lineHeight: "1.5",
                  color: "var(--black)",
                }}>
                  {s.name}
                </p>
              )}
              <p style={{
                fontFamily: "var(--font-franklin)",
                fontSize: "0.7rem",
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                color: "var(--gray)",
                whiteSpace: "nowrap",
                paddingTop: "0.15rem",
              }}>
                {s.confidence} confidence
              </p>
              <p style={{
                fontFamily: "var(--font-franklin)",
                fontSize: "0.7rem",
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                color: "var(--gray)",
                whiteSpace: "nowrap",
                paddingTop: "0.15rem",
              }}>
                {s.volatility} volatility
              </p>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
