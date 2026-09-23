import { ImageResponse } from "next/og";

// Default share card (Open Graph / Twitter) for every page, generated at build
// time like icon.tsx. Text only, in the site palette.
export const dynamic = "force-static";
export const alt = "ARI3LLA INDEX: a public, source-linked archive of style language";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "72px",
          background: "#f8f6f1",
          color: "#0a0a0a",
          fontFamily: "serif",
        }}
      >
        <div style={{ fontSize: 28, letterSpacing: 6, color: "#c8102e", fontFamily: "sans-serif" }}>
          WEEKLY STYLE SIGNAL REPORT
        </div>
        <div style={{ display: "flex", flexDirection: "column", fontSize: 150, lineHeight: 0.9 }}>
          <span>ARI3LLA</span>
          <span>INDEX</span>
        </div>
        <div style={{ fontSize: 32, color: "#6b6b6b", fontFamily: "sans-serif" }}>
          A public, source-linked archive of style language
        </div>
      </div>
    ),
    { ...size },
  );
}
