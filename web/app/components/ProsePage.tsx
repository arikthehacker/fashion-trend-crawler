// Shared layout for plain prose pages (privacy, terms, accessibility):
// the shared page masthead (h1 + last-updated line) and titled sections.

export type ProseSection = { title: string; body: React.ReactNode[] };

function slug(text: string): string {
  return text.replace(/\W+/g, "-").toLowerCase();
}

export default function ProsePage({ title, updated, sections }: { title: string; updated: string; sections: ProseSection[] }) {
  return (
    <main id="main-content" className="prose-page">
      <header className="page-masthead">
        <h1 className="page-title">{title}</h1>
        <p className="page-intro">Last updated {updated}</p>
      </header>
      <div className="prose-body">
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
