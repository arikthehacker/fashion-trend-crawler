"""ARI3 review: one window for the owner's review work.

Two decks, each usable with big touch buttons or the keyboard:
  Style labels   the is_style_signal queue. Keys: Y yes, N no, Space skip,
                 Backspace undo, O open article, Esc menu
  Lexicon        every term in docs/lexicon/terms_v1_draft.md, one card each,
                 with real headlines from the store that contain it

Lexicon keys: K keep, D drop, U unsure, N add a note, A add a new term,
Backspace undo, O open the first example article, Esc back to the menu.
Lexicon answers are saved on every keypress to docs/lexicon/terms_v1_review.json.

Run: pythonw src/ari3_review.pyw   (or double-click "ARI3 Review" on the Desktop)
"""

import json
import os
import re
import sys
import tkinter as tk
import webbrowser
from tkinter import font as tkfont
from tkinter import simpledialog

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from item_store import DEFAULT_DB, assign_split, connect, utc_now  # noqa: E402
import label_tool  # noqa: E402

DEV = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANNING = os.path.dirname(DEV)
DRAFT = os.path.join(PLANNING, "docs", "lexicon", "terms_v1_draft.md")
REVIEW = os.path.join(PLANNING, "docs", "lexicon", "terms_v1_review.json")
SKIP_SECTIONS = {"Not included, and why"}
AL_QUEUE = "is_style_signal_al1"

BG, FG, DIM, ACCENT = "#faf8f5", "#1d1b19", "#6b655e", "#8a3b2e"


def parse_draft(path=DRAFT):
    """Return [{term, variants, group, count, warning, note}] from the draft list."""
    terms, group = [], None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip()
        if line.startswith("## "):
            group = line[3:].strip()
            continue
        if not line.startswith("- ") or group is None or group in SKIP_SECTIONS:
            continue
        body = line[2:]
        warning = body.startswith("⚠")
        body = body.lstrip("⚠ ").strip()
        m = re.match(r"(.+?)\s*\(([^)]*)\)\.?\s*(.*)$", body)
        name, count, note = (m.group(1), m.group(2), m.group(3)) if m else (body, "", "")
        variants = [v.strip() for v in name.split("/") if v.strip()]
        terms.append({"term": variants[0], "variants": variants, "group": group,
                      "count": count, "warning": warning, "note": note})
    return terms


def load_review():
    try:
        with open(REVIEW, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"decisions": {}, "added": []}


def save_review(data):
    tmp = REVIEW + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    os.replace(tmp, REVIEW)


def examples(con, variants, limit=3):
    rows = []
    for v in variants:
        pat = re.compile(r"\b" + re.escape(v), re.I)
        for title, excerpt, domain, day, url in con.execute(
                """SELECT i.title, i.text_excerpt, o.domain, substr(i.published_at,1,10), i.url
                   FROM items i JOIN outlets o USING (outlet_id)
                   WHERE i.title LIKE ? OR i.text_excerpt LIKE ?
                   ORDER BY i.published_at DESC LIMIT 40""", (f"%{v}%", f"%{v}%")):
            if pat.search(f"{title} {excerpt or ''}"):
                rows.append((title, domain, day, url))
            if len(rows) >= limit:
                return rows
    return rows


def labels_left(con, name="is_style_signal"):
    with open(label_tool.queue_path(name), encoding="utf-8") as fh:
        q = json.load(fh)
    done = {r[0] for r in con.execute(
        "SELECT item_id FROM labels WHERE task='is_style_signal' AND source='human'")}
    return sum(1 for i in q["item_ids"] if i not in done), len(q["item_ids"])


