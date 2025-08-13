from .AbstractAnalyzer import AbstractAnalyzer
from utils import Label
from articles.Article import Article


class QuestionnaryAnalyzer(AbstractAnalyzer):
    """
    Analyzer that uses a yes/no decision tree built from LLM prompts.

    Each node asks the LLM a yes/no question using a formatted prompt,
    then routes the article to a follow-up node depending on the answer.
    Leaf nodes assign a final label.

    The full tree can be built from a structured JSON.
    """

    def __init__(self, llm, prompt: str = None, question_name: str = '', if_no=None, if_yes=None, min_size: int = 0):
        super().__init__()
        self.prompt = prompt
        self.llm = llm
        self.question_name = question_name
        self.if_no = if_no
        self.if_yes = if_yes
        self.min_size = min_size

    def analyze(self, article: Article) -> Article:
        """
        Analyze an article by asking a yes/no question and branching accordingly.
        """
        content = (article.content or "").strip()
        if len(content) < self.min_size:
            article.set_label(Label.TOO_SHORT)
            article.add_metadata("error", f"Content too short: {len(content)} characters")
            article.mark_as_treated()
            return article

        prompt = self.prompt.format(article=content)

        try:
            raw_output: str = self.llm(prompt, max_tokens=300, stop=["</s>"])
        except Exception as e:
            article.add_metadata("error", f"LLM call failed: {e}")
            article.set_label(Label.ERROR)
            article.mark_as_treated()
            return article

        article.add_analysis(self.question_name, raw_output)

        if "yes" in raw_output.lower():
            return self.if_yes.analyze(article)
        elif "no" in raw_output.lower():
            return self.if_no.analyze(article)
        else:
            article.add_metadata("error", f"Invalid response from question '{self.question_name}': {raw_output}")
            article.set_label(Label.ERROR)
            article.mark_as_treated()
            return article

    @staticmethod
    def build_tree_from_json(data: dict, llm) -> AbstractAnalyzer:
        """
        Recursively constructs the tree from a JSON structure.
        """
        node_objects = {}
        min_size = data.get("min_size", 0)

        # Create all leaf nodes
        for leaf_id, label_str in data["leaves"].items():
            node_objects[leaf_id] = leaf(Label[label_str])

        # Create internal nodes without linking branches yet
        for node_id, node_data in data["nodes"].items():
            node_objects[node_id] = QuestionnaryAnalyzer(
                llm=llm,
                prompt=node_data["prompt"],
                question_name=node_data["question_name"],
                if_yes=None,  # Will be set in next loop
                if_no=None,
                min_size=min_size
            )

        # Link child branches
        for node_id, node_data in data["nodes"].items():
            node = node_objects[node_id]
            node.if_yes = node_objects[node_data["if_yes"]]
            node.if_no = node_objects[node_data["if_no"]]

        return node_objects[data["root"]]

    def __str__(self):
        return self.r__str__(0)

    def r__str__(self, level=0):
        """
        Recursive string representation (useful for debugging tree structure).
        """
        ret = "\t" * level + f"$(question_name={self.question_name})\n"
        ret += "\t" * (level + 1) + f"if_yes:\n{self.if_yes.r__str__(level + 1)}\n"
        ret += "\t" * (level + 1) + f"if_no:\n{self.if_no.r__str__(level + 1)}\n"
        ret += "\t" * (level + 1) + "$"
        return ret


class leaf(QuestionnaryAnalyzer):
    """
    Represents a leaf in the decision tree that directly assigns a label.
    """

    def __init__(self, answer: Label):
        self.answer = answer

    def analyze(self, article: Article) -> Article:
        article.set_label(self.answer)
        article.add_metadata("small_content", article.content[:200] if article.content else "")
        article.mark_as_treated()
        article.add_analysis("leaf_answer", str(self.answer.value))
        return article

    def r__str__(self, level=0):
        return "\t" * (level + 1) + f"LEAF: {self.answer.value}\n"
