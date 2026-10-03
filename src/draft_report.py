"""Deterministic report drafter: item store -> style filter -> lexicon mentions -> candidate
signals with evidence -> a draft report for the editor.

It writes no interpretive prose, calls no model, and never writes to data/reports/ (the
published archive) or to the item store. The editor writes every prose field and every
human_editor_note. Owner decisions applied (site update plan, 2026-10-02):
  Q18  only confident {yes} prediction sets count as style
  Q20  software drafts evidence only, the editor writes the prose
  Q22  terms flagged for a sense check stay out of every count (decision 0009)
  Q24  the limitations draft states the EXP-003A result and the corpus composition

Candidate rule (draft-report-v1): a lexicon term without a sense-check flag that appears in
at least MIN_ITEMS style-positive items from at least MIN_OUTLETS distinct outlets in the
window. Terms below the rule are listed for the editor, not dropped silently.

usage:
  python src/draft_report.py --start 2026-09-28 --end 2026-10-04
      [--out data/store/drafts/2026-10-04.draft.json] [--review PATH.md]
"""

import argparse
import collections
import json
import os
import sys
from datetime import datetime, timezone

from item_store import ROOT

DRAFTER_VERSION = "draft-report-v1"
STYLE_MODEL = "ari3-v0.0.2"
STYLE_TASK = "is_style_signal"
EXTRACTOR = "lexicon-match-v1"
CONFIDENT_STYLE = ["yes"]
MIN_ITEMS = 2
MIN_OUTLETS = 2
DRAFT_DIR = os.path.join(ROOT, "data", "store", "drafts")
EXP003A = {"accuracy": 0.833, "criterion": 0.85, "n": 150, "artifact": "models/ari3-v0.0.3/exp003a/result.json",
           "claim": "C-0012"}

ITEM_SQL = """
SELECT i.item_id, i.url, i.title, i.published_at, i.fetched_at, i.first_seen_at, i.first_seen_basis, i.lang,
       o.domain, coalesce(s.sector_id, 'unclear'), coalesce(s.coarse_group, 'unclear'), i.content_hash
FROM items i
JOIN outlets o ON o.outlet_id = i.outlet_id
LEFT JOIN outlet_sector_history h ON h.outlet_id = i.outlet_id
     AND h.valid_from <= substr(i.published_at, 1, 10)
     AND (h.valid_to IS NULL OR substr(i.published_at, 1, 10) < h.valid_to)
LEFT JOIN sectors s ON s.sector_id = h.sector_id
WHERE i.published_at >= ? AND i.published_at < ? AND i.syndicated_of IS NULL
ORDER BY i.item_id"""


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_window(con, start, end):
    from lexicon import window_bounds
    lo, hi = window_bounds(start, end)
    items = {}
    for r in con.execute(ITEM_SQL, (lo, hi)):
        items[r[0]] = {"item_id": r[0], "url": r[1], "title": r[2] or "", "published_at": r[3], "retrieved_at": r[4],
                       "first_seen_at": r[5], "first_seen_basis": r[6], "lang": r[7] or "unknown",
                       "outlet_domain": r[8], "sector": r[9], "sector_group": r[10], "content_hash": r[11]}
    if not items:
        return items, {}
    marks = ",".join("?" * len(items))
    preds = {}
    for item_id, cset, p, created in con.execute(
            f"""SELECT item_id, conformal_set, calibrated_probability, created_at FROM label_predictions
                WHERE task=? AND model_version=? AND item_id IN ({marks}) ORDER BY created_at""",
            (STYLE_TASK, STYLE_MODEL, *items)):
        preds[item_id] = {"style_set": json.loads(cset), "p_style": round(p, 4) if p is not None else None,
                          "scored_at": created}  # latest prediction wins (one per item today)
    for i, it in items.items():
        it.update(preds.get(i, {"style_set": None, "p_style": None, "scored_at": None}))
        it["style_positive"] = it["style_set"] == CONFIDENT_STYLE
        it["terms"], it["excluded_terms"] = [], []
    mentions = collections.defaultdict(list)
    for item_id, term_id, canonical, signal_type, sense in con.execute(
            f"""SELECT m.item_id, t.term_id, t.canonical, t.signal_type, r.needs_sense_check
                FROM mentions m JOIN terms t ON t.term_id = m.term_id JOIN term_rules r ON r.term_id = t.term_id
                WHERE m.extractor_version=? AND t.merged_into IS NULL AND m.item_id IN ({marks})
                ORDER BY m.item_id, t.term_id""", (EXTRACTOR, *items)):
        key = "excluded_terms" if sense else "terms"
        if term_id not in items[item_id][key]:
            items[item_id][key].append(term_id)
        mentions[term_id].append(item_id)
    terms = {r[0]: {"term_id": r[0], "canonical": r[1], "signal_type": r[2], "needs_sense_check": bool(r[3])}
             for r in con.execute("SELECT t.term_id, t.canonical, t.signal_type, r.needs_sense_check "
                                  "FROM terms t JOIN term_rules r USING (term_id) WHERE t.merged_into IS NULL")}
    return items, terms


