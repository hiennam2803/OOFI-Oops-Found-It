# config/__init__.py

from config.model    import (
    LOCAL_MODELS,
    CLOUD_MODELS,
    detect_recommended_tier,
    get_model_name,
    get_model_info,
    get_ram_gb,
)
from config.settings import (
    load_settings,
    save_settings,
    get_active_tier,
)

__all__ = [
    # model
    "LOCAL_MODELS",
    "CLOUD_MODELS",
    "detect_recommended_tier",
    "get_model_name",
    "get_model_info",
    "get_ram_gb",
    # settings
    "load_settings",
    "save_settings",
    "get_active_tier",
]