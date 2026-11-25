// Shared pieces of the ARI3 notebook pages, photocopy edition (site-mock.html, a3chrome and friends).

import { Fragment, type ReactNode } from "react";
import { Folio } from "../components/Chrome";
import { fmtDay } from "../../lib/editorial";
import type { Metric } from "../../lib/ari3";
import Ari3Nav, { type Ari3Tab } from "./Ari3Nav";

/** main, the folio rule, then the section tabs. The folio carries the page's h1 unless the page has its own. */
export function Ari3Page({ label, current, folioH1 = true, children }: { label: string; current?: Ari3Tab; folioH1?: boolean; children: ReactNode }) {
  return (
    <main id="main-content">
      <Folio h1={folioH1} left={`ARI3 · ${label}`} right="The model behind the index" />
      <Ari3Nav current={current} />
      {children}
    </main>
  );
}

/** Text whose `backticked` spans are file names or hashes, rendered as code. */
export function Tx({ text }: { text: string }) {
  return <>{text.split("`").map((part, i) => (i % 2 ? <code key={i}>{part}</code> : <Fragment key={i}>{part}</Fragment>))}</>;
}

export function Bul({ items }: { items: string[] }) {
  return <ul className="bul">{items.map((x, i) => <li key={i}><Tx text={x} /></li>)}</ul>;
}

/** An h2.sec with a bulleted list, or nothing when the list is empty. */
export function ListSection({ title, items }: { title: string; items?: string[] }) {
  if (!items || !items.length) return null;
  return (
    <>
      <h2 className="sec">{title}</h2>
      <Bul items={items} />
    </>
  );
}

/** "Sep 23, 2026" for an ISO date; any other text (such as "Standing rule") as written. */
export function day(s: string) {
  return /^\d{4}-\d{2}-\d{2}/.test(s) ? fmtDay(s, true) : s;
}

/** Proportions and scores to three decimals; counts as whole numbers. */
export function fmtVal(v: number, f: Metric["format"]) {
  return (f === "pct" || !Number.isInteger(v)) && Math.abs(v) <= 1 ? v.toFixed(3) : v.toLocaleString("en-US");
}