def term_table(items, terms):
    rows = []
    for tid, t in sorted(terms.items()):
        hits = [it for it in items.values() if tid in it["terms"] or tid in it["excluded_terms"]]
        if not hits:
            continue
        pos = [it for it in hits if it["style_positive"]]
        rows.append({"term_id": tid, "canonical": t["canonical"], "signal_type": t["signal_type"],
                     "excluded_by_sense_check": t["needs_sense_check"],
                     "items_any_prediction": len(hits),
                     "style_positive_items": len(pos),
                     "not_sure_items": sum(1 for it in hits if it["style_set"] == ["yes", "no"]),
                     "not_style_items": sum(1 for it in hits if it["style_set"] == ["no"]),
                     "unscored_items": sum(1 for it in hits if it["style_set"] is None),
                     "style_positive_outlets": len({it["outlet_domain"] for it in pos}),
                     "meets_candidate_rule": (not t["needs_sense_check"] and len(pos) >= MIN_ITEMS
                                              and len({it["outlet_domain"] for it in pos}) >= MIN_OUTLETS)})
    return sorted(rows, key=lambda r: (-r["style_positive_items"], r["term_id"]))


EVIDENCE_KEYS = ["item_id", "url", "title", "outlet_domain", "sector", "sector_group", "published_at", "retrieved_at",
                 "first_seen_at", "first_seen_basis", "content_hash", "lang", "style_set", "p_style", "terms"]


def candidate_signals(items, terms, table):
    from report_schema import derive_confidence
    out = []
    for row in table:
        if not row["meets_candidate_rule"]:
            continue
        tid = row["term_id"]
        ev = sorted((it for it in items.values() if it["style_positive"] and tid in it["terms"]),
                    key=lambda it: (it["published_at"], it["item_id"]))
        sectors = sorted({it["sector"] for it in ev})
        outlets = sorted({it["outlet_domain"] for it in ev})
        signal = {"signal_id": tid, "name": terms[tid]["canonical"], "type": terms[tid]["signal_type"],
                  "source_sectors": sectors, "source_domains": outlets, "source_corroboration_count": len(outlets),
                  "confidence": "", "confidence_source": "derived", "volatility": "", "origin_classification": "unclear",
                  "evidence": "", "index_note": "", "human_editor_note": "",
                  "evidence_items": [{k: it[k] for k in EVIDENCE_KEYS} for it in ev]}
        signal["confidence"] = derive_confidence(signal)
        groups = sorted({it["sector_group"] for it in ev})
        signal["draft_audit"] = {
            "why_surfaced": f"{len(ev)} style-positive items from {len(outlets)} outlets mention the term "
                            f"(rule: at least {MIN_ITEMS} items from at least {MIN_OUTLETS} outlets)",
            "dates": sorted({it["published_at"][:10] for it in ev}),
            "items_by_sector": dict(collections.Counter(it["sector"] for it in ev).most_common()),
            "sector_groups": groups,
            "cross_sector": len(sectors) > 1, "cross_sector_group": len(groups) > 1,
            "reconstructed_first_seen_items": sum(it["first_seen_basis"] == "reconstructed" for it in ev),
            "not_sure_items_with_term": sorted(it["item_id"] for it in items.values()
                                               if tid in it["terms"] and it["style_set"] == ["yes", "no"]),
            "not_style_items_with_term": sorted(it["item_id"] for it in items.values()
                                                if tid in it["terms"] and it["style_set"] == ["no"]),
            "max_items_from_one_outlet": max(collections.Counter(it["outlet_domain"] for it in ev).values())}
        out.append(signal)
    return out


