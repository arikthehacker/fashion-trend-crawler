"""Rapid human labeling for gold data: one item on screen, one keypress per answer.

A queue is a JSON file in data/store/queues/ naming a task, the question, the
answer keys and the items to show. Answers go straight into the `labels` table
as source='human', with the split fixed by item_store.assign_split.

Usage:
    python src/label_tool.py make-queue is_style_signal --n 300
    python src/label_tool.py label is_style_signal
    python src/label_tool.py label is_style_signal --labeler ariella

Keys while labeling: the answer keys shown on screen, Space to skip,
Backspace to undo the last answer, O to open the article, Esc to quit.
Progress is saved on every keypress, so quitting and resuming loses nothing.
"""

import argparse
import json
import os
import random
import sys
import webbrowser

from item_store import DEFAULT_DB, ROOT, assign_split, connect, utc_now

QUEUE_DIR = os.path.join(ROOT, "data", "store", "queues")

# Built-in task definitions. New tasks are added here or written as queue files.
TASKS = {
    "is_style_signal": {
        "question": "Is this item about style (what people wear, how, and what it is called)?",
        "help": ("Yes: garments, silhouettes, materials, colors, styling, aesthetic terms, "
                 "collections, collaborations described as clothing. "
                 "No: earnings, deals, executive moves, store openings, celebrity news "
                 "with no clothing content. Unsure: skip."),
        "choices": [{"key": "y", "label": "Yes", "value": "yes"},
                    {"key": "n", "label": "No", "value": "no"}],
    },
    "is_forecast": {
        "question": "Does this item predict what will happen, instead of reporting what happened?",
        "help": "Yes: 'will be big', 'trends for 2027', 'predictions'. No: reports, reviews, releases.",
        "choices": [{"key": "y", "label": "Predicts", "value": "yes"},
                    {"key": "n", "label": "Reports", "value": "no"}],
    },
}


def queue_path(name: str) -> str:
    return os.path.join(QUEUE_DIR, f"{name}.json")


def make_queue(con, task: str, n: int, seed: int = 7) -> str:
    """Sample items with an excerpt, stratified by sector so small sectors appear."""
    spec = TASKS[task]
    rows = con.execute(
        """SELECT i.item_id, COALESCE(h.sector_id, 'unclear') AS sector
           FROM items i
           LEFT JOIN outlet_sector_history h
             ON h.outlet_id = i.outlet_id AND h.valid_to IS NULL
           WHERE i.text_excerpt IS NOT NULL AND i.syndicated_of IS NULL
             AND i.item_id NOT IN (SELECT item_id FROM labels WHERE task = ? AND source = 'human')""",
        (task,)).fetchall()
    by_sector = {}
    for item_id, sector in rows:
        by_sector.setdefault(sector, []).append(item_id)
    rng = random.Random(seed)
    for ids in by_sector.values():
        rng.shuffle(ids)
    # Round-robin across sectors until n items are picked.
    picked, pools = [], list(by_sector.values())
    while len(picked) < n and any(pools):
        for pool in pools:
            if pool and len(picked) < n:
                picked.append(pool.pop())
    rng.shuffle(picked)
    os.makedirs(QUEUE_DIR, exist_ok=True)
    path = queue_path(task)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"task": task, **spec, "item_ids": picked}, f, indent=1)
    return path


