import json
import os
from pathlib import Path
from typing import Any

from config.model import DEFAULT_MODEL_KEY

# Lưu ở %APPDATA%\OOFI\oofi_config.json trên Windows
# (C:\Users\<tên>\AppData\Roaming\OOFI\oofi_config.json)
# Tách khỏi thư mục cài đặt app → không bị mất dữ liệu khi update/cài lại.
_CONFIG_DIR  = Path(os.environ.get("APPDATA", Path.home())) / "OOFI"
_CONFIG_FILE = _CONFIG_DIR / "oofi_config.json"

DEFAULT_CONFIG: dict[str, Any] = {
    # Model AI đang được chọn hiện tại
    "selected_model": DEFAULT_MODEL_KEY,

    # API Keys — lưu trống, người dùng điền qua GUI Settings khi dùng Cloud
    "api_keys": {
        "gemini"  : "",
        "groq"    : "",
        "openai"  : "",
    },

    # Danh sách thư mục nhạy cảm người dùng tự thêm (ngoài SYSTEM_BLACKLIST)
    # Ví dụ: ["C:/Users/Nam/Desktop/DoAn", "D:/TaiLieuQuanTrong"]
    "user_blacklist": [],

    # Chế độ chạy thử — mặc định BẬT để an toàn tuyệt đối khi mới xài
    "dry_run": True,

    # Giao diện ứng dụng
    "theme": "dark",          # "dark" | "light"
    "language": "vi",         # "vi" | "en" (song ngữ, ưu tiên tiếng Việt)

    # Hệ thống lưu vết (Logging)
    "log_enabled": True,
    "log_max_lines": 5000,    # Tự xoay vòng log sạch sẽ khi vượt số dòng này
}


# ──────────────────────────────────────────────
# 3. LỚP QUẢN LÝ CẤU HÌNH (SETTINGS)
# ──────────────────────────────────────────────

class Settings:
    """
    Singleton-style class quản lý cấu hình tối thượng cho OOFI.
    Đã lược bỏ chế độ Server để tối ưu hiệu năng và trải nghiệm tinh gọn.

    Cách dùng:
        from config.settings import settings   # import instance toàn cục
        settings.get("dry_run")                # đọc giá trị
        settings.set("dry_run", False)         # ghi + tự lưu xuống đĩa
    """

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self.load()

    # ── Đọc/Ghi File ──────────────────────────────────────────────────────

    def load(self) -> None:
        """
        Đọc cấu hình từ đĩa cứng. Nếu file chưa có hoặc hỏng hóc,
        tự động reset về DEFAULT_CONFIG cho an toàn, không sập app.
        """
        if _CONFIG_FILE.exists():
            try:
                with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                # Merge đệ quy: giữ data cũ của user, cập nhật key mới từ DEV
                self._data = _deep_merge(DEFAULT_CONFIG, saved)
            except (json.JSONDecodeError, OSError):
                # File hỏng vờ cờ lờ → reset ngay về mặc định
                self._data = DEFAULT_CONFIG.copy()
                self.save()
        else:
            self._data = DEFAULT_CONFIG.copy()
            self.save()

    def save(self) -> None:
        """Ghi cấu hình hiện tại xuống đĩa. Tự tạo folder cha nếu chưa có."""
        try:
            _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except OSError:
            # Bẫy lỗi lỡ xui hệ điều hành chặn quyền ghi file
            pass

    # ── Getter / Setter Chung ─────────────────────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        """Lấy giá trị cấu hình theo key. Trả về default nếu không thấy."""
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Cập nhật giá trị cấu hình và đồng bộ xuống file JSON rẹt rẹt."""
        self._data[key] = value
        self.save()

    # ── API Keys ──────────────────────────────────────────────────────────

    def get_api_key(self, provider: str) -> str:
        """Lấy API Key. Trả chuỗi rỗng "" nếu chưa điền."""
        return self._data.get("api_keys", {}).get(provider, "")

    def set_api_key(self, provider: str, key: str) -> None:
        """Lưu API Key của từng nhà cung cấp và ghi xuống đĩa."""
        if "api_keys" not in self._data:
            self._data["api_keys"] = {}
        self._data["api_keys"][provider] = key.strip()
        self.save()

    def has_api_key(self, provider: str) -> bool:
        """Kiểm tra nhanh xem đã có API Key chưa (né khoảng trắng)."""
        return bool(self.get_api_key(provider))

    # ── User Blacklist (Bảo vệ vùng đất linh thiêng) ────────────────────────

    def get_blacklist(self) -> list[str]:
        """Trả về danh sách các folder nhạy cảm do người dùng tự chặn."""
        return self._data.get("user_blacklist", [])

    def add_to_blacklist(self, folder_path: str) -> None:
        """Chuẩn hóa và thêm một thư mục vào blacklist (nếu chưa tồn tại)."""
        bl = self.get_blacklist()
        try:
            normalized = str(Path(folder_path).resolve())
            if normalized not in bl:
                bl.append(normalized)
                self.set("user_blacklist", bl)
        except Exception:
            # Đường dẫn ngáo đá vờ cờ lờ thì không thêm
            pass

    def remove_from_blacklist(self, folder_path: str) -> None:
        """Xóa thư mục khỏi danh sách blacklist của người dùng."""
        try:
            normalized = str(Path(folder_path).resolve())
            bl = [p for p in self.get_blacklist() if p != normalized]
            self.set("user_blacklist", bl)
        except Exception:
            pass

    # ── Dry-Run Property ──────────────────────────────────────────────────

    @property
    def dry_run(self) -> bool:
        return bool(self._data.get("dry_run", True))

    @dry_run.setter
    def dry_run(self, value: bool) -> None:
        self.set("dry_run", value)

    # ── Bảng Tóm Tắt Tiện Ích Debug ────────────────────────────────────────

    def summary(self) -> str:
        """
        In ra bảng cấu hình cực đẹp mắt ở Terminal để dễ debug.
        API Key được gọt giũa chỉ hiện 4 ký tự cuối để bảo mật thông tin.
        """
        lines = [
            "── OOFI CONFIG SUMMARY ──────────────────",
            f"  Cấu hình tại : {_CONFIG_FILE}",
            f"  Model hiện tại: {self.get('selected_model')}",
            f"  Chế độ Dry-Run: {self.dry_run}",
            f"  Giao diện/Theme: {self.get('theme').upper()}",
            f"  Ghi Log hệ thống: {self.get('log_enabled')}",
            "  Trạng thái API Keys:",
        ]
        for provider, key in self._data.get("api_keys", {}).items():
            masked = f"***{key[-4:]}" if len(key) > 4 else ("*" * len(key) if key else "(chưa điền)")
            lines.append(f"    - {provider:8}: {masked}")
            
        lines.append("  Danh sách User Blacklist:")
        for path in self.get_blacklist():
            lines.append(f"    [CẤM] ➔ {path}")
        if not self.get_blacklist():
            lines.append("    (trống)")
        lines.append("──────────────────────────────────────────")
        return "\n".join(lines)


# ──────────────────────────────────────────────
# 4. HÀM NỘI BỘ (DEEP MERGE)
# ──────────────────────────────────────────────

def _deep_merge(base: dict, override: dict) -> dict:
    """
    Hàm trộn đệ quy siêu khôn: Giữ nguyên cấu hình người dùng cũ, 
    nhưng tự động đắp thêm các key tính năng mới nếu dev cập nhật DEFAULT_CONFIG.
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


# Khởi tạo một đối tượng duy nhất xài chung toàn bộ dự án
settings = Settings()