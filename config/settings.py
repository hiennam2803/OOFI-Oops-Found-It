# config/settings.py

import json
import psutil
from pathlib import Path
from config.model import detect_recommended_tier

CONFIG_DIR  = Path.home() / ".localfileagent"
CONFIG_FILE = CONFIG_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "mode":         "local",   # "local" | "cloud"
    "local_tier":   None,      # None = tự detect khi lần đầu chạy
    "cloud_tier":   "smart",
    "groq_api_key": "",
    "ollama_url":   "http://localhost:11434",
    "first_run":    True,
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
    """Nếu chưa chọn tier thì tự detect theo RAM."""
    tier = settings.get("local_tier")
    if not tier:
        return detect_recommended_tier()
    return tier