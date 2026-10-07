"""Finish a prepared report from the editor's decisions in ARI3 Review.

  apply         the editor's keep / drop / merge / label / prune / duplicate decisions -> the working report
                (merged evidence deduplicated, exact mirrors collapsed, counts recomputed, rule checked)
  text          put drafted evidence text, index notes, the summary and the copyedited editor notes into
                the working report, after checking every count and the voice rules; nothing structural moves
  approval      build the approval deck for ARI3 Review from the working report
  gate          every structural, evidence and publish-readiness check, once
  publish-file  write data/reports/<date>.json once the editor has approved every card (no commit, no push)
  status        where a report stands

Frozen inputs are only read: the prepared draft, the evidence review snapshot and the decision log.
Software never invents a decision or an editor note. Committing and pushing stay with the editor's word.

usage: python src/report_finalize.py <command> <report_date> [file] [--groups FILE] [--base DIR]
"""

import argparse
import collections
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

import report_review as rr

MIN_ITEMS, MIN_OUTLETS = 2, 2
AI_HEAD = ("ARI3’s deterministic pipeline surfaced candidate signals and bound the report to a frozen evidence snapshot. An AI "
           "assistant drafted the executive summary, evidence text, and index notes using only the locked report evidence, including "
           "translations of non-English headlines. ")
AI_DRAFT = AI_HEAD + ("The editor selected and merged signals, set labels and confidence overrides, pruned evidence, and is responsible "
                      "for final review, editor notes, and approval.")
AI_FINAL = AI_HEAD + ("The editor selected and merged signals, set labels and confidence overrides, pruned evidence, reviewed the "
                      "drafted text, wrote the editor notes, and approved the final report.")
DEDUP_LIMITATION = ("Exact mirrors and syndicated, translated or lightly re-edited versions of the same publication across publisher "
                    "domains are collapsed to one report evidence unit. The frozen source snapshot retains the raw records.")
BANNED = ["—", ";", "must-have", "obsessed", "everyone is wearing", "this season is all about", "declared", "revealed", "proves",
          "rising", "surging", "taking over", "next big", "consumers are", "moving toward", "discovered"]
FIRST_PERSON = re.compile(r"\b(I|I'm|I've|I'd|me|my|myself|mine|we|our|us)\b")


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write(path, obj, indent=1):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=indent, ensure_ascii=False)
        f.write("\n")