def composition(items):
    n = len(items)
    pos = [it for it in items.values() if it["style_positive"]]
    share = lambda xs, key: {k: {"items": v, "share": round(v / len(xs), 4)}
                             for k, v in collections.Counter(it[key] for it in xs).most_common()} if xs else {}
    return {"items": n, "style_positive_items": len(pos),
            "prediction_sets": dict(collections.Counter(json.dumps(it["style_set"]) for it in items.values())),
            "sector": share(list(items.values()), "sector"), "sector_group": share(list(items.values()), "sector_group"),
            "style_positive_sector": share(pos, "sector"),
            "first_seen_basis": dict(collections.Counter(it["first_seen_basis"] for it in items.values())),
            "outlets": len({it["outlet_domain"] for it in items.values()}),
            "languages": dict(collections.Counter(it["lang"] for it in items.values()).most_common())}


def limitations_draft(comp, corpus_editorial_share, window_complete, as_of):
    ed = comp["sector"].get("editorial", {}).get("share", 0)
    grp = comp["sector_group"].get("editorial", {}).get("share", 0)
    social = comp["sector"].get("social", {}).get("items", 0)
    resale = comp["sector"].get("resale", {}).get("items", 0)
    n = comp["items"]
    unsure = comp["prediction_sets"].get(json.dumps(["yes", "no"]), 0)
    lims = [
        f"Items are counted as style only when the ARI3 style classifier (frozen v0.0.2) gives a confident yes. "
        f"On a {EXP003A['n']}-item prospective holdout of articles published after the classifier was frozen, its "
        f"accuracy was {EXP003A['accuracy']}, below its pre-registered {EXP003A['criterion']} criterion (EXP-003A, "
        f"H2 not supported). The editor reviews every evidence item used in this report.",
        f"In this window, {unsure:,} of {n:,} items ({unsure / n if n else 0:.1%}) received a not-sure prediction set "
        f"and were excluded from style-positive counts.",
        f"In this window, {ed:.1%} of collected items came from the editorial sector and {grp:.1%} from the "
        f"editorial group (editorial, trade intelligence and independent criticism). The stored corpus as a whole "
        f"is {corpus_editorial_share:.1%} editorial sector.",
        f"The window has {social} items from social platforms, which are not collected, and {resale} from resale "
        f"sources. The report describes the language of the collected sources, not style culture, fashion "
        f"consumers or the public at large.",
        "Signal interpretation and evidence review are done by one editor.",
        "ARI3 stores each item's headline and feed excerpt, not the full article.",
        f"{comp['first_seen_basis'].get('reconstructed', 0)} of the window's {comp['items']} items were stored before "
        f"2026-09-30, so their first-seen times are reconstructed from earlier records, not recorded as they happened.",
        "Seven ambiguous lexicon terms (western, brat, demure, lace, bow, sustainable, glamour) are left out of every "
        "count until their uses are checked one by one.",
    ]
    if not window_complete:
        lims.append(f"DRAFT ONLY: the collection window had not ended when this draft was made ({as_of}). "
                    f"Regenerate the draft after the window closes.")
    return lims


def corpus_editorial_share(con):
    from rag_corpus import ITEM_JOINS
    n = con.execute("SELECT count(*) FROM items").fetchone()[0]
    ed = con.execute(f"SELECT count(*) {ITEM_JOINS} WHERE s.sector_id = 'editorial'").fetchone()[0]
    return ed / n if n else 0.0


