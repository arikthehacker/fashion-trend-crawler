"""The editor's definitions for the "Report decisions" deck: one entry per option, in her words.

One file, read in two places: ARI3 Review shows it beside every report-decision card, and the
EXP-007 prompt includes it word for word. Software never writes a definition.

The editor writes them in the ARI3 Review deck "Report definitions (your words)": one card per
option plus one for her rules, each a free text box. Every save is appended to
editorial/report_definitions_log.jsonl (latest answer wins), and the Markdown file is rewritten
from the log with her text exactly as typed.

Format (editorial/report_definitions.md): a `## Section` heading, then `- key: definition`
lines, with further lines of a definition indented by two spaces. The Rules section holds free
`- rule` lines. A line with nothing after the key (or an empty `-` in Rules) is unwritten.
"""

import hashlib
import json
import os
import re

from item_store import ROOT, utc_now

PATH = os.path.join(ROOT, "editorial", "report_definitions.md")
LOG = os.path.join(ROOT, "editorial", "report_definitions_log.jsonl")
QUEUE_NAME = "report_definitions"
TITLE = "Report definitions (your words)"
RULES = "Rules"
REVIEWER = "ariella"
WHERE = {"Decision": "the Decision list on every candidate card",
         "Possible duplicates": "the Decision list on a Possible duplicates card",
         "Type": "the Type list on every candidate card",
         "Confidence": "the Confidence list on every candidate card",
         "Volatility": "the Volatility list on every candidate card",
         "Origin": "the Origin list on every candidate card"}
# What the software does with each field today (facts about the code, not definitions).
WHAT = {"Decision": "Only keep puts a signal in the published report. Merge adds its evidence to the kept signal you "
                    "pick. Drop and watchlist both leave it out of this week's report, and the app records which one "
                    "you chose.",
        "Possible duplicates": "One story: the items are counted once, keeping the earliest record. Separate pieces: "
                               "each item counts.",
        "Type": "Printed on the signal in the report. It starts as the drafter's guess.",
        "Confidence": "Baseline is a rule: high if the evidence comes from 2 or more outlets in 2 or more sectors, "
                      "medium if from 2 or more outlets in one sector (or one outlet in a high-reliability sector), "
                      "otherwise low. Choosing low, medium or high replaces the rule.",
        "Volatility": "Required to keep. Printed on the signal in the report.",
        "Origin": "Printed on the signal in the report. Stays unclear unless you choose.",
        "Rules": "Rules apply to every decision. The software already enforces one: after your edits, a kept signal "
                 "must still have at least 2 items from at least 2 outlets, or the report stops."}


def expected_keys():
    """{section: [keys]} the file must define, from the option lists the app offers."""
    from report_review import CONFIDENCE, DECISIONS, SIGNAL_TYPES
    from taxonomy import ORIGIN_CLASSIFICATIONS, VOLATILITY_LABELS
    return {"Decision": list(DECISIONS), "Possible duplicates": ["one story", "separate pieces"],
            "Type": list(SIGNAL_TYPES), "Confidence": ["baseline"] + list(CONFIDENCE),
            "Volatility": list(VOLATILITY_LABELS), "Origin": list(ORIGIN_CLASSIFICATIONS)}


