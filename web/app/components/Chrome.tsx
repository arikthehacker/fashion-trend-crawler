// Shared pieces of the photocopy edition (design/SITE_SPEC_photocopy.md).
// Pages compose these; none of them holds content of its own.

import type { ReactNode } from "react";
import type { EvidenceItem, Report } from "../../lib/reports";
import { fmtDay, longWindow, type Footnote, type NotePlace } from "../../lib/editorial";
import { EDITOR_LABEL } from "../../lib/site";

/** The rule under the nameplate: a page label on the left, a note or link on the right. */
export function Folio({ left, right, h1 = false }: { left: ReactNode; right?: ReactNode; h1?: boolean }) {
  return (
    <div className="folio">
      {h1 ? <h1 className="fl">{left}</h1> : <span><b>{left}</b></span>}
      {right ? <span>{right}</span> : <span />}
    </div>
  );
}

/** "Week of November 16 – 22, 2026", between double rules. */
export function Dateline({ report, children }: { report: Report; children?: ReactNode }) {
  return (
    <p className="dateline">
      Week of <time dateTime={`${report.collection_window.start}/${report.collection_window.end}`}>{longWindow(report)}</time>
      {children}
      {report.report_date !== report.collection_window.end ? <small>Issued {fmtDay(report.report_date, true)}</small> : null}
    </p>
  );
}

export function Byline({ children }: { children?: ReactNode }) {
  return <p className="byline">From the {EDITOR_LABEL.toLowerCase()}{children}</p>;
}

export function Mark({ n }: { n: number }) {
  return <sup className="fn"><a href={`#note-${n}`} id={`ref-${n}`} aria-label={`Note ${n}`}>†{n}</a></sup>;
}

export function Marks({ notes, place }: { notes: Footnote[]; place: NotePlace }) {
  return <>{notes.filter((x) => x.place === place).map((x) => <Mark key={x.n} n={x.n} />)}</>;
}

export function Notes({ notes, title = "Notes" }: { notes: Footnote[]; title?: string }) {
  if (!notes.length) return null;
  return (
    <section aria-labelledby="notes-h">
      <h2 className="sec" id="notes-h">{title}</h2>
      <ol className="notes">
        {notes.map((x) => (
          <li key={x.n} id={`note-${x.n}`}><b>†{x.n}</b>{x.text}<a className="back" href={`#ref-${x.n}`}>back to text</a></li>
        ))}
      </ol>
    </section>
  );
}

function Src({ it, withDate = true }: { it: EvidenceItem; withDate?: boolean }) {
  return (
    <li>
      <a href={it.url} rel="noopener">{it.title || it.url}</a>
      <span>{it.outlet_domain ?? ""}{withDate && it.published_at ? <> · <time dateTime={it.published_at.slice(0, 10)}>{fmtDay(it.published_at)}</time></> : null}</span>
    </li>
  );
}

/** The first few sources, then the rest behind "All N articles" (hidden when there is nothing more). */
export function SrcList({ items, show = 4, withDate = true }: { items: EvidenceItem[]; show?: number; withDate?: boolean }) {
  const key = (it: EvidenceItem, i: number) => `${it.item_id ?? it.url}-${i}`;
  return (
    <>
      <ul className="srcs">{items.slice(0, show).map((it, i) => <Src key={key(it, i)} it={it} withDate={withDate} />)}</ul>
      {items.length > show ? (
        <details className="more">
          <summary>All {items.length} articles</summary>
          <ul className="srcs">{items.slice(show).map((it, i) => <Src key={key(it, i)} it={it} withDate={withDate} />)}</ul>
        </details>
      ) : null}
    </>
  );
}

const STAMP_NEG = /not supported|closed|withdrawn/i;
const STAMP_SOFT = /planned|not started|historical|superseded|pending/i;
export function Stamp({ children }: { children: string }) {
  const cls = STAMP_NEG.test(children) ? "stamp neg" : STAMP_SOFT.test(children) ? "stamp soft" : "stamp";
  return <span className={cls}>{children}</span>;
}
