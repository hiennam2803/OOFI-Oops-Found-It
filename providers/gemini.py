# providers/gemini.py

import requests
from providers.base import BaseProvider
from config import CLOUD_MODELS


class GeminiProvider(BaseProvider):
    """
    Chạy LLM qua Gemini API — miễn phí, quota lớn.
    Dùng requests thuần — không cần SDK.
    """

    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, model: str = "flash", api_key: str = ""):
        self.model_key  = model
        self.api_key    = api_key
        self.model_name = CLOUD_MODELS["gemini"].get(model, CLOUD_MODELS["gemini"]["flash"])

    def chat(self, prompt: str) -> str:
        if not self.api_key:
            return '{"error": "Chưa nhập Gemini API Key. Vào Settings → Cloud."}'
        try:
            url  = self.API_URL.format(model=self.model_name)
            resp = requests.post(
                url,
                params={"key": self.api_key},
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0,
                        "maxOutputTokens": 1024,
                    }
                },
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except requests.exceptions.Timeout:
            return '{"error": "Gemini timeout"}'
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            r = requests.get("https://generativelanguage.googleapis.com", timeout=3)
            return r.status_code < 500
        except Exception:
            return False

    def is_key_format_valid(self) -> bool:
        return bool(self.api_key) and self.api_key.startswith("AIza")

    def get_label(self) -> str:
        return f"🧠 Gemini · {self.model_name}"

    @staticmethod
    def get_signup_url() -> str:
        return "https://aistudio.google.com/apikey"