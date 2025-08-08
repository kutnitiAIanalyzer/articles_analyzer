from typing import List, Tuple
from articles.Article import Article
from utils import Label
from sklearn.metrics import classification_report, confusion_matrix
import os
import json


class ArticleEvaluator:
    """
    Compute evaluation metrics for labeled articles and export error datasets.

    This evaluator works in two modes:
    - Multiclass classification report across the Label enum values
    - Binary relevance collapsed into {relevant, irrelevant}

    It also supports exporting misclassified items for manual analysis.
    """

    def __init__(self, articles: List[Article]):
        """
        Initialize the evaluator with a list of processed articles.

        Args:
            articles (List[Article]): Articles that contain both true and predicted labels.
        """
        self.articles = articles

    # ---------- helpers ----------

    def _extract_gold_and_pred(self) -> Tuple[List[str], List[str]]:
        """
        Extract ground-truth and predicted labels as strings, skipping items with missing labels.

        Returns:
            Tuple[List[str], List[str]]: (y_true, y_pred) lists with aligned items.
        """
        y_true, y_pred = [], []
        for a in self.articles:
            if a.true_label is None or a.predicted_label is None:
                continue
            y_true.append(str(a.true_label.value))
            y_pred.append(str(a.predicted_label.value))
        return y_true, y_pred

    # ---------- multiclass ----------

    def evaluate(self) -> None:
        """
        Print a multiclass classification report and confusion matrix.

        This uses all available labeled items where both true and predicted labels exist.
        """
        y_true, y_pred = self._extract_gold_and_pred()
        if not y_true:
            print("[WARN] No items with both true and predicted labels. Skipping multiclass evaluation.")
            return

        labels = sorted(list({*y_true, *y_pred}))
        print("=== Multiclass Classification Report ===")
        print(classification_report(y_true, y_pred, labels=labels, zero_division=0))
        print("=== Confusion Matrix ===")
        print(confusion_matrix(y_true, y_pred, labels=labels))

    # ---------- binary relevance ----------

    @staticmethod
    def _to_binary_rel(label_str: str) -> str:
        """
        Map a Label string to binary relevance.

        Args:
            label_str (str): Label value (e.g., 'positive', 'irrelevant').

        Returns:
            str: 'relevant' | 'irrelevant' | 'skip'
        """
        if label_str in {
            str(Label.POSITIVE.value),
            str(Label.NEGATIVE.value),
            str(Label.NEUTRAL.value),
        }:
            return "relevant"
        if label_str == str(Label.IRRELEVANT.value):
            return "irrelevant"
        return "skip"  # UNCERTAIN, ERROR, TOO_SHORT, NEED_HUMAN_REVIEW, UNGRADED

    def _extract_binary_rel(self) -> Tuple[List[str], List[str]]:
        """
        Extract binary relevance gold/pred vectors, skipping items we cannot score.

        Returns:
            Tuple[List[str], List[str]]: (y_true, y_pred) with values in {'relevant','irrelevant'}.
        """
        y_true_bin, y_pred_bin = [], []
        for a in self.articles:
            if a.true_label is None or a.predicted_label is None:
                continue
            t = self._to_binary_rel(str(a.true_label.value))
            p = self._to_binary_rel(str(a.predicted_label.value))
            if t == "skip" or p == "skip":
                continue
            y_true_bin.append(t)
            y_pred_bin.append(p)
        return y_true_bin, y_pred_bin

    def evaluate_binary_relevance(self) -> None:
        """
        Print a classification report and confusion matrix for binary relevance.
        """
        y_true, y_pred = self._extract_binary_rel()
        if not y_true:
            print("[WARN] No items suitable for binary relevance evaluation.")
            return

        labels = ["relevant", "irrelevant"]
        print("=== Binary Relevance Report ===")
        print(classification_report(y_true, y_pred, labels=labels, zero_division=0))
        print("=== Binary Relevance Confusion Matrix ===")
        print(confusion_matrix(y_true, y_pred, labels=labels))

    # ---------- export errors ----------

    def export_errors_by_model(self, output_dir: str = "error_datasets") -> None:
        """
        Export misclassified items into JSON files grouped by predicted label.

        The exported JSON includes a compact view of each article:
        id, content excerpt, true_label, predicted_label, and useful analysis/meta fields.

        Args:
            output_dir (str): Directory where error JSON files will be written.
        """
        os.makedirs(output_dir, exist_ok=True)

        errors_by_pred = {}  # predicted_label -> list[dict]
        for a in self.articles:
            if a.true_label is None or a.predicted_label is None:
                continue
            t = str(a.true_label.value)
            p = str(a.predicted_label.value)
            if t == p:
                continue  # correct prediction, skip

            item = {
                "id": a.id,
                "true_label": t,
                "predicted_label": p,
                "content": (a.content[:800] + "...") if a.content else "",
                "analysis": a.analysis or {},
                "meta": a.meta or {},
            }
            errors_by_pred.setdefault(p, []).append(item)

        # Write one file per predicted label
        for pred_label, items in errors_by_pred.items():
            out_path = os.path.join(output_dir, f"errors_pred_{pred_label}.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
        print(f"[INFO] Exported error datasets to '{output_dir}/'.")
