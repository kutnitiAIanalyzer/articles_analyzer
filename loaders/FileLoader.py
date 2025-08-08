from .AbstractLoader import AbstractLoader
from articles.Article import Article
import os
from typing import List
import pandas as pd
from utils import Label


class FileLoader(AbstractLoader):
    """
    Loads Article objects from a directory of .txt files, using an index CSV for labels.

    Expects:
    - Each article as a .txt file in `data_dir`
    - An optional `index.csv` file mapping filenames to true labels

    Skips already treated articles using the logic from AbstractLoader.
    """

    def __init__(self, data_dir: str = "../data", treated_file: str = "treated_items.csv"):
        """
        Initialize the file loader.

        Args:
            data_dir (str): Path to the directory containing text files and index.csv.
            treated_file (str): Path to JSON file storing already treated articles.
        """
        super().__init__(treated_file)
        self.data_dir = data_dir

        index_path = os.path.join(data_dir, "index.csv")
        if os.path.exists(index_path):
            index_df = pd.read_csv(index_path)
            # Build a mapping from file basename (without .txt) to label string
            self.index = {
                str(row["filename"])[:-4]: row["label"]
                for _, row in index_df.iterrows()
                if pd.notna(row["label"])
            }
        else:
            print(f"[WARNING] index.csv not found in {data_dir}")
            self.index = {}

        print(f"[INFO] Loaded index with {len(self.index)} items from '{index_path}'.")

    def _get_untreated_filenames(self) -> List[str]:
        """
        Get the list of .txt files in the data directory that have not been treated yet.

        Returns:
            List of untreated filenames (including .txt extension).
        """
        treated_ids = {id for id in self.treated_items.keys()}
        all_txt_files = [f for f in os.listdir(self.data_dir) if f.endswith('.txt')]
        return [f for f in all_txt_files if f[:-4] not in treated_ids]

    def _load_one(self) -> Article:
        """
        Load one untreated article from disk.

        Returns:
            An Article object, or None if no untreated files remain.
        """
        untreated_files = self._get_untreated_filenames()
        if not untreated_files:
            return None

        file_name = untreated_files[0]
        article_id = file_name[:-4]
        file_path = os.path.join(self.data_dir, file_name)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Use the label from the index if available
        label_str = self.index.get(article_id, "").lower()
        true_label = Label(label_str) if label_str in Label._value2member_map_ else None

        return Article(
            id=article_id,
            content=content,
            true_label=true_label,
            meta={"filename": file_name}
        )
