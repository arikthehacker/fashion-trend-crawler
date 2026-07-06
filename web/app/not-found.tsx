// not-found.tsx
// Custom 404 for the App Router (convention: app/not-found.tsx). Without this file
// Next.js renders its generic unstyled default — off-brand, no nav, no route back
// into the archive. Voice per doc section 2: no hype, plain statement of fact.

import Link from "next/link";

export const metadata = {
  title: "Not Found: ARI3LLA INDEX",
};

export default function NotFound() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background: "var(--white)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        padding: "4rem 2rem",
      }}
    >
      <h1
        style={{
          fontFamily: "var(--font-instrument)",
          fontSize: "clamp(2.5rem, 8vw, 5rem)",
          fontWeight: "400",
          lineHeight: "0.9",
          letterSpacing: "-0.03em",
          color: "var(--black)",
        }}
      >
        404
      </h1>

      <p
        style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "0.85rem",
          letterSpacing: "0.15em",
          textTransform: "uppercase",
          color: "var(--black)",
          marginTop: "1.5rem",
        }}
      >
        Page Not Found
      </p>

      <p
        style={{
          fontFamily: "var(--font-franklin)",
          fontSize: "1rem",
          lineHeight: "1.7",
          color: "var(--gray)",
          maxWidth: "480px",
          margin: "1.5rem auto 0",
        }}
      >
        No record exists at this address. It may have been mistyped, or the report it
        pointed to has not been archived.
      </p>

      <nav
        aria-label="Site sections"
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          gap: "1.5rem",
          marginTop: "2.5rem",
        }}
      >
        {[
          { href: "/", label: "Home" },
          { href: "/archive", label: "Archive" },
          { href: "/search", label: "Search" },
          { href: "/about", label: "About" },
        ].map((item) => (
          <Link
            key={item.href}
            href={item.href}
            style={{
              fontFamily: "var(--font-franklin)",
              fontSize: "0.7rem",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: "var(--black)",
              textDecoration: "underline",
              textUnderlineOffset: "3px",
              display: "inline-block",
              padding: "0.65rem 0",
            }}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </main>
  );
}
