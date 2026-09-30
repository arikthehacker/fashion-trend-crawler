"""Commit guard: staged-secret scan, commit-message authorship check, author identity check.

The local git hooks call it (hooks live in .git/hooks and are never pushed):
    python src/commit_guard.py staged              # pre-commit: scan lines being added
    python src/commit_guard.py identity            # pre-commit: author must be the owner
    python src/commit_guard.py message <msg-file>  # commit-msg: no AI attribution

Exit status 0 means the check passed. 1 means it blocked the commit or could not run,
so a broken check fails closed. Findings name the file, line and rule, never the value.
"""

import glob
import os
import re
import subprocess
import sys

EXPECTED_IDENTITY = "arikthehacker <128088661+arikthehacker@users.noreply.github.com>"

# A local .env value is matched literally only if its variable name looks secret and the
# value is long and not a placeholder. Shorter values produce false positives.
MIN_LOCAL_SECRET_LEN = 12

SECRET_NAME = r"(?:API_?KEY|ACCESS_?KEY|SECRET_?KEY|PRIVATE_?KEY|SECRET|TOKEN|PASSWORD|PASSWD|CREDENTIALS?)"

ENV_ASSIGNMENT = re.compile(r"^\s*(?:export\s+)?([A-Z0-9_]*" + SECRET_NAME + r")\s*=\s*(.*)$")
CODE_LITERAL = re.compile(r"(?i)\b\w*" + SECRET_NAME + r"['\"]?\s*[:=]\s*[rbuf]?(['\"])([^'\"\s]{12,})\1")

PATTERNS = [
    ("authorization", re.compile(r"(?i)\bauthorization\b['\"]?\s*[:=]\s*['\"]?\s*(?:bearer|basic|token)\s+"
                                 r"[A-Za-z0-9._~+/=-]{12,}")),
    ("bearer_token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{20,}")),
    ("known_prefix", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}"
                                r"|\bsk-(?:proj|svcacct|admin)-[A-Za-z0-9_-]{20,}"
                                r"|\bsk-[A-Za-z0-9]{32,}"
                                r"|\bgh[pousr]_[A-Za-z0-9]{36,}"
                                r"|\bgithub_pat_[A-Za-z0-9_]{22,}"
                                r"|\bAKIA[0-9A-Z]{16}\b"
                                r"|\bAIza[0-9A-Za-z_-]{35}"
                                r"|\bhf_[A-Za-z0-9]{30,}"
                                r"|\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("private_key", re.compile("-----BEGIN " + r"(?:[A-Z0-9]+ )*" + "PRIVATE KEY-----")),
]

# Values that point at a secret instead of containing one.
REFERENCE = re.compile(r"^(?:\$|os\.environ|os\.getenv|getenv\(|process\.env|env\(|None$|null$|[A-Z][A-Z0-9_]*$)")
PLACEHOLDER = re.compile(r"(?i)^(?:<.*>|your[-_].*|.*example.*|changeme|xxx+|true|false|\d+)$")

VENDORS = r"(?:claude|anthropic|chatgpt|openai|deepseek|copilot|gemini)"
MESSAGE_RULES = [
    ("attribution_trailer", re.compile(r"(?i)^\s*(?:co-authored-by|generated-by|assisted-by|created-by|written-by)\s*:")),
    ("generated_by_ai", re.compile(r"(?i)\b(?:generated|created|written|authored|produced)\s+(?:with|by|using)\b.{0,40}"
                                   r"(?:\b" + VENDORS + r"\b|\bgpt\b|\ban? ai\b|\bai\b|\bllm\b)")),
    ("ai_marker", re.compile(r"(?i)noreply@anthropic\.com|noreply@openai\.com|claude-session:|claude\.com/claude-code"
                             "|\U0001F916")),
]
TRAILER = re.compile(r"^[A-Za-z][A-Za-z0-9-]*:\s+\S")
VENDOR = re.compile(r"(?i)\b" + VENDORS + r"\b")


def _unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        value = value[1:-1]
    return value.strip()


def scan_line(line, local_values=()):
    """Rule names that match one added line. Never returns the matched text."""
    hits = []
    m = ENV_ASSIGNMENT.match(line)
    if m:
        value = _unquote(m.group(2).split(" #")[0])
        if value and not REFERENCE.match(value):
            hits.append("env_assignment")
    m = CODE_LITERAL.search(line)
    if m and not REFERENCE.match(m.group(2)) and "{" not in m.group(2):  # "{" marks an f-string or template
        hits.append("code_literal")
    hits += [name for name, pattern in PATTERNS if pattern.search(line)]
    if any(v in line for v in local_values):
        hits.append("local_env_value")
    return sorted(set(hits))


