from llama_cpp import Llama
from .LLMClient import LLMClient

class LlamaCppClient(LLMClient):
    """Simple llama-cpp wrapper with overridable call parameters."""

    def __init__(self, model_path: str, **kwargs) -> None:
        self._llama = Llama(model_path=model_path, **kwargs)
        

    # LlamaCppClient.py (only __call__ changed)
    def __call__(self, prompt: str, **gen_kwargs) -> str:
        params = {**gen_kwargs}
        out = self._llama(prompt, **params)

        # Normalize to plain string; raise if we can't.
        if isinstance(out, dict):
            if "choices" in out and out["choices"]:
                text = out["choices"][0].get("text")
                if isinstance(text, str):
                    return text
            if isinstance(out.get("content"), str):
                return out["content"]
            raise ValueError("Unexpected LLM output shape; no text field found.")
        if isinstance(out, str):
            return out
        raise ValueError(f"Unexpected LLM output type: {type(out).__name__}")