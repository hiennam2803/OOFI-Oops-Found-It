"""
providers/local.py
AI provider chạy offline qua Ollama.
Tự động phát hiện GPU (NVIDIA/AMD) và ưu tiên sử dụng nếu có.
"""

import requests
import subprocess
from providers.base import BaseProvider
from config import LOCAL_MODELS, get_active_tier


class LocalProvider(BaseProvider):
    """
    Chạy LLM trực tiếp trên máy người dùng qua Ollama API.
    - Hoàn toàn offline, không giới hạn số lượng câu hỏi.
    - Tự detect GPU: NVIDIA (nvidia-smi) hoặc AMD (rocminfo).
    - Fallback về CPU nếu không có GPU.
    """

    def __init__(self, tier: str = "normal", ollama_url: str = "http://localhost:11434"):
        if tier not in LOCAL_MODELS:
            raise ValueError(
                f"Tier không hợp lệ: '{tier}'. "
                f"Các tier hợp lệ: {list(LOCAL_MODELS.keys())}"
            )
        self.tier       = tier
        self.ollama_url = ollama_url
        self.config     = LOCAL_MODELS[tier]

    # ── BaseProvider interface ────────────────────────────

    def chat(self, prompt: str) -> str:
        """
        Gửi prompt tới Ollama /api/generate và nhận response.
        Dùng cho các lệnh thông thường — trả về JSON tool call.
        """
        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model":  self.config["name"],
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_ctx":     self.config["num_ctx"],
                        "num_thread":  4,
                        "num_gpu":     self._detect_gpu(),
                        "temperature": 0,
                    },
                },
                timeout=120,
            )
            resp.raise_for_status()
            return resp.json().get("response", "").strip()
        except requests.exceptions.Timeout:
            return '{"error": "Ollama timeout — model xử lý quá lâu, thử lại sau."}'
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'

    def is_available(self) -> bool:
        """Kiểm tra Ollama server đang chạy."""
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def get_label(self) -> str:
        gpu = "GPU" if self._detect_gpu() > 0 else "CPU"
        return f"💻 Local · {self.config['name']} · {gpu}"

    # ── Extended methods ──────────────────────────────────

    def chat_raw(self, system: str, user: str) -> str:
        """
        Gửi request tới /api/chat với system prompt tùy chỉnh.
        Dùng cho tác vụ tóm tắt — tránh model trả về JSON
        do bị ảnh hưởng từ system prompt mặc định.
        """
        try:
            resp = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model":  self.config["name"],
                    "stream": False,
                    "options": {
                        "num_ctx":     self.config["num_ctx"],
                        "num_thread":  4,
                        "num_gpu":     self._detect_gpu(),
                        "temperature": 0,
                    },
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user",   "content": user},
                    ],
                },
                timeout=120,
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"].strip()
        except Exception as e:
            return f"[Lỗi gọi Ollama: {e}]"

    def is_model_downloaded(self) -> bool:
        """Kiểm tra model đã được tải về chưa."""
        try:
            resp   = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            models = [m["name"] for m in resp.json().get("models", [])]
            return any(self.config["name"] in m for m in models)
        except Exception:
            return False

    def get_pull_command(self) -> str:
        """Lệnh tải model — hiển thị cho người dùng khi chưa cài."""
        return f"ollama pull {self.config['name']}"

    def has_gpu(self) -> bool:
        """Kiểm tra máy có GPU được hỗ trợ không."""
        return self._detect_gpu() > 0

    @staticmethod
    def get_all_tiers() -> dict:
        """Trả về toàn bộ cấu hình các tier — dùng cho màn hình Settings."""
        return LOCAL_MODELS

    # ── Private helpers ───────────────────────────────────

    def _detect_gpu(self) -> int:
        """
        Phát hiện GPU và trả về số layers đẩy lên GPU.
        - 0   : Không có GPU, dùng CPU hoàn toàn.
        - 999 : Có GPU, Ollama tự quyết định phân bổ tối đa.
        """
        # NVIDIA GPU
        try:
            result = subprocess.run(
                ["nvidia-smi"], capture_output=True, timeout=3
            )
            if result.returncode == 0:
                return 999
        except Exception:
            pass

        # AMD GPU
        try:
            result = subprocess.run(
                ["rocminfo"], capture_output=True, timeout=3
            )
            if result.returncode == 0:
                return 999
        except Exception:
            pass

        return 0