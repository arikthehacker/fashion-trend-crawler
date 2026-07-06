import { ImageResponse } from "next/og";

// Route-segment metadata file: Next.js auto-detects this and generates a
// favicon + injects the appropriate <link rel="icon"> tag. No binary image
// asset needed — consistent with the site's text-only-by-design approach
// (see the twitter/openGraph comment in layout.tsx).
//
// Required for output: "export" (static export) — same fix pattern as
// sitemap.ts/robots.ts (run 24): a route handler needs an explicit static
// marker or the build fails with "not configured on route ... with
// output: export" (found run 53 consolidation).
export const dynamic = "force-static";

export const size = {
  width: 32,
  height: 32,
};
export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#000",
          color: "#fff",
          fontSize: 20,
          fontWeight: 700,
          fontFamily: "sans-serif",
        }}
      >
        A
      </div>
    ),
    { ...size }
  );
}
