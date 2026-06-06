# providers/groq.py

import requests
from providers.base import BaseProvider
from config import CLOUD_MODELS


class GroqProvider(BaseProvider):
    """
    Chạy LLM qua Groq API — miễn phí, siêu nhanh.
    Dùng requests thuần — không cần SDK.
    """

    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, model: str = "llama-3.3-70b", api_key: str = ""):
        self.model_key = model
        self.api_key   = api_key
        self.model_name = CLOUD_MODELS["groq"].get(model, CLOUD_MODELS["groq"]["llama-3.3-70b"])

    def chat(self, prompt: str) -> str:
        if not self.api_key:
            return '{"error": "Chưa nhập Groq API Key. Vào Settings → Cloud."}'
        try:
            resp = requests.post(
                self.API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type":  "application/json",
                },
                json={
                    "model":       self.model_name,
                    "messages":    [{"role": "user", "content": prompt}],
                    "temperature": 0,
                    "max_tokens":  1024,
                },
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except requests.exceptions.Timeout:
            return '{"error": "Groq timeout"}'
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'

    def is_available(self) -> bool:
        if not self.is_key_format_valid():
            return False
        try:
            r = requests.get("https://api.groq.com", timeout=3)
            return r.status_code < 500
        except Exception:
            return False

    def is_key_format_valid(self) -> bool:
        return bool(self.api_key) and self.api_key.startswith("gsk_")

    def get_label(self) -> str:
        return f"⚡ Groq · {self.model_name}"

    @staticmethod
    def get_signup_url() -> str:
        return "https://console.groq.com"