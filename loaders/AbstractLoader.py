from abc import ABC, abstractmethod
from typing import Iterator, Dict, List
import json
import os
from articles.Article import Article
from utils import liberer_memoire
from tqdm import tqdm

# TODO: TREATED_ITEMS should be a dict of Article objects, not a list, with id as key
# This allows for faster lookups and ensures uniqueness of articles.

class AbstractLoader(ABC):
    """
    Abstract base class for loading Article objects from any data source.

    Responsibilities:
    - Avoid reloading already treated items
    - Track treated articles and persist them to disk
    - Provide batch loading and iteration mechanisms
    """

    def __init__(self, treated_file: str = "treated_items.json", keep_content: bool = False):
        """
        Initialize the loader.

        Args:
            treated_file: Path to the JSON file storing already treated articles.
            keep_content: Whether to retain article content in memory and in treated file.
        """
        self.treated_file = treated_file
        self.keep_content = keep_content
        self.treated_items: Dict[str, Article] = {}

        if os.path.exists(self.treated_file):
            with open(self.treated_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, list):
                        print(f"[ERROR] Expected list in JSON, got {type(data)}. Starting fresh.")
                        data = []
                except json.JSONDecodeError:
                    print(f"[ERROR] Failed to decode JSON. Starting with an empty list.")
                    data = []

            for article_data in data:
                article = Article.from_dict(article_data, keep_content=keep_content)
                self.treated_items[article.get_id()] = article  # Use dict to ensure uniqueness
            print(f"[INFO] Loaded {len(self.treated_items)} treated items from '{self.treated_file}'.")
        else:
            print(f"[WARNING] Treated file '{self.treated_file}' not found. Starting with an empty list.")

    def load_batch(self, batch_size: int = 5) -> List[Article]:
        """
        Load a batch of articles that have not been treated yet.

        Args:
            batch_size: Maximum number of articles to return.

        Returns:
            List of Article objects.
        """
        items = []
        for article in self.iter_articles():
            items.append(article)
            if len(items) >= batch_size:
                break
        if not items:
            print("[INFO] No more items to load.")
        return items

    def iter_articles(self) -> Iterator[Article]:
        """
        Generator yielding untreated articles one at a time.

        Yields:
            Article objects not already marked as treated.
        """
        while True:
            article = self._load_one()
            if article is None:
                break
            yield article

    def mark_as_treated(self, treated_item: Article):
        """
        Mark an article as treated and persist it to file.

        Args:
            treated_item: The article that has been processed.
        """
        article_id = treated_item.get_id()
        if article_id in self.treated_items:
            print(f"[INFO] Article '{article_id}' already marked as treated.")
            return

        self.treated_items[article_id] = treated_item
        treated_list = [
            article.to_dict(include_content=self.keep_content)
            for article in self.treated_items.values()
        ]
        with open(self.treated_file, "w", encoding="utf-8") as f:
            json.dump(treated_list, f, ensure_ascii=False, indent=2)

        tqdm.write(f"[INFO] Total marked {len(self.treated_items)} items as treated.")
        liberer_memoire()

    def get_treated_items(self) -> Dict[str, Article]:
        """
        Return all articles that have already been treated.

        Returns:
            Dictionary of treated articles (id -> Article).
        """
        return self.treated_items

    @abstractmethod
    def _load_one(self) -> Article:
        """
        Load a single article from the data source.

        Returns:
            One Article instance or None if data is exhausted.
        """
        pass

    def delete_treated_items(self):
        """
        Delete the treated items file and clear internal memory.
        """
        if os.path.exists(self.treated_file):
            os.remove(self.treated_file)
            print(f"[INFO] Deleted treated items file: {self.treated_file}")
        else:
            print(f"[WARNING] Treated items file '{self.treated_file}' does not exist.")

        self.treated_items.clear()
        print("[INFO] Cleared in-memory treated items list.")
