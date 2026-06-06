# config/settings.py

import json
import psutil
from pathlib import Path
from config.model import detect_recommended_tier

CONFIG_DIR  = Path.home() / ".oofi"
CONFIG_FILE = CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS = {
    # Chế độ AI
    "mode":          "local",    # "local" | "groq" | "gemini"
    "local_tier":    None,       # None = tự detect khi lần đầu chạy
    "groq_model":    "llama-3.3-70b",
    "gemini_model":  "flash",

    # API Keys
    "groq_api_key":   "",
    "gemini_api_key": "",

    # Local
    "ollama_url":    "http://localhost:11434",

    # Bảo vệ — user tự thêm thư mục cấm
    "user_blacklist": [],

    # App
    "first_run":     True,
    "theme":         "dark",     # "dark" | "light"
    "language":      "vi",       # "vi" | "en"
}


def load_settings() -> dict:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            return {**DEFAULT_SETTINGS, **saved}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def get_active_tier(settings: dict) -> str:
    tier = settings.get("local_tier")
    if not tier:
        return detect_recommended_tier()
    return tier