def build_draft(con, start, end, now=None):
    now = now or _now()
    items, terms = load_window(con, start, end)
    table = term_table(items, terms)
    signals = candidate_signals(items, terms, table)
    comp = composition(items)
    from lexicon import window_bounds
    complete = now >= window_bounds(start, end)[1]
    unscored = sorted(i for i, it in items.items() if it["style_set"] is None)
    report = {
        "report_date": end, "collection_window": {"start": start, "end": end},
        "sources_scanned": comp["outlets"], "items_collected": comp["items"],
        "source_sector_breakdown": {k: v["items"] for k, v in comp["sector"].items()},
        "executive_summary": "", "top_signals": signals,
        "repeated_keywords": [], "garments": [], "silhouettes": [], "materials": [], "colors": [],
        "aesthetic_terms": [], "cultural_references": [],
        "limitations": limitations_draft(comp, corpus_editorial_share(con), complete, now),
        "archive_tags": [], "collection_status": "normal" if signals else "thin", "review_status": "draft",
        "draft_meta": {
            "drafter": DRAFTER_VERSION, "generated_at": now, "window_complete": complete,
            "style_model": STYLE_MODEL, "style_rule": "confident {yes} prediction sets only (owner decision Q18)",
            "extractor": EXTRACTOR, "lexicon_version": 1,
            "candidate_rule": {"min_style_positive_items": MIN_ITEMS, "min_outlets": MIN_OUTLETS},
            "excluded_terms": sorted(t for t, v in terms.items() if v["needs_sense_check"]),
            "composition": comp, "unscored_items": unscored, "term_table": table,
            "exp003a": EXP003A,
            "prose_fields_left_for_editor": ["executive_summary", "top_signals[].evidence", "top_signals[].index_note",
                                              "top_signals[].human_editor_note", "top_signals[].volatility",
                                              "ai_assistance"]},
    }
    return report


