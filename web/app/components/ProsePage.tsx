// Plain text pages (privacy, terms, accessibility): the About template, one column of text.

import { Folio } from "./Chrome";

export type ProseSection = { title: string; body: React.ReactNode[] };

function slug(text: string): string {
  return text.replace(/\W+/g, "-").toLowerCase();
}

export default function ProsePage({ title, updated, sections }: { title: string; updated: string; sections: ProseSection[] }) {
  return (
    <main id="main-content">
      <Folio left={title} right={<>Last updated {updated}</>} />
      <h1 className="hed md toner">{title}</h1>
      <div className="prose">
        {sections.map((s) => (
          <section key={s.title} aria-labelledby={`h-${slug(s.title)}`}>
            <h2 id={`h-${slug(s.title)}`}>{s.title}</h2>
            {s.body.map((p, i) => <p key={i}>{p}</p>)}
          </section>
        ))}
      </div>
    </main>
  );
}
