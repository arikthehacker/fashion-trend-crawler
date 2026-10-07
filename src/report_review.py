"""Report review in ARI3 Review: the editor's decisions on a drafted report, then her approval of
the finished text. No tkinter here, so it can be tested.

Round 1 (decisions): one card per candidate signal, one per possible duplicate group, one for
report-level thoughts. The editor chooses keep / drop / merge / watchlist, the labels, the items
to remove and writes her thoughts. Software never fills these in.

Round 2 (approval): one card per finished signal, plus the summary, the limitations and
AI-assistance text and the collapsed duplicates. Approve or ask for a change.

Both logs are append-only JSON lines in the planning folder (reports-editing/app/), never in the
published archive. The latest answer per card wins.
"""

import hashlib
import json
import os

from item_store import DEFAULT_DB, ROOT, utc_now
from taxonomy import CONFIDENCE_LEVELS, ORIGIN_CLASSIFICATIONS, VOLATILITY_LABELS

PLANNING = os.path.dirname(ROOT)
SIGNAL_TYPES = ["aesthetic_term", "color_print", "commerce_language", "footwear", "garment_silhouette", "material"]
DECISIONS = ["keep", "drop", "merge", "watchlist"]
CONFIDENCE = [c for c in CONFIDENCE_LEVELS if c != "archival"]
APPROVAL_OPTIONS = [("a", "Approve", "APPROVE"), ("c", "Change (press T to say what)", "CHANGE")]
REVIEWER = "ariella"


class Paths:
    """Where a report's working files live. `base` puts everything in one folder (tests, dry runs)."""

    def __init__(self, base=None, db=None):
        self.db = db or DEFAULT_DB
        store = os.path.join(ROOT, "data", "store")
        if base:
            self.drafts, self.evidence, self.queues, self.editing, self.app, self.backups, self.reports = (
                os.path.join(base, d) for d in ("drafts", "evidence", "queues", "editing", "app", "backups", "reports"))
            self.log = os.path.join(base, "report-prep-log.jsonl")
            self.ingest_log = os.path.join(base, "ingest-log.jsonl")
        else:
            self.drafts = os.path.join(store, "drafts")
            self.evidence = os.path.join(ROOT, "data", "evidence")
            self.queues = os.path.join(store, "queues")
            self.editing = os.path.join(PLANNING, "reports-editing", "1-needs-editing")
            self.app = os.path.join(PLANNING, "reports-editing", "app")
            self.backups = os.path.join(store, "backups")
            self.reports = os.path.join(ROOT, "data", "reports")
            self.log = os.path.join(store, "report-prep-log.jsonl")
            self.ingest_log = os.path.join(store, "ingest-log.jsonl")

    def draft(self, end):
        return os.path.join(self.drafts, f"{end}.final.draft.json")

    def audit(self, end):
        return os.path.join(self.drafts, f"{end}.duplicates.json")

    def report(self, end):
        return os.path.join(self.drafts, f"{end}.report.json")

    def snapshot(self, end):
        return os.path.join(self.evidence, f"{end}.snapshot.json")

    def queue(self, end):
        return os.path.join(self.queues, f"report_{end}.json")

    def approval_queue(self, end):
        return os.path.join(self.queues, f"report_{end}_approval.json")

    def decisions(self, end):
        return os.path.join(self.app, f"{end}-decisions.jsonl")

    def approvals(self, end):
        return os.path.join(self.app, f"{end}-approvals.jsonl")

    def published(self, end):
        return os.path.join(self.reports, f"{end}.json")


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def weaknesses(signal):
    """The drafter's weakness flags for one candidate (same rules as its review package)."""
    a, n = signal["draft_audit"], len(signal["evidence_items"])
    out = []
    if a["max_items_from_one_outlet"] * 2 > n:
        out.append(f"half or more of the evidence comes from one outlet ({a['max_items_from_one_outlet']} of {n} items)")
    if not a["cross_sector"]:
        out.append("one sector only")
    elif not a["cross_sector_group"]:
        out.append("several sectors, all inside one sector group")
    outside = sum(v for k, v in a["items_by_sector"].items() if k != "editorial")
    if a["cross_sector"] and outside <= 1:
        out.append(f"only {outside} item comes from outside the editorial sector")
    if a["reconstructed_first_seen_items"]:
        out.append(f"{a['reconstructed_first_seen_items']} items have reconstructed first-seen times")
    if a["not_sure_items_with_term"]:
        out.append(f"{len(a['not_sure_items_with_term'])} more items mention the term but got a not-sure prediction (not counted)")
    return out


