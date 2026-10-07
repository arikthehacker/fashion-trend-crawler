"""ARI3 review: one window for the owner's review work.

Decks, each usable with big touch buttons or the keyboard:
  Style labels   the is_style_signal queue. Keys: Y yes, N no, Space skip,
                 Backspace undo, O open article, Esc menu
  Relevance      EXP-004 relevance judgments (src/rag_review.py). Keys: R relevant,
                 N not relevant, U unsure, Space skip, Backspace back, O open, Esc menu.
                 Answers are appended to the experiment's judgment log.
  Answers        EXP-005 answer review (src/exp005_review.py): one judgment per card,
                 with the cited or supplied evidence in a scrollable panel. Keys shown on the
                 buttons; Space skip, Backspace back, Esc menu.
  Questions      EXP-004 question review (src/rag_questions.py), shown until the set is
                 frozen. No retrieval result is shown. Keys: A approve, E edit, R reject,
                 M ambiguous, D duplicate, Space skip, Backspace back, Esc menu.
  Lexicon        every term in docs/lexicon/terms_v1_draft.md, one card each,
                 with real headlines from the store that contain it
  Report         a prepared weekly report (src/report_prepare.py). "Report decisions": one card
                 per candidate signal with its evidence; choose keep, drop, merge or watchlist,
                 set the labels, list items to remove and write your thoughts. Ctrl+Enter saves.
                 "Report approval" (after Claude applies the decisions) uses the Answers deck:
                 A approve, C change, T to say what should change.

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
from tkinter import messagebox, simpledialog, ttk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from item_store import DEFAULT_DB, assign_split, connect, utc_now  # noqa: E402
import label_tool  # noqa: E402
import exp005_review  # noqa: E402
import exp005_review_v2  # noqa: E402
import rag_questions  # noqa: E402
import rag_review  # noqa: E402
import report_review  # noqa: E402

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


QUEUE_TITLES = {"is_style_signal": "Style labels", AL_QUEUE: "Hard cases (active learning)"}


def load_queue(name):
    with open(label_tool.queue_path(name), encoding="utf-8") as fh:
        return json.load(fh)


def labels_left(con, name="is_style_signal"):
    q = load_queue(name)
    if q.get("kind") == "rag_relevance":
        return rag_review.left(q)
    if q.get("kind") == "gen_review":
        done = (exp005_review_v2.done if q.get("notes") else exp005_review.done)(q)
        return sum(1 for t in q["tasks"] if t["task_id"] not in done), len(q["tasks"])
    if q.get("kind") == "report_decisions":
        return report_review.left(q)
    done = {r[0] for r in con.execute(
        "SELECT item_id FROM labels WHERE task=? AND source='human'", (q["task"],))}
    return sum(1 for i in q["item_ids"] if i not in done), len(q["item_ids"])


def all_queues():
    names = sorted(f[:-5] for f in os.listdir(label_tool.QUEUE_DIR) if f.endswith(".json"))
    return [(n, load_queue(n).get("title") or QUEUE_TITLES.get(n, n)) for n in names]


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
        self.root.unbind("<Control-Return>")
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
        terms = parse_draft()
        review = load_review()
        t_left = sum(1 for t in terms if t["term"] not in review["decisions"])
        decks = []
        for name, title in all_queues():
            q_left, q_total = labels_left(self.con, name)
            kind = load_queue(name).get("kind")
            deck = {"rag_relevance": self.relevance, "gen_review": self.genreview,
                    "report_decisions": self.reportdeck}.get(kind, self.labels)
            decks.append((f"{title}\n{q_left} of {q_total} left", lambda n=name, d=deck: d(n)))
        if not os.path.exists(rag_questions.FROZEN):
            status = rag_questions.review_status()
            q_left = status["decisions"].get("unreviewed", 0) + status["decisions"].get("ambiguous", 0)
            decks.append((f"Question review (EXP-004)\n{q_left} of {status['questions']} open", self.qreview))
        decks.append((f"Lexicon\n{t_left} of {len(terms)} terms left", self.lexicon))
        for text, cmd in decks:
            tk.Button(f, text=text, command=cmd, font=(self.base, 20, "bold"), bg="#ffffff", fg=FG,
                      activebackground="#ffffff", relief="solid", bd=1, pady=26,
                      cursor="hand2").pack(fill="x", pady=6)
        self.label(f, "Keyboard: press the number of a deck (1, 2, 3).", 11, color=DIM, pady=(14, 0))
        keys = {str(i + 1): cmd for i, (_, cmd) in enumerate(decks)}
        self.root.bind("<Key>", lambda e: keys.get(e.char, lambda: None)())

    # Style labels deck --------------------------------------------------
    def labels(self, name="is_style_signal"):
        self.q = load_queue(name)
        if self.q.get("kind") in ("rag_relevance", "gen_review"):  # never answer these as style labels
            messagebox.showerror("Wrong deck", "This queue has its own deck.")
            return self.menu()
        self.task = self.q["task"]
        done = {r[0] for r in self.con.execute(
            "SELECT item_id FROM labels WHERE task=? AND source='human'", (self.task,))}
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
            (item, self.task, value, self.q.get("split") or assign_split(item, self.task), utc_now(),
             self.q.get("item_notes", {}).get(str(item), self.q.get("note"))))
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
        self.con.execute("DELETE FROM labels WHERE item_id=? AND task=? "
                         "AND source='human' AND labeler='ariella'", (last, self.task))
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

    # Relevance deck (EXP-004) --------------------------------------------
    def relevance(self, name):
        self.rq = load_queue(name)
        try:
            self.r_questions = rag_review.frozen_questions()
            for card in self.rq["cards"]:
                rag_review.card_view(card, self.r_questions)
        except (RuntimeError, OSError) as e:
            messagebox.showerror("Deck not opened", str(e))
            return self.menu()
        done = rag_review.judged(self.rq)
        self.r_cards = [c for c in self.rq["cards"] if (c["question_id"], c["item_id"]) not in done]
        self.r_done0 = len(self.rq["cards"]) - len(self.r_cards)
        self.r_hist, self.r_pos = [], 0
        f = self.clear()
        self.buttons(f, [
            [("RELEVANT  (R)", lambda: self.rel_answer("relevant"), "yes"),
             ("NOT RELEVANT  (N)", lambda: self.rel_answer("not_relevant"), "no")],
            [("Unsure  (U)", lambda: self.rel_answer("unsure"), "plain"), ("Skip", self.rel_skip, "plain"),
             ("Back", self.rel_back, "plain")],
            [("Open article", self.rel_open, "plain"), ("Menu", self.menu, "plain")],
        ])
        self.rb_prog = self.label(f, size=11, color=DIM)
        self.label(f, "QUESTION", 10, True, color=ACCENT, pady=(8, 0))
        self.rb_q = self.label(f, size=17, bold=True, pady=(2, 0))
        self.label(f, "FILTERS / CONSTRAINTS", 10, True, color=ACCENT, pady=(10, 0))
        self.rb_filters = self.label(f, size=12, pady=(2, 0))
        self.label(f, "CANDIDATE EVIDENCE", 10, True, color=ACCENT, pady=(14, 0))
        self.rb_meta = self.label(f, size=11, color=DIM, pady=(2, 0))
        self.rb_title = self.label(f, size=18, bold=True, pady=(2, 6))
        self.rb_ex = self.label(f, size=13)
        self.rb_prompt = self.label(f, self.rq.get("question", ""), 14, True, pady=(14, 0))
        self.label(f, self.rq.get("help", ""), 10, color=DIM)
        self.root.bind("<Key>", self.rel_key)
        self.rewrap()
        self.rel_show()

    def rel_current(self):
        return self.r_cards[self.r_pos] if self.r_pos < len(self.r_cards) else None

    def rel_show(self):
        self.rb_prog.config(text=f"{self.r_done0 + len(self.r_hist)} of {len(self.rq['cards'])} judged")
        card = self.rel_current()
        if card is None:
            for w in (self.rb_q, self.rb_filters, self.rb_meta, self.rb_ex):
                w.config(text="")
            self.rb_title.config(text="Queue finished. Judgments are saved.")
            return
        t, ex, domain, day, lang = self.con.execute(
            """SELECT i.title, i.text_excerpt, o.domain, substr(i.published_at,1,10), i.lang
               FROM items i JOIN outlets o USING (outlet_id) WHERE i.item_id=?""", (card["item_id"],)).fetchone()
        view = rag_review.card_view(card, self.r_questions)  # question text from the frozen file
        self.rb_q.config(text=view["question"])
        self.rb_filters.config(text=view["constraints"])
        self.rb_meta.config(text=f"{domain}   {day}   {lang or ''}")
        self.rb_title.config(text=t or "(no title)")
        self.rb_ex.config(text=ex or "")

    def rel_answer(self, value):
        card = self.rel_current()
        if card is None:
            return
        rag_review.record(self.con, self.rq, card, value)
        if card not in self.r_hist:
            self.r_hist.append(card)
        self.r_pos += 1
        self.rel_show()

    def rel_skip(self):
        if self.rel_current() is not None:
            self.r_pos += 1
            self.rel_show()

    def rel_back(self):
        """Show the previous card again. A new answer is appended and replaces the old one."""
        if self.r_pos > 0:
            self.r_pos -= 1
            self.rel_show()

    def rel_open(self):
        card = self.rel_current()
        if card is not None:
            webbrowser.open(self.con.execute("SELECT url FROM items WHERE item_id=?",
                                             (card["item_id"],)).fetchone()[0])

    def rel_key(self, e):
        action = {"r": lambda: self.rel_answer("relevant"), "n": lambda: self.rel_answer("not_relevant"),
                  "u": lambda: self.rel_answer("unsure"), "space": self.rel_skip, "backspace": self.rel_back,
                  "o": self.rel_open, "escape": self.menu}.get(e.keysym.lower())
        if action:
            action()

    # Answer review deck (EXP-005) ----------------------------------------
    def genreview(self, name):
        self.gq = load_queue(name)
        done = (exp005_review_v2.done if self.gq.get("notes") else exp005_review.done)(self.gq)
        self.g_tasks = [t for t in self.gq["tasks"] if t["task_id"] not in done]
        self.g_done0 = len(self.gq["tasks"]) - len(self.g_tasks)
        self.g_pos, self.g_answered = 0, 0
        f = self.clear()
        self.g_bar = tk.Frame(f, bg=BG)
        self.g_bar.pack(side="bottom", fill="x", pady=(10, 0))
        self.gb_prog = self.label(f, size=11, color=DIM)
        self.label(f, "QUESTION", 10, True, color=ACCENT, pady=(8, 0))
        self.gb_q = self.label(f, size=15, bold=True, pady=(2, 0))
        self.gb_prompt = self.label(f, size=14, bold=True, color=ACCENT, pady=(10, 4))
        box = tk.Frame(f, bg=BG)
        box.pack(fill="both", expand=True)
        scroll = tk.Scrollbar(box)
        scroll.pack(side="right", fill="y")
        self.gb_body = tk.Text(box, wrap="word", font=(self.base, 12), bg="#ffffff", fg=FG, relief="solid", bd=1,
                               padx=10, pady=8, yscrollcommand=scroll.set)
        self.gb_body.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.gb_body.yview)
        self.root.bind("<Key>", self.gen_key)
        self.rewrap()
        self.gen_show()

    def gen_current(self):
        return self.g_tasks[self.g_pos] if self.g_pos < len(self.g_tasks) else None

    def gen_show(self):
        for w in self.g_bar.winfo_children():
            w.destroy()
        self.gb_prog.config(text=f"{self.g_done0 + self.g_answered} of {len(self.gq['tasks'])} reviewed")
        task = self.gen_current()
        self.gb_body.config(state="normal")
        self.gb_body.delete("1.0", "end")
        if task is None:
            self.gb_q.config(text="Queue finished. Reviews are saved.")
            self.gb_prompt.config(text="")
            self.gb_body.config(state="disabled")
            tk.Button(self.g_bar, text="Menu", command=self.menu, font=(self.base, 14, "bold")).pack(fill="x")
            return
        self.gb_q.config(text=task["question"])
        self.gb_prompt.config(text=task["prompt"])
        self.gb_body.insert("1.0", task["body"])
        self.gb_body.config(state="disabled")
        row = tk.Frame(self.g_bar, bg=BG)
        row.pack(fill="x", pady=4)
        for i, o in enumerate(task["options"]):
            tk.Button(row, text=f"{o['label']}  ({o['key'].upper()})", command=lambda v=o["value"]: self.gen_answer(v),
                      font=(self.base, 14, "bold"), pady=12, bg="#ffffff", fg=FG, relief="solid", bd=1,
                      cursor="hand2").grid(row=0, column=i, sticky="nsew", padx=4)
            row.grid_columnconfigure(i, weight=1, uniform="g")
        nav = tk.Frame(self.g_bar, bg=BG)
        nav.pack(fill="x", pady=4)
        navs = [("Skip", self.gen_skip), ("Back", self.gen_back), ("Menu", self.menu)]
        if self.gq.get("notes"):
            navs.insert(0, ("Add note  (T)", self.gen_note))
        for i, (text, cmd) in enumerate(navs):
            tk.Button(nav, text=text, command=cmd, font=(self.base, 12), pady=8).grid(row=0, column=i, sticky="nsew",
                                                                                     padx=4)
            nav.grid_columnconfigure(i, weight=1, uniform="n")

    def gen_answer(self, value):
        task = self.gen_current()
        if task is None:
            return
        exp005_review.record(self.gq, task, value)
        self.g_answered += 1
        self.g_pos += 1
        self.gen_show()

    def gen_note(self):
        """An optional reviewer note on the current card (rubric v2). Qualitative only."""
        task = self.gen_current()
        if task is None or not self.gq.get("notes"):
            return
        text = simpledialog.askstring("Reviewer note", "Note (unsupported detail, citation mismatch, omission, "
                                                       "overstatement, causal overreach, other):", parent=self.root)
        if text and text.strip():
            exp005_review_v2.record_note(self.gq, task, text)

    def gen_skip(self):
        if self.gen_current() is not None:
            self.g_pos += 1
            self.gen_show()

    def gen_back(self):
        if self.g_pos > 0:
            self.g_pos -= 1
            self.gen_show()

    def gen_key(self, e):
        k = e.keysym.lower()
        task = self.gen_current()
        if task is not None:
            for o in task["options"]:
                if k == o["key"]:
                    return self.gen_answer(o["value"])
        action = {"space": self.gen_skip, "backspace": self.gen_back, "escape": self.menu,
                  "t": self.gen_note}.get(k)
        if action:
            action()

    # Report decisions deck ------------------------------------------------
    def reportdeck(self, name):
        self.rq = load_queue(name)
        done = report_review.latest(self.rq)
        cards = self.rq["cards"]
        self.r_pos = next((i for i, c in enumerate(cards) if c["kind"] != "report" and c["card_id"] not in done), 0)
        f = self.clear()
        self.r_form = tk.Frame(f, bg=BG)
        self.r_form.pack(side="bottom", fill="x", pady=(8, 0))
        self.r_prog = self.label(f, size=11, color=DIM)
        self.r_title = self.label(f, size=17, bold=True, pady=(4, 4))
        box = tk.Frame(f, bg=BG)
        box.pack(fill="both", expand=True)
        scroll = tk.Scrollbar(box)
        scroll.pack(side="right", fill="y")
        self.r_body = tk.Text(box, wrap="word", font=(self.base, 11), bg="#ffffff", fg=FG, relief="solid", bd=1,
                              padx=10, pady=8, height=10, yscrollcommand=scroll.set)
        self.r_body.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.r_body.yview)
        self.root.bind("<Control-Return>", lambda _e: self.rep_save())
        self.rep_show()

    def rep_current(self):
        cards = self.rq["cards"]
        return cards[self.r_pos] if 0 <= self.r_pos < len(cards) else None

    def rep_field(self, row, col, text, widget):
        tk.Label(self.r_form, text=text, bg=BG, fg=DIM, font=(self.base, 10)).grid(row=row, column=col, sticky="w", padx=4)
        widget.grid(row=row + 1, column=col, sticky="ew", padx=4, pady=(0, 6))
        return widget

    def rep_show(self):
        for w in self.r_form.winfo_children():
            w.destroy()
        left, total = report_review.left(self.rq)
        card = self.rep_current()
        self.r_body.config(state="normal")
        self.r_body.delete("1.0", "end")
        if card is None:
            self.r_prog.config(text=f"{total - left} of {total} decided")
            self.r_title.config(text="End of the deck." if left else "Every card is decided. Tell Claude the report decisions are in.")
            self.r_body.config(state="disabled")
            for i, (text, cmd) in enumerate((("Back", self.rep_back), ("Menu", self.menu))):
                tk.Button(self.r_form, text=text, command=cmd, font=(self.base, 13), pady=8).grid(row=0, column=i, sticky="ew", padx=4)
                self.r_form.grid_columnconfigure(i, weight=1)
            return
        prior = report_review.latest(self.rq).get(card["card_id"], {})
        self.r_prog.config(text=f"Card {self.r_pos + 1} of {len(self.rq['cards'])}  |  {total - left} of {total} decided"
                                + ("  |  saved" if prior else ""))
        self.r_title.config(text={"signal": card.get("name", ""), "duplicate": "Possible duplicates",
                                  "report": "Report-level thoughts"}[card["kind"]])
        self.r_body.insert("1.0", report_review.card_text(card))
        self.r_body.config(state="disabled")
        for c in range(3):
            self.r_form.grid_columnconfigure(c, weight=1, uniform="r")
        box = lambda values, value: ttk.Combobox(self.r_form, values=values, state="readonly", font=(self.base, 11))
        self.r_w = {}
        row = 0
        if card["kind"] == "signal":
            others = [c["signal_id"] for c in self.rq["cards"] if c["kind"] == "signal" and c["signal_id"] != card["signal_id"]]
            baseline = f"baseline ({card['baseline_confidence']})"
            fields = [("decision", "Decision", report_review.DECISIONS, prior.get("decision", "")),
                      ("merge_into", "Merge into (only for merge)", [""] + others, prior.get("merge_into") or ""),
                      ("type", "Type", report_review.SIGNAL_TYPES, prior.get("type") or card["type"]),
                      ("confidence", "Confidence", [baseline] + report_review.CONFIDENCE, prior.get("confidence") or baseline),
                      ("volatility", "Volatility (needed to keep)", report_review.VOLATILITY_LABELS, prior.get("volatility", "")),
                      ("origin", "Origin", report_review.ORIGIN_CLASSIFICATIONS, prior.get("origin") or "unclear")]
            for n, (key, text, values, value) in enumerate(fields):
                w = self.rep_field(row + 2 * (n // 3), n % 3, text, box(values, value))
                w.set(value)
                self.r_w[key] = w
            row += 4
            name = tk.Entry(self.r_form, font=(self.base, 11))
            name.insert(0, prior.get("name") or card["name"])
            self.r_w["name"] = self.rep_field(row, 0, "Name as published", name)
            remove = tk.Entry(self.r_form, font=(self.base, 11))
            remove.insert(0, ", ".join(str(i) for i in prior.get("remove_item_ids") or []))
            self.r_w["remove"] = self.rep_field(row, 1, "Item IDs to remove (comma-separated)", remove)
            row += 2
        elif card["kind"] == "duplicate":
            values = ["one story: count once", "separate pieces: count each"]
            w = self.rep_field(row, 0, "Decision", box(values, ""))
            if "collapse" in prior:
                w.set(values[0] if prior["collapse"] else values[1])
            self.r_w["collapse"] = w
            row += 2
        hint = {"signal": "Your thoughts (for a kept signal they become your editor note)", "duplicate": "Your thoughts (optional)",
                "report": "Your thoughts about the week as a whole (optional)"}[card["kind"]]
        tk.Label(self.r_form, text=hint, bg=BG, fg=DIM, font=(self.base, 10)).grid(row=row, column=0, columnspan=3, sticky="w", padx=4)
        thoughts = tk.Text(self.r_form, wrap="word", font=(self.base, 12), height=5, relief="solid", bd=1, padx=8, pady=6)
        thoughts.insert("1.0", prior.get("thoughts", ""))
        thoughts.grid(row=row + 1, column=0, columnspan=3, sticky="ew", padx=4, pady=(0, 8))
        self.r_w["thoughts"] = thoughts
        nav = tk.Frame(self.r_form, bg=BG)
        nav.grid(row=row + 2, column=0, columnspan=3, sticky="ew")
        for i, (text, cmd, bold) in enumerate((("Save and next  (Ctrl+Enter)", self.rep_save, True), ("Skip", self.rep_skip, False),
                                               ("Back", self.rep_back, False), ("Menu", self.menu, False))):
            tk.Button(nav, text=text, command=cmd, font=(self.base, 13, "bold" if bold else "normal"), pady=10,
                      bg=FG if bold else "#ffffff", fg="#ffffff" if bold else FG, relief="solid", bd=1,
                      cursor="hand2").grid(row=0, column=i, sticky="ew", padx=4)
            nav.grid_columnconfigure(i, weight=2 if bold else 1)

    def rep_save(self):
        card = self.rep_current()
        if card is None:
            return
        w = self.r_w
        payload = {"thoughts": w["thoughts"].get("1.0", "end").strip()}
        if card["kind"] == "signal":
            try:
                remove = [int(x) for x in w["remove"].get().replace(";", ",").split(",") if x.strip()]
            except ValueError:
                messagebox.showerror("Not saved", "Item IDs to remove must be numbers separated by commas.")
                return
            name = w["name"].get().strip()
            payload.update({"decision": w["decision"].get(), "merge_into": w["merge_into"].get() or None,
                            "name": "" if name == card["name"] else name,
                            "type": "" if w["type"].get() == card["type"] else w["type"].get(),
                            "confidence": "" if w["confidence"].get().startswith("baseline") else w["confidence"].get(),
                            "volatility": w["volatility"].get(), "origin": "" if w["origin"].get() == "unclear" else w["origin"].get(),
                            "remove_item_ids": remove})
        elif card["kind"] == "duplicate":
            choice = w["collapse"].get()
            payload["collapse"] = None if not choice else choice.startswith("one story")
        try:
            report_review.record(self.rq, card["card_id"], payload)
        except ValueError as e:
            messagebox.showerror("Not saved", str(e).replace("; ", "\n"))
            return
        self.r_pos += 1
        self.rep_show()

    def rep_skip(self):
        if self.rep_current() is not None:
            self.r_pos += 1
            self.rep_show()

    def rep_back(self):
        if self.r_pos > 0:
            self.r_pos -= 1
            self.rep_show()

    # Question review deck (EXP-004) -------------------------------------
    def qreview(self):
        latest = rag_questions.latest_reviews()
        drafts = rag_questions.load_jsonl(rag_questions.DRAFTS, rag_questions.Question)
        open_first = [q for q in drafts if latest.get(q.question_id) is None
                      or latest[q.question_id].action == "ambiguous"]
        self.qr_list = open_first + [q for q in drafts if q not in open_first]
        self.qr_pos = 0
        f = self.clear()
        self.buttons(f, [
            [("APPROVE  (A)", lambda: self.qr_decide("approve"), "yes"),
             ("REJECT  (R)", lambda: self.qr_decide("reject"), "no")],
            [("Edit  (E)", self.qr_edit, "plain"), ("Ambiguous  (M)", lambda: self.qr_decide("ambiguous"), "plain"),
             ("Duplicate  (D)", self.qr_duplicate, "plain")],
            [("Skip", self.qr_skip, "plain"), ("Back", self.qr_back, "plain"), ("Menu", self.menu, "plain")],
        ])
        self.qb_prog = self.label(f, size=11, color=DIM)
        self.qb_meta = self.label(f, size=11, color=DIM, pady=(6, 0))
        self.qb_q = self.label(f, size=19, bold=True, pady=(4, 8))
        self.qb_detail = self.label(f, size=12)
        self.qb_note = self.label(f, size=11, color=DIM, pady=(8, 0))
        self.qb_state = self.label(f, size=11, color=ACCENT, pady=(8, 0))
        self.root.bind("<Key>", self.qr_key)
        self.rewrap()
        self.qr_show()

    def qr_current(self):
        return self.qr_list[self.qr_pos] if self.qr_pos < len(self.qr_list) else None

    def qr_show(self):
        status = rag_questions.review_status()
        done = status["questions"] - status["decisions"].get("unreviewed", 0)
        self.qb_prog.config(text=f"{done} of {status['questions']} reviewed")
        q = self.qr_current()
        if q is None:
            for w in (self.qb_meta, self.qb_detail, self.qb_note, self.qb_state):
                w.config(text="")
            self.qb_q.config(text="End of the list. Decisions are saved.")
            return
        latest = rag_questions.latest_reviews().get(q.question_id)
        filters = rag_review.describe_filters(q.filters.model_dump(exclude_none=True))
        expected = "answerable" if q.answerable_expected else "unanswerable"
        self.qb_meta.config(text=f"{q.question_id}   {q.query_type}   language {q.language}")
        self.qb_q.config(text=q.question)
        self.qb_detail.config(text=f"Retrieval query: {q.query}\nFilters: {filters}\nDrafted as: {expected}")
        self.qb_note.config(text=f"Draft note: {q.notes}" if q.notes else "")
        self.qb_state.config(text=f"Current decision: {latest.action}" if latest else "Not reviewed yet")

    def qr_save(self, action, **kw):
        q = self.qr_current()
        if q is None:
            return
        try:
            rag_questions.record_review(q.question_id, action, **kw)
        except (ValueError, RuntimeError) as e:
            messagebox.showerror("Not saved", str(e))
            return
        self.qr_pos += 1
        self.qr_show()

    def qr_decide(self, action):
        note = ""
        if action in ("reject", "ambiguous"):
            note = simpledialog.askstring("Note", "Optional note (why):", parent=self.root)
            if note is None:
                return
        self.qr_save(action, note=note)

    def qr_duplicate(self):
        other = simpledialog.askstring("Duplicate", "Duplicate of which question ID (for example q012)?",
                                       parent=self.root)
        if other:
            self.qr_save("duplicate", duplicate_of=other.strip().lower())

    def qr_edit(self):
        q = self.qr_current()
        if q is None:
            return
        text = simpledialog.askstring("Edit question", "Question:", initialvalue=q.question, parent=self.root)
        if text is None:
            return
        query = simpledialog.askstring("Edit question", "Retrieval query:", initialvalue=q.query, parent=self.root)
        if query is None:
            return
        answerable = messagebox.askyesnocancel("Edit question", "Should this question be answerable from the corpus?")
        if answerable is None:
            return
        current = json.dumps(q.filters.model_dump(exclude_none=True, exclude_defaults=True), ensure_ascii=False)
        filters = simpledialog.askstring("Edit question", "Filters as JSON ({} for none):", initialvalue=current,
                                         parent=self.root)
        if filters is None:
            return
        edits = {}
        if text.strip() != q.question:
            edits["question"] = text.strip()
        if query.strip() != q.query:
            edits["query"] = query.strip()
        if answerable != q.answerable_expected:
            edits["answerable_expected"] = answerable
        try:
            new_filters = json.loads(filters or "{}")
        except ValueError:
            messagebox.showerror("Not saved", "The filters are not valid JSON.")
            return
        if new_filters != json.loads(current):
            edits["filters"] = new_filters
        if not edits:
            messagebox.showinfo("No change", "Nothing was changed, so nothing was saved.")
            return
        self.qr_save("edit", edits=edits)

    def qr_skip(self):
        if self.qr_current() is not None:
            self.qr_pos += 1
            self.qr_show()

    def qr_back(self):
        if self.qr_pos > 0:
            self.qr_pos -= 1
            self.qr_show()

    def qr_key(self, e):
        action = {"a": lambda: self.qr_decide("approve"), "r": lambda: self.qr_decide("reject"),
                  "m": lambda: self.qr_decide("ambiguous"), "e": self.qr_edit, "d": self.qr_duplicate,
                  "space": self.qr_skip, "backspace": self.qr_back, "escape": self.menu}.get(e.keysym.lower())
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
