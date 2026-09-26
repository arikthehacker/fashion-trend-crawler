"use client";
// Section tabs shared by every ARI3 notebook page, with a back link on inner pages.

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/ari3", label: "Overview" },
  { href: "/ari3/evaluation", label: "Evaluation" },
  { href: "/ari3/models", label: "Model cards" },
  { href: "/ari3/data", label: "Dataset cards" },
  { href: "/ari3/decisions", label: "Decisions" },
  { href: "/ari3/timeline", label: "Timeline" },
  { href: "/ari3/philosophy", label: "Philosophy" },
];

export default function Ari3Nav() {
  const path = (usePathname() || "/ari3").replace(/\/$/, "").replace(/\.html$/, "");
  const isExperiment = /^\/ari3\/exp-\d+/.test(path);
  const current = isExperiment ? "/ari3" : path;
  return (
    <>
      {path !== "/ari3" && (
        <Link href={isExperiment ? "/ari3#h-experiment-registry" : "/ari3"} className="ari3-back">
          ← {isExperiment ? "All experiments" : "ARI3 overview"}
        </Link>
      )}
      <nav aria-label="ARI3 sections" className="ari3-tabs">
        {TABS.map((t) => (
          <Link key={t.href} href={t.href} aria-current={current === t.href ? "page" : undefined}>
            {t.label}
          </Link>
        ))}
      </nav>
    </>
  );
}
