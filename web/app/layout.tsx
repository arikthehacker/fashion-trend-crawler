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
  title: "RUNWAY: Fashion Trend Intelligence",
  description: "Weekly fashion trend analysis for the busy woman who still wants to know.",
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
