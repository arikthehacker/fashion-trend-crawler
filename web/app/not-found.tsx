// not-found.tsx
// Custom 404 for the App Router (convention: app/not-found.tsx). Without this file
// Next.js renders its generic unstyled default — off-brand, no nav, no route back
// into the archive. Voice per doc section 2: no hype, plain statement of fact.

import Link from "next/link";

export const metadata = {
  title: "Page not found",
  robots: { index: false },
};

export default function NotFound() {
  return (
    <main id="main-content" style={{ flex: 1, width: "100%" }}>
      <header className="page-masthead">
        <p className="page-eyebrow">Page not found</p>
        <h1 className="page-title">404</h1>
        <p className="page-intro">
          No record exists at this address. It may have been mistyped, or the report it
          pointed to has not been archived.
        </p>
        <p className="page-intro">
          <Link href="/" style={{ color: "var(--black)", textDecoration: "underline", textUnderlineOffset: "3px" }}>
            Return to the index
          </Link>
        </p>
      </header>
    </main>
  );
}
