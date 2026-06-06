# config/model.py

import psutil


# ── Local models ─────────────────────────────────────────
LOCAL_MODELS = {
    "light": {
        "name":         "qwen2.5:1.5b",
        "file_size":    "1 GB",
        "ram_required": 4,
        "ram_usage":    2,
        "num_ctx":      2048,
        "label":        "🟢 Nhẹ — qwen2.5:1.5b (RAM 4GB+)",
    },
    "normal": {
        "name":         "qwen2.5:3b",
        "file_size":    "2 GB",
        "ram_required": 6,
        "ram_usage":    3,
        "num_ctx":      4096,
        "label":        "🔴 Mạnh — qwen2.5:3b (RAM 6GB+)",
    },
}

# ── Cloud models ──────────────────────────────────────────
CLOUD_MODELS = {
    "groq": {
        "llama-3.1-8b":  "llama-3.1-8b-instant",
        "llama-3.3-70b": "llama-3.3-70b-versatile",
        "label":         "⚡ Groq — Llama 3 (Miễn phí, siêu nhanh)",
    },
    "gemini": {
        "flash":  "gemini-2.5-flash",
        "label":  "🧠 Gemini — 2.5 Flash (Miễn phí, quota lớn)",
    },
}


def detect_recommended_tier() -> str:
    ram_gb = psutil.virtual_memory().total / (1024 ** 3)
    if ram_gb < 8:
        return "light"
    else:
        return "normal"


def get_ram_gb() -> float:
    return round(psutil.virtual_memory().total / (1024 ** 3), 1)