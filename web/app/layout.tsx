import type { Metadata } from "next";
import { Instrument_Serif, Libre_Franklin, Reenie_Beanie } from "next/font/google";
import "./globals.css";

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

export const metadata: Metadata = {
  title: "ARI3LLA INDEX: Weekly Style Signal Report",
  description: "A source-linked index tracking recurring style language, silhouettes, materials, aesthetics, and cultural signals across the web.",
  alternates: {
    types: {
      "application/rss+xml": "/rss.xml",
    },
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
        {children}
      </body>
    </html>
  );
}
