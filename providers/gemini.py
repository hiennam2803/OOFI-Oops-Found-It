"""
providers/gemini.py
AI provider sử dụng Google Gemini API.
Dùng requests thuần — không phụ thuộc SDK ngoài.
Gemini 2.5 Flash: context window 1,000,000 token, miễn phí quota lớn.
"""

import requests
from providers.base import BaseProvider
from config import CLOUD_MODELS


class GeminiProvider(BaseProvider):
    """
    Gọi LLM qua Gemini API.
    Ưu điểm so với Groq: context window cực lớn (1M token),
    phù hợp cho tác vụ tóm tắt tài liệu dài.
    Đăng ký API key miễn phí tại: https://aistudio.google.com/apikey
    """

    API_URL = (
        "https://generativelanguage.googleapis.com"
        "/v1beta/models/{model}:generateContent"
    )

    def __init__(self, model: str = "flash", api_key: str = ""):
        self.model_key  = model
        self.api_key    = api_key
        self.model_name = CLOUD_MODELS["gemini"].get(
            model, CLOUD_MODELS["gemini"]["flash"]
        )

    # ── BaseProvider interface ────────────────────────────

    def chat(self, prompt: str) -> str:
        """Gửi prompt tới Gemini API và nhận response."""
        if not self.api_key:
            return '{"error": "Chưa nhập Gemini API Key. Vào Settings → Cloud để cấu hình."}'
        try:
            url  = self.API_URL.format(model=self.model_name)
            resp = requests.post(
                url,
                params={"key": self.api_key},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature":    0,
                        "maxOutputTokens": 1024,
                    },
                },
                timeout=30,
            )
            resp.raise_for_status()
            return (
                resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            )
        except requests.exceptions.Timeout:
            return '{"error": "Gemini API timeout. Vui lòng thử lại."}'
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                return '{"error": "Gemini API Key không hợp lệ hoặc request sai định dạng."}'
            if e.response.status_code == 429:
                return '{"error": "Gemini API rate limit. Vui lòng chờ một chút."}'
            return f'{{"error": "HTTP {e.response.status_code}: {str(e)}"}}'
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'

    def is_available(self) -> bool:
        """Kiểm tra API key tồn tại và có kết nối internet."""
        if not self.api_key:
            return False
        try:
            r = requests.get(
                "https://generativelanguage.googleapis.com", timeout=3
            )
            return r.status_code < 500
        except Exception:
            return False

    def get_label(self) -> str:
        return f"🧠 Gemini · {self.model_name}"

    # ── Extended methods ──────────────────────────────────

    def is_key_format_valid(self) -> bool:
        """Kiểm tra nhanh format key. Gemini key bắt đầu bằng 'AIza'."""
        return bool(self.api_key) and self.api_key.startswith("AIza")

    @staticmethod
    def get_signup_url() -> str:
        return "https://aistudio.google.com/apikey"