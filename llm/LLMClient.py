from abc import ABC, abstractmethod

class LLMClient(ABC):
    """Interface for LLM wrappers."""

    @abstractmethod
    def __call__(self, prompt: str, **kwargs) -> str:
        """Return the raw text output from the model."""
        raise NotImplementedError