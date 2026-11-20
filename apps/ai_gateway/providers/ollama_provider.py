from .base import BaseProvider
import requests
import logging
logger = logging.getLogger(__name__)
class OllamaProvider(BaseProvider):
    """Ollama local inference provider for offline-capable schools."""
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self.base_url = base_url.rstrip("/")
        self.model = model
    @property
    def provider_name(self) -> str:
        return "ollama"
    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        logger.info(f"Ollama provider calling {self.model} for: {prompt[:50]}...")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False},
                timeout=60
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}.")
            return "[Ollama is not available. Please start Ollama with: ollama serve]"
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return f"[Ollama error: {str(e)}]"
