// Section tabs shared by every ARI3 notebook page. A server component: each page
// says which tab it is, so the static export needs no client code for this.

import Link from "next/link";

const TABS = [
  { href: "/ari3", label: "Overview" },
  { href: "/ari3/evaluation", label: "Evaluation" },
  { href: "/ari3/claims", label: "Claims" },
  { href: "/ari3/models", label: "Model cards" },
  { href: "/ari3/data", label: "Dataset cards" },
  { href: "/ari3/decisions", label: "Decisions" },
  { href: "/ari3/timeline", label: "Timeline" },
  { href: "/ari3/philosophy", label: "Philosophy" },
] as const;

export type Ari3Tab = (typeof TABS)[number]["href"];

/** `current` is the tab for this page. Experiment entries pass none, since no tab is that page. */
export default function Ari3Nav({ current }: { current?: Ari3Tab }) {
  return (
    <nav aria-label="ARI3 sections">
      <ul className="tabs">
        {TABS.map((t) => (
          <li key={t.href}>
            <Link href={t.href} aria-current={current === t.href ? "page" : undefined}>{t.label}</Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
