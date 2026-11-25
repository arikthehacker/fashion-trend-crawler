"use client";
// The photocopy edition's chrome: status line, section links and the nameplate.
// The nameplate is large on the front page and small everywhere else.

import Link from "next/link";
import { usePathname } from "next/navigation";
import { PRIMARY_NAV } from "../../lib/nav";

function isCurrent(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`) || (href === "/archive" && pathname.startsWith("/reports/"));
}

export default function SiteHeader({ status }: { status: { date: string; label: string } | null }) {
  const pathname = (usePathname() || "/").replace(/\/$/, "") || "/";
  const big = pathname === "/";
  return (
    <>
      <div className="topnav">
        <p className="status">
          {status ? <Link href={`/reports/${status.date}`}>{status.label}</Link> : "No report has been published yet."}
        </p>
        <nav aria-label="Sections">
          <ul>
            {PRIMARY_NAV.map((item) => (
              <li key={item.href}>
                <Link href={item.href} aria-current={isCurrent(pathname, item.href) ? "page" : undefined}>{item.label}</Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>
      <header className={big ? "plate" : "plate small"}>
        <Link className="name toner" href="/" aria-label="ARI3LLA INDEX, front page">ARI3LLA INDEX</Link>
      </header>
    </>
  );
}
