## `evaluators/` – Evaluation and Error Analysis

This folder contains tools to measure the quality of predicted labels and to export error datasets for manual review. The main component is `ArticleEvaluator`.

---

### Purpose

* Compute classification metrics (precision, recall, F1) on multi-class labels
* Compute a binary relevance score (relevant vs. irrelevant)
* Export false positives/negatives into JSON files for error inspection

---

### API

```python
class ArticleEvaluator:
    def __init__(self, articles: List[Article]): ...
    def evaluate(self): ...                      # multi-class report + confusion matrix
    def evaluate_binary_relevance(self): ...     # relevance vs. irrelevance
    def export_errors_by_model(output_dir: str = "error_datasets"): ...
```

---

### Expected Labels

The evaluator expects labels defined in `utils.Label`. For binary relevance, the mapping is:

* **relevant**: `POSITIVE`, `NEGATIVE`, `NEUTRAL`
* **irrelevant**: `IRRELEVANT`
* Skipped/ignored: `UNCERTAIN`, `ERROR`, `TOO_SHORT`, `NEED_HUMAN_REVIEW`, `UNGRADED`

---

### Example

```python
from evaluators.ArticleEvaluator import ArticleEvaluator

# Assume `results` is a list[Article] returned by the processing pipeline
Evaluator = ArticleEvaluator(results)
Evaluator.evaluate()                    # multi-class
Evaluator.evaluate_binary_relevance()   # binary relevance
Evaluator.export_errors_by_model()      # writes JSON files under error_datasets/
```

---

### Related

* `articles/` – carries `true_label`, `predicted_label`, and metadata
* `utils.py` – defines the `Label` enum
* `processors/` – creates the `results` list consumed here