class App:
    def __init__(self):
        self.con = connect(DEFAULT_DB)
        self.root = tk.Tk()
        self.root.title("ARI3 review")
        self.root.geometry("1000x780")
        self.root.minsize(520, 600)
        self.root.configure(bg=BG)
        self.base = tkfont.nametofont("TkDefaultFont").actual()["family"]
        self.frame = None
        self.wrapped = []
        self.root.bind("<Configure>", self.rewrap)
        self.menu()

    # Layout helpers -----------------------------------------------------
    def clear(self):
        if self.frame:
            self.frame.destroy()
        self.root.unbind("<Key>")
        self.wrapped = []
        self.frame = tk.Frame(self.root, bg=BG)
        self.frame.pack(fill="both", expand=True, padx=24, pady=18)
        return self.frame

    def rewrap(self, _e=None):
        width = max(300, self.root.winfo_width() - 60)
        for w in self.wrapped:
            if w.winfo_exists():
                w.config(wraplength=width)

    def label(self, parent, text="", size=13, bold=False, color=FG, **pack):
        w = tk.Label(parent, text=text, bg=BG, fg=color, justify="left",
                     font=(self.base, size, "bold" if bold else "normal"))
        w.pack(anchor="w", **pack)
        self.wrapped.append(w)
        return w

    def buttons(self, parent, rows):
        """Big touch buttons. rows = [[(text, command, style), ...], ...]"""
        bar = tk.Frame(parent, bg=BG)
        bar.pack(side="bottom", fill="x", pady=(10, 0))
        colors = {"yes": ("#1f6f43", "#ffffff"), "no": ("#8a3b2e", "#ffffff"),
                  "main": (FG, "#ffffff"), "plain": ("#ffffff", FG)}
        for row in rows:
            r = tk.Frame(bar, bg=BG)
            r.pack(fill="x", pady=4)
            for i, (text, cmd, style) in enumerate(row):
                bg, fg = colors[style]
                big = style != "plain"
                b = tk.Button(r, text=text, command=cmd, bg=bg, fg=fg, activebackground=bg,
                              activeforeground=fg, relief="solid", bd=1, cursor="hand2",
                              font=(self.base, 16 if big else 14, "bold"), pady=16 if big else 10)
                b.grid(row=0, column=i, sticky="nsew", padx=4)
                r.grid_columnconfigure(i, weight=1, uniform="b")
        return bar

    # Menu ---------------------------------------------------------------
    def menu(self):
        f = self.clear()
        self.label(f, "ARI3 review", 24, True, pady=(0, 20))
        left, total = labels_left(self.con)
        terms = parse_draft()
        review = load_review()
        t_left = sum(1 for t in terms if t["term"] not in review["decisions"])
        decks = [(f"Style labels\n{left} of {total} left", self.labels)]
        if os.path.exists(label_tool.queue_path(AL_QUEUE)):
            al_left, al_total = labels_left(self.con, AL_QUEUE)
            decks.append((f"Hard cases (active learning)\n{al_left} of {al_total} left",
                          lambda: self.labels(AL_QUEUE)))
        decks.append((f"Lexicon\n{t_left} of {len(terms)} terms left", self.lexicon))
        for text, cmd in decks:
            tk.Button(f, text=text, command=cmd, font=(self.base, 20, "bold"), bg="#ffffff", fg=FG,
                      activebackground="#ffffff", relief="solid", bd=1, pady=26,
                      cursor="hand2").pack(fill="x", pady=8)
        self.label(f, "Keyboard: press the number of a deck (1, 2, 3).", 11, color=DIM, pady=(14, 0))
        keys = {str(i + 1): cmd for i, (_, cmd) in enumerate(decks)}
        self.root.bind("<Key>", lambda e: keys.get(e.char, lambda: None)())

    # Style labels deck --------------------------------------------------
    def labels(self, name="is_style_signal"):
        with open(label_tool.queue_path(name), encoding="utf-8") as fh:
            self.q = json.load(fh)
        done = {r[0] for r in self.con.execute(
            "SELECT item_id FROM labels WHERE task='is_style_signal' AND source='human'")}
        self.l_todo = [i for i in self.q["item_ids"] if i not in done]
        self.l_done0 = len(self.q["item_ids"]) - len(self.l_todo)
        self.l_hist, self.l_pos = [], 0
        f = self.clear()
        self.buttons(f, [
            [("YES  (Y)", lambda: self.lab_answer("yes"), "yes"),
             ("NO  (N)", lambda: self.lab_answer("no"), "no")],
            [("Skip", self.lab_skip, "plain"), ("Undo", self.lab_undo, "plain")],
            [("Open article", self.lab_open, "plain"), ("Menu", self.menu, "plain")],
        ])
        self.lb_prog = self.label(f, size=11, color=DIM)
        self.label(f, self.q["question"], 15, True, pady=(6, 2))
        self.label(f, self.q.get("help", ""), 10, color=DIM)
        self.lb_meta = self.label(f, size=11, color=DIM, pady=(16, 0))
        self.lb_title = self.label(f, size=20, bold=True, pady=(4, 8))
        self.lb_ex = self.label(f, size=13)
        self.root.bind("<Key>", self.lab_key)
        self.rewrap()
        self.lab_show()

    def lab_current(self):
        return self.l_todo[self.l_pos] if self.l_pos < len(self.l_todo) else None

    def lab_show(self):
        self.lb_prog.config(text=f"{self.l_done0 + len(self.l_hist)} of {len(self.q['item_ids'])} labeled")
        item = self.lab_current()
        if item is None:
            self.lb_meta.config(text="")
            self.lb_title.config(text="Queue finished. Answers are saved.")
            self.lb_ex.config(text="")
            return
        t, ex, domain, day, lang = self.con.execute(
            """SELECT i.title, i.text_excerpt, o.domain, substr(i.published_at,1,10), i.lang
               FROM items i JOIN outlets o USING (outlet_id) WHERE i.item_id=?""", (item,)).fetchone()
        self.lb_meta.config(text=f"{domain}   {day}   {lang or ''}")
        self.lb_title.config(text=t or "(no title)")
        self.lb_ex.config(text=ex or "")

    def lab_answer(self, value):
        item = self.lab_current()
        if item is None:
            return
        self.con.execute(
            """INSERT INTO labels (item_id, task, label, source, labeler, split, created_at, note)
               VALUES (?,?,?,'human','ariella',?,?,?)
               ON CONFLICT (item_id, task, source, labeler)
               DO UPDATE SET label=excluded.label, created_at=excluded.created_at, note=excluded.note""",
            (item, "is_style_signal", value, assign_split(item, "is_style_signal"), utc_now(),
             self.q.get("note")))
        self.con.commit()
        self.l_hist.append(item)
        self.l_pos += 1
        self.lab_show()

    def lab_skip(self):
        if self.lab_current() is not None:
            self.l_pos += 1
            self.lab_show()

    def lab_undo(self):
        if not self.l_hist:
            return
        last = self.l_hist.pop()
        self.con.execute("DELETE FROM labels WHERE item_id=? AND task='is_style_signal' "
                         "AND source='human' AND labeler='ariella'", (last,))
        self.con.commit()
        self.l_pos = self.l_todo.index(last)
        self.lab_show()

    def lab_open(self):
        item = self.lab_current()
        if item is not None:
            webbrowser.open(self.con.execute("SELECT url FROM items WHERE item_id=?", (item,)).fetchone()[0])

    def lab_key(self, e):
        action = {"y": lambda: self.lab_answer("yes"), "n": lambda: self.lab_answer("no"),
                  "space": self.lab_skip, "backspace": self.lab_undo, "o": self.lab_open,
                  "escape": self.menu}.get(e.keysym.lower())
        if action:
            action()

    # Lexicon deck -------------------------------------------------------
    def lexicon(self):
        self.terms = parse_draft()
        self.review = load_review()
        self.order = [t for t in self.terms if t["term"] not in self.review["decisions"]]
        self.history = []
        self.pos = 0
        f = self.clear()
        self.buttons(f, [
            [("KEEP (K)", lambda: self.lex_decide("keep"), "yes"),
             ("DROP (D)", lambda: self.lex_decide("drop"), "no"),
             ("UNSURE (U)", lambda: self.lex_decide("unsure"), "main")],
            [("Keep with note", self.lex_note, "plain"), ("Add term", self.lex_add, "plain")],
            [("Undo", self.lex_undo, "plain"), ("Open example", self.lex_open, "plain"),
             ("Menu", self.menu, "plain")],
        ])
        self.l_progress = self.label(f, size=11, color=DIM)
        self.l_group = self.label(f, size=12, color=DIM, pady=(10, 0))
        self.l_term = self.label(f, size=30, bold=True, pady=(2, 0))
        self.l_variants = self.label(f, size=12, color=DIM)
        self.l_warn = self.label(f, size=13, color=ACCENT, pady=(6, 0))
        self.l_ex_head = self.label(f, size=11, bold=True, pady=(16, 2))
        self.l_ex = self.label(f, size=13)
        self.root.bind("<Key>", self.lex_key)
        self.rewrap()
        self.lex_show()

    def lex_current(self):
        return self.order[self.pos] if self.pos < len(self.order) else None

    def lex_show(self):
        self.l_progress.config(text=f"{len(self.review['decisions'])} of {len(self.terms)} terms reviewed")
        t = self.lex_current()
        if t is None:
            for w in (self.l_group, self.l_variants, self.l_warn, self.l_ex_head, self.l_ex):
                w.config(text="")
            self.l_term.config(text="Lexicon finished.")
            self.ex = []
            return
        self.l_group.config(text=t["group"])
        self.l_term.config(text=t["term"])
        extra = t["variants"][1:]
        self.l_variants.config(text=("Variants: " + ", ".join(extra) + "    " if extra else "")
                               + (f"In {t['count']} stored items (count from the draft)" if t["count"] else ""))
        self.l_warn.config(text=("⚠ " + t["note"]) if t["warning"] else t["note"])
        self.ex = examples(self.con, t["variants"])
        self.l_ex_head.config(text="Recent headlines containing it" if self.ex else "No stored headline contains it yet")
        self.l_ex.config(text="\n\n".join(f"{ti}\n{dom}  {day}" for ti, dom, day, _ in self.ex))

    def lex_decide(self, decision, note=None):
        t = self.lex_current()
        if t is None:
            return
        self.review["decisions"][t["term"]] = {
            "decision": decision, "variants": t["variants"], "group": t["group"],
            "note": note, "decided_at": utc_now()}
        save_review(self.review)
        self.history.append(t["term"])
        self.pos += 1
        self.lex_show()

    def lex_note(self):
        t = self.lex_current()
        if t:
            note = simpledialog.askstring("Note", f"Note for “{t['term']}”:", parent=self.root)
            if note:
                self.lex_decide("keep_with_note", note)

    def lex_add(self):
        new = simpledialog.askstring("Add term", "New term (variants separated by /):", parent=self.root)
        if new:
            self.review["added"].append({"variants": [v.strip() for v in new.split("/") if v.strip()],
                                         "added_at": utc_now()})
            save_review(self.review)

    def lex_undo(self):
        if not self.history:
            return
        last = self.history.pop()
        self.review["decisions"].pop(last, None)
        save_review(self.review)
        self.pos = next(i for i, x in enumerate(self.order) if x["term"] == last)
        self.lex_show()

    def lex_open(self):
        if getattr(self, "ex", None):
            webbrowser.open(self.ex[0][3])

    def lex_key(self, e):
        action = {"k": lambda: self.lex_decide("keep"), "d": lambda: self.lex_decide("drop"),
                  "u": lambda: self.lex_decide("unsure"), "n": self.lex_note, "a": self.lex_add,
                  "backspace": self.lex_undo, "o": self.lex_open, "escape": self.menu}.get(e.keysym.lower())
        if action:
            action()


if __name__ == "__main__":
    App().root.mainloop()
