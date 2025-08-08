from .BaseLLMAnalyzer import BaseLLMAnalyzer


class NaiveAnalyzer(BaseLLMAnalyzer):
    """
    Analyzer simulating a thoughtful but non-expert reader.

    This prompt is designed to reflect how an ordinary person might perceive
    the article’s tone and image of India, without requiring deep political knowledge.
    """

    def build_prompt(self, article_text: str) -> str:
        """
        Constructs the prompt sent to the LLM for naive analysis.
        """
        return (
            "[INST] Imagine you are a thoughtful, open-minded person with no strong opinion about India.\n"
            "After reading the following article, reflect honestly on the image of India it gives you.\n"
            "If the article doesn't clearly influence your perception — if it's too vague, technical, or off-topic —\n"
            "it's okay to say that you don’t know or can’t form an opinion. In that case, don’t assign a score.\n\n"

            "Step 1: Summarize the article in 2–3 sentences.\n"
            "Step 2: Is the article related to India? (Yes / No). Explain.\n"
            "Step 3: What impression of India does the article give you? If none, explain why.\n"
            "Step 4: If the article clearly shapes your impression, give a score from -2 to +2:\n"
            "-2 = very negative impression\n"
            "-1 = somewhat negative\n"
            " 0 = mixed or unclear\n"
            "+1 = somewhat positive\n"
            "+2 = very positive\n"
            "If you cannot form an opinion, write: Score = Unclear - [explain why]\n\n"

            "Format your answer like this:\n"
            "Step 1: [...]\n"
            "Step 2: [Yes/No] - [...]\n"
            "Step 3: [...]\n"
            "Step 4: Score = [one of -2, -1, 0, +1, +2, or Unclear] - [...]\n\n"

            f"Article:\n{article_text}\n\n"
            "Your response: [/INST]"
        )
