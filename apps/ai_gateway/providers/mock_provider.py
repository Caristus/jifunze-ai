from .base import BaseProvider
import logging
logger = logging.getLogger(__name__)
class MockProvider(BaseProvider):
    """Enhanced mock provider for development and testing."""
    def __init__(self):
        self.model = "mock-dev-mode"
    @property
    def provider_name(self) -> str:
        return "mock"
    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        logger.info(f"Mock provider generating response for: {prompt[:50]}...")
        context_preview = kwargs.get("context_preview", "No context provided")
        return f"""I understand you're asking about: {prompt}
Based on the materials available to your school, here's what I found:
{context_preview[:200] if len(context_preview) > 200 else context_preview}
**Key points:**
1. [Relevant concept from your school's resources]
2. [Supporting evidence from uploaded materials]
3. [Connection to your curriculum level]
*Note: This is a development mock. Configure Ollama in AI Settings for production responses.*"""
