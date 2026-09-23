// page.tsx
// taxonomy page for ARI3LLA INDEX — weekly style signal report

import Link from "next/link";

const signalTypes = [
  "Garment", "Silhouette", "Material", "Color", "Styling behavior", "Aesthetic term",
  "Commerce language", "Cultural reference", "Brand behavior", "Platform behavior",
  "Designer-origin signal", "Retail adoption signal", "Visual mood", "Accessory signal",
  "Beauty/fragrance signal", "Lifestyle signal",
];

const sourceSectors = [
  { name: "Designer-origin", def: "Official brand websites, collection pages, show notes, lookbooks, campaign pages, press releases, designer interviews, creative director statements." },
  { name: "Runway/editorial", def: "Runway coverage and style publications reporting on collections, shows, and seasonal direction." },
  { name: "Retail/commerce", def: "Product titles, category names, new arrivals, material and color labels, styling copy, sold-out language, retailer trend edits." },
  { name: "Social/platform", def: "TikTok, Instagram, YouTube, Reddit, and Pinterest language — captions, comments, and creator trend content." },
  { name: "Visual archive/search", def: "Visual search and reference platforms used to observe recurring imagery rather than public commentary." },
  { name: "Independent criticism", def: "Substack fashion writers, independent newsletters, long-form blogs, and cultural commentary outside institutional media." },
  { name: "Institutional/historical", def: "Museum collections, costume history databases, academic papers, and archival runway records." },
  { name: "Street/user-generated", def: "Street style photography and public outfit documentation, distinct from platform-native captions and comments." },
  { name: "Resale/secondhand", def: "Secondhand marketplace listings and descriptions — a separate signal channel from primary retail." },
  { name: "Trade intelligence", def: "B2B commercial trend-forecasting and retail-analytics vendors, whose public content markets a paid prediction or merchandising product rather than reporting independently on discourse. Excluded from high-reliability sectors." },
];

const volatility = [
  { label: "Stable", def: "Consistent presence with no strong upward or downward movement." },
  { label: "Emerging", def: "Newly appearing with early but not yet broad recurrence." },
  { label: "Seasonal", def: "Tied to a predictable calendar, weather, or retail rhythm." },
  { label: "Volatile", def: "Fluctuates quickly, concentrated in short-cycle or platform-driven sources." },
  { label: "Flash", def: "Appears suddenly in high-noise sources with little broader support." },
  { label: "Microtrend", def: "Visible in social/platform language but likely short-cycle." },
  { label: "Recurring", def: "Appears repeatedly across reports over time." },
  { label: "Revival", def: "Clearly connected to a previous era or documented style cycle." },
  { label: "Long-tail", def: "Not dominant but continues appearing over an extended period." },
  { label: "Saturated", def: "Over-repeated, likely near exhaustion." },
  { label: "Declining", def: "Mentions or coherence are decreasing over successive reports." },
];

const confidence = [
  { label: "Low", def: "Appears in one noisy source type or weakly across sources." },
  { label: "Medium", def: "Appears across two or more source types with some language consistency." },
  { label: "High", def: "Appears across multiple distinct sectors, such as designer, editorial, retail, social, and visual search." },
  { label: "Archival", def: "Recurring across multiple time periods or connected to documented historical cycles." },
];

const originClassification = [
  { label: "Designer-originated", def: "Traced to a brand or creative team's own material — collection pages, show notes, campaigns, interviews — before any outside interpretation." },
  { label: "Editorial-amplified", def: "Carried into wider discourse primarily through runway coverage or style-publication interpretation of what a designer showed or meant." },
  { label: "Retail-adopted", def: "Carried into wider discourse primarily through product naming, category language, or trend-edit copy applied at the point of sale." },
  { label: "Social-amplified", def: "Carried into wider discourse primarily through platform captions, comments, or creator content, independent of editorial or retail framing." },
  { label: "Platform-native", def: "Originates on a social platform itself, with no clear designer, editorial, or retail point of origin." },
  { label: "Archive revival", def: "Traced to a previously documented style cycle or archival record resurfacing rather than a new origin point." },
  { label: "Unclear", def: "No reliable origin point could be established from available sources." },
];