def added_lines(diff_text):
    """(path, line number, text) for every added line of a `git diff -U0` patch.
    Binary files are skipped."""
    path, lineno = None, 0
    for raw in diff_text.splitlines():
        if raw.startswith("+++ "):
            target = raw[4:]
            path = None if target == "/dev/null" else target[2:] if target.startswith("b/") else target
        elif raw.startswith("@@"):
            m = re.search(r"\+(\d+)", raw)
            lineno = int(m.group(1)) if m else 0
        elif raw.startswith("+") and path is not None:
            yield path, lineno, raw[1:]
            lineno += 1


def local_secret_values(roots):
    """Values of secret-named variables in local .env files under the given folders."""
    values = set()
    for root in roots:
        for pattern in (".env", ".env.*", os.path.join("web", ".env"), os.path.join("web", ".env.*")):
            for path in glob.glob(os.path.join(root, pattern)):
                if path.endswith(".example") or not os.path.isfile(path):
                    continue
                with open(path, encoding="utf-8", errors="replace") as f:
                    for line in f:
                        m = re.match(r"^\s*(?:export\s+)?([A-Za-z0-9_]+)\s*=\s*(.*)$", line)
                        if not m or not re.search(SECRET_NAME, m.group(1), re.I):
                            continue
                        value = _unquote(m.group(2))
                        if (len(value) >= MIN_LOCAL_SECRET_LEN and not PLACEHOLDER.match(value)
                                and len(set(value)) > 1):
                            values.add(value)
    return values


def scan_diff(diff_text, local_values=()):
    return [(path, lineno, rule) for path, lineno, text in added_lines(diff_text)
            for rule in scan_line(text, local_values)]


def check_message(text):
    """(line number, rule) for each attribution found in a commit message."""
    lines = text.splitlines()
    found = [(i, name) for i, line in enumerate(lines, 1) if not line.startswith("#")
             for name, rule in MESSAGE_RULES if rule.search(line)]
    paragraphs, current = [], []
    for i, line in enumerate(lines, 1):
        if line.startswith("#"):
            continue
        if line.strip():
            current.append((i, line))
        elif current:
            paragraphs.append(current)
            current = []
    if current:
        paragraphs.append(current)
    if len(paragraphs) > 1:
        found += [(i, "vendor_trailer") for i, line in paragraphs[-1] if TRAILER.match(line) and VENDOR.search(line)]
    return sorted(set(found))


def _git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=True).stdout.decode("utf-8", "replace")


def repo_roots(cwd=None):
    """The worktree being committed, plus the main checkout that owns the git folder."""
    top = _git("rev-parse", "--show-toplevel", cwd=cwd).strip()
    common = os.path.abspath(os.path.join(top, _git("rev-parse", "--git-common-dir", cwd=cwd).strip()))
    return sorted({os.path.normpath(top), os.path.normpath(os.path.dirname(common))})


def cmd_staged(cwd=None):
    diff = _git("-c", "core.quotepath=off", "diff", "--cached", "-U0", "--no-color", "--no-ext-diff",
                "--diff-filter=ACMR", cwd=cwd)
    findings = scan_diff(diff, local_secret_values(repo_roots(cwd)))
    for path, lineno, rule in findings:
        print(f"secret check: possible credential in {path}:{lineno} (rule: {rule})", file=sys.stderr)
    if findings:
        print("BLOCKED: remove the value from the staged content. Do not bypass this check.", file=sys.stderr)
    return 1 if findings else 0


def cmd_identity(cwd=None):
    ident = re.sub(r"\s+\d+\s+[+-]\d{4}$", "", _git("var", "GIT_AUTHOR_IDENT", cwd=cwd).strip())
    if ident != EXPECTED_IDENTITY:
        print(f"BLOCKED: commit author is {ident!r}, expected {EXPECTED_IDENTITY!r}. "
              "Git identity is never changed automatically.", file=sys.stderr)
        return 1
    return 0


def cmd_message(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        findings = check_message(f.read())
    for lineno, rule in findings:
        print(f"commit message: line {lineno} (rule: {rule})", file=sys.stderr)
    if findings:
        print("BLOCKED: commit messages carry no AI co-author or attribution lines.", file=sys.stderr)
    return 1 if findings else 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        if argv[:1] == ["staged"]:
            return cmd_staged()
        if argv[:1] == ["identity"]:
            return cmd_identity()
        if argv[:1] == ["message"] and len(argv) == 2:
            return cmd_message(argv[1])
        print(__doc__, file=sys.stderr)
        return 1
    except Exception as e:  # fail closed, without echoing content that might hold a secret
        print(f"BLOCKED: commit guard could not run ({type(e).__name__}).", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
