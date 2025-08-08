# Project Overview

This project is a modular framework for loading, processing, analyzing, and evaluating text articles. It is organized into clearly defined components, each in its own folder, with `main.py` orchestrating the workflow.

---

## Structure

* **`main.py`** – Entry point. Parses arguments, initializes components, and runs the processing pipeline.
* **`config.py`** – Stores global configuration variables, paths, and environment-driven settings.
* **`utils.py`** – Utility functions and shared enums (`Label`) used across the project.
* **`loaders/`** – Modules for retrieving raw articles from different sources (e.g., text files). Responsible for avoiding duplicates.
* **`articles/`** – Data model (`Article`) representing the content, metadata, and labels of each item.
* **`analyzers/`** – Implementations of analysis strategies to label articles based on their content.
* **`processors/`** – Glue layer between a loader and an analyzer. Runs the pipeline for a batch or stream of articles.
* **`evaluators/`** – Tools to measure model performance and export misclassifications for review.
* **`tree_questioning/`** – Example Jupyter Notebook and generated JSONs for building questionnaires.

---

## Workflow

1. **Load articles** – A loader (e.g., `FileLoader`) reads articles and tracks treated ones.
2. **Analyze articles** – An analyzer processes each article to assign a `predicted_label`.
3. **Process pipeline** – `ArticleProcessor` iterates through loader output, applies the analyzer, and saves results.
4. **Evaluate performance** – `ArticleEvaluator` computes metrics and exports error datasets.

---

## Example Usage

```bash
python main.py --analyzer questionnary \
  --tree-path tree_questioning/tree.json \
  --data-dir data \
  --treated-file treated_items.json \
  --evaluate
```

---

## Extensibility

* **Add new loaders** in `loaders/` by inheriting `AbstractLoader`.
* **Add new analyzers** in `analyzers/` by implementing `AbstractAnalyzer`.
* **Add evaluation methods** in `evaluators/` to support new metrics or export formats.

---

## Related Documentation

Each folder contains its own `README.md` with detailed explanations:

* [loaders/README.md](loaders/README.md)
* [articles/README.md](articles/README.md)
* [analyzers/README.md](analyzers/README.md)
* [processors/README.md](processors/README.md)
* [evaluators/README.md](evaluators/README.md)
