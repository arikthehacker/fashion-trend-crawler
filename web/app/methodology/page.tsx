// page.tsx
// methodology page for ARI3LLA INDEX — weekly style signal report

import Link from "next/link";

const sections: { title: string; body: string[] }[] = [
  {
    title: "What This Index Tracks",
    body: [
      "ARI3LLA INDEX tracks recurring style language, silhouettes, materials, colors, aesthetic terms, and cultural references as they appear across public web sources.",
      "Signals are collected on a recurring schedule and preserved as dated reports, forming a historical record of style discourse rather than a single snapshot.",
    ],
  },
  {
    title: "What This Index Does Not Track",
    body: [
      "This is not a trend forecasting tool, a shopping guide, a brand analytics product, or an influencer trend recap.",
      "The Index does not predict what will sell, recommend purchases, or advise brands on production. It does not treat any single platform or publication as an authority.",
    ],
  },
  {
    title: "Source Sectors",
    body: [
      "Sources are grouped into sectors: designer-origin, runway/editorial, retail/commerce, social/platform, visual archive and search, independent criticism, institutional/historical, street/user-generated, and resale/secondhand.",
      "Each sector carries a different incentive structure, and reports note which sectors a signal is drawn from. A full breakdown is available on the Sources page.",
    ],
  },
  {
    title: "How Signals Are Classified",
    body: [
      "Signals are not ranked by popularity alone. Reports consider recurrence, source diversity, source type, specificity of language, visual coherence, historical continuity, and persistence across reporting periods.",
      "Each signal is also assigned an origin classification — designer-originated, editorial-amplified, retail-adopted, social-amplified, platform-native, archive revival, or unclear — to separate what a designer made from what editors, retailers, and platforms did with it afterward.",
    ],
  },
  {
    title: "How Confidence Is Assigned",
    body: [
      "Confidence reflects how many distinct source sectors report a signal and how consistent the language is across them. Low confidence indicates a signal drawn from one noisy source type; high confidence requires recurrence across multiple distinct sectors.",
      "Full confidence definitions are listed on the Taxonomy page.",
    ],
  },
  {
    title: "How Volatility Is Assigned",
    body: [
      "Volatility describes how a signal is likely to behave over time — flash, microtrend, seasonal, recurring, revival, long-tail, saturated, or declining.",
      "Volatility is assigned independently of confidence: a signal can be widely reported and still classified as volatile if its recurrence is concentrated in short-cycle, platform-driven sources.",
    ],
  },
  {
    title: "How Social and Platform Signals Are Handled",
    body: [
      "Social platform signals are classified as high-noise by default. They may indicate cultural velocity, but they are not treated as stable style evidence unless supported by recurrence across multiple sectors or reporting periods.",
      "TikTok/social signals are identified and tracked, but classified as volatile unless supported by non-social evidence across multiple reporting periods. Coverage of a social signal by an editorial outlet does not automatically upgrade its confidence.",
    ],
  },
  {
    title: "How Editorial Authority Is Treated",
    body: [
      "Editorial coverage is treated as a source sector, not as final authority. Reports account for the fact that editorial media may also be shaped by commerce, PR, platform attention, and affiliate incentives.",
      "Runway reviews and editorial interpretation sit below designer-originated material and above social-media reposting in the Index's source hierarchy for designer intent.",
    ],
  },
  {
    title: "How AI Is Used",
    body: [
      "Language models are used to extract, cluster, and summarize source material. They are not treated as independent authorities. Final classification depends on the Index taxonomy and human review.",
      "This project uses AI for summarization and organization, not for replacing designers, journalists, stylists, archivists, or cultural analysis. The goal is to make public style discourse easier to scan while keeping human interpretation central.",
    ],
  },
  {
    title: "Limitations",
    body: [
      "Coverage is bounded by the sources scanned in a given collection window and is not a representative sample of all style discourse. Reports may under-represent sources without accessible public text, or that require API access not yet integrated.",
      "Signal classification involves human judgment applied to machine-extracted data, and reports may reflect that interpretive layer as much as the underlying source material.",
    ],
  },
  {
    title: "How Low-Volatility Windows Are Reported",
    body: [
      "Some collection windows return a `collection_status` of \"thin,\" meaning fewer signals met the recurrence and source-diversity thresholds than in a typical reporting period.",
      "A thin status is not treated as a gap to be filled. Where possible it is checked against raw source volume for that window; when source volume was itself low, the reduced signal count reflects observed style discourse rather than a collection failure.",
      "Reports do not manufacture signals to normalize a thin window to a target count. A verified low-volatility period is recorded as a data point in the archive, the same as any other classification.",
    ],
  },
  {
    title: "Corrections",
    body: [
      "When a signal classification or a stated fact is found to be wrong, the affected report is not silently edited. A dated correction note is appended to the report, stating what was wrong and what changed.",
      "The original entry is preserved alongside the correction so the archive reflects what was published at the time, not a retroactively cleaned-up version of it.",
    ],
  },
  {
    title: "Editorial Independence",
    body: [
      "ARI3LLA INDEX is an independent research project. It is not sponsored by, affiliated with, or produced on behalf of any brand, publication, retailer, or platform referenced in its reports.",
      "Editorial sources are cited as a source sector, not treated as neutral. Editorial coverage can be shaped by advertising relationships, affiliate commerce, and access to designers and PR — reports account for that incentive structure rather than assuming editorial framing is disinterested.",
    ],
  },
  {
    title: "AI Involvement",
    body: [
      "AI assists with crawling source material, extracting recurring language, clustering related terms, and drafting summaries. It does not make final classification decisions.",
      "A human reviews AI-assisted output before publication, deciding what a cluster of terms means culturally, assigning taxonomy and origin classification, and recording judgment calls in a human-editor note attached to the report data.",
    ],
  },
  {
    title: "Ethical Scraping and Source Policy",
    body: [
      "Collection respects robots.txt and platform terms, avoids bypassing platform protections, and uses official APIs where available.",
      "Reports store metadata and source links rather than reproducing copyrighted content in full, and cite sources directly so claims can be checked against the original material.",
    ],
  },
  {
    title: "Human Review Process",
    body: [
      "Raw extraction identifies repeated language and clusters related terms. Human review interprets whether those terms belong together, assigns classification and origin, downgrades hype, and connects signals to historical context where relevant.",
      "The scraping collects signals. The taxonomy interprets them.",
    ],
  },
];