def review_markdown(report):
    m = report["draft_meta"]
    c = m["composition"]
    out = [f"# Review package: draft report {report['collection_window']['start']} to {report['collection_window']['end']}", ""]
    out += ["**Status:** DRAFT. Not published. Nothing here is a claim until the editor approves it.", "",
            f"- Drafter `{m['drafter']}`, generated {m['generated_at']}. Window complete: **{m['window_complete']}**.",
            f"- Style rule: {m['style_rule']}. Model `{m['style_model']}`. Extractor `{m['extractor']}`, Lexicon v{m['lexicon_version']}.",
            f"- Candidate rule: a term in at least {m['candidate_rule']['min_style_positive_items']} style-positive items "
            f"from at least {m['candidate_rule']['min_outlets']} outlets. Terms held out for a sense check: "
            f"{', '.join(m['excluded_terms'])}.",
            f"- Unscored window items: {len(m['unscored_items'])}.", "",
            "## Window composition", "",
            f"{c['items']} items from {c['outlets']} outlets. Prediction sets: "
            + ", ".join(f"{k} {v}" for k, v in c["prediction_sets"].items()) + f". Style-positive: {c['style_positive_items']}.", "",
            "| Sector | Items | Share | Style-positive items |", "|---|---|---|---|"]
    for k, v in c["sector"].items():
        out.append(f"| {k} | {v['items']} | {v['share']:.1%} | {c['style_positive_sector'].get(k, {}).get('items', 0)} |")
    out += ["", "First-seen basis: " + ", ".join(f"{k} {v}" for k, v in c["first_seen_basis"].items()) + ".", ""]
    out += ["## Candidate signals", "",
            "Each candidate comes from counts only. The editor decides whether it survives, what it is called, "
            "and what (if anything) it says. Inclusion and drop decisions are left blank on purpose.", ""]
    for n, s in enumerate(report["top_signals"], 1):
        a = s["draft_audit"]
        weak = []
        if a["max_items_from_one_outlet"] * 2 > len(s["evidence_items"]):
            weak.append(f"half or more of the evidence comes from one outlet ({a['max_items_from_one_outlet']} items)")
        if not a["cross_sector"]:
            weak.append("one sector only")
        elif not a["cross_sector_group"]:
            weak.append("several sectors, but all inside one sector group")
        outside = sum(v for k, v in a["items_by_sector"].items() if k != "editorial")
        if a["cross_sector"] and outside <= 1:
            weak.append(f"only {outside} item comes from outside the editorial sector, yet the baseline rule counts the "
                        f"signal as cross-sector")
        if a["reconstructed_first_seen_items"]:
            weak.append(f"{a['reconstructed_first_seen_items']} evidence items have reconstructed first-seen times")
        if a["not_sure_items_with_term"]:
            weak.append(f"{len(a['not_sure_items_with_term'])} more items mention the term but got a not-sure set (not counted)")
        out += [f"### {n}. {s['name']} (`{s['signal_id']}`, {s['type']})", "",
                f"- Why surfaced: {a['why_surfaced']}.",
                f"- Count: {len(s['evidence_items'])} style-positive items, {s['source_corroboration_count']} outlets.",
                f"- Sectors: " + ", ".join(f"{k} {v}" for k, v in a["items_by_sector"].items())
                + f" (groups: {', '.join(a['sector_groups'])}). "
                f"Cross-sector: {'yes' if a['cross_sector'] else 'no'}.",
                f"- Dates: {', '.join(a['dates'])}.",
                f"- Baseline confidence (existing `derive_confidence` rule): {s['confidence']}.",
                f"- Weaknesses: {'; '.join(weak) if weak else 'none flagged by the drafter'}.",
                "- Editor decision: [ ] keep  [ ] drop  [ ] merge with ____", "",
                "| Item | Published | Outlet | Sector | First seen | Style set (p) | Terms | Title | URL |",
                "|---|---|---|---|---|---|---|---|---|"]
        for e in s["evidence_items"]:
            out.append(f"| {e['item_id']} | {e['published_at'][:16]} | {e['outlet_domain']} | {e['sector']} | "
                       f"{e['first_seen_basis']} | {e['style_set']} ({e['p_style']}) | {', '.join(e['terms'])} | "
                       f"{(e['title'] or '').replace('|', '/')} | {e['url']} |")
        if a["not_sure_items_with_term"] or a["not_style_items_with_term"]:
            out.append("")
            out.append(f"Not counted (audit): not-sure items {a['not_sure_items_with_term']}; "
                       f"not-style items {a['not_style_items_with_term']}.")
        out.append("")
    out += ["## Terms below the candidate rule", "",
            "| Term | Type | Style-positive items | Outlets | Not sure | Not style | Held out (sense check) |",
            "|---|---|---|---|---|---|---|"]
    for r in m["term_table"]:
        if not r["meets_candidate_rule"]:
            out.append(f"| {r['canonical']} | {r['signal_type']} | {r['style_positive_items']} | "
                       f"{r['style_positive_outlets']} | {r['not_sure_items']} | {r['not_style_items']} | "
                       f"{'yes' if r['excluded_by_sense_check'] else 'no'} |")
    out += ["", "## Limitations draft (for the editor to keep, edit or cut)", ""]
    out += [f"- {l}" for l in report["limitations"]]
    out += ["", "## Left for the editor", "",
            "- executive summary, each signal's evidence text, index note and editor note, and each signal's volatility label",
            "- `ai_assistance`: record what software or AI did for this report (nothing written yet)",
            "- which candidates survive, and the final wording", ""]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--out")
    ap.add_argument("--review")
    args = ap.parse_args(argv)
    from rag_corpus import open_corpus
    con = open_corpus()  # read-only: the drafter never writes to the store
    report = build_draft(con, args.start, args.end)
    out = args.out or os.path.join(DRAFT_DIR, f"{args.end}.draft.json")
    if os.path.abspath(out).startswith(os.path.abspath(os.path.join(ROOT, "data", "reports"))):
        print("refused: drafts never go into data/reports/ (the published archive)", file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
    if args.review:
        with open(args.review, "w", encoding="utf-8", newline="\n") as f:
            f.write(review_markdown(report))
    m = report["draft_meta"]
    print(json.dumps({"draft": out, "window_complete": m["window_complete"], "items": m["composition"]["items"],
                      "style_positive": m["composition"]["style_positive_items"],
                      "candidates": [s["signal_id"] for s in report["top_signals"]]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
