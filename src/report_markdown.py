#############################################################
# report_markdown.py
# turn a report JSON into a readable Markdown file for the editor, and
# apply the edited Markdown back onto the JSON.
#
# only prose fields are editable: the executive summary, each signal's
# name, evidence text, index note and human-editor note, and the
# limitations. dates, evidence links, labels and everything else are
# shown for context and marked locked; edits to locked lines are ignored.
#
# usage:
#   python src/report_markdown.py export <report.json> <out.md>
#   python src/report_markdown.py apply  <edited.md> <report.json>
#       writes the edited prose into the JSON, marks the report reviewed
#       only if the editor set "Approved: yes", and prints what changed.
#############################################################

import json
import re
import sys

LOCK = "🔒"
APPROVAL_LINE = "Approved:"


def export_markdown(report: dict) -> str:
    r = report
    out = []
    out.append(f"# Report {r['report_date']} (draft for editing)")
    out.append("")
    out.append("> How to edit: change the text under any heading marked ✏️. Lines starting with 🔒 are shown for "
               "context and can't be changed here. When you're finished, set the approval line at the bottom to "
               "`Approved: yes` (or leave it `no` if you want another round), save, and move this file to "
               "`2-done-editing`.")
    out.append("")
    out.append(f"{LOCK} Collection window: {r['collection_window']['start']} to {r['collection_window']['end']}. "
               f"Sources scanned: {r.get('sources_scanned')}. Items collected: {r.get('items_collected')}.")
    out.append("")
    out.append("## ✏️ Executive summary")
    out.append("")
    out.append(r.get("executive_summary", "").strip())
    out.append("")
    if r.get("evidence_items"):
        out.append(f"{LOCK} Evidence for the summary:")
        for e in r["evidence_items"]:
            out.append(f"{LOCK} - {e.get('title') or e['url']} ({e.get('outlet_domain', '')}, published {e['published_at'][:10]}) {e['url']}")
        out.append("")
    for i, s in enumerate(r.get("top_signals", []), 1):
        out.append(f"## Signal {i}: {s.get('signal_id') or s['name']}")
        out.append("")
        out.append(f"{LOCK} Type: {s.get('type')}. Confidence: {s.get('confidence')}. Volatility: {s.get('volatility')}. "
                   f"Origin: {s.get('origin_classification')}. Sectors: {', '.join(s.get('source_sectors', []))}.")
        for e in s.get("evidence_items", []):
            out.append(f"{LOCK} - {e.get('title') or e['url']} ({e.get('outlet_domain', '')}, published {e['published_at'][:10]}) {e['url']}")
        out.append("")
        for field, label in (("name", "Name"), ("evidence", "Evidence text"), ("index_note", "Index note"),
                             ("human_editor_note", "Your editor note (only you write this; leave empty if none)")):
            out.append(f"### ✏️ {label}")
            out.append("")
            out.append((s.get(field) or "").strip())
            out.append("")
    out.append("## ✏️ Limitations (one per line, starting with - )")
    out.append("")
    for lim in r.get("limitations", []):
        out.append(f"- {lim}")
    out.append("")
    out.append("## Approval")
    out.append("")
    out.append(f"{APPROVAL_LINE} no")
    out.append("")
    return "\n".join(out)


def _sections(md: str) -> list:
    """split into (heading, body) pairs on ## and ### headings."""
    parts = re.split(r"(?m)^(#{2,3} .*)$", md)
    pairs = []
    for i in range(1, len(parts), 2):
        pairs.append((parts[i].strip(), parts[i + 1]))
    return pairs


def _clean(body: str) -> str:
    lines = [l for l in body.strip().split("\n") if not l.startswith(LOCK) and not l.startswith(">")]
    return "\n".join(lines).strip()


def apply_markdown(md: str, report: dict) -> tuple:
    """return (new_report, changes, approved). changes lists (field, old, new)."""
    new = json.loads(json.dumps(report))
    changes = []
    signal_index = -1
    approved = False

    def set_field(target, key, value, label):
        old = (target.get(key) or "").strip()
        if value != old:
            changes.append((label, old, value))
            target[key] = value

    for heading, body in _sections(md):
        text = _clean(body)
        h = heading.lstrip("#").strip()
        if h == "✏️ Executive summary":
            set_field(new, "executive_summary", text, "executive_summary")
        elif h.startswith("Signal "):
            signal_index += 1
        elif h.startswith("✏️ Limitations"):
            lims = [l[2:].strip() for l in text.split("\n") if l.startswith("- ") and l[2:].strip()]
            if lims != new.get("limitations", []):
                changes.append(("limitations", new.get("limitations", []), lims))
                new["limitations"] = lims
        elif h == "Approval":
            m = re.search(rf"{APPROVAL_LINE}\s*(\w+)", body)
            approved = bool(m and m.group(1).lower() in ("yes", "y", "true"))
        elif signal_index >= 0 and h.startswith("✏️ "):
            sig = new["top_signals"][signal_index]
            key = {"✏️ Name": "name", "✏️ Evidence text": "evidence", "✏️ Index note": "index_note"}.get(h)
            if h.startswith("✏️ Your editor note"):
                key = "human_editor_note"
            if key:
                set_field(sig, key, text, f"top_signals[{signal_index}].{key}")
    if approved:
        new["review_status"] = "reviewed"
        new["reviewed_by"] = new.get("reviewed_by") or "the editor"
    return new, changes, approved


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    if len(argv) != 3 or argv[0] not in ("export", "apply"):
        print(__doc__ or "usage: report_markdown.py export|apply ...")
        return 2
    cmd, a, b = argv
    if cmd == "export":
        report = json.load(open(a, encoding="utf-8"))
        open(b, "w", encoding="utf-8").write(export_markdown(report))
        print(f"wrote {b}")
        return 0
    md = open(a, encoding="utf-8").read()
    report = json.load(open(b, encoding="utf-8"))
    new, changes, approved = apply_markdown(md, report)
    with open(b, "w", encoding="utf-8") as f:
        json.dump(new, f, indent=2, ensure_ascii=False)
        f.write("\n")
    for field, old, value in changes:
        print(f"CHANGED {field}:\n  was: {old}\n  now: {value}")
    print(f"{len(changes)} field(s) changed. Approved: {'yes' if approved else 'no'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
