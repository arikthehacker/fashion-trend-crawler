import { pageMetadata } from "../../lib/site";

export const metadata = pageMetadata("/methodology", "Methodology", "How ARI3LLA INDEX collects, classifies and cites style signals: source sectors, confidence, volatility, citations, corrections and AI involvement.");

// page.tsx
// methodology page for ARI3LLA INDEX — weekly style signal report


const sections: { title: string; body: string[] }[] = [
  {
    title: "What the index records",
    body: [
      "ARI3LLA INDEX records recurring style language, silhouettes, materials, colors, aesthetic terms and cultural references as they appear in public sources.",
      "Each weekly report covers a stated collection window and is kept as a dated record, so the archive shows how style language changes over time.",
    ],
  },
  {
    title: "Scope",
    body: [
      "The index is not a trend forecasting tool, a shopping guide, a brand analytics product or an influencer trend recap.",
      "It does not predict what will sell, recommend purchases or advise brands on production. It does not treat any single platform or publication as an authority.",
    ],
  },
  {
    title: "Source sectors",
    body: [
      "Sources are grouped into sectors: designer origin, runway, editorial, independent criticism, trade intelligence, institutional, visual archive, retail, resale, social, and street or user-generated. Each sector has its own incentives, and every signal names the sectors it was drawn from. The outlets are listed on the Sources page.",
      "A domain that has not been mapped to a sector is classified as unclear instead of being guessed into one. Unclear is not counted as a separate sector for confidence, and it says nothing against the source. It marks a gap in the index's coverage.",
    ],
  },
  {
    title: "How signals are classified",
    body: [
      "Signals are not ranked by popularity alone. Reports weigh recurrence, source diversity, source type, specificity of language, visual coherence, historical continuity and persistence across reporting periods.",
      "Each signal also gets an origin classification: designer originated, editorial amplified, retail adopted, social amplified, platform native, archive revival or unclear. It separates what a designer made from what editors, retailers and platforms did with it afterwards.",
    ],
  },
  {
    title: "How confidence is assigned",
    body: [
      "Confidence reflects how many distinct source sectors report a signal and how consistent the language is across them. Low confidence means the signal comes from one noisy source type. High confidence requires recurrence across several distinct sectors.",
      "A computed baseline is checked against the evidence and is never applied automatically. Two sources with different sector labels do not count as independent if one reprints the other's announcement.",
      "A single source from a high-reliability sector (designer origin, editorial, institutional or independent criticism) can lift a signal above the single-source floor, but only if that source did its own reporting. A source that repeats signals already in the archive without citing new evidence gets no such credit, whatever its sector.",
      "Confidence definitions are listed on the Taxonomy page.",
    ],
  },
  {
    title: "How volatility is assigned",
    body: [
      "Volatility describes how a signal is likely to behave over time: flash, microtrend, seasonal, recurring, revival, long-tail, saturated or declining.",
      "Volatility is assigned separately from confidence. A widely reported signal can still be classified as volatile if its recurrence comes mostly from short-cycle, platform-driven sources.",
    ],
  },
  {
    title: "Social and platform signals",
    body: [
      "Social platform signals are treated as high-noise by default. They can show how fast attention is moving, but they are not treated as stable evidence unless the signal recurs across several sectors or reporting periods.",
      "Social signals are classified as volatile unless non-social evidence supports them across several reporting periods. Editorial coverage of a social signal does not raise its confidence on its own.",
      "Social platforms are never scraped. Social data comes from official platform reports and APIs, or is sampled by hand and recorded with an editor's note.",
    ],
  },
  {
    title: "Editorial sources",
    body: [
      "Editorial coverage is one source sector, and it is not treated as final authority. Editorial media is also shaped by commerce, PR, platform attention and affiliate income, and reports account for that.",
      "On the question of what a designer intended, runway reviews and editorial interpretation rank below designer-originated material and above social media reposts.",
    ],
  },
  {
    title: "AI and the editor",
    body: [
      "Software collects source material, extracts recurring language, clusters related terms and drafts summaries. It does not decide what matters.",
      "The editor decides whether terms belong together, assigns classification and origin, removes hype and connects signals to historical context. The human-editor note on each signal is written by the editor, never by software. No report is published without the editor's review.",
    ],
  },
  {
    title: "Citations",
    body: [
      "Every claim links to the specific, dated article, post or record it rests on. An outlet's homepage or section page does not count as a citation, and a claim without a link is not published.",
      "Each cited item records its URL, its publication date and the date it was retrieved, so a reader can check the claim against the original and see when it was said.",
      "Attribution matches the evidence. A signal from one outlet is never described as coming from \"sources\" in the plural.",
      "Sources in languages other than English are named as such, and translated terms are marked as translations.",
    ],
  },
  {
    title: "Thin collection windows",
    body: [
      "Some collection windows are marked thin, which means fewer signals met the recurrence and source-diversity thresholds than in a typical week.",
      "A thin week is not padded. Where possible it is checked against the raw source volume for that window. If source volume was also low, the smaller signal count reflects the discourse and is not a collection failure.",
      "Reports never invent signals to reach a target count. A verified quiet week is recorded like any other.",
    ],
  },
  {
    title: "How recurrence is tracked",
    body: [
      "Each signal keeps a permanent identifier across reports. Its page lists every dated report it appeared in, in order, and states whether it appeared in the most recent report or how many reports have passed since.",
      "A signal that stops recurring is not automatically marked resolved. A style signal whose discussion has dropped can be closed. An open factual question that keeps going unanswered is handled differently, because its absence from coverage means no answer has been found. It does not mean the question is settled. After a long run without new information it can be marked untracked, and tracking resumes if new coverage appears.",
    ],
  },
  {
    title: "Corrections",
    body: [
      "A published report is never silently edited. When a classification or a stated fact turns out to be wrong, a dated correction note is added to the report, saying what was wrong and what changed.",
      "The original entry is kept beside the correction, so the archive shows what was published at the time.",
      "Each correction also records which signals were added, removed or changed, and which fields changed. A hash of the earlier signal content is kept, so the archive can prove the content changed even if a correction note were incomplete.",
      "Suspected errors can be reported by email to ariella@duck.com or as an issue on the project's public repository (github.com/arikthehacker/fashion-trend-crawler/issues). Response time is not guaranteed.",
    ],
  },
  {
    title: "Independence",
    body: [
      "ARI3LLA INDEX is an independent research project. It is not sponsored by, affiliated with or produced for any brand, publication, retailer or platform named in its reports.",
    ],
  },
  {
    title: "Collection and copyright",
    body: [
      "Collection respects robots.txt and platform terms, does not bypass platform protections, and uses official APIs where they exist.",
      "Reports store links and metadata and never republish copyrighted content in full. Runway images are linked and never rehosted.",
    ],
  },
  {
    title: "Limitations",
    body: [
      "Coverage is limited to the sources collected in each window and is not a representative sample of all style discourse. Sources without public text, or that require API access not yet granted, are under-represented. Most collected sources are currently editorial.",
      "Classification is an interpretive judgment, and reports reflect that judgment as well as the sources.",
    ],
  },
];

export default function Methodology() {
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
          Methodology
        </h1>
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
          How ARI3LLA INDEX collects sources, classifies signals, cites evidence and corrects
          mistakes, and where the method has limits.
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

    </main>
  );
}