function Table({ rows }: { rows: { label: string; def: string }[] }) {
  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      {rows.map((r) => (
        <div
          key={r.label}
          style={{
            display: "grid",
            gridTemplateColumns: "160px 1fr",
            gap: "1.5rem",
            padding: "1rem 0",
            borderBottom: "1px solid var(--border)",
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
              paddingTop: "0.15rem",
            }}
          >
            {r.label}
          </p>
          <p
            style={{
              fontFamily: "var(--font-franklin)",
              fontSize: "0.95rem",
              lineHeight: "1.6",
              color: "var(--gray)",
            }}
          >
            {r.def}
          </p>
        </div>
      ))}
    </div>
  );
}

export default function Taxonomy() {
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
          Taxonomy
        </h1>
        <nav
          aria-label="Site sections"
          style={{ display: "flex", justifyContent: "center", gap: "1.5rem", marginTop: "1.5rem" }}
        >
          {[
            { href: "/", label: "Report" },
            { href: "/methodology", label: "Methodology" },
            { href: "/sources", label: "Sources" },
            { href: "/glossary", label: "Glossary" },
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
                display: "inline-block",
                padding: "0.65rem 0",
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
          Signals are classified along five dimensions: signal type, source sector, volatility,
          confidence, and origin classification. Definitions below are applied consistently across
          reports. This page does not
          define style or aesthetic terminology (e.g. quiet luxury, Y2K nostalgia) — for that, see{" "}
          <Link href="/glossary" style={{ color: "var(--black)", textDecoration: "underline" }}>
            Glossary
          </Link>
          .
        </p>

        <div style={{ marginBottom: "3.5rem" }}>
          <h2
            style={{
              fontFamily: "var(--font-instrument)",
              fontSize: "1.5rem",
              fontWeight: "400",
              marginBottom: "1rem",
              borderTop: "1px solid var(--border)",
              paddingTop: "1.5rem",
            }}
          >
            Signal Types
          </h2>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
              gap: "0.75rem 1.5rem",
            }}
          >
            {signalTypes.map((t) => (
              <p
                key={t}
                style={{
                  fontFamily: "var(--font-franklin)",
                  fontSize: "0.9rem",
                  color: "var(--black)",
                  padding: "0.5rem 0",
                  borderBottom: "1px solid var(--border)",
                }}
              >
                {t}
              </p>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: "3.5rem" }}>
          <h2
            style={{
              fontFamily: "var(--font-instrument)",
              fontSize: "1.5rem",
              fontWeight: "400",
              marginBottom: "1rem",
              borderTop: "1px solid var(--border)",
              paddingTop: "1.5rem",
            }}
          >
            Source Sectors
          </h2>
          <Table rows={sourceSectors.map((s) => ({ label: s.name, def: s.def }))} />
        </div>

        <div style={{ marginBottom: "3.5rem" }}>
          <h2
            style={{
              fontFamily: "var(--font-instrument)",
              fontSize: "1.5rem",
              fontWeight: "400",
              marginBottom: "1rem",
              borderTop: "1px solid var(--border)",
              paddingTop: "1.5rem",
            }}
          >
            Volatility Labels
          </h2>
          <Table rows={volatility} />
        </div>

        <div>
          <h2
            style={{
              fontFamily: "var(--font-instrument)",
              fontSize: "1.5rem",
              fontWeight: "400",
              marginBottom: "1rem",
              borderTop: "1px solid var(--border)",
              paddingTop: "1.5rem",
            }}
          >
            Confidence Levels
          </h2>
          <Table rows={confidence} />
        </div>

        <div style={{ marginTop: "3.5rem" }}>
          <h2
            style={{
              fontFamily: "var(--font-instrument)",
              fontSize: "1.5rem",
              fontWeight: "400",
              marginBottom: "1rem",
              borderTop: "1px solid var(--border)",
              paddingTop: "1.5rem",
            }}
          >
            Origin Classification
          </h2>
          <p
            style={{
              fontFamily: "var(--font-franklin)",
              fontSize: "0.9rem",
              lineHeight: "1.6",
              color: "var(--gray)",
              marginBottom: "1.25rem",
            }}
          >
            Recorded separately from confidence and volatility, to keep what a designer made,
            what editors said it meant, what retailers sold it as, and what a platform renamed it
            from collapsing into a single undifferentiated &ldquo;trending&rdquo; label.
          </p>
          <Table rows={originClassification} />
        </div>
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
          ARI3LLA INDEX is an independent style signal archive. Reports are compiled from public, linked
          source material and structured for historical reference. No purchasing recommendation is
          implied.
        </p>
      </footer>
    </main>
  );
}
