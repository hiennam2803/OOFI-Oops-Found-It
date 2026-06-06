# providers/__init__.py

from providers.base   import BaseProvider
from providers.local  import LocalProvider
from providers.groq   import GroqProvider
from providers.gemini import GeminiProvider


def create_provider(settings: dict) -> BaseProvider:
    """
    Factory — tạo đúng provider theo settings.
    Hàm DUY NHẤT cần gọi từ bên ngoài thư mục providers/.
    """
    mode = settings.get("mode", "local")

    if mode == "groq":
        return GroqProvider(
            model   = settings.get("groq_model", "llama-3.3-70b"),
            api_key = settings.get("groq_api_key", ""),
        )
    elif mode == "gemini":
        return GeminiProvider(
            model   = settings.get("gemini_model", "flash"),
            api_key = settings.get("gemini_api_key", ""),
        )
    else:
        from config import get_active_tier
        return LocalProvider(
            tier       = get_active_tier(settings),
            ollama_url = settings.get("ollama_url", "http://localhost:11434"),
        )


__all__ = [
    "BaseProvider",
    "LocalProvider",
    "GroqProvider",
    "GeminiProvider",
    "create_provider",
]