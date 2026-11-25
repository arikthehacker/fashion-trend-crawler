// Shared footer: the reference pages, legal pages and machine-readable feeds.

import Link from "next/link";
import { FOOTER_NAV, CONTACT_EMAIL, REPO_URL } from "../../lib/nav";

export default function SiteFooter() {
  return (
    <footer className="foot">
      <nav aria-label="More">
        <ul>
          {FOOTER_NAV.map((item) =>
            item.href.endsWith(".xml") || item.href.endsWith(".txt") || item.href.endsWith(".json") ? (
              <li key={item.href}><a href={item.href}>{item.label}</a></li>
            ) : (
              <li key={item.href}><Link href={item.href}>{item.label}</Link></li>
            ),
          )}
        </ul>
      </nav>
      <p className="foot-line">
        <span>Corrections: <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a></span>
        <a href={REPO_URL}>Source code</a>
      </p>
    </footer>
  );
}
