import type { Metadata, Viewport } from "next";
import { Hedvig_Letters_Serif, Funnel_Sans } from "next/font/google";
import "./globals.css";
import { Analytics } from "@vercel/analytics/next";
import { SITE_URL, SITE_NAME, SITE_DESCRIPTION, OG_IMAGE, LLMS_TXT } from "../lib/site";
import { getLatestReport } from "../lib/reports";
import { shortWindow } from "../lib/editorial";
import SiteHeader from "./components/SiteHeader";
import SiteFooter from "./components/SiteFooter";

const hedvig = Hedvig_Letters_Serif({ subsets: ["latin"], weight: "400", variable: "--font-hedvig", display: "swap" });
const funnel = Funnel_Sans({ subsets: ["latin"], style: ["normal", "italic"], variable: "--font-funnel", display: "swap" });

const DEFAULT_TITLE = "ARI3LLA INDEX: a weekly, source-linked record of style language";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: DEFAULT_TITLE, template: `%s | ${SITE_NAME}` },
  description: SITE_DESCRIPTION,
  applicationName: SITE_NAME,
  alternates: { canonical: SITE_URL, types: { "application/rss+xml": "/rss.xml", "text/plain": LLMS_TXT } },
  openGraph: { siteName: SITE_NAME, title: DEFAULT_TITLE, description: SITE_DESCRIPTION, url: SITE_URL, type: "website", locale: "en_US", images: [OG_IMAGE] },
  twitter: { card: "summary_large_image", title: DEFAULT_TITLE, description: SITE_DESCRIPTION, images: [OG_IMAGE.url] },
  robots: { index: true, follow: true, "max-image-preview": "large", "max-snippet": -1 },
  formatDetection: { telephone: false, email: false, address: false },
};

export const viewport: Viewport = { themeColor: "#f1f0ec", width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const latest = getLatestReport();
  const status = latest ? { date: latest.report_date, label: `Latest report: week of ${shortWindow(latest)}` } : null;
  return (
    <html lang="en" className={`${hedvig.variable} ${funnel.variable}`}>
      <body>
        <a href="#main-content" className="skip-link">Skip to main content</a>
        {/* Photocopy texture filters, used by .toner, .toner-lite and .stamp. */}
        <svg width="0" height="0" style={{ position: "absolute" }} aria-hidden="true" focusable="false">
          <defs>
            <filter id="rough" x="-2%" y="-2%" width="104%" height="104%">
              <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={2} seed={4} result="n" />
              <feDisplacementMap in="SourceGraphic" in2="n" scale={1.3} xChannelSelector="R" yChannelSelector="G" />
            </filter>
            <filter id="roughpatchy" x="-2%" y="-2%" width="104%" height="104%">
              <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={2} seed={4} result="n" />
              <feDisplacementMap in="SourceGraphic" in2="n" scale={1.8} xChannelSelector="R" yChannelSelector="G" result="d" />
              <feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves={2} seed={11} result="t" />
              <feColorMatrix in="t" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1.8 0 0 0 1.62" result="mask" />
              <feComposite in="d" in2="mask" operator="in" />
            </filter>
          </defs>
        </svg>
        <div className="sheet">
          <div className="page">
            <SiteHeader status={status} />
            {children}
            <SiteFooter />
          </div>
        </div>
        <Analytics />
      </body>
    </html>
  );
}
