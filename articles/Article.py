from pydantic import BaseModel, Field
from typing import Optional, Dict
from utils import Label


class Article(BaseModel):
    """
    Represents a text article to be analyzed and labeled.

    This structure holds both the raw content and the processing metadata,
    including true and predicted labels, analysis traces, and free-form metadata.
    """

    id: str
    content: Optional[str] = ""
    treated: bool = False
    true_label: Optional[Label] = None
    predicted_label: Optional[Label] = None

    # Optional dictionaries for analysis steps and debug/info metadata
    analysis: Optional[Dict[str, str]] = None
    meta: Optional[Dict[str, str]] = None

    def mark_as_treated(self):
        """
        Mark the article as processed.
        """
        self.treated = True

    def set_label(self, label: Label):
        """
        Set the predicted label for this article.
        """
        self.predicted_label = label

    def add_analysis(self, method: str, result: str):
        """
        Add or update an analysis output (e.g., result of a step).
        """
        if self.analysis is None:
            self.analysis = {}
        self.analysis[method] = result

    def add_metadata(self, key: str, value: str):
        """
        Add or update metadata (e.g., model used, error messages, etc.).
        """
        if self.meta is None:
            self.meta = {}
        self.meta[key] = value

    def short_str(self, max_chars: int = 50) -> str:
        """
        Return a short string preview of the article.
        """
        preview = self.content[:max_chars] + "..." if self.content else "[No content]"
        return f"Article(id={self.id}, label={self.predicted_label}, treated={self.treated}, content={preview})"

    def to_dict(self, include_content: bool = True) -> dict:
        """
        Export the article as a serializable dictionary, with optional content field.
        Converts enum labels and nested fields to strings.
        """
        data = self.model_dump()

        if not include_content:
            data.pop("content", None)

        # Serialize labels and fields
        data["true_label"] = str(self.true_label.value) if self.true_label else None
        data["predicted_label"] = str(self.predicted_label.value) if self.predicted_label else None

        if self.analysis is not None:
            data["analysis"] = {k: str(v) for k, v in self.analysis.items()}

        if self.meta is not None:
            data["meta"] = {k: str(v) for k, v in self.meta.items()}

        return data

    @classmethod
    def from_dict(cls, data: dict, keep_content: bool = True) -> "Article":
        """
        Restore an Article object from a dictionary.
        """
        if not keep_content:
            data.pop("content", None)

        return cls(**data)

    def get_id(self) -> str:
        """
        Return the article's ID.
        """
        return self.id