def sha_obj(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _recount(signal):
    from report_schema import derive_confidence
    ev = signal["evidence_items"]
    signal["source_sectors"] = sorted({e["sector"] for e in ev})
    signal["source_domains"] = sorted({e["outlet_domain"] for e in ev})
    signal["source_corroboration_count"] = len(signal["source_domains"])
    if signal["confidence_source"] == "derived":
        signal["confidence"] = derive_confidence({**signal, "confidence": ""})
    signal["draft_audit"].update({
        "dates": sorted({e["published_at"][:10] for e in ev}),
        "items_by_sector": dict(collections.Counter(e["sector"] for e in ev).most_common()),
        "sector_groups": sorted({e["sector_group"] for e in ev}),
        "cross_sector": len(signal["source_sectors"]) > 1, "cross_sector_group": len({e["sector_group"] for e in ev}) > 1,
        "reconstructed_first_seen_items": sum(e["first_seen_basis"] == "reconstructed" for e in ev),
        "max_items_from_one_outlet": max(collections.Counter(e["outlet_domain"] for e in ev).values()) if ev else 0})


def duplicate_groups(queue, decisions, audit, records, extra=None):
    """Every group of records that counts as one evidence unit, with the order in which to keep them.
    Exact mirrors: the record on the alphabetically first domain (so the mirror domain adds no outlet).
    Editions and translations (the editor's ruling): the earliest published record, lowest item ID on a tie."""
    groups = []
    for g in audit.get("exact", []):
        ids = [i["item_id"] for i in g["items"]]
        groups.append({"rule": "exact mirror", "why": g["why"],
                       "order": sorted(ids, key=lambda i: (records[i]["outlet_domain"], i))})
    possible = {c["card_id"]: c for c in queue["cards"] if c["kind"] == "duplicate"}
    chosen = [(c["why"], [i["item_id"] for i in c["items"]]) for cid, c in possible.items() if decisions.get(cid, {}).get("collapse")]
    chosen += [(g.get("why", "the same editorial story on another edition"), list(g["items"])) for g in (extra or [])]
    for why, ids in chosen:
        missing = [i for i in ids if i not in records]
        if missing:
            raise ValueError(f"duplicate group names items that are not candidate evidence: {missing}")
        groups.append({"rule": "same editorial story", "why": why, "order": sorted(ids, key=lambda i: (records[i]["published_at"], i))})
    return groups


def apply_decisions(draft, queue, decisions, audit, extra_groups=None, draft_sha=None):
    """The working report. Raises ValueError listing every problem if the decisions are incomplete."""
    cards = {c["signal_id"]: c for c in queue["cards"] if c["kind"] == "signal"}
    by = {s["signal_id"]: s for s in draft["top_signals"]}
    problems = []
    if list(cards) != list(by):
        raise ValueError("the decision deck was not built from this draft")
    choice = {}
    for sid, card in cards.items():
        p = decisions.get(card["card_id"])
        if p is None:
            problems.append(f"{sid}: no decision yet")
            continue
        problems += [f"{sid}: {e}" for e in rr.payload_errors(queue, card, p)]
        choice[sid] = p
    for cid in (c["card_id"] for c in queue["cards"] if c["kind"] == "duplicate"):
        if cid not in decisions:
            problems.append(f"{cid}: no decision yet")
    kept = [sid for sid in by if choice.get(sid, {}).get("decision") == "keep"]
    for sid, p in choice.items():
        if p["decision"] == "merge" and p.get("merge_into") not in kept:
            problems.append(f"{sid}: merges into {p.get('merge_into')!r}, which is not kept")
    if problems:
        raise ValueError("\n".join(problems))

    records = {e["item_id"]: e for s in draft["top_signals"] for e in s["evidence_items"]}
    groups = duplicate_groups(queue, decisions, audit, records, extra_groups)
    report = json.loads(json.dumps(draft))
    signals, collapsed_any = [], False
    for sid in kept:
        p, s = choice[sid], json.loads(json.dumps(by[sid]))
        pool = {e["item_id"]: e for e in s["evidence_items"]}
        merged, removed = {}, set(p.get("remove_item_ids") or [])
        for other, q in choice.items():
            if q["decision"] == "merge" and q["merge_into"] == sid:
                ids = [e["item_id"] for e in by[other]["evidence_items"]]
                merged[other] = {"items": len(ids), "already_in_signal": sorted(i for i in ids if i in pool),
                                 "added": sum(1 for i in ids if i not in pool)}
                for e in by[other]["evidence_items"]:
                    pool.setdefault(e["item_id"], json.loads(json.dumps(e)))
                removed |= set(q.get("remove_item_ids") or [])
        for i in removed:
            pool.pop(i, None)
        collapsed = []
        for g in groups:
            present = [i for i in g["order"] if i in pool]
            for i in present[1:]:
                collapsed.append({"collapsed_item_id": i, "collapsed_domain": pool[i]["outlet_domain"], "collapsed_url": pool[i]["url"],
                                  "retained_item_id": present[0], "retained_domain": pool[present[0]]["outlet_domain"],
                                  "rule": g["rule"], "basis": g["why"]})
                pool.pop(i)
        collapsed_any |= bool(collapsed)
        s["evidence_items"] = sorted(pool.values(), key=lambda e: (e["published_at"], e["item_id"]))
        s["name"] = (p.get("name") or "").strip() or s["name"]
        s["type"] = p.get("type") or s["type"]
        s["volatility"] = p["volatility"]
        s["origin_classification"] = p.get("origin") or "unclear"
        s["confidence_source"] = "manual" if p.get("confidence") else "derived"
        if p.get("confidence"):
            s["confidence"] = p["confidence"]
        s["evidence"], s["index_note"], s["human_editor_note"] = "", "", ""
        _recount(s)
        s["draft_audit"].update({"merged_terms": merged, "removed_by_editor": sorted(removed), "collapsed_duplicates": collapsed})
        if len(s["evidence_items"]) < MIN_ITEMS or s["source_corroboration_count"] < MIN_OUTLETS:
            problems.append(f"{sid}: after the decisions it has {len(s['evidence_items'])} items from {s['source_corroboration_count']} "
                            f"outlets, below the report rule ({MIN_ITEMS} items from {MIN_OUTLETS} outlets). Decide again.")
        signals.append(s)
    if problems:
        raise ValueError("\n".join(problems))
    report["top_signals"] = signals
    report["executive_summary"] = ""
    report["review_status"] = "draft"
    report["collection_status"] = "normal" if signals else "thin"
    report["limitations"] = list(draft["limitations"]) + ([DEDUP_LIMITATION] if collapsed_any else [])
    report["ai_assistance"] = AI_DRAFT
    report["draft_meta"]["editor_decisions"] = {
        "decided_by": "the editor, in ARI3 Review", "applied_at": _now(), "applied_to_draft_sha256": draft_sha,
        "applied_by": "software, structure only: no prose and no editor note written",
        "decisions": {sid: {k: v for k, v in p.items() if k != "thoughts" and v not in ("", None, [])} for sid, p in choice.items()},
        "editor_thoughts": {**{sid: p.get("thoughts", "") for sid, p in choice.items() if (p.get("thoughts") or "").strip()},
                            **({"_report": decisions["report"]["thoughts"]} if (decisions.get("report") or {}).get("thoughts") else {})},
        "duplicate_groups": groups, "revisions": []}
    return report


# ---------- text ----------

def structure(report):
    """Everything except the prose fields and the revision log."""
    x = json.loads(json.dumps(report))
    x["executive_summary"] = ""
    for s in x["top_signals"]:
        s["evidence"], s["index_note"], s["human_editor_note"] = "", "", ""
    x["draft_meta"]["editor_decisions"].pop("revisions", None)
    x.pop("ai_assistance", None)
    return x


def text_of(report):
    return {"executive_summary": report["executive_summary"],
            "signals": {s["signal_id"]: {k: s[k] for k in ("evidence", "index_note", "human_editor_note")} for s in report["top_signals"]}}


def text_errors(report, text):
    """Counts and voice. An empty list means the text can go in."""
    errors = []
    counts = {s["signal_id"]: (len(s["evidence_items"]), s["source_corroboration_count"]) for s in report["top_signals"]}
    summary = text.get("executive_summary") or ""
    if not summary.strip():
        errors.append("executive_summary is empty")
    if set(text.get("signals") or {}) != set(counts):
        errors.append(f"text must cover exactly these signals: {sorted(counts)}")
        return errors
    for sid, (n, o) in counts.items():
        t = text["signals"][sid]
        for field in ("evidence", "index_note", "human_editor_note"):
            if not (t.get(field) or "").strip():
                errors.append(f"{sid}.{field} is empty")
        if f"{n} items from {o} outlets" not in (t.get("index_note") or ""):
            errors.append(f"{sid}.index_note must state the exact count: '{n} items from {o} outlets'")
        for field in ("evidence", "index_note"):
            for a, b in re.findall(r"(\d[\d,]*) items from (\d+) outlets", t.get(field) or ""):
                if (int(a.replace(",", "")), int(b)) != (n, o):
                    errors.append(f"{sid}.{field} states {a} items from {b} outlets, the evidence has {n} from {o}")
    for a, b in re.findall(r"(\d[\d,]*) (?:items )?from (\d+)(?: outlets)?", summary):
        pair = (int(a.replace(",", "")), int(b))
        if pair not in counts.values() and pair != (report["items_collected"], report["sources_scanned"]):
            errors.append(f"the summary states {a} from {b}, which matches no signal")
    raw = f"{report['items_collected']:,} raw source records from {report['sources_scanned']} outlet domains"
    if raw not in summary:
        errors.append(f"the summary must state the collection as: '{raw}'")
    machine = [("executive_summary", summary)] + [(f"{sid}.{f}", text["signals"][sid].get(f) or "")
                                                  for sid in counts for f in ("evidence", "index_note")]
    notes = [(f"{sid}.human_editor_note", text["signals"][sid].get("human_editor_note") or "") for sid in counts]
    for where, value in machine:
        errors += [f"{where} uses {b!r}" for b in BANNED
                   if (re.search(rf"\b{re.escape(b)}\b", value, re.I) if b[0].isalpha() else b in value)]
    for where, value in machine + notes:
        if FIRST_PERSON.search(value):
            errors.append(f"{where} is in the first person")
        if "—" in value or ";" in value:
            errors.append(f"{where} has an em dash or a semicolon")
    return errors


def set_text(report, text):
    before = sha_obj(structure(report))
    errors = text_errors(report, text)
    if errors:
        raise ValueError("\n".join(errors))
    out = json.loads(json.dumps(report))
    out["executive_summary"] = text["executive_summary"].strip()
    for s in out["top_signals"]:
        for field in ("evidence", "index_note", "human_editor_note"):
            s[field] = text["signals"][s["signal_id"]][field].strip()
    out["draft_meta"]["editor_decisions"]["revisions"].append({"at": _now(), "what": "evidence text, index notes, summary and copyedited editor notes set"})
    assert sha_obj(structure(out)) == before
    return out


# ---------- approval deck (the app's existing review deck) ----------

def approval_queue(report, reviews_path):
    thoughts = report["draft_meta"]["editor_decisions"]["editor_thoughts"]
    tasks = []

    def add(key, title, kind, body):
        tasks.append({"task_id": f"{key}:{hashlib.sha256(body.encode()).hexdigest()[:10]}", "question_id": key, "question": title,
                      "kind": kind, "target": key, "prompt": "Approve this as it will be published, or ask for a change.", "body": body,
                      "options": [{"key": k, "label": label, "value": v} for k, label, v in rr.APPROVAL_OPTIONS]})

    add("summary", "Executive summary", "report_text", report["executive_summary"])
    for s in report["top_signals"]:
        a = s["draft_audit"]
        body = (f"{len(s['evidence_items'])} items from {s['source_corroboration_count']} outlets  |  type {s['type']}  |  confidence "
                f"{s['confidence']} ({s['confidence_source']})  |  volatility {s['volatility']}  |  origin {s['origin_classification']}\n"
                f"Sectors: " + ", ".join(f"{k} {v}" for k, v in a["items_by_sector"].items()) + "\n\n"
                f"EVIDENCE TEXT\n{s['evidence']}\n\nINDEX NOTE\n{s['index_note']}\n\n"
                f"EDITOR NOTE AS IT WILL APPEAR\n{s['human_editor_note']}\n\nYOUR THOUGHTS AS YOU WROTE THEM\n{thoughts.get(s['signal_id'], '')}\n\n"
                f"Merged in: {', '.join(a['merged_terms']) or 'none'}. Removed by you: {a['removed_by_editor'] or 'none'}. "
                f"Duplicates counted once: {len(a['collapsed_duplicates'])}.")
        add(f"signal:{s['signal_id']}", s["name"], "report_signal", body)
    dup = [f"- {c['rule']}: item {c['collapsed_item_id']} ({c['collapsed_domain']}) counted with item {c['retained_item_id']} "
           f"({c['retained_domain']}) in {s['name']}" for s in report["top_signals"] for c in s["draft_audit"]["collapsed_duplicates"]]
    add("duplicates", "Duplicates counted once", "report_text", "\n".join(dup) or "No duplicates were collapsed.")
    add("limitations", "Limitations and AI-assistance statement", "report_text",
        "LIMITATIONS\n" + "\n".join(f"- {x}" for x in report["limitations"]) + "\n\nAI ASSISTANCE (as it will read once approved)\n" + AI_FINAL)
    return {"kind": "gen_review", "task": f"report_{report['report_date']}_approval",
            "title": f"Report approval {report['collection_window']['start']} to {report['collection_window']['end']}",
            "outputs_sha256": sha_obj(text_of(report)), "notes": True, "reviews_path": reviews_path, "tasks": tasks, "item_ids": []}


def approval_status(queue):
    """{approved, changes, open, notes}: the latest answer per card of the current deck."""
    path = os.path.join(rr.ROOT, queue["reviews_path"])
    rows = rr.load_rows(path)
    latest = {}
    for r in sorted((r for r in rows if r["kind"] != "note"), key=lambda r: r["reviewed_at"]):
        latest[r["task_id"]] = r["value"]
    ids = [t["task_id"] for t in queue["tasks"]]
    return {"approved": [i for i in ids if latest.get(i) == "APPROVE"], "changes": [i for i in ids if latest.get(i) == "CHANGE"],
            "open": [i for i in ids if i not in latest],
            "notes": [{"card": r["question_id"], "note": r["value"]} for r in rows if r["kind"] == "note" and r["task_id"] in ids]}


# ---------- gate ----------

def gate(paths, end, report=None):
    """(checks, info). The report is publish-ready when every check is true."""
    import evidence_manifest as em
    import validate_all_reports as v
    from report_schema import validate_report
    report = report or _read(paths.report(end))
    draft, snap = _read(paths.draft(end)), _read(paths.snapshot(end))
    frozen = {e["item_id"]: e for s in draft["top_signals"] for e in s["evidence_items"]}
    snap_by_id = {i["item_id"]: i for i in snap["items"]}
    ev = [e for s in report["top_signals"] for e in s["evidence_items"]]
    store = em.load_store_index(paths.db)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    pub = published_form(report)
    try:
        validate_report(report)
        validate_report(pub)
        schema = True
    except Exception as e:
        schema = str(e)[:200]
    dedup = report["limitations"][len(draft["limitations"]):]
    checks = {
        "bound_to_the_frozen_snapshot": em.snapshot_errors(snap, report) == [],
        "snapshot_matches_the_store": store is not None and em.store_errors(snap, store) == [],
        "draft_is_the_one_the_decisions_were_applied_to": rr.sha256_file(paths.draft(end)) == report["draft_meta"]["editor_decisions"]["applied_to_draft_sha256"],
        "every_signal_meets_the_report_rule": all(len(s["evidence_items"]) >= MIN_ITEMS and s["source_corroboration_count"] >= MIN_OUTLETS
                                                  for s in report["top_signals"]),
        "no_duplicate_items_in_a_signal": all(len({e["item_id"] for e in s["evidence_items"]}) == len(s["evidence_items"]) for s in report["top_signals"]),
        "every_item_is_frozen_evidence_unchanged": all(e["item_id"] in snap_by_id and frozen.get(e["item_id"]) == e
                                                       and snap_by_id[e["item_id"]]["content_hash"] == e["content_hash"] for e in ev),
        "only_exact_yes_items": all(e["style_set"] == ["yes"] for e in ev),
        "counts_match_the_evidence": all(s["source_corroboration_count"] == len({e["outlet_domain"] for e in s["evidence_items"]})
                                         and s["source_domains"] == sorted({e["outlet_domain"] for e in s["evidence_items"]})
                                         for s in report["top_signals"]),
        "schema_valid": schema is True,
        "text_complete_and_consistent": text_errors(report, text_of(report)) == [],
        "limitations_are_the_drafters_plus_dedup": report["limitations"][:len(draft["limitations"])] == draft["limitations"]
                                                   and dedup in ([], [DEDUP_LIMITATION]),
        "ai_assistance_is_an_approved_wording": report.get("ai_assistance") in (AI_DRAFT, AI_FINAL),
        "report_date_not_in_the_future": report["report_date"] <= today,
        "publish_gate_passes_once_approved": v.publish_gate_errors(pub, today, store, snap) == [],
        "not_published_yet": not os.path.exists(paths.published(end)),
    }
    info = {"signals": [(s["signal_id"], len(s["evidence_items"]), s["source_corroboration_count"], s["confidence"], s["volatility"])
                        for s in report["top_signals"]],
            "distinct_evidence_units": len({e["item_id"] for e in ev}), "snapshot_items": len(snap["items"]),
            "report_sha256": rr.sha256_file(paths.report(end)) if os.path.exists(paths.report(end)) else None,
            "evidence_snapshot_sha256": snap["snapshot_sha256"], "schema": schema}
    return checks, info


def published_form(report):
    """The report as it goes into data/reports/: approved, final AI-assistance wording, no draft-only sections."""
    pub = json.loads(json.dumps(report))
    pub["review_status"], pub["reviewed_by"], pub["ai_assistance"] = "reviewed", "the editor", AI_FINAL
    pub.pop("draft_meta", None)
    for s in pub["top_signals"]:
        s.pop("draft_audit", None)
    return pub


# ---------- commands ----------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["apply", "text", "approval", "gate", "publish-file", "status"])
    ap.add_argument("report_date")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--groups", help="JSON list of extra same-story groups: [{\"items\": [id, ...], \"why\": \"...\"}]")
    ap.add_argument("--base")
    ap.add_argument("--db")
    args = ap.parse_args(argv)
    paths, end = rr.Paths(args.base, args.db), args.report_date
    out = {"command": args.cmd, "report_date": end}
    try:
        if args.cmd == "apply":
            if os.path.exists(paths.published(end)):
                raise ValueError("this report is already published")
            draft, queue, audit = _read(paths.draft(end)), _read(paths.queue(end)), _read(paths.audit(end))
            report = apply_decisions(draft, queue, rr.latest(queue), audit, _read(args.groups) if args.groups else None,
                                     rr.sha256_file(paths.draft(end)))
            _write(paths.report(end), report)
            out.update(report=paths.report(end), signals=[(s["signal_id"], s["name"], len(s["evidence_items"]), s["source_corroboration_count"],
                                                           s["confidence"], s["volatility"]) for s in report["top_signals"]],
                       distinct_evidence_units=len({e["item_id"] for s in report["top_signals"] for e in s["evidence_items"]}),
                       collapsed=sum(len(s["draft_audit"]["collapsed_duplicates"]) for s in report["top_signals"]))
        elif args.cmd == "text":
            report = set_text(_read(paths.report(end)), _read(args.file))
            _write(paths.report(end), report)
            out.update(report=paths.report(end), report_sha256=rr.sha256_file(paths.report(end)))
        elif args.cmd == "approval":
            report = _read(paths.report(end))
            errors = text_errors(report, text_of(report))
            if errors:
                raise ValueError("the text is not ready for approval:\n" + "\n".join(errors))
            reviews = paths.approvals(end)
            same_drive = os.path.splitdrive(reviews)[0] == os.path.splitdrive(rr.ROOT)[0]
            queue = approval_queue(report, os.path.relpath(reviews, rr.ROOT).replace(os.sep, "/") if same_drive else reviews)
            _write(paths.approval_queue(end), queue)
            out.update(queue=paths.approval_queue(end), cards=len(queue["tasks"]), **{k: len(v) for k, v in approval_status(queue).items()})
        elif args.cmd == "status" and not os.path.exists(paths.report(end)):
            queue = _read(paths.queue(end))
            done = rr.latest(queue)
            out.update(result="PASS", stage="decisions", title=queue["title"],
                       undecided=[c["card_id"] for c in queue["cards"] if c["kind"] != "report" and c["card_id"] not in done],
                       decided=sum(1 for c in queue["cards"] if c["card_id"] in done), cards=len(queue["cards"]))
        elif args.cmd in ("gate", "status", "publish-file"):
            checks, info = gate(paths, end)
            status = approval_status(_read(paths.approval_queue(end))) if os.path.exists(paths.approval_queue(end)) else None
            failed = sorted(k for k, ok in checks.items() if not ok)
            out.update(result="PASS" if not failed else "FAIL", failed=failed, checks=len(checks), **info,
                       approval=None if status is None else {"approved": len(status["approved"]), "changes": status["changes"],
                                                             "open": status["open"], "notes": status["notes"]})
            if args.cmd == "publish-file":
                if failed:
                    raise ValueError(f"the gate failed: {failed}")
                if status is None or status["changes"] or status["open"]:
                    raise ValueError("the editor has not approved every card of the current approval deck")
                import report_markdown
                pub = published_form(_read(paths.report(end)))
                os.makedirs(paths.reports, exist_ok=True)
                with open(paths.published(end), "x", encoding="utf-8", newline="\n") as f:
                    json.dump(pub, f, indent=2, ensure_ascii=False)
                    f.write("\n")
                archive = os.path.join(os.path.dirname(paths.editing), "3-published")
                os.makedirs(archive, exist_ok=True)
                with open(os.path.join(archive, f"{end}.md"), "w", encoding="utf-8", newline="\n") as f:
                    f.write(report_markdown.export_markdown(pub).replace("Approved: no", "Approved: yes"))
                out.update(published_file=paths.published(end), published_sha256=rr.sha256_file(paths.published(end)),
                           note="written, not committed: commit and push only on the editor's word")
    except (ValueError, FileNotFoundError, FileExistsError) as e:
        out.update(result="STOPPED", reason=str(e))
        print(json.dumps(out, indent=1, ensure_ascii=False))
        return 1
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0 if out.get("result", "PASS") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
