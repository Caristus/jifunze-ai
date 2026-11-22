import json
import os
import urllib.request
import urllib.error
from .base import BaseProvider
class OllamaProvider(BaseProvider):
    provider_name = "ollama"
    def __init__(self, model=None, base_url=None):
        self.model = model or os.environ.get("OLLAMA_MODEL", "llama3")
        self.base_url = (base_url or os.environ.get("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
    def generate(self, prompt, system_prompt=None, **kwargs):
        url = self.base_url + "/api/generate"
        body = json.dumps({
            "model": self.model,
            "prompt": (system_prompt + "\n\n" if system_prompt else "") + prompt,
            "stream": False,
        }).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read().decode())
            return data.get("response", "")
        except urllib.error.URLError as e:
            raise ValueError("Ollama connection failed: %s" % str(e)) from e
        except Exception as e:
            raise ValueError("Ollama error: %s" % str(e)) from e
