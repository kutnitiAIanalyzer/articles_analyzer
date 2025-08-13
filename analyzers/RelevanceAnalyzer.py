from analyzers.AbstractAnalyzer import AbstractAnalyzer
from articles.Article import Article
from utils import Label


class RelevanceAnalyzer(AbstractAnalyzer):
    """
    Analyzer that determines whether an article is relevant to India.

    The model is prompted with a structured list of criteria:
    - When is an article considered relevant?
    - When is it clearly irrelevant?

    The output is parsed to assign one of three labels:
    - POSITIVE → relevant to India
    - IRRELEVANT → clearly not relevant
    - UNCERTAIN → not enough information or ambiguous
    """

    def __init__(self, llm, max_chars: int = 2000):
        self.llm = llm
        self.max_chars = max_chars

    def analyze(self, article: Article) -> Article:
        content = (article.content or "")[:self.max_chars].strip()

        prompt = (
            "[INST] You are a relevance classification assistant. Your task is to decide if an article affects "
            "the reader's perception of India — politically, socially, or symbolically.\n\n"
            "An article is RELEVANT if any of the following applies:\n"
            "1. India is one of the main subjects of the article.\n"
            "2. The article focuses on Indian political/institutional figures in a meaningful way.\n"
            "3. India is directly involved (host, participant, target, etc.).\n"
            "4. It discusses Indian foreign/domestic policy or international image.\n"
            "5. It reflects on how India or its institutions are perceived.\n\n"
            "An article is IRRELEVANT if:\n"
            "1. India is briefly mentioned or appears in a list.\n"
            "2. 'India' refers to something else (e.g., hemp, Native Americans).\n"
            "3. The topic is unrelated sports, celebrity gossip, or market data.\n"
            "4. It covers another country's affairs without mentioning India.\n\n"
            "Instructions:\n"
            "Step 1: Summarize the article in 2–3 sentences.\n"
            "Step 2: Is India a main subject? Explain.\n"
            "Step 3: Any exclusion criteria matched? Justify.\n"
            "Step 4: relevancy: [yes/no/missing information] [END]\n\n"
            "Now analyze the following article:\n"
            f"Article:\n{content}\n\n"
            "Your response:\n[/INST]"
        )

        try:
            output: str = self.llm(prompt, max_tokens=300, stop=["</s>"])
        except Exception as e:
            article.add_metadata("error", f"LLM call failed: {e}")
            article.set_label(Label.ERROR)
            article.mark_as_treated()
            return article

        article.analysis = article.analysis or {}
        article.analysis["relevance_answer"] = output

        last_line = output.splitlines()[-1].strip()

        if "yes" in last_line:
            article.predicted_label = Label.POSITIVE
        elif "no" in last_line:
            article.predicted_label = Label.IRRELEVANT
        elif "missing information" in last_line:
            article.predicted_label = Label.UNCERTAIN
        else:
            article.add_metadata("error", "Unrecognized relevance response format")
            article.predicted_label = Label.ERROR

        article.mark_as_treated()
        return article