def text(path=PATH):
    with open(path, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def sha256(path=PATH):
    return hashlib.sha256(text(path).encode("utf-8")).hexdigest()


def parse(raw):
    """{section: [(key, definition)]}; Rules entries have key None. Lines indented by two
    spaces continue the previous entry."""
    out, section = {}, None
    for line in raw.split("\n"):
        h = re.match(r"^##\s+(.+?)\s*$", line)
        if h:
            section = h.group(1)
            out.setdefault(section, [])
            continue
        if section is not None and line.startswith("  ") and line.strip() and out[section]:
            key, prev = out[section][-1]
            out[section][-1] = (key, f"{prev}\n{line[2:]}" if prev else line[2:])
            continue
        if section is None or not line.startswith("-"):
            continue
        body = line[1:].strip()
        if section == RULES:
            out[section].append((None, body))
        else:
            key, _, definition = body.partition(":")
            out[section].append((key.strip(), definition.strip()))
    return out


def problems(path=PATH):
    """Why the file is not ready: missing sections, unknown or missing keys, unwritten lines."""
    parsed = parse(text(path))
    issues = []
    for section, keys in expected_keys().items():
        have = dict(parsed.get(section, []))
        for k in keys:
            if k not in have:
                issues.append(f"{section}: '{k}' is missing")
            elif not have[k]:
                issues.append(f"{section}: '{k}' is not written yet")
        for k in have:
            if k not in keys:
                issues.append(f"{section}: '{k}' is not an option the app offers")
    if not any(d for _, d in parsed.get(RULES, [])):
        issues.append("Rules: no rule written yet")
    return issues


def panel_text(path=PATH):
    """What the app shows: the file as written, with unwritten lines marked."""
    lines = []
    for line in text(path).rstrip("\n").split("\n"):
        stripped = line.rstrip()
        if stripped == "-" or (stripped.startswith("- ") and stripped.endswith(":")):
            line = f"{stripped} (not written yet)"
        lines.append(line)
    return "\n".join(lines)


# ---------- the deck ----------

def cards():
    """One card per option the app offers, then one card for the rules."""
    out = [{"card_id": f"{section}:{key}", "section": section, "key": key, "where": WHERE[section]}
           for section, keys in expected_keys().items() for key in keys]
    out.append({"card_id": RULES, "section": RULES, "key": None, "where": "every report decision"})
    return out


def load_log(path=LOG):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def latest(path=LOG):
    """{card_id: text}, the newest answer per card."""
    out = {}
    for r in sorted(load_log(path), key=lambda r: r["written_at"]):
        out[r["card_id"]] = r["text"]
    return out


def render(answers):
    """The Markdown file from the latest answers, her text exactly as written."""
    lines = ["# Report decision definitions"]
    for section, keys in expected_keys().items():
        lines += ["", f"## {section}"]
        for key in keys:
            body = (answers.get(f"{section}:{key}") or "").strip("\n")
            parts = body.split("\n") if body.strip() else [""]
            lines.append(f"- {key}: {parts[0]}".rstrip() if parts[0].strip() else f"- {key}:")
            lines += [f"  {p}" for p in parts[1:]]
    lines += ["", f"## {RULES}"]
    rules = [r.strip() for r in (answers.get(RULES) or "").split("\n") if r.strip()]
    lines += [f"- {r}" for r in rules] or ["-"]
    return "\n".join(lines) + "\n"


def record(card_id, body, log=LOG, path=PATH, reviewer=REVIEWER, copyedit=None, approvals=None):
    """Append one brain-dump answer, then rewrite the definitions file."""
    if card_id not in {c["card_id"] for c in cards()}:
        raise ValueError(f"unknown card {card_id}")
    row = {"card_id": card_id, "text": body.rstrip(), "reviewer": reviewer, "written_at": utc_now()}
    _append(log, row)
    write_file(log, path, copyedit, approvals)
    return row


def _append(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_file(log=LOG, path=PATH, copyedit=None, approvals=None):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(final_answers(log, copyedit, approvals)))


# ---------- copyedit approval ----------
# After the brain dump, Claude writes a minimal copyedit of each answer to COPYEDIT
# ({card_id: {"original_sha256", "copyedit", "flag"}}): spelling, punctuation and broken
# sentences only, nothing added, meaning unchanged. An unclear passage is flagged, not
# guessed at. The editor then chooses per card in the "Report definitions approval" deck:
# the copyedit, her original, or her own rewrite. Only those choices reach the file.

COPYEDIT = os.path.join(ROOT, "editorial", "report_definitions_copyedit.json")
APPROVALS = os.path.join(ROOT, "editorial", "report_definitions_approvals.jsonl")
APPROVAL_QUEUE = "report_definitions_approval"
APPROVAL_TITLE = "Report definitions approval"
CHOICES = ("copyedit", "original", "rewrite")


def text_sha(body):
    return hashlib.sha256((body or "").rstrip().encode("utf-8")).hexdigest()


def load_copyedits(path=None):
    path = path or COPYEDIT
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def approvals_latest(path=None):
    out = {}
    for r in sorted(load_log(path or APPROVALS), key=lambda r: r["approved_at"]):
        out[r["card_id"]] = r
    return out


def approval_rows(log=LOG, copyedit=None, approvals=None):
    """One row per card: her latest text, the copyedit, and her valid choice if any. A choice
    or copyedit made for an older version of her text does not count."""
    raw, edits, chosen = latest(log), load_copyedits(copyedit), approvals_latest(approvals)
    rows = []
    for c in cards():
        original = raw.get(c["card_id"], "")
        sha = text_sha(original)
        e = edits.get(c["card_id"])
        edit_ok = bool(e) and e.get("original_sha256") == sha
        a = chosen.get(c["card_id"])
        rows.append({**c, "original": original, "copyedit": e["copyedit"] if edit_ok else None,
                     "flag": e.get("flag") if edit_ok else None, "stale_copyedit": bool(e) and not edit_ok,
                     "approval": a if a and a["original_sha256"] == sha else None})
    return rows


def record_approval(card_id, choice, rewrite=None, log=LOG, path=PATH, copyedit=None, approvals=None,
                    reviewer=REVIEWER):
    if choice not in CHOICES:
        raise ValueError(f"choice must be one of {CHOICES}")
    row = next((r for r in approval_rows(log, copyedit, approvals) if r["card_id"] == card_id), None)
    if row is None:
        raise ValueError(f"unknown card {card_id}")
    if choice == "copyedit" and row["copyedit"] is None:
        raise ValueError("there is no current copyedit for this card")
    if choice == "rewrite" and not (rewrite or "").strip():
        raise ValueError("a rewrite needs text")
    final = {"copyedit": row["copyedit"], "original": row["original"], "rewrite": (rewrite or "").rstrip()}[choice]
    out = {"card_id": card_id, "choice": choice, "text": final, "original_sha256": text_sha(row["original"]),
           "copyedit_sha256": text_sha(row["copyedit"]) if row["copyedit"] is not None else None,
           "reviewer": reviewer, "approved_at": utc_now()}
    _append(approvals or APPROVALS, out)
    write_file(log, path, copyedit, approvals)
    return out


def final_answers(log=LOG, copyedit=None, approvals=None):
    """Her latest brain dump per card, replaced by her approved choice where one is current."""
    out = latest(log)
    for r in approval_rows(log, copyedit, approvals):
        if r["approval"]:
            out[r["card_id"]] = r["approval"]["text"]
    return out


def approval_left(log=LOG, copyedit=None, approvals=None):
    rows = approval_rows(log, copyedit, approvals)
    return sum(1 for r in rows if not r["approval"]), len(rows)


def write_approval_queue():
    import label_tool
    return label_tool._write_queue(APPROVAL_QUEUE, {"kind": "definitions_approval", "task": APPROVAL_QUEUE,
                                                    "title": APPROVAL_TITLE, "item_ids": []})


def left(log=LOG):
    """(cards still unwritten, all cards)."""
    done = {k for k, v in latest(log).items() if v.strip()}
    all_cards = cards()
    return sum(1 for c in all_cards if c["card_id"] not in done), len(all_cards)


def write_queue():
    """The deck file, so ARI3 Review lists the deck in its menu."""
    import label_tool
    return label_tool._write_queue(QUEUE_NAME, {"kind": "definitions", "task": QUEUE_NAME, "title": TITLE,
                                                "item_ids": []})
