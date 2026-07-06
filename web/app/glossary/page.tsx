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

import fs from "fs";
import path from "path";
import Link from "next/link";

interface ReportShape {
  aesthetic_terms?: string[];
  cultural_references?: string[];
  top_signals?: { name?: string }[];
}

// Curated short definitions in wire-service voice. Only terms that are found in
// at least one archived report are rendered — this dictionary intentionally
// includes more entries than any single report so it stays valid as new reports
// are added; entries never observed in the archive are simply not shown.
const DEFINITIONS: Record<string, string> = {
  "1970s boho": "A style reference to loose, textured, folk-influenced dressing associated with the 1970s, cited when current coverage draws an explicit historical parallel.",
  "1990s minimalism": "A pared-back, low-ornamentation aesthetic associated with 1990s fashion, referenced when current minimal styling is framed as a revival rather than a new development.",
  "1990s sitcom style": "A style reference to the casual, brand-forward dressing seen in 1990s American television, cited as a visual shorthand rather than a designer-originated term.",
  "archival romanticism": "Styling that draws visibly on historical or archival garment references — antique construction, period silhouettes, preserved detailing — presented as romantic rather than costume-like.",
  "aspirational realism": "A menswear framing describing loose, soft, muted tailoring positioned as attainable rather than formal or overtly luxury-coded.",
  "boho revival": "A recurrence of loose, layered, folk- and craft-influenced dressing associated with earlier bohemian style cycles.",
  "bug-eye sunglasses": "Oversized, rounded, wraparound-style sunglasses noted repeatedly across sources as a recurring accessory shape.",
  "coastal cowgirl": "A styling term combining beach-adjacent casualwear with Western references such as denim, fringe, and boots.",
  "color drenching": "A styling approach of dressing in a single color head-to-toe, including accessories, rather than mixing multiple colors in one look.",
  "eighties luxury": "A style reference to the structured, high-shine, status-signaling dressing associated with 1980s luxury fashion.",
  "funmaxxing": "A maximalist-play aesthetic cluster observed on TikTok combining icy-blue and candy-pink palettes, 1980s technical sportswear, and tassels or fringe; logged as the narrower, checkable styling cluster rather than the broader generational-mood framing some coverage has attached to the term.",
  "layered tops styling": "A styling pattern of wearing multiple visible top layers — camisoles, shirts, sweaters — rather than a single garment, observed primarily in social-platform sources.",
  "maximalism": "A styling approach favoring visible pattern mixing, layering, color, and ornamentation, framed in coverage as a counterpoint to pared-back minimalism.",
  "micro-bag styling": "The continued presence of small, low-capacity handbags as a recurring accessory signal rather than a newly emerging one.",
  "off-duty varsity": "A styling pattern combining sports-team jerseys or collegiate references with casual, non-athletic pieces such as cargo bottoms.",
  "office siren": "A style reference combining traditionally formal, buttoned-up officewear with more overtly styled or revealing elements.",
  "peplum / exaggerated-waistline revival": "A silhouette signal describing the recurrence of flared, structured, or exaggerated waist treatments, tracked across several reports as a forecast-stage signal not yet confirmed at retail.",
  "poetcore": "A dark-academia-adjacent, literary-coded aesthetic term originating on Pinterest, associated with muted tones and vintage-inflected styling.",
  "preppy layering": "A styling pattern combining traditionally preppy garments — collared shirts, sweater vests, knee socks — in layered combinations.",
  "preppy uniform dressing": "Styling that borrows structural elements of school-uniform dressing — collars, pleats, knee-length hems — read through a preppy aesthetic lens.",
  "quiet luxury": "A style term describing unbranded, understated, high-quality dressing that avoids visible logos or overt status signaling.",
  "saturated purple": "A specific, highly pigmented shade of purple noted as a recurring dominant color across a reporting period.",
  "sheer layering": "A styling pattern combining sheer or transparent fabrics with opaque layers underneath or over them.",
  "soft minimalism": "A minimalist styling approach that favors rounded silhouettes and softer fabrics over the sharper, more austere lines of earlier minimalist cycles.",
  "soft tailoring": "Tailoring that retains structured garment shapes — blazers, trousers — while using looser fit and softer fabrication than traditional formal tailoring.",
  "textured maximalist layering": "A styling pattern combining multiple contrasting textures — fur, sheer fabric, denim — within a single maximalist look.",
  "uneven and handkerchief-hem silhouettes": "Garment hems cut at asymmetric or angular lengths rather than a uniform hemline, named for their resemblance to a folded handkerchief corner.",
  "utility belt": "A wide, hardware-heavy belt style referencing workwear and functional gear rather than purely decorative belting.",
  "victorian undergarments": "A historical reference to 19th-century foundation garments — corsetry, underpinnings — cited when current silhouettes are read as drawing on that period.",
  "y2k nostalgia": "A style reference to early-2000s fashion — low-rise cuts, logo-forward branding, metallics — recurring across reports as a sustained rather than one-off revival.",
};

function normalize(term: string): string {
  return term
    .replace(/\s*\(carryover\)\s*$/i, "")
    .replace(/,\s*(forecast stage|third and final recheck|still unconfirmed at [^)]*|dormancy check|continuing|social)\s*$/i, "")
    .replace(/^"funmaxxing".*$/i, "funmaxxing")
    .trim();
}

function loadGlossaryTerms(): { term: string; def: string }[] {
  const dir = path.join(process.cwd(), "..", "data", "reports");
  const found = new Map<string, string>(); // lowercase key -> display term

  if (fs.existsSync(dir)) {
    const files = fs.readdirSync(dir).filter((f) => f.endsWith(".json"));
    for (const file of files) {
      const report = JSON.parse(
        fs.readFileSync(path.join(dir, file), "utf-8")
      ) as ReportShape;

      const candidates = [
        ...(report.aesthetic_terms ?? []),
        ...(report.cultural_references ?? []),
        ...(report.top_signals ?? []).map((s) => s.name ?? ""),
      ];

      for (const raw of candidates) {
        const cleaned = normalize(raw);
        const key = cleaned.toLowerCase();
        if (DEFINITIONS[key] && !found.has(key)) {
          found.set(key, cleaned);
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
          Glossary
        </h1>
        <nav
          aria-label="Site sections"
          style={{ display: "flex", justifyContent: "center", gap: "1.5rem", marginTop: "1.5rem", flexWrap: "wrap" }}
        >
          {[
            { href: "/", label: "Report" },
            { href: "/methodology", label: "Methodology" },
            { href: "/taxonomy", label: "Taxonomy" },
            { href: "/sources", label: "Sources" },
            { href: "/timeline", label: "Timeline" },
            { href: "/archive", label: "Archive" },
            { href: "/search", label: "Search" },
            { href: "/about", label: "About" },
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
          Definitions for style and aesthetic terms that have recurred across the archive.
          This page defines the terms themselves; the Taxonomy page defines the
          classification system used to sort them. Entries are drawn only from terms that
          have appeared in an archived report. This glossary does not cover source sectors
          or confidence/volatility labels (e.g. flash, microtrend, revival) — for that
          vocabulary, see{" "}
          <Link href="/taxonomy" style={{ color: "var(--black)", textDecoration: "underline" }}>
            Taxonomy
          </Link>
          .
        </p>

        <dl style={{ display: "flex", flexDirection: "column", margin: 0 }}>
          {terms.map((t) => (
            <div
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
