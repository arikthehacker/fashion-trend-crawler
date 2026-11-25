// lib/og.tsx
// Share cards (Open Graph / Twitter) in the photocopy style, rendered at build time.
// Fonts are fetched from Google Fonts during the build; if that fails, the card
// still renders in the default font, so a network blip can never break a deploy.

import { ImageResponse } from "next/og";

export const OG_SIZE = { width: 1200, height: 630 };
const PAPER = "#f1f0ec", INK = "#0f0f10", MUTED = "#45443f";

async function googleFont(family: string, text: string, weight = 400): Promise<ArrayBuffer | null> {
  try {
    const css = await (await fetch(`https://fonts.googleapis.com/css2?family=${family.replace(/ /g, "+")}:wght@${weight}&text=${encodeURIComponent(text)}`)).text();
    const src = css.match(/src: url\((.+?)\) format\('(opentype|truetype)'\)/);
    if (!src) return null;
    const res = await fetch(src[1]);
    return res.ok ? await res.arrayBuffer() : null;
  } catch {
    return null;
  }
}

export async function shareCard({ kicker, title, lines = [], foot }: { kicker: string; title: string; lines?: string[]; foot: string }) {
  const text = ["ARI3LLA INDEX", kicker, title, ...lines, foot].join(" ");
  const [serif, sans] = await Promise.all([googleFont("Hedvig Letters Serif", text), googleFont("Funnel Sans", text, 600)]);
  const fonts = [
    ...(serif ? [{ name: "Serif", data: serif, weight: 400 as const, style: "normal" as const }] : []),
    ...(sans ? [{ name: "Sans", data: sans, weight: 600 as const, style: "normal" as const }] : []),
  ];
  const size = title.length > 70 ? 54 : title.length > 45 ? 64 : 76;
  return new ImageResponse(
    (
      <div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", background: PAPER, color: INK, padding: "44px 60px", fontFamily: "Serif" }}>
        <div style={{ display: "flex", justifyContent: "center", borderTop: `2px solid ${INK}`, paddingTop: 14, fontSize: 64, letterSpacing: 3 }}>ARI3LLA INDEX</div>
        <div style={{ display: "flex", flexDirection: "column", marginTop: 10 }}>
          <div style={{ display: "flex", height: 1, background: INK }} />
          <div style={{ display: "flex", height: 1, background: INK, marginTop: 3 }} />
          <div style={{ display: "flex", justifyContent: "center", padding: "8px 0", fontSize: 26 }}>{kicker}</div>
          <div style={{ display: "flex", height: 1, background: INK }} />
          <div style={{ display: "flex", height: 1, background: INK, marginTop: 3 }} />
        </div>
        <div style={{ display: "flex", flex: 1, flexDirection: "column", justifyContent: "center" }}>
          <div style={{ display: "flex", fontSize: size, lineHeight: 1.02, letterSpacing: -1 }}>{title}</div>
          {lines.length ? (
            <div style={{ display: "flex", flexDirection: "column", marginTop: 22, fontFamily: "Sans", fontSize: 24, color: MUTED }}>
              {lines.map((l) => <div key={l} style={{ display: "flex" }}>{l}</div>)}
            </div>
          ) : null}
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", borderTop: `2px solid ${INK}`, paddingTop: 12, fontFamily: "Sans", fontSize: 22, letterSpacing: 2 }}>
          <span>{foot}</span><span>ari3lla.com</span>
        </div>
      </div>
    ),
    { ...OG_SIZE, fonts: fonts.length ? fonts : undefined },
  );
}
