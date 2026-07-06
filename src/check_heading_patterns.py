"""
check_heading_patterns.py

Heuristic scanner for the recurring "styled <p> standing in for a real
heading" bug (see docs/agent-logs/heading-lint-automation.md, run 22, and
docs/agent-logs/accessibility-audit-run29.md, run 29 -- 4th recurrence).

ESLint/jsx-a11y cannot catch this (confirmed run 22): it only inspects tag
semantics, never computed visual styling. This script is a project-specific
heuristic that looks at the *styling convention this codebase actually uses*
for heading-scale/heading-shaped text, and flags <p> tags that match it.

Two independent visual signatures have been observed in real fixed instances
(see docs/agent-logs/heading-hierarchy-fix.md and accessibility-audit-run29.md):

  1. "Display heading" pattern: fontFamily: var(--font-instrument), the
     site's dedicated heading/display font (grep-confirmed: used exclusively
     inside real <h1>-<h3> tags across every page as of this run, with one
     exception -- see LIMITATIONS below).
  2. "Section-label" pattern: small uppercase text with letterSpacing acting
     as a section/subsection title (the run-29 case-study bug: fontFamily
     var(--font-franklin), fontSize 0.75rem, uppercase, letterSpacing --
     visually a "kicker" but functioning as that section's only title).

Pattern 2 is inherently ambiguous: this exact style is ALSO used
legitimately for real kickers/eyebrows/bylines that sit next to a real <h1>
(e.g. case-study/page.tsx's "Case Study" masthead label). The heuristic
tries to tell these apart by content length and by whether a real heading
tag appears immediately adjacent -- but this is a heuristic, not a proof.
Expect both false positives (legitimate kickers) and false negatives
(section labels this heuristic doesn't recognize).

This is NOT a CI gate. It prints a warning list for human/agent review,
same spirit as audit_confidence.py and check_field_coverage.py.

Usage:
    python src/check_heading_patterns.py [root]

    root defaults to web/app relative to the repo root.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Matches a <p ...>...</p> block, capturing the opening-tag attributes and
# the inner content separately. Non-greedy; assumes <p> is not nested inside
# another <p> (true for JSX/HTML). DOTALL so it can span multiple lines.
P_TAG_RE = re.compile(r"<p([^>]*)>(.*?)</p>", re.DOTALL)

# A very small set of style-prop extractors. These are regexes over the raw
# text of the opening tag, not a real JS/TS parser -- good enough for this
# codebase's consistent inline-style convention, not a general solution.
STYLE_PROP_RE = {
    "fontFamily": re.compile(r'fontFamily:\s*"([^"]*)"'),
    "fontSize": re.compile(r'fontSize:\s*"([^"]*)"'),
    "letterSpacing": re.compile(r"letterSpacing:"),
    "textTransform": re.compile(r'textTransform:\s*"uppercase"'),
    "fontWeight": re.compile(r'fontWeight:\s*"?(\d+|bold)"?'),
}

# Strip JSX expressions ({...}), tags, and whitespace to approximate the
# rendered text content of a <p> for a word/char count.
JSX_EXPR_RE = re.compile(r"\{[^{}]*\}")
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")

HEADING_TAG_RE = re.compile(r"<h[1-6]\b")


@dataclass
class Candidate:
    file: Path
    line: int
    text_preview: str
    score: int
    reasons: list[str] = field(default_factory=list)


def approx_text(inner: str) -> str:
    stripped = JSX_EXPR_RE.sub(" ", inner)
    stripped = TAG_RE.sub(" ", stripped)
    stripped = WS_RE.sub(" ", stripped).strip()
    return stripped


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def score_candidate(attrs: str, inner: str, full_text: str, match_start: int, match_end: int) -> tuple[int, list[str]]:
    score = 0
    reasons = []

    font_family_m = STYLE_PROP_RE["fontFamily"].search(attrs)
    font_family = font_family_m.group(1) if font_family_m else ""

    if "var(--font-instrument)" in font_family:
        score += 3
        reasons.append("uses the site's dedicated heading/display font (--font-instrument)")

    is_uppercase = bool(STYLE_PROP_RE["textTransform"].search(attrs))
    has_letter_spacing = bool(STYLE_PROP_RE["letterSpacing"].search(attrs))
    if is_uppercase and has_letter_spacing:
        score += 2
        reasons.append("uppercase + letterSpacing (section-label/kicker visual pattern)")

    fw_m = STYLE_PROP_RE["fontWeight"].search(attrs)
    if fw_m:
        val = fw_m.group(1)
        if val == "bold" or (val.isdigit() and int(val) >= 600):
            score += 1
            reasons.append(f"bold-ish fontWeight ({val})")

    text = approx_text(inner)
    word_count = len(text.split())
    if 0 < word_count <= 6:
        score += 2
        reasons.append(f"short label-like text ({word_count} word(s)): {text!r}")
    elif word_count == 0:
        # empty/dynamic-only content, can't judge -- neutral
        pass
    else:
        score -= 1
        reasons.append(f"longer prose-like text ({word_count} words) -- likely body copy")

    # Adjacency check: if a real heading tag appears within ~200 chars
    # before or after this <p>, it's more likely a legitimate kicker/caption
    # sitting next to an actual heading, not a smuggled-in heading itself.
    window_before = full_text[max(0, match_start - 200):match_start]
    window_after = full_text[match_end:match_end + 200]
    if HEADING_TAG_RE.search(window_before) or HEADING_TAG_RE.search(window_after):
        score -= 2
        reasons.append("a real <h1>-<h6> appears immediately adjacent (likely an intentional kicker/caption, not a standalone label)")

    return score, reasons


def scan_file(path: Path) -> list[Candidate]:
    text = path.read_text(encoding="utf-8")
    candidates = []
    for m in P_TAG_RE.finditer(text):
        attrs, inner = m.group(1), m.group(2)
        if "style={{" not in attrs and "style={" not in attrs:
            continue
        score, reasons = score_candidate(attrs, inner, text, m.start(), m.end())
        if score >= 4:
            preview = approx_text(inner)[:60]
            candidates.append(
                Candidate(
                    file=path,
                    line=line_of(text, m.start()),
                    text_preview=preview,
                    score=score,
                    reasons=reasons,
                )
            )
    return candidates


def scan_root(root: Path) -> list[Candidate]:
    all_candidates = []
    for tsx_file in sorted(root.rglob("*.tsx")):
        all_candidates.extend(scan_file(tsx_file))
    return all_candidates


def main(argv: list[str]) -> int:
    if argv:
        root = Path(argv[0])
    else:
        repo_root = Path(__file__).resolve().parent.parent
        root = repo_root / "web" / "app"

    if not root.exists():
        print(f"error: root path does not exist: {root}", file=sys.stderr)
        return 2

    candidates = scan_root(root)

    print(f"check_heading_patterns.py -- scanned {root}")
    print(f"heuristic candidates found: {len(candidates)}")
    print()

    if not candidates:
        print("No candidate styled-<p>-as-heading patterns found.")
        print("Reminder: this is a heuristic, not proof of absence -- still do a manual")
        print("visual read of any new page copy per SKILL.md workflow convention #3.")
        return 0

    for c in sorted(candidates, key=lambda c: -c.score):
        print(f"[score {c.score}] {c.file}:{c.line}")
        print(f"    text: {c.text_preview!r}")
        for r in c.reasons:
            print(f"    - {r}")
        print()

    print(
        "These are NOT confirmed bugs -- review each manually against the file's real "
        "<h1>-<h6> outline. This script is non-blocking and not wired into CI."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
