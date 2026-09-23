import type { Metadata } from "next";
import { Instrument_Serif, Libre_Franklin, Reenie_Beanie } from "next/font/google";
import "./globals.css";
import { Analytics } from "@vercel/analytics/next";
import { SITE_URL, SITE_NAME } from "../lib/site";
import SiteHeader from "./components/SiteHeader";
import SiteFooter from "./components/SiteFooter";

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
  title: {
    default: "ARI3LLA INDEX: Weekly Style Signal Report",
    template: "%s | ARI3LLA INDEX",
  },
  alternates: { types: { "application/rss+xml": "/rss.xml" } },
  description: SITE_DESCRIPTION,
  openGraph: {
    siteName: SITE_NAME,
    title: "ARI3LLA INDEX: Weekly Style Signal Report",
    description: SITE_DESCRIPTION,
    url: SITE_URL,
    type: "website",
  },
  // The share image is generated from app/opengraph-image.tsx at build time.
  twitter: {
    card: "summary_large_image",
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
        <SiteHeader />
        {children}
        <SiteFooter />
        <Analytics />
      </body>
    </html>
  );
}
