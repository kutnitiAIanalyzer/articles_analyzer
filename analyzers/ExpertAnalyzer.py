from .BaseLLMAnalyzer import BaseLLMAnalyzer


class ExpertAnalyzer(BaseLLMAnalyzer):
    """
    Analyzer that simulates a neutral media expert specialized in Indian geopolitics.

    It asks the LLM to:
    1. Summarize the article
    2. Assess its relevance to Indian affairs
    3. Describe the image it projects about India
    4. Assign a sentiment score from -2 to +2
    """

    def build_prompt(self, article_text: str) -> str:
        """
        Constructs the prompt sent to the LLM.
        """
        return (
            "[INST] You are a neutral media analyst specialized in Indian geopolitics.\n"
            "Read the following article and answer the four questions below, step by step.\n"
            "Base your analysis on the facts reported, how India is portrayed, and the implications for India's image — not just the tone.\n"
            "If the article does not allow you to form a clear judgment of India's image, you may answer 'Unclear' and skip scoring.\n\n"

            "Step 1 — Summarize:\n"
            "Summarize the article in 2–3 sentences.\n\n"

            "Step 2 — Relevance:\n"
            "Is the article relevant to Indian politics, society, international image, or government actions? (Yes / No). Justify briefly.\n\n"

            "Step 3 — Projected Image:\n"
            "What kind of image of India does the article convey? Be honest — if you can't say, explain why.\n\n"

            "Step 4 — Sentiment Score:\n"
            "Assign a score from -2 to +2 only if appropriate:\n"
            "-2 = strongly negative image\n"
            "-1 = somewhat negative\n"
            " 0 = neutral or unclear\n"
            "+1 = somewhat positive\n"
            "+2 = strongly positive image\n"
            "If no clear image is conveyed, write: Score = Unclear - [Justification]\n\n"

            "Please format your response like this:\n"
            "Step 1: [...]\n"
            "Step 2: [Yes/No] - [...]\n"
            "Step 3: [...]\n"
            "Step 4: Score = [score or 'Unclear'] - [...]\n\n"

            f"Article:\n{article_text}\n\n"
            "Your response: [/INST]"
        )
