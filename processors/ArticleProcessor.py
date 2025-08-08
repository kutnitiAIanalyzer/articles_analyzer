from loaders.AbstractLoader import AbstractLoader
from analyzers.AbstractAnalyzer import AbstractAnalyzer
from articles.Article import Article
from typing import Optional
from tqdm import tqdm


class ArticleProcessor:
    """
    Connects a Loader and an Analyzer to process and label articles in sequence.

    It handles:
    - Iterating over articles using a loader
    - Applying an analyzer to each article
    - Storing results
    - Marking articles as treated
    """

    def __init__(self, loader: AbstractLoader, analyzer: AbstractAnalyzer):
        """
        Initialize the processing pipeline.

        Args:
            loader (AbstractLoader): The source of articles to process.
            analyzer (AbstractAnalyzer): The analyzer to apply to each article.
        """
        self.loader = loader
        self.analyzer = analyzer
        self.results = []
        self.total_processed = 0

    def run(self, limit: Optional[int] = None):
        """
        Process and analyze articles until the loader is exhausted or a limit is reached.

        Args:
            limit (Optional[int]): Maximum number of articles to process. If None, process all.
        """
        total_processed = 0

        iterator = self.loader.iter_articles()
        if limit:
            iterator = tqdm(iterator, total=limit, desc="Processing articles")
        else:
            iterator = tqdm(iterator, desc="Processing articles")

        for article in iterator:
            tqdm.write(f"[INFO] Processing article: {article.id} - {article.meta.get('filename', 'Unknown')}")
            analyzed = self.analyzer.analyze(article)

            self.results.append(analyzed)
            self.total_processed += 1
            total_processed += 1

            self.loader.mark_as_treated(analyzed)

            if limit and total_processed >= limit:
                break

        print(f"[INFO] Processed {total_processed} articles.")
