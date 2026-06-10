"""
tools/file_delete.py
Xóa file an toàn bằng send2trash — hỗ trợ xóa đơn hoặc batch theo pattern (wildcard).
"""

import os
import fnmatch
from pathlib import Path
from send2trash import send2trash


def _normalize_path(path_str: str) -> str:
    if not path_str:
        return ""
    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    path_str = path_str.replace("[username]", username).replace("{username}", username)
    path_str = path_str.strip().strip("'\"")
    # Sửa lỗi "Download" -> "Downloads" nếu thư mục không tồn tại
    if "Download" in path_str and not Path(path_str).exists():
        path_str = path_str.replace("Download", "Downloads")
    return path_str


def delete_file(path: str = "", pattern: str = "", folder: str = "", **kwargs) -> str:
    """
    Xóa file hoặc thư mục (đơn hoặc batch theo pattern).
    
    Các chế độ:
    - Xóa đơn: path = "đường_dẫn"
    - Xóa batch: pattern = "*.txt", folder = "C:/Users/..."
    """
    # Batch delete theo pattern
    if pattern and folder:
        folder_path = _normalize_path(folder)
        folder_path = Path(folder_path)
        if not folder_path.exists():
            return f"❌ Thư mục không tồn tại: {folder_path}"
        if not folder_path.is_dir():
            return f"❌ Không phải thư mục: {folder_path}"
        try:
            items = list(folder_path.iterdir())
        except PermissionError:
            return f"❌ Không thể đọc thư mục: {folder_path}"
        matched = []
        for item in items:
            if fnmatch.fnmatch(item.name.lower(), pattern.lower()):
                matched.append(item)
        if not matched:
            return f"⚠️ Không tìm thấy mục nào khớp với pattern '{pattern}' trong '{folder_path}'"
        deleted = []
        errors = []
        for item in matched:
            try:
                send2trash(str(item))
                deleted.append(item.name)
            except Exception as e:
                errors.append(f"{item.name}: {e}")
        result = f"🗑️ Đã chuyển {len(deleted)} mục vào Recycle Bin từ '{folder_path}'"
        if deleted:
            result += ":\n  " + "\n  ".join(deleted[:20])
            if len(deleted) > 20:
                result += f"\n  ... và {len(deleted)-20} mục khác"
        if errors:
            result += f"\n⚠️ Lỗi: {', '.join(errors[:5])}"
        return result

    # Xóa đơn (giữ nguyên logic cũ)
    if not path:
        return "❌ Vui lòng cung cấp 'path' (xóa đơn) hoặc 'pattern' + 'folder' (xóa batch)."
    path = _normalize_path(path)
    target = Path(path)
    if not target.exists():
        return f"❌ File hoặc thư mục không tồn tại: {path}"
    item_type = "Thư mục" if target.is_dir() else "File"
    try:
        send2trash(str(target))
        return f"🗑️ Đã chuyển {item_type.lower()} vào Recycle Bin.\n  Đường dẫn: {path}\n  Bạn có thể khôi phục từ Recycle Bin nếu cần."
    except PermissionError:
        return f"❌ Không có quyền xóa: {path} (File đang được sử dụng hoặc bị khóa)"
    except Exception as e:
        return f"❌ Lỗi khi xóa: {e}"