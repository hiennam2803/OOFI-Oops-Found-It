# config/__init__.py

from config.model import (
    LOCAL_MODELS,
    CLOUD_MODELS,
    detect_recommended_tier,
    get_ram_gb,
)
from config.settings import (
    load_settings,
    save_settings,
    get_active_tier,
)

__all__ = [
    "LOCAL_MODELS",
    "CLOUD_MODELS",
    "detect_recommended_tier",
    "get_ram_gb",
    "load_settings",
    "save_settings",
    "get_active_tier",
]