from abc import ABC, abstractmethod
from articles.Article import Article


class AbstractAnalyzer(ABC):
    """
    Interface for all article analyzers.

    Any class implementing this interface must provide a method `analyze`,
    which takes an Article instance, processes it, and returns the modified Article.

    This is the base contract used by all analyzer strategies, including
    LLM-based, rule-based, or tree-based analyzers.
    """

    @abstractmethod
    def analyze(self, article: Article) -> Article:
        """
        Analyze the given article and return a modified version.

        This method may update fields such as:
        - predicted_label
        - treated status
        - analysis results
        - metadata

        Args:
            article (Article): The article to be analyzed.

        Returns:
            Article: The updated article after analysis.
        """
        pass
