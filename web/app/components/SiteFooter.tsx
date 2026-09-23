"use client";
// Shared site footer: disclaimer, secondary/legal links, contact, license.

import Link from "next/link";
import { usePathname } from "next/navigation";
import { CONTACT_EMAIL, FOOTER_NAV, ISSUES_URL } from "../../lib/nav";

export default function SiteFooter() {
  const pathname = usePathname() || "/";
  const year = new Date().getFullYear();
  return (
    <footer className="site-footer">
      <p className="site-footer-lede">
        ARI3LLA INDEX is an independent style signal archive. Reports are compiled from public,
        linked source material and structured for historical reference. No purchasing
        recommendation is implied.
      </p>
      <nav aria-label="Footer" className="no-print">
        <ul className="site-footer-nav">
          {FOOTER_NAV.map((item) => (
            <li key={item.href}>
              <Link href={item.href} aria-current={pathname === item.href ? "page" : undefined}>{item.label}</Link>
            </li>
          ))}
        </ul>
      </nav>
      <p className="site-footer-meta">
        Contact: <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a> ·{" "}
        <a href={ISSUES_URL} rel="noopener noreferrer">Report an error on GitHub</a>
      </p>
      <p className="site-footer-meta">
        © {year} ARI3LLA INDEX. Index classifications are licensed{" "}
        <a href="https://creativecommons.org/licenses/by/4.0/" rel="license noopener noreferrer">CC BY 4.0</a>;
        linked articles belong to their publishers.
      </p>
    </footer>
  );
}
