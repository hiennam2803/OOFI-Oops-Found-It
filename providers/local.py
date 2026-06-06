# providers/local.py

import requests
import subprocess
from providers.base import BaseProvider
from config import LOCAL_MODELS, get_active_tier, load_settings


class LocalProvider(BaseProvider):
    """
    Chạy LLM qua Ollama — offline hoàn toàn.
    Tự detect GPU nếu có, fallback CPU nếu không.
    """

    def __init__(self, tier: str = "normal", ollama_url: str = "http://localhost:11434"):
        if tier not in LOCAL_MODELS:
            raise ValueError(f"Tier không hợp lệ: '{tier}'. Chọn: {list(LOCAL_MODELS.keys())}")
        self.tier       = tier
        self.ollama_url = ollama_url
        self.config     = LOCAL_MODELS[tier]

    def chat(self, prompt: str) -> str:
        """Gửi prompt → nhận response string từ Ollama."""
        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model":  self.config["name"],
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_ctx":    self.config["num_ctx"],
                        "num_thread": 4,
                        "num_gpu":    self._detect_gpu(),
                        "temperature":0,
                    }
                },
                timeout=120,
            )
            resp.raise_for_status()
            return resp.json().get("response", "").strip()
        except requests.exceptions.Timeout:
            return '{"error": "Ollama timeout — model xử lý quá lâu"}'
        except Exception as e:
            return f'{{"error": "{str(e)}"}}'
        
    def chat_raw(self, system: str, user: str) -> str:
        """
        Gọi Ollama với system prompt tùy chỉnh.
        Dùng cho summarize — tránh model trả JSON.
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
                    ]
                },
                timeout=120,
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"].strip()
        except Exception as e:
            return f"[Lỗi: {e}]"

    def is_available(self) -> bool:
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def is_model_downloaded(self) -> bool:
        try:
            resp   = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            models = [m["name"] for m in resp.json().get("models", [])]
            return any(self.config["name"] in m for m in models)
        except Exception:
            return False

    def get_label(self) -> str:
        gpu = "GPU" if self._detect_gpu() > 0 else "CPU"
        return f"💻 Local · {self.config['name']} · {gpu}"

    def get_pull_command(self) -> str:
        return f"ollama pull {self.config['name']}"

    def _detect_gpu(self) -> int:
        try:
            r = subprocess.run(["nvidia-smi"], capture_output=True, timeout=3)
            if r.returncode == 0:
                return 999
        except Exception:
            pass
        try:
            r = subprocess.run(["rocminfo"], capture_output=True, timeout=3)
            if r.returncode == 0:
                return 999
        except Exception:
            pass
        return 0

    def has_gpu(self) -> bool:
        return self._detect_gpu() > 0

    @staticmethod
    def get_all_tiers() -> dict:
        return LOCAL_MODELS