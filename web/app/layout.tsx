import type { Metadata } from "next";
import { Instrument_Serif, Libre_Franklin, Reenie_Beanie } from "next/font/google";
import "./globals.css";
import { SITE_URL, SITE_NAME } from "../lib/site";

const instrumentSerif = Instrument_Serif({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-instrument",
});

const libreFranklin = Libre_Franklin({
  subsets: ["latin"],
  variable: "--font-franklin",
});

const reenieBeanie = Reenie_Beanie({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-reenie",
});

const SITE_DESCRIPTION =
  "A source-linked index tracking recurring style language, silhouettes, materials, aesthetics, and cultural signals across the web.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: "ARI3LLA INDEX: Weekly Style Signal Report",
  description: SITE_DESCRIPTION,
  alternates: {
    types: {
      "application/rss+xml": "/rss.xml",
    },
  },
  openGraph: {
    siteName: SITE_NAME,
    title: "ARI3LLA INDEX: Weekly Style Signal Report",
    description: SITE_DESCRIPTION,
    url: SITE_URL,
    type: "website",
  },
  // No image assets exist on this site (text-only by design) — "summary" is the
  // correct Twitter card type here, not "summary_large_image", which needs an image.
  twitter: {
    card: "summary",
    title: "ARI3LLA INDEX: Weekly Style Signal Report",
    description: SITE_DESCRIPTION,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={`${instrumentSerif.variable} ${libreFranklin.variable} ${reenieBeanie.variable}`}
      >
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>
        {children}
      </body>
    </html>
  );
}
