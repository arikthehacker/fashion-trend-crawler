import Link from "next/link";
import { pageMetadata } from "../../../lib/site";
import { TIMELINE } from "../../../lib/ari3_cards";
import { Page, Pill, bodyText, mono } from "../ui";

export const metadata = pageMetadata(
  "/ari3/timeline",
  "ARI3 research timeline",
  "How ARI3 developed, from the first crawl to pre-registered experiments. Dates are real. Planned steps carry no date."
);

export default function Timeline() {
  return (
    <Page title="Research timeline">
      <p style={{ ...bodyText, margin: 0 }}>
        <Link href="/ari3" style={{ color: "var(--black)" }}>ARI3 research notebook</Link>
      </p>
      <p style={{ ...bodyText, fontSize: "1.05rem", color: "var(--black)", marginTop: "1rem" }}>
        Every dated step happened on that date (UTC). Planned steps carry no date.
      </p>
      <ol style={{ listStyle: "none", margin: "2rem 0 0", padding: 0, borderLeft: "2px solid var(--black)" }}>
        {TIMELINE.map((t, i) => (
          <li key={i} style={{ position: "relative", padding: "0 0 1.6rem 1.4rem" }}>
            <span aria-hidden="true" style={{ position: "absolute", left: "-7px", top: "0.35rem", width: "12px", height: "12px", borderRadius: "50%", background: t.planned ? "var(--white)" : "var(--black)", border: "2px solid var(--black)" }} />
            <div style={{ display: "flex", gap: "0.7rem", alignItems: "baseline", flexWrap: "wrap" }}>
              <span style={{ fontFamily: mono, fontSize: "0.8rem", color: "var(--gray)" }}>{t.date}</span>
              {t.planned && <Pill tone="gray">Planned</Pill>}
            </div>
            <h2 style={{ fontFamily: "var(--font-instrument)", fontSize: "1.45rem", fontWeight: 400, margin: "0.2rem 0 0.3rem", color: t.planned ? "var(--gray)" : "var(--black)" }}>
              {t.href ? <Link href={t.href} style={{ color: "inherit" }}>{t.title}</Link> : t.title}
            </h2>
            <p style={{ ...bodyText, margin: 0 }}>{t.detail}</p>
          </li>
        ))}
      </ol>
    </Page>
  );
}
