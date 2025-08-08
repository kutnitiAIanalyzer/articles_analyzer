## `loaders/` – Data Loading Modules

This folder defines the loading interface and implementation used to fetch `Article` objects from various data sources. All loaders inherit from the `AbstractLoader` base class.

---

### Purpose

Loaders are responsible for:

* Reading raw data (text, CSV, JSON)
* Converting data into `Article` instances
* Avoiding duplicates (using a cache of treated articles)
* Supporting batch or streaming (iterator) loading

---

### Architecture

All loaders inherit from:

```python
class AbstractLoader(ABC):
    def load_batch(batch_size: int) -> List[Article]: ...
    def iter_articles() -> Iterator[Article]: ...
    def mark_as_treated(article: Article): ...
```

The key method to override is:

```python
@abstractmethod
_def _load_one() -> Optional[Article]:_
```

---

### Loaders

| Class            | Description                                                                                                                                  |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `AbstractLoader` | Defines the interface for loading articles and storing treated items in a persistent JSON file. Handles deduplication and memory management. |
| `FileLoader`     | Loads `.txt` articles from a directory. Uses `index.csv` for true labels. Skips articles already treated.                                    |

---

### File Structure Expectations (for `FileLoader`)

```
data/
├── article_001.txt
├── article_002.txt
├── index.csv       # CSV format: filename,label
```

The CSV `index.csv` file should contain two columns:

```
filename,label
article_001.txt,POSITIVE
article_002.txt,IRRELEVANT
```

Labels must match values defined in the `Label` enum.

---

### Example Usage

```python
loader = FileLoader("data/")
for article in loader.load_batch(5):
    print(article.short_str())
    loader.mark_as_treated(article)
```

---

### Related

* See `articles/Article.py` for the article structure
* See `analyzers/` for how articles are processed
* See `exporters/` for saving results
