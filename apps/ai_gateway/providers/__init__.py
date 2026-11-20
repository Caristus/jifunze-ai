from abc import ABC, abstractmethod
from typing import Optional
class BaseProvider(ABC):
    """Abstract base class for AI providers."""
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text from prompt."""
        pass
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider identifier."""
        pass
