"""ARI3 v0.0.3 INTEGRITAS release manifest (PREREGISTRATION.md section 9, criterion 5).

v0.0.3 adds no new style model. The style head stays frozen v0.0.2. The release records
both EXP-003 results, the frozen is_forecast head (not used in any count), every
amendment, and the analysis choices that were not in the pre-registration.

usage:
  python src/ari3_v003_release.py check   # read-only: verify every fingerprint, print the manifest
  python src/ari3_v003_release.py write   # once, on the owner's go-ahead: writes models/ari3-v0.0.3/manifest.json
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys

from item_store import ROOT, utc_now

V3 = os.path.join(ROOT, "models", "ari3-v0.0.3")
V2 = os.path.join(ROOT, "models", "ari3-v0.0.2")
OUT = os.path.join(V3, "manifest.json")
PREREG_SHA = "fa65367d3166cba52903229bfd849ce34022b536e93ae6c62341325e7911aff1"
NOTEBOOK_ENTRY = "https://ari3lla.com/ari3/exp-003"
AMENDMENTS = ["AMENDMENT_2026-09-26_findings.md", "AMENDMENT_2026-09-30_holdout_eligibility.md",
              "AMENDMENT_2026-10-02_exp003a_diagnostics.md"]


def text_sha(path):
    """SHA-256 with CRLF normalized to LF, matching the committed file."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def bytes_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def first_commit(rel):
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%h", "--", rel], cwd=ROOT,
                         capture_output=True, text=True).stdout.split()
    return out[-1] if out else None


def build():
    problems = []
    prereg = text_sha(os.path.join(V3, "PREREGISTRATION.md"))
    if prereg != PREREG_SHA:
        problems.append("the pre-registration differs from its committed text")
    with open(os.path.join(V2, "manifest.json"), encoding="utf-8") as f:
        v2 = json.load(f)
    if bytes_sha(os.path.join(V2, "weights.npz")) != v2["sha256"]["weights.npz"]:
        problems.append("v0.0.2 weights differ from their manifest")
    with open(os.path.join(V3, "is_forecast", "manifest.json"), encoding="utf-8") as f:
        fc = json.load(f)
    if bytes_sha(os.path.join(V3, "is_forecast", "weights.npz")) != fc["sha256"]["weights.npz"]:
        problems.append("is_forecast weights differ from their manifest")
    with open(os.path.join(V3, "exp003a", "gold_v1.manifest.json"), encoding="utf-8") as f:
        gold = json.load(f)
    if text_sha(os.path.join(V3, "exp003a", "gold_v1.jsonl")) != gold["gold_sha256"]:
        problems.append("the EXP-003A gold changed")
    with open(os.path.join(V3, "exp003a", "result.json"), encoding="utf-8") as f:
        res = json.load(f)
    if res["gold"]["sha256"] != gold["gold_sha256"] or res["model"]["weights_sha256"] != v2["sha256"]["weights.npz"]:
        problems.append("the EXP-003A result is not bound to this gold and model")
    h = {**{k: {"test": v["test"], "value": v["value"], "verdict": v["verdict"]} for k, v in res["hypotheses"].items()},
         **{k: {"test": v["test"], "value": v["value"],
                "verdict": "SUPPORTED" if v["supported"] else "NOT SUPPORTED"} for k, v in fc["hypotheses"].items()}}
    body = {
        "model": "ARI3", "version": "ari3-v0.0.3", "name": "INTEGRITAS", "motto": "The evidence can be trusted.",
        "released_at": None,
        "what_changed": "No new style model. The style head stays frozen ari3-v0.0.2. v0.0.3 adds a frozen "
                        "is_forecast head that is not used in any count, and the results of EXP-003A and EXP-003B.",
        "preregistration": {"path": "models/ari3-v0.0.3/PREREGISTRATION.md", "commit": "2ff1c53", "sha256": prereg},
        "amendments": {a: {"sha256": text_sha(os.path.join(V3, a)),
                           "commit": first_commit(f"models/ari3-v0.0.3/{a}")} for a in AMENDMENTS},
        "heads": {
            "is_style_signal": {"version": "ari3-v0.0.2", "weights_sha256": v2["sha256"]["weights.npz"],
                                "manifest_sha256": v2["manifest_sha256"], "changed": False},
            "is_forecast": {"path": "models/ari3-v0.0.3/is_forecast/", "weights_sha256": fc["sha256"]["weights.npz"],
                            "manifest_sha256": fc["manifest_sha256"], "used_in_counts": False}},
        "datasets": {
            "exp003a_time_holdout": {"path": gold["gold"], "sha256": gold["gold_sha256"], "n": res["gold"]["n"],
                                     "distribution": res["gold"]["distribution"],
                                     "deck_item_ids_sha256": gold["deck"]["item_ids_sha256"], "seed": 13},
            "exp003b_is_forecast": {"sha256": fc["labels"]["sha256"], "n": fc["labels"]["count"], "seed": 11}},
        "results": {"exp003a": {"path": "models/ari3-v0.0.3/exp003a/result.json",
                                "sha256": text_sha(os.path.join(V3, "exp003a", "result.json")),
                                "commit": first_commit("models/ari3-v0.0.3/exp003a/result.json")},
                    "exp003b": {"path": "models/ari3-v0.0.3/is_forecast/manifest.json",
                                "commit": first_commit("models/ari3-v0.0.3/is_forecast/manifest.json")}},
        "hypotheses": h,
        "claims": ["C-0007", "C-0008", "C-0011", "C-0012", "C-0013"],
        "analysis_choices_not_in_preregistration": [
            "EXP-003A eligibility amended before any label existed: publish time and first-seen time after the "
            "freeze, plus a check against every surviving pre-freeze record (amendment 2026-09-30).",
            "EXP-003A metrics use evaluate() from src/ari3_v002_run.py, the function behind v0.0.2's own results. "
            "The not-sure share counts prediction sets equal to {yes, no}.",
            "EXP-003B probability-ceiling and AUC checks were made after the result (amendment 2026-09-26, post-hoc).",
            "EXP-003A diagnostics were chosen after the result and are descriptive only (amendment 2026-10-02, post-hoc)."],
        "results_notebook_entry": NOTEBOOK_ENTRY,
        "release_criteria": {"1": "pre-registration committed before any label, text unchanged (checked above)",
                             "2": "EXP-003A run once", "3": "EXP-003B run once, head frozen and hashed",
                             "4": "all five hypotheses reported", "5": "results published at the notebook entry",
                             "6": "is_forecast changes no count"},
    }
    return body, problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["check", "write"])
    args = ap.parse_args(argv)
    body, problems = build()
    if problems:
        print("not ready: " + "; ".join(problems), file=sys.stderr)
        return 1
    if args.cmd == "write":
        if os.path.exists(OUT):
            print("not written: the v0.0.3 manifest already exists", file=sys.stderr)
            return 1
        body["released_at"] = utc_now()
        text = json.dumps(body, indent=2, sort_keys=True)
        body["manifest_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        with open(OUT, "x", encoding="utf-8", newline="\n") as f:
            json.dump(body, f, indent=2, sort_keys=True)
    print(json.dumps(body, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
