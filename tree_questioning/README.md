## `tree_questioning/` – Question Tree Generation and Evaluation

This folder contains tools for designing, exporting, and evaluating decision trees used by the `QuestionnaryAnalyzer`. It serves as an example-based approach to show how articles can be labeled using step-by-step logic via LLMs.

---

### Contents

* `creat_json.ipynb` — Jupyter notebook that builds a decision tree and saves it as `tree.json`
* `tree.json` — JSON file describing the tree structure (nodes, prompts, routing)
* `*.json` — Additional JSON outputs for evaluation (e.g., false positives, false negatives, results)

---

### How It Works

1. **Tree Definition:**

   * Each internal node defines:

     * A `question_name`
     * A `prompt` (used with the LLM)
     * `if_yes` and `if_no` links
   * Each leaf node assigns a final `Label`.

2. **Serialization:**

   * The whole tree is saved in `tree.json`.
   * This file is compatible with `QuestionnaryAnalyzer.build_tree_from_json(...)`

3. **Execution:**

   * Run the analyzer via CLI:

```bash
python main.py --analyzer tree --tree-file tree_questioning/tree.json --treated-file results.json --limit 100
```

4. **Evaluation:**

   * Metrics like accuracy, false positives/negatives are computed.
   * You can export errors for review.

---

### Tree Format Example

```json
{
  "min_size": 300,
  "root": "q1",
  "nodes": {
    "q1": {
      "question_name": "Is India mentioned as a central topic?",
      "prompt": "[INST] ... [/INST]",
      "if_yes": "leaf1",
      "if_no": "leaf2"
    }
  },
  "leaves": {
    "leaf1": "POSITIVE",
    "leaf2": "IRRELEVANT"
  }
}
```

---

### Notes

* This tree logic is used by `QuestionnaryAnalyzer` in `analyzers/`
* Prompts should be clear and binary-oriented (yes/no only)
* Leaf nodes are mapped to the `Label` enum

---

### Related

* See `analyzers/QuestionnaryAnalyzer.py` for execution logic
* See `main.py` for integration
* See `articles/` for how results are saved in `Article` objects
