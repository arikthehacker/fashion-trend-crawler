// app/glossary/page.tsx
// Glossary in the photocopy edition: an A-to-Z book index of style terms.
//
// Terms are sourced from the archive's aesthetic_terms, cultural_references and
// top_signals[].name fields (data/reports/*.json), read at build time and matched
// against a curated definition set below. Only terms that appear in the archive
// are rendered, so the glossary stays tied to what the index has observed rather
// than an abstract style dictionary. Distinct from /taxonomy, which documents the
// classification system rather than the aesthetic terms themselves.

import Link from "next/link";
import { getAllReports } from "../../lib/reports";
import { pageMetadata } from "../../lib/site";
import { Folio } from "../components/Chrome";

export const metadata = pageMetadata("/glossary", "Glossary", "Definitions of the style and aesthetic terms used in ARI3LLA INDEX reports, each added only when a report's evidence supports it.");

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

// A glossary term is short vocabulary (e.g. "peplum", "quiet luxury"), not a
// sentence tracking a signal's status. This filters out long or sentence-like
// candidates before they are checked against DEFINITIONS, so build-time
// warnings only surface terms worth defining.
function isPlausibleGlossaryTerm(term: string): boolean {
  if (term.length > 40) return false;
  if (term.split(/\s+/).length > 5) return false;
  if (/[()]/.test(term)) return false;
  if (/[,;:]/.test(term)) return false;
  if (/--|—|–/.test(term)) return false;
  if (/[.!?]\s*$/.test(term)) return false;
  return true;
}

function loadGlossaryTerms(): { term: string; def: string }[] {
  const found = new Map<string, string>(); // lowercase key -> display term
  const reports = getAllReports() as unknown as ReportShape[];
  for (const report of reports) {
    const candidates = [
      ...(report.aesthetic_terms ?? []),
      ...(report.cultural_references ?? []),
      ...(report.top_signals ?? []).map((s) => s.name ?? ""),
    ];
    for (const raw of candidates) {
      const cleaned = normalize(raw);
      if (!cleaned || !isPlausibleGlossaryTerm(cleaned)) continue;
      const key = cleaned.toLowerCase();
      if (DEFINITIONS[key]) {
        if (!found.has(key)) found.set(key, cleaned);
      } else {
        // Non-blocking build-time warning: surfaces archive terms that have no
        // curated definition, so they do not silently drop off /glossary.
        console.warn(
          `[glossary] no DEFINITIONS entry for term "${cleaned}" (from ${(report as { report_date?: string }).report_date ?? "unknown report"}); term will not be shown on /glossary`
        );
      }
    }
  }
  return Array.from(found.entries())
    .map(([key, term]) => ({ term, def: DEFINITIONS[key] }))
    .sort((a, b) => a.term.localeCompare(b.term));
}

export default function Glossary() {
  const terms = loadGlossaryTerms();
  const groups = new Map<string, typeof terms>();
  for (const t of terms) {
    const letter = /[a-z]/i.test(t.term[0]) ? t.term[0].toUpperCase() : "#";
    groups.set(letter, [...(groups.get(letter) ?? []), t]);
  }

  return (
    <main id="main-content">
      <Folio h1 left="Glossary" right={terms.length ? `${terms.length} term${terms.length === 1 ? "" : "s"}, A to Z` : "A to Z"} />
      <p className="lede-intro">
        Definitions of style and aesthetic terms that have appeared in archived reports. A term
        is listed only after it appears in a report. Source sectors and the confidence and
        volatility labels are defined on the <Link href="/taxonomy">Taxonomy</Link> page.
      </p>

      {terms.length === 0 ? (
        <p className="note" style={{ marginTop: 18 }}>
          No term has a definition yet. A definition is added only when a published report uses the term and that report&apos;s evidence supports the definition.
        </p>
      ) : (
        <div className="bindex" style={{ marginTop: 24 }}>
          {Array.from(groups.entries()).map(([letter, xs]) => (
            <section key={letter} className="letter" aria-labelledby={`l-${letter}`}>
              <h2 id={`l-${letter}`}>{letter}</h2>
              {xs.map((t) => (
                <p key={t.term}>
                  <dfn style={{ fontFamily: "var(--serif)", fontSize: 18, fontStyle: "normal" }}>{t.term}</dfn>{" "}
                  <span>{t.def}</span>
                </p>
              ))}
            </section>
          ))}
        </div>
      )}
    </main>
  );
}
