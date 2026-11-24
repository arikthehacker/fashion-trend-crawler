"""Screenshots for the "Report definitions (your words)" deck: the real Report decisions card
in ARI3 Review, with the field being defined boxed in red.

The card holds a made-up example candidate, so no real candidate is shown before the editor
decides it. Run on the desktop: a window opens for a few seconds while the shots are taken.

usage: python src/report_definitions_screens.py
"""

import ctypes
import importlib.machinery
import importlib.util
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from item_store import ROOT  # noqa: E402

OUT = os.path.join(ROOT, "editorial", "definitions_screens")
SECTION_FIELD = {"Decision": "decision", "Type": "type", "Confidence": "confidence", "Volatility": "volatility",
                 "Origin": "origin", "Possible duplicates": "collapse", "Rules": None}


def slug(section):
    return section.lower().replace(" ", "_")


def path_for(section):
    return os.path.join(OUT, f"{slug(section)}.png")


def example_queue():
    ev = [{"item_id": 101 + n, "published": f"2026-10-0{n + 1}", "outlet": o, "sector": s,
           "title": f"Example headline {n + 1} about the example term", "url": "https://example.com"}
          for n, (o, s) in enumerate([("example-magazine.com", "editorial"), ("example-shop.com", "retail"),
                                      ("example-runway.com", "designer_runway")])]
    signal = {"card_id": "signal:example-term", "kind": "signal", "signal_id": "example-term", "name": "example term",
              "type": "garment_silhouette", "baseline_confidence": "high", "items": 3, "outlets": 3,
              "sectors": {"editorial": 1, "retail": 1, "designer_runway": 1}, "dates": ["2026-10-01", "2026-10-03"],
              "weaknesses": [], "evidence": ev}
    other = dict(signal, card_id="signal:another-term", signal_id="another-term", name="another term")
    dup = {"card_id": "duplicate:1", "kind": "duplicate", "why": "example: same brand, same day, similar headline",
           "items": [{"item_id": 201, "outlet": "example-magazine.com", "published": "2026-10-02",
                      "signals": ["example term"], "title": "Example story, one edition"},
                     {"item_id": 202, "outlet": "example-magazine.co.uk", "published": "2026-10-02",
                      "signals": ["example term"], "title": "Example story, another edition"}]}
    return {"kind": "report_decisions", "task": "report_example", "title": "Report decisions (EXAMPLE CARD)",
            "report_date": "2026-10-04", "reviews_path": os.path.join(ROOT, "editorial", "_example_never_written.jsonl"),
            "cards": [signal, other, dup, {"card_id": "report", "kind": "report"}], "item_ids": []}


def capture():
    from PIL import ImageDraw, ImageGrab
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # screen and Tk coordinates in the same pixels
    except (AttributeError, OSError):
        pass
    loader = importlib.machinery.SourceFileLoader("ari3_review_app", os.path.join(ROOT, "src", "ari3_review.pyw"))
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader("ari3_review_app", loader))
    loader.exec_module(m)
    q = example_queue()
    m.load_queue = lambda name: q
    m.report_review.latest = lambda queue, reviewer=None: {}  # the example card has no saved answers
    m.report_definitions.panel_text = lambda path=None: "(your definitions appear here, beside every card)"
    app = m.App()
    app.root.geometry("1000x880+20+20")
    app.root.attributes("-topmost", True)
    os.makedirs(OUT, exist_ok=True)
    written = []
    app.reportdeck("example")
    for section, key in SECTION_FIELD.items():
        app.r_pos = 2 if section == "Possible duplicates" else 0
        app.rep_show()
        app.root.update()
        time.sleep(0.6)
        app.root.update()
        r = app.root
        x0, y0 = r.winfo_rootx(), r.winfo_rooty()
        img = ImageGrab.grab(bbox=(x0, y0, x0 + r.winfo_width(), y0 + r.winfo_height()), all_screens=True)
        if key:
            w = app.r_w[key]
            wx, wy = w.winfo_rootx() - x0, w.winfo_rooty() - y0
            pad = 6
            ImageDraw.Draw(img).rectangle([wx - pad, wy - 22, wx + w.winfo_width() + pad, wy + w.winfo_height() + pad],
                                          outline=(220, 0, 0), width=5)
        img.save(path_for(section))
        written.append(path_for(section))
    app.root.destroy()
    return written


if __name__ == "__main__":
    for p in capture():
        print(p)
