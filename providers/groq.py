"""
providers/groq.py
AI provider sử dụng Groq Cloud API.
Dùng requests thuần — không phụ thuộc SDK ngoài.
Free tier: 6,000 token/phút, 500,000 token/ngày.
"""

import requests
from providers.base import BaseProvider
from config import CLOUD_MODELS


class GroqProvider(BaseProvider):
    """
    Gọi LLM qua Groq API với tốc độ phản hồi rất nhanh (~2-3 giây).
    Hỗ trợ các model Llama 3 series.
    Đăng ký API key miễn phí tại: https://console.groq.com
    """

    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, model: str = "llama-3.3-70b", api_key: str = ""):
        self.model_key  = model
        self.api_key    = api_key
        self.model_name = CLOUD_MODELS["groq"].get(
            model, CLOUD_MODELS["groq"]["llama-3.3-70b"]
        )

    # ── BaseProvider interface ────────────────────────────

    def chat(self, prompt: str) -> str:
        """Gửi prompt tới Groq API và nhận response."""
        if not self.api_key:
            return '{"error": "Chưa nhập Groq API Key. Vào Settings → Cloud để cấu hình."}'
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
            return '{"error": "Groq API timeout. Vui lòng thử lại."}'
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return '{"error": "Groq API Key không hợp lệ."}'
            if e.response.status_code == 429:
                return '{"error": "Groq API rate limit. Vui lòng chờ một chút."}'
            return f'{{"error": "HTTP {e.response.status_code}: {str(e)}"}}'
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'

    def is_available(self) -> bool:
        """Kiểm tra format API key và kết nối internet."""
        if not self.is_key_format_valid():
            return False
        try:
            r = requests.get("https://api.groq.com", timeout=3)
            return r.status_code < 500
        except Exception:
            return False

    def get_label(self) -> str:
        return f"⚡ Groq · {self.model_name}"

    # ── Extended methods ──────────────────────────────────

    def is_key_format_valid(self) -> bool:
        """Kiểm tra nhanh format key mà không gọi API. Groq key bắt đầu bằng 'gsk_'."""
        return bool(self.api_key) and self.api_key.startswith("gsk_")

    @staticmethod
    def get_signup_url() -> str:
        return "https://console.groq.com"