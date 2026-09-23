"use client";
// Shared site header: wordmark + primary navigation, identical on every page.
// The current section is marked with aria-current so screen readers announce it.

import Link from "next/link";
import { usePathname } from "next/navigation";
import { PRIMARY_NAV } from "../../lib/nav";

function isCurrent(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export default function SiteHeader() {
  const pathname = usePathname() || "/";
  return (
    <header className="site-header no-print">
      <Link href="/" className="site-wordmark" aria-label="ARI3LLA INDEX, home">
        ARI3LLA INDEX
      </Link>
      <nav aria-label="Primary">
        <ul className="site-nav">
          {PRIMARY_NAV.map((item) => (
            <li key={item.href}>
              <Link href={item.href} aria-current={isCurrent(pathname, item.href) ? "page" : undefined}>
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  );
}
