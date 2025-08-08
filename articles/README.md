## `articles/` – Article Data Structure

This module defines the central data object used across the entire project: the `Article` class. An `Article` holds the text to be analyzed and all the associated metadata produced during processing.

---

### Purpose

The `Article` object is the input and output unit for all `Analyzer` implementations. It is responsible for:

* Storing raw article text
* Recording the true (ground-truth) label
* Storing predicted labels
* Tracking whether it has been analyzed
* Collecting LLM traces and metadata for debugging or training

---

### Attributes

| Field             | Type                       | Description                                         |
| ----------------- | -------------------------- | --------------------------------------------------- |
| `id`              | `str`                      | Unique identifier of the article                    |
| `content`         | `Optional[str]`            | The article’s full content                          |
| `treated`         | `bool`                     | Whether the article has been analyzed               |
| `true_label`      | `Optional[Label]`          | Ground-truth label (if available)                   |
| `predicted_label` | `Optional[Label]`          | Label predicted by the analyzer                     |
| `analysis`        | `Optional[Dict[str, str]]` | Step-by-step outputs (summary, score, etc.)         |
| `meta`            | `Optional[Dict[str, str]]` | Freeform metadata: error messages, debug info, etc. |

---

### Key Methods

| Method                          | Purpose                                       |
| ------------------------------- | --------------------------------------------- |
| `mark_as_treated()`             | Marks the article as processed                |
| `set_label(label)`              | Sets the predicted label                      |
| `add_analysis(key, value)`      | Adds or updates an analysis step result       |
| `add_metadata(key, value)`      | Adds or updates debugging or trace info       |
| `short_str(max_chars=50)`       | Returns a short preview string of the article |
| `to_dict(include_content=True)` | Converts the article into a dictionary        |
| `from_dict(...)`                | Reconstructs an article from a dictionary     |
| `get_id()`                      | Returns the article ID                        |

---

### Example Usage

```python
article = Article(id="abc123", content="India is participating in the G20 summit.")
article.set_label(Label.POSITIVE)
article.mark_as_treated()
article.add_analysis("summary", "The article discusses India's role in G20.")
article.add_metadata("model", "gpt-4")
```

---

### Related

* Used extensively by all `analyzers/`
* Serialized/deserialized by `loaders/` and CLI entry points
* Label values are defined in `utils.Label`
