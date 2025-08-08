## `processors/` – Processing Pipeline

This folder contains components that orchestrate the flow between data loaders and analyzers. The main class here is `ArticleProcessor`.

---

### Purpose

`ArticleProcessor` runs the core processing loop:

* Retrieves articles from a `Loader`
* Applies an `Analyzer` to each article
* Stores results and marks items as treated

---

### API

```python
class ArticleProcessor:
    def __init__(self, loader: AbstractLoader, analyzer: AbstractAnalyzer): ...
    def run(self, limit: Optional[int] = None): ...
```

* `loader` must implement `AbstractLoader`
* `analyzer` must implement `AbstractAnalyzer`

---

### Example

```python
from loaders.FileLoader import FileLoader
from analyzers.ExpertAnalyzer import ExpertAnalyzer
from processors.ArticleProcessor import ArticleProcessor

loader = FileLoader(data_dir="data/", treated_file="treated_items.json")
analyzer = ExpertAnalyzer(llm)

processor = ArticleProcessor(loader, analyzer)
processor.run(limit=50)
```

---

### Related

* `loaders/` – where articles come from
* `analyzers/` – how articles are labeled
* `evaluators/` – how results are measured
