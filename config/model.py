# config/model.py

import psutil


# ── Local models — chạy qua Ollama ──────────────────────
LOCAL_MODELS = {
    "light": {
        "name":         "qwen2.5:1.5b",
        "file_size":    "1 GB",
        "ram_required": 4,          # RAM tối thiểu của máy
        "ram_usage":    2,          # RAM model thực tế chiếm
        "label":        "Máy yếu (RAM 4GB+)",
    },
    "medium": {
        "name":         "qwen2.5:3b",
        "file_size":    "2 GB",
        "ram_required": 6,
        "ram_usage":    3,
        "label":        "Máy trung bình (RAM 6GB+)",
    },
    "strong": {
        "name":         "qwen2.5:7b",
        "file_size":    "5 GB",
        "ram_required": 8,
        "ram_usage":    6,
        "label":        "Máy mạnh (RAM 8GB+)",
    },
}

# ── Cloud models — chạy qua Groq API ────────────────────
CLOUD_MODELS = {
    "fast": {
        "name":  "llama-3.1-8b-instant",
        "label": "Nhanh — Llama 3.1 8B",
    },
    "smart": {
        "name":  "llama-3.3-70b-versatile",
        "label": "Thông minh — Llama 3.3 70B (khuyến nghị)",
    },
}


def detect_recommended_tier() -> str:
    ram_gb = psutil.virtual_memory().total / (1024 ** 3)

    if ram_gb < 8:
        return "light"
    elif ram_gb < 16:
        return "medium"
    else:
        return "strong"


def get_model_name(tier: str) -> str:
    return LOCAL_MODELS.get(tier, LOCAL_MODELS["strong"])["name"]


def get_model_info(tier: str) -> dict:
    return LOCAL_MODELS.get(tier, LOCAL_MODELS["strong"])


def get_ram_gb() -> float:
    return round(psutil.virtual_memory().total / (1024 ** 3), 1)