def run_ui(con, queue: dict, labeler: str) -> None:
    import tkinter as tk
    from tkinter import font as tkfont

    task = queue["task"]
    keys = {c["key"]: c["value"] for c in queue["choices"]}
    done = {r[0] for r in con.execute(
        "SELECT item_id FROM labels WHERE task=? AND source='human' AND labeler=?", (task, labeler))}
    todo = [i for i in queue["item_ids"] if i not in done]
    total = len(queue["item_ids"])
    history = []  # item_ids answered this session, for undo
    state = {"pos": 0}

    root = tk.Tk()
    root.title(f"ARI3LLA labeling: {task}")
    root.geometry("900x560")
    base = tkfont.nametofont("TkDefaultFont").actual()["family"]
    bg, fg, dim = "#faf8f5", "#1d1b19", "#6b655e"
    root.configure(bg=bg)

    q = tk.Label(root, text=queue["question"], font=(base, 13, "bold"), bg=bg, fg=fg,
                 wraplength=840, justify="left")
    q.pack(anchor="w", padx=24, pady=(18, 2))
    tk.Label(root, text=queue.get("help", ""), font=(base, 9), bg=bg, fg=dim,
             wraplength=840, justify="left").pack(anchor="w", padx=24)
    meta = tk.Label(root, font=(base, 9), bg=bg, fg=dim)
    meta.pack(anchor="w", padx=24, pady=(14, 0))
    title = tk.Label(root, font=(base, 17, "bold"), bg=bg, fg=fg, wraplength=840, justify="left")
    title.pack(anchor="w", padx=24, pady=(4, 8))
    excerpt = tk.Label(root, font=(base, 11), bg=bg, fg=fg, wraplength=840, justify="left")
    excerpt.pack(anchor="w", padx=24)
    keyline = "    ".join(f"[{c['key'].upper()}] {c['label']}" for c in queue["choices"])
    tk.Label(root, text=keyline + "    [Space] skip    [Backspace] undo    [O] open    [Esc] quit",
             font=(base, 10, "bold"), bg=bg, fg=fg).pack(side="bottom", pady=14)
    progress = tk.Label(root, font=(base, 10), bg=bg, fg=dim)
    progress.pack(side="bottom")

    def current():
        return todo[state["pos"]] if state["pos"] < len(todo) else None

    def show():
        answered = len(done) + len(history)
        progress.config(text=f"{answered} of {total} labeled")
        item_id = current()
        if item_id is None:
            title.config(text="Queue finished.")
            excerpt.config(text="Close the window. Answers are saved.")
            meta.config(text="")
            return
        row = con.execute(
            """SELECT i.title, i.text_excerpt, o.domain, substr(i.published_at,1,10), i.lang
               FROM items i JOIN outlets o USING (outlet_id) WHERE i.item_id=?""",
            (item_id,)).fetchone()
        t, ex, domain, day, lang = row
        meta.config(text=f"{domain}   {day}   {lang or ''}   item {item_id}")
        title.config(text=t or "(no title)")
        excerpt.config(text=ex or "")

    def answer(value):
        item_id = current()
        if item_id is None:
            return
        con.execute(
            """INSERT INTO labels (item_id, task, label, source, labeler, split, created_at)
               VALUES (?,?,?,'human',?,?,?)
               ON CONFLICT (item_id, task, source, labeler)
               DO UPDATE SET label=excluded.label, created_at=excluded.created_at""",
            (item_id, task, value, labeler, assign_split(item_id, task), utc_now()))
        con.commit()
        history.append(item_id)
        state["pos"] += 1
        show()

    def on_key(e):
        k = e.keysym.lower()
        if k in keys:
            answer(keys[k])
        elif k == "space":
            state["pos"] += 1
            show()
        elif k == "backspace" and history:
            last = history.pop()
            con.execute("DELETE FROM labels WHERE item_id=? AND task=? AND source='human' AND labeler=?",
                        (last, task, labeler))
            con.commit()
            state["pos"] = todo.index(last)
            show()
        elif k == "o" and current() is not None:
            url = con.execute("SELECT url FROM items WHERE item_id=?", (current(),)).fetchone()[0]
            webbrowser.open(url)
        elif k == "escape":
            root.destroy()

    root.bind("<Key>", on_key)
    show()
    root.mainloop()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=DEFAULT_DB)
    sub = ap.add_subparsers(dest="cmd", required=True)
    mq = sub.add_parser("make-queue")
    mq.add_argument("task", choices=sorted(TASKS))
    mq.add_argument("--n", type=int, default=300)
    lb = sub.add_parser("label")
    lb.add_argument("queue")
    lb.add_argument("--labeler", default="ariella")
    args = ap.parse_args(argv)

    con = connect(args.db)
    if args.cmd == "make-queue":
        path = make_queue(con, args.task, args.n)
        n = len(json.load(open(path, encoding="utf-8"))["item_ids"])
        print(f"Wrote {n} items to {path}")
        return 0
    with open(queue_path(args.queue), encoding="utf-8") as f:
        run_ui(con, json.load(f), args.labeler)
    return 0


if __name__ == "__main__":
    sys.exit(main())
