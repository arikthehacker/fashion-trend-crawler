# EXP-008 prompt: EXP-007's prompt plus one profile

The prompt is EXP-007's `protocol/prompt_v1.md` (in `experiments/exp-007-report-labeler-alignment/`), built by the same code (`exp007.render`), with exactly two changes. `src/exp008.py` `render` makes them, and refuses to run if either anchor is missing.

1. **[ADDED, changed]** The opening paragraph ends "followed by the editor's definitions and a profile of how the editor decides." instead of "followed by the editor's definitions."
2. **[ADDED, new]** Right after the definitions block, and before the app's save rules on signal cards:

```
HOW THE EDITOR DECIDES (a profile written by an AI from the editor's decisions and thoughts in other weeks, not this one)

<the sealed profile for the card's week, stripped of leading and trailing blank lines>
```

The profile for a card in week W is the one written without week W (leave one week out). The same profile is used in both option orders. Everything else (the card, the form fields, the option lists and their swap, the definitions, the JSON keys, the one retry on an unsaveable answer, the model and its settings) is unchanged from EXP-007's thinking-off reader.
