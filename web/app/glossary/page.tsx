// page.tsx
// glossary page for ARI3LLA INDEX — weekly style signal report
// doc section 24: "style terms, aesthetic terms, recurring classifications"
//
// Terms are sourced from the archive's aesthetic_terms, cultural_references, and
// top_signals[].name fields (data/reports/*.json), read at build time and matched
// against a curated definition set below. Only terms that actually appear in the
// archive are rendered, so the glossary stays tied to what the Index has observed
// rather than an abstract style dictionary. Distinct from /taxonomy, which documents
// the classification system rather than the aesthetic terms themselves.

import Link from "next/link";
import { getAllReports } from "../../lib/reports";
import { pageMetadata } from "../../lib/site";

export const metadata = pageMetadata("/glossary", "Glossary", "Definitions of the style terms, source sectors, confidence and volatility labels used across ARI3LLA INDEX reports.");


interface ReportShape {
  aesthetic_terms?: string[];
  cultural_references?: string[];
  top_signals?: { name?: string }[];
}

// Definitions are added only for terms that appear in a published report, and
// each one must be supported by that report's evidence. None exists yet.
const DEFINITIONS: Record<string, string> = {};

function normalize(term: string): string {
  return term
    .replace(/\s*\(carryover\)\s*$/i, "")
    .replace(/,\s*(forecast stage|third and final recheck|still unconfirmed at [^)]*|dormancy check|continuing|social)\s*$/i, "")
    .replace(/^"funmaxxing".*$/i, "funmaxxing")
    .trim();
}

// A genuine glossary term is short vocabulary (e.g. "peplum", "quiet luxury"),
// not a narrative sentence tracking a signal's status. This filters out
// long/sentence-like candidates before they're ever checked against
// DEFINITIONS, so build-time warnings only surface real curatable terms.
// See docs/agent-logs/glossary-build-warning-run38.md for the ~130-hit
// warning list this was written to reduce.
function isPlausibleGlossaryTerm(term: string): boolean {
  if (term.length > 40) return false;
  if (term.split(/\s+/).length > 5) return false;
  // Sentence-like punctuation: parenthetical explanations, commas joining
  // clauses, dashes used as asides, or terminal punctuation.
  if (/[()]/.test(term)) return false;
  if (/[,;:]/.test(term)) return false;
  if (/--|—|–/.test(term)) return false;
  if (/[.!?]\s*$/.test(term)) return false;
  return true;
}

function loadGlossaryTerms(): { term: string; def: string }[] {
  const found = new Map<string, string>(); // lowercase key -> display term

  {
    const reports = getAllReports() as unknown as ReportShape[];
    for (const report of reports) {
      const candidates = [
        ...(report.aesthetic_terms ?? []),
        ...(report.cultural_references ?? []),
        ...(report.top_signals ?? []).map((s) => s.name ?? ""),
      ];

      for (const raw of candidates) {
        const cleaned = normalize(raw);
        if (!cleaned) continue;
        if (!isPlausibleGlossaryTerm(cleaned)) continue;
        const key = cleaned.toLowerCase();
        if (DEFINITIONS[key]) {
          if (!found.has(key)) {
            found.set(key, cleaned);
          }
        } else {
          // Non-blocking build-time warning: surfaces terms observed in the
          // archive that have no curated definition, so they don't silently
          // drop off /glossary. See docs/agent-logs/glossary-freshness-check-run37.md.
          console.warn(
            `[glossary] no DEFINITIONS entry for term "${cleaned}" (from ${(report as { report_date?: string }).report_date ?? "unknown report"}) — term will not be shown on /glossary`
          );
        }
      }
    }
  }

  return Array.from(found.entries())
    .map(([key, term]) => ({ term, def: DEFINITIONS[key] }))
    .sort((a, b) => a.term.localeCompare(b.term));
}

export default function Glossary() {
  const terms = loadGlossaryTerms();

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
          Glossary
        </h1>
      </header>

      <section style={{ width: "100%", maxWidth: "760px", padding: "4rem 2rem" }}>
        <p
          style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "1rem",
            lineHeight: "1.8",
            color: "var(--gray)",
            marginBottom: "3.5rem",
          }}
        >
          Definitions of style and aesthetic terms that have appeared in archived reports. A term
          is listed only after it appears in a report. Source sectors and the confidence and
          volatility labels are defined on the{" "}
          <Link href="/taxonomy" style={{ color: "var(--black)", textDecoration: "underline" }}>
            Taxonomy
          </Link>{" "}
          page.
        </p>

        {terms.length === 0 && (
          <p style={{ fontFamily: "var(--font-franklin)", fontSize: "1rem", lineHeight: "1.8", color: "var(--black)" }}>
            No term has a definition yet. A definition is added only when a published report uses the term and that report&apos;s evidence supports the definition.
          </p>
        )}

        <dl style={{ display: "flex", flexDirection: "column", margin: 0 }}>
          {terms.map((t) => (
            <div className="stack-sm"
              key={t.term}
              style={{
                display: "grid",
                gridTemplateColumns: "220px 1fr",
                gap: "1.5rem",
                padding: "1.1rem 0",
                borderBottom: "1px solid var(--border)",
                alignItems: "start",
              }}
            >
              <dt
                style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.85rem",
                  letterSpacing: "0.02em",
                  color: "var(--black)",
                  paddingTop: "0.15rem",
                  textTransform: "capitalize",
                }}
              >
                {t.term}
              </dt>
              <dd
                style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.95rem",
                  lineHeight: "1.6",
                  color: "var(--gray)",
                  margin: 0,
                }}
              >
                {t.def}
              </dd>
            </div>
          ))}
        </dl>
      </section>

    </main>
  );
}
