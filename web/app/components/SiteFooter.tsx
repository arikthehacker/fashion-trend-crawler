// Shared footer: the reference pages, legal pages and machine-readable feeds.

import Link from "next/link";
import { FOOTER_NAV } from "../../lib/nav";

export default function SiteFooter() {
  return (
    <footer className="foot">
      <nav aria-label="More">
        <ul>
          {FOOTER_NAV.map((item) =>
            item.href.startsWith("http") || item.href.endsWith(".xml") || item.href.endsWith(".txt") || item.href.endsWith(".json") ? (
              <li key={item.href}><a href={item.href}>{item.label}</a></li>
            ) : (
              <li key={item.href}><Link href={item.href}>{item.label}</Link></li>
            ),
          )}
        </ul>
      </nav>
    </footer>
  );
}
