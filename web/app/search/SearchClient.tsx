"use client";
// Search over every signal and every headline behind it. Loads /data/search.json
// (built from the reports) on first use; reads and writes ?q= so results can be linked.

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

type Week = { d: string; w: string; s: { id: string; n: string; t: string; a: [string, string, string, string][] }[] };

function fmt(iso: string) {
  return new Date(`${iso}T00:00:00Z`).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", timeZone: "UTC" });
}

export default function SearchClient() {
  const [q, setQ] = useState("");
  const [data, setData] = useState<Week[] | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const initial = new URLSearchParams(window.location.search).get("q") ?? "";
    fetch("/data/search.json")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d: Week[]) => { setData(d); if (initial) setQ((cur) => cur || initial); })
      .catch(() => { setFailed(true); if (initial) setQ((cur) => cur || initial); });
  }, []);

  useEffect(() => {
    const url = new URL(window.location.href);
    if (q.trim()) url.searchParams.set("q", q.trim()); else url.searchParams.delete("q");
    window.history.replaceState(null, "", url.toString());
  }, [q]);

  const results = useMemo(() => {
    const Q = q.trim().toLowerCase();
    if (!data || Q.length < 2) return null;
    const out: { key: string; signal?: { id: string; n: string; w: string }; item?: { t: string; o: string; d: string; u: string; sid: string; sn: string } }[] = [];
    const seen = new Set<string>();
    for (const wk of data) for (const s of wk.s) {
      if (s.n.toLowerCase().includes(Q) && !seen.has(s.id)) { seen.add(s.id); out.push({ key: `s-${s.id}`, signal: { id: s.id, n: s.n, w: wk.w } }); }
      for (const [t, o, d, u] of s.a) if (t.toLowerCase().includes(Q) || o.toLowerCase().includes(Q)) out.push({ key: `i-${wk.d}-${s.id}-${u}`, item: { t, o, d, u, sid: s.id, sn: s.n } });
    }
    return out;
  }, [data, q]);

  return (
    <div className="search">
      <label htmlFor="q">Search signals and headlines</label>
      <input id="q" type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Try “trench” or “suede”" autoComplete="off" enterKeyHint="search" />
      <div className="res" aria-live="polite">
        {failed ? <p className="note">The search index could not be loaded. Every report is listed in <Link href="/archive">Back issues</Link>.</p> : null}
        {!failed && !data && q.trim().length >= 2 ? <p className="note">Loading the index…</p> : null}
        {results ? (
          results.length ? (
            <>
              <p className="note">{results.length} result{results.length === 1 ? "" : "s"}{results.length > 80 ? ", showing the first 80" : ""}</p>
              <ul>
                {results.slice(0, 80).map((r) => (
                  <li key={r.key}>
                    {r.signal ? (
                      <><Link href={`/signals/${r.signal.id}`}>{r.signal.n}</Link> <span className="note">signal · latest week of {r.signal.w}</span></>
                    ) : r.item ? (
                      <><a href={r.item.u} rel="noopener">{r.item.t || r.item.u}</a><br /><span className="note">{r.item.o} · {fmt(r.item.d)} · in <Link href={`/signals/${r.item.sid}`}>{r.item.sn}</Link></span></>
                    ) : null}
                  </li>
                ))}
              </ul>
            </>
          ) : <p className="note">Nothing in the archive matches “{q.trim()}”.</p>
        ) : null}
      </div>
    </div>
  );
}