export default function Methodology() {
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
          Methodology
        </h1>
        <nav
          aria-label="Site sections"
          style={{ display: "flex", justifyContent: "center", gap: "1.5rem", marginTop: "1.5rem" }}
        >
          {[
            { href: "/", label: "Report" },
            { href: "/taxonomy", label: "Taxonomy" },
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
          maxWidth: "760px",
          padding: "4rem 2rem",
        }}
      >
        <p
          style={{
            fontFamily: "var(--font-franklin)",
            fontSize: "1rem",
            lineHeight: "1.8",
            color: "var(--gray)",
            marginBottom: "3.5rem",
          }}
        >
          This report identifies recurring style signals observed across public web sources during
          the collection window. Signals are ranked by recurrence, source diversity, and clarity of
          language. The sections below describe how that process works, and where its limits are.
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: "2.5rem" }}>
          {sections.map((s) => (
            <div key={s.title} style={{ borderTop: "1px solid var(--border)", paddingTop: "1.5rem" }}>
              <h2
                style={{
                  fontFamily: "var(--font-instrument)",
                  fontSize: "1.5rem",
                  fontWeight: "400",
                  marginBottom: "0.75rem",
                }}
              >
                {s.title}
              </h2>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.9rem" }}>
                {s.body.map((p, i) => (
                  <p
                    key={i}
                    style={{
                      fontFamily: "var(--font-franklin)",
                      fontSize: "0.95rem",
                      lineHeight: "1.7",
                      color: "var(--gray)",
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
