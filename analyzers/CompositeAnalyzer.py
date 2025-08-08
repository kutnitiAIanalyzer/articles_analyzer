from analyzers.AbstractAnalyzer import AbstractAnalyzer
from articles.Article import Article
from utils import Label
from typing import List


class CompositeAnalyzer(AbstractAnalyzer):
    """
    Analyzer that combines the outputs of multiple analyzers.

    It aggregates predicted labels and scores to produce a final decision.
    Useful to reduce bias or uncertainty by relying on multiple perspectives.

    Aggregation logic:
    - If any analyzer returns IRRELEVANT → IRRELEVANT
    - If any analyzer returns UNCERTAIN → UNCERTAIN
    - If any analyzer returns ERROR → fallback to another non-error label
    - Otherwise, compute the average score and map it to a label
    """

    def __init__(self, analyzers: List[AbstractAnalyzer]):
        self.analyzers = analyzers

    def analyze(self, article: Article) -> Article:
        predictions = []
        scores = []
        errors = []

        # Run all analyzers on the article
        for analyzer in self.analyzers:
            result = analyzer.analyze(article)
            pred = result.predicted_label
            predictions.append(pred)

            score_str = result.analysis.get("score")
            try:
                score = int(score_str) if score_str else None
            except Exception:
                score = None
            scores.append(score)

            error = result.meta.get("error")
            errors.append(error)

        # Save raw predictions and scores
        article.meta["predictions"] = {f"model_{i}": p.value for i, p in enumerate(predictions)}
        article.analysis["scores"] = {f"model_{i}": s for i, s in enumerate(scores)}

        # Aggregation rules
        if Label.UNCERTAIN in predictions:
            final_label = Label.UNCERTAIN
        elif Label.IRRELEVANT in predictions:
            final_label = Label.IRRELEVANT
        elif Label.ERROR in predictions:
            non_error = [p for i, p in enumerate(predictions) if p != Label.ERROR]
            final_label = non_error[0] if non_error else Label.ERROR
        else:
            valid_scores = [s for s in scores if s is not None]
            if valid_scores:
                avg_score = sum(valid_scores) / len(valid_scores)
                article.analysis["average_score"] = avg_score

                if avg_score <= -1:
                    final_label = Label.NEGATIVE
                elif avg_score == 0:
                    final_label = Label.NEUTRAL
                else:
                    final_label = Label.POSITIVE
            else:
                final_label = Label.UNCERTAIN

        article.predicted_label = final_label
        article.mark_as_treated()
        return article
