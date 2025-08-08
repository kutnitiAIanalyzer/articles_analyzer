import gc
from enum import Enum


def liberer_memoire():
    """
    Force garbage collection and free GPU memory if available.

    This function is safe to call even if PyTorch is not installed.
    It is typically called after processing large data batches to
    reduce memory usage.

    Steps:
        1. Trigger Python's garbage collector.
        2. If PyTorch with CUDA is available, empty the GPU cache.
    """
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        # PyTorch is not installed, ignore
        pass


class Label(Enum):
    """
    Enumeration of possible labels for an Article.

    These values are used for both ground-truth (`true_label`)
    and model predictions (`predicted_label`).

    Members:
        UNGRADED (str): Item has not been graded yet.
        IRRELEVANT (str): Content is not relevant to the topic.
        UNCERTAIN (str): Label could not be confidently assigned.
        NEED_HUMAN_REVIEW (str): Requires manual annotation.
        TOO_SHORT (str): Text too short to analyze.
        POSITIVE (str): Positive sentiment/content.
        NEGATIVE (str): Negative sentiment/content.
        NEUTRAL (str): Neutral sentiment/content.
        ERROR (str): An error occurred during processing.
    """

    UNGRADED = "ungraded"
    IRRELEVANT = "irrelevant"
    UNCERTAIN = "uncertain"
    NEED_HUMAN_REVIEW = "need_human_review"
    TOO_SHORT = "too_short"
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    ERROR = "error"

    def __str__(self):
        """Return the string value of the label."""
        return self.value
