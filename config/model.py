from dataclasses import dataclass
from enum import Enum

class ProviderType(Enum):
    """Phân biệt ai đang chạy model: máy mình hay server của người khác."""
    LOCAL  = "local"   # Chạy offline qua Ollama, không cần internet
    CLOUD  = "cloud"   # Gọi API qua internet, cần API Key


@dataclass(frozen=True)   # frozen=True → bất biến, tránh vô tình sửa nhầm
class ModelDefinition:
    """
    Bản mô tả đầy đủ của một model AI.

    Thuộc tính:
        display_name   : Tên hiện lên GUI cho người dùng thấy
        provider_type  : LOCAL hay CLOUD
        provider_key   : Tên provider ("ollama" | "gemini" | "groq" | "openai")
        model_id       : Chuỗi model ID truyền vào API call
        api_base_url   : URL gốc của API endpoint
        needs_api_key  : True nếu cần người dùng nhập API Key
        context_window : Số token ngữ cảnh tối đa (để cảnh báo khi tóm tắt file lớn)
        note           : Ghi chú thêm hiện trong phần tooltip GUI
    """
    display_name   : str
    provider_type  : ProviderType
    provider_key   : str
    model_id       : str
    api_base_url   : str
    needs_api_key  : bool
    context_window : int
    note           : str = ""

ALL_MODELS: dict[str, ModelDefinition] = {

    "qwen2.5:1.5b": ModelDefinition(
        display_name   = "Qwen 2.5 1.5B (Siêu nhẹ, Offline)",
        provider_type  = ProviderType.LOCAL,
        provider_key   = "ollama",
        model_id       = "qwen2.5:1.5b",
        api_base_url   = "http://localhost:11434",
        needs_api_key  = False,
        context_window = 32_768,
        note           = "Máy cỏ không GPU vẫn mượt. JSON output cực chuẩn.",
    ),
    "qwen2.5:3b": ModelDefinition(
        display_name   = "Qwen 2.5 3B (Nhẹ, Offline)",
        provider_type  = ProviderType.LOCAL,
        provider_key   = "ollama",
        model_id       = "qwen2.5:3b",
        api_base_url   = "http://localhost:11434",
        needs_api_key  = False,
        context_window = 32_768,
        note           = "Mạnh hơn 1.5B, vẫn chạy offline ngon lành.",
    ),

    "gemini-2.5-flash": ModelDefinition(
        display_name   = "Gemini 2.5 Flash ⭐ (Cloud, Miễn phí)",
        provider_type  = ProviderType.CLOUD,
        provider_key   = "gemini",
        model_id       = "gemini-2.5-flash",
        api_base_url   = "https://generativelanguage.googleapis.com/v1beta",
        needs_api_key  = True,
        context_window = 1_048_576,   # ~1 triệu token — vô địch để tóm tắt PDF nặng
        note           = "Quota miễn phí cực lớn. Bộ nhớ ngữ cảnh vô địch.",
    ),

    "llama3-8b-groq": ModelDefinition(
        display_name   = "Llama 3 8B via Groq (Cloud, Siêu nhanh)",
        provider_type  = ProviderType.CLOUD,
        provider_key   = "groq",
        model_id       = "llama3-8b-8192",
        api_base_url   = "https://api.groq.com/openai/v1",
        needs_api_key  = True,
        context_window = 8_192,
        note           = "Tốc độ phản hồi vãi linh hồn. Backup hoàn hảo khi Gemini bận.",
    ),

    "gpt-4o-mini": ModelDefinition(
        display_name   = "GPT-4o Mini (Cloud, Trả phí)",
        provider_type  = ProviderType.CLOUD,
        provider_key   = "openai",
        model_id       = "gpt-4o-mini",
        api_base_url   = "https://api.openai.com/v1",
        needs_api_key  = True,
        context_window = 128_000,
        note           = "Dành cho ai có sẵn OpenAI API Key.",
    ),
}

# Model mặc định khi khởi động lần đầu (chưa có cấu hình)
DEFAULT_MODEL_KEY = "gemini-2.5-flash"

# Danh sách key để GUI tạo dropdown menu
MODEL_KEYS = list(ALL_MODELS.keys())

def get_model(key: str) -> ModelDefinition:
    """
    Lấy ModelDefinition theo key.
    Ném ValueError nếu key không tồn tại — bắt lỗi sớm hơn là im lặng.
    """
    if key not in ALL_MODELS:
        available = ", ".join(ALL_MODELS.keys())
        raise ValueError(
            f"Model '{key}' không tồn tại trong OOFI.\n"
            f"Các model hợp lệ: {available}"
        )
    return ALL_MODELS[key]


def get_models_by_provider(provider_type: ProviderType) -> dict[str, ModelDefinition]:
    """Lọc danh sách model theo loại LOCAL hoặc CLOUD."""
    return {
        k: v for k, v in ALL_MODELS.items()
        if v.provider_type == provider_type
    }


def get_display_names() -> dict[str, str]:
    """
    Trả về dict {key: display_name} để GUI dùng tạo dropdown.
    Ví dụ: {"gemini-2.5-flash": "Gemini 2.5 Flash ⭐ (Cloud, Miễn phí)", ...}
    """
    return {k: v.display_name for k, v in ALL_MODELS.items()}