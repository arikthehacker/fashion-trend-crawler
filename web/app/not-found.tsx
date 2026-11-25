// not-found.tsx
// Custom 404 for the App Router (convention: app/not-found.tsx). The layout
// renders the header and footer; this page states the fact and offers routes back.

import type { Metadata } from "next";
import Link from "next/link";
import { Folio } from "./components/Chrome";

export const metadata: Metadata = {
  title: "Page not found",
  robots: { index: false },
};

export default function NotFound() {
  return (
    <main id="main-content">
      <Folio h1 left="Page not found" />
      <p className="lede-intro">This page does not exist or has moved.</p>
      <nav className="inside" aria-label="Places to go instead">
        <b>Instead</b>
        <Link href="/">The latest report</Link>
        <Link href="/archive">Back issues</Link>
        <Link href="/search">Search</Link>
      </nav>
    </main>
  );
}
