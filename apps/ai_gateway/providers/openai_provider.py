import json
import os
import urllib.request
from .base import BaseProvider
class OpenAIProvider(BaseProvider):
    provider_name = "openai"
    def __init__(self, model=None):
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    def generate(self, prompt, system_prompt=None, **kwargs):
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY is not configured.")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        body = json.dumps({"model": self.model, "messages": messages, "temperature": 0.4}).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions", data=body,
            headers={"Content-Type": "application/json", "Authorization": "Bearer %s" % key},
            method="POST")
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode())
        return data["choices"][0]["message"]["content"]
