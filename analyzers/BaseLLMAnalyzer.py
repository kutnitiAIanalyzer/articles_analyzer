from abc import abstractmethod
from articles.Article import Article
from utils import Label
import re
from .AbstractAnalyzer import AbstractAnalyzer
from llm.LLMClient import LLMClient


class BaseLLMAnalyzer(AbstractAnalyzer):
    """
    Base class for all LLM-based analyzers.

    This class provides the generic flow for analyzing an article with a language model:
    - Truncate content
    - Build a prompt (to be defined by subclasses)
    - Send it to the LLM
    - Parse the output
    - Store the results in the Article object
    """

    def __init__(self, llm: LLMClient, max_chars: int = 2000):
        """
        Args:
            llm: The language model instance to use (e.g. llama_cpp.Llama)
            max_chars: Max number of characters to send to the model
        """
        self.llm = llm
        self.max_chars = max_chars

    def analyze(self, article: Article) -> Article:
        """
        Main analysis method. Truncates the article, builds a prompt, sends it to the LLM,
        parses the output and updates the article.

        Returns:
            The modified Article object with predictions and metadata.
        """
        content = (article.content or "")[:self.max_chars].strip()
        prompt = self.build_prompt(content)

        try:
            raw_output: str = self.llm(prompt, max_tokens=300, stop=["</s>"])
        except Exception as e:
            article.add_metadata("error", f"LLM call failed: {e}")
            article.set_label(Label.ERROR)
            article.mark_as_treated()
            return article

        parsed = self.parse_output(raw_output)

        for k, v in (parsed.get("analysis") or {}).items():
            article.add_analysis(k, v)
        for k, v in (parsed.get("meta") or {}).items():
            article.add_metadata(k, v)

        article.predicted_label = parsed.get("label", Label.UNCERTAIN)
        article.mark_as_treated()
        return article

    @abstractmethod
    def build_prompt(self, article_text: str) -> str:
        """
        Subclasses must implement this to define how to prompt the LLM.
        """
        pass

    def parse_output(self, output: str) -> dict:
        """
        Extracts metadata and labels from the LLM output.
        Returns a dictionary with keys: label, analysis, meta
        """
        try:
            summary = self._extract_step(output, r"Step\s*1[:\-–]\s*(.*?)(?=\nStep\s*2[:\-–])")
            step2 = self._extract_step(output, r"Step\s*2[:\-–]\s*(.*?)(?=\nStep\s*3[:\-–])")
            politics = "yes" in step2.lower() if step2 else None
            image = self._extract_step(output, r"Step\s*3[:\-–]\s*(.*?)(?=\nStep\s*4[:\-–])")
            score_line = self._extract_step(output, r"Step\s*4[:\-–]\s*Score\s*=\s*(.*)")
            scores = re.findall(r"Score\s*=\s*([+-]?\d+)", output)

            ambiguous = len(set(scores)) > 1
            error = None
            score = None

            if score_line:
                if "unclear" in score_line.lower():
                    error = "unclear"
                else:
                    try:
                        score = int(re.search(r"[+-]?\d+", score_line).group(0))
                    except:
                        error = "invalid_score"

            label = self.infer_label(politics, score, ambiguous, error)

            return {
                "label": label,
                "analysis": {
                    "summary": summary or "",
                    "image": image or "",
                    "score": str(score) if score is not None else "",
                },
                "meta": {
                    "politics": str(politics),
                    "ambiguous": str(ambiguous),
                    "error": error or "",
                    "raw_output": output
                }
            }
        except Exception as e:
            return {
                "label": Label.UNCERTAIN,
                "analysis": {},
                "meta": {
                    "error": f"Parsing failed: {str(e)}",
                    "raw_output": output
                }
            }

    def _extract_step(self, text, pattern):
        """
        Utility to extract a specific step from the LLM output using regex.
        """
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else None

    def infer_label(self, politics, score, ambiguous, error) -> Label:
        """
        Deduce the final label from parsed metadata.
        """
        if politics is False:
            return Label.IRRELEVANT
        if error == "unclear":
            return Label.NEED_HUMAN_REVIEW
        if error or ambiguous:
            return Label.UNCERTAIN
        if score is not None:
            if score <= -1:
                return Label.NEGATIVE
            elif score == 0:
                return Label.NEUTRAL
            elif score >= 1:
                return Label.POSITIVE
        return Label.UNCERTAIN