def build_decision_queue(draft, audit, reviews_path):
    """The round-1 queue from a frozen draft and its duplicate audit."""
    cards = []
    for s in draft["top_signals"]:
        a = s["draft_audit"]
        cards.append({
            "card_id": f"signal:{s['signal_id']}", "kind": "signal", "signal_id": s["signal_id"], "name": s["name"],
            "type": s["type"], "baseline_confidence": s["confidence"], "items": len(s["evidence_items"]),
            "outlets": s["source_corroboration_count"], "sectors": a["items_by_sector"], "dates": a["dates"],
            "weaknesses": weaknesses(s),
            "evidence": [{"item_id": e["item_id"], "published": e["published_at"][:10], "outlet": e["outlet_domain"],
                          "sector": e["sector"], "title": e["title"], "url": e["url"]} for e in s["evidence_items"]]})
    for n, g in enumerate(audit.get("possible", []), 1):
        cards.append({"card_id": f"duplicate:{n}", "kind": "duplicate", "items": g["items"], "why": g["why"]})
    cards.append({"card_id": "report", "kind": "report"})
    return {"kind": "report_decisions", "task": f"report_{draft['report_date']}",
            "title": f"Report decisions {draft['collection_window']['start']} to {draft['collection_window']['end']}",
            "report_date": draft["report_date"], "collection_window": draft["collection_window"],
            "evidence_snapshot_sha256": draft.get("evidence_snapshot_sha256"), "reviews_path": reviews_path,
            "exact_mirrors": audit.get("exact", []), "cards": cards, "item_ids": []}


def log_path(queue):
    return os.path.join(ROOT, queue["reviews_path"])  # an absolute reviews_path wins on its own


def payload_errors(queue, card, payload):
    """Why a decision cannot be saved. An empty list means it can."""
    errors = []
    if card["kind"] == "report":
        return errors
    if card["kind"] == "duplicate":
        if payload.get("collapse") not in (True, False):
            errors.append("choose whether these are one story (collapse) or separate")
        return errors
    decision = payload.get("decision")
    if decision not in DECISIONS:
        return [f"decision must be one of {DECISIONS}"]
    ids = {c["signal_id"] for c in queue["cards"] if c["kind"] == "signal"}
    if decision == "merge":
        if payload.get("merge_into") not in ids - {card["signal_id"]}:
            errors.append("choose which signal this merges into")
    if decision == "keep":
        if payload.get("volatility") not in VOLATILITY_LABELS:
            errors.append("a kept signal needs a volatility label")
        if not (payload.get("thoughts") or "").strip():
            errors.append("a kept signal needs the editor's thoughts (they become the editor note)")
        if payload.get("type") and payload["type"] not in SIGNAL_TYPES:
            errors.append("unknown type")
        if payload.get("confidence") and payload["confidence"] not in CONFIDENCE:
            errors.append("unknown confidence")
        if payload.get("origin") and payload["origin"] not in ORIGIN_CLASSIFICATIONS:
            errors.append("unknown origin")
    have = {e["item_id"] for e in card["evidence"]}
    bad = [i for i in payload.get("remove_item_ids") or [] if i not in have]
    if bad:
        errors.append(f"items {bad} are not evidence of this candidate")
    return errors


def record(queue, card_id, payload, reviewer=REVIEWER):
    """Append one decision. Raises ValueError with the reasons if it is incomplete."""
    card = next(c for c in queue["cards"] if c["card_id"] == card_id)
    errors = payload_errors(queue, card, payload)
    if errors:
        raise ValueError("; ".join(errors))
    row = {"card_id": card_id, "kind": card["kind"], "payload": payload, "reviewer": reviewer, "reviewed_at": utc_now(),
           "report_date": queue["report_date"], "evidence_snapshot_sha256": queue.get("evidence_snapshot_sha256")}
    path = log_path(queue)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def load_rows(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def latest(queue, reviewer=REVIEWER):
    """{card_id: payload}, the newest answer per card."""
    out = {}
    for r in sorted(load_rows(log_path(queue)), key=lambda r: r["reviewed_at"]):
        if r["reviewer"] == reviewer:
            out[r["card_id"]] = r["payload"]
    return out


def left(queue):
    """(cards still to decide, cards that need a decision). The report-thoughts card is optional."""
    need = [c["card_id"] for c in queue["cards"] if c["kind"] != "report"]
    done = latest(queue)
    return sum(1 for c in need if c not in done), len(need)


def card_text(card):
    """What the app shows for one card."""
    if card["kind"] == "report":
        return ("REPORT-LEVEL THOUGHTS (optional)\n\nAnything about the week as a whole: what the summary should stress, "
                "what to play down, anything the candidates above do not capture.")
    if card["kind"] == "duplicate":
        lines = ["POSSIBLE DUPLICATES", "", f"Why flagged: {card['why']}", "",
                 "Are these the same underlying story (count once) or separate pieces?", ""]
        lines += [f"item {i['item_id']}  |  {i['outlet']}  |  {i['published']}  |  in: {', '.join(i['signals'])}\n{i['title']}\n"
                  for i in card["items"]]
        return "\n".join(lines)
    lines = [f"{card['items']} style-positive items from {card['outlets']} outlets  |  type {card['type']}  |  baseline confidence "
             f"{card['baseline_confidence']}",
             "Sectors: " + ", ".join(f"{k} {v}" for k, v in card["sectors"].items()),
             f"Dates: {card['dates'][0]} to {card['dates'][-1]}",
             "Weaknesses: " + ("; ".join(card["weaknesses"]) or "none flagged"), "", "EVIDENCE", ""]
    lines += [f"{e['item_id']}  |  {e['published']}  |  {e['outlet']}  |  {e['sector']}\n{e['title']}\n" for e in card["evidence"]]
    return "\n".join(lines)
