"""
tools/file_delete.py
Xóa file an toàn bằng send2trash — đẩy vào Recycle Bin thay vì xóa vĩnh viễn.
"""

import os
from pathlib import Path
from send2trash import send2trash


def delete_file(path: str) -> str:
    """
    Xóa file hoặc thư mục bằng cách đưa vào Recycle Bin hệ thống.
    Người dùng có thể khôi phục lại từ Recycle Bin nếu cần.

    Args:
        path: Đường dẫn file hoặc thư mục cần xóa.

    Returns:
        Thông báo kết quả.
    """
    if not path:
        return "❌ Vui lòng cung cấp đường dẫn."

    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    path     = path.replace("[username]", username).replace("[YourUsername]", username)
    path     = path.replace("{username}", username).strip().strip("'\"")

    target = Path(path)

    if not target.exists():
        return f"❌ File hoặc thư mục không tồn tại: {path}"

    item_type = "Thư mục" if target.is_dir() else "File"

    try:
        send2trash(str(target))
        return (
            f"🗑️ Đã chuyển {item_type.lower()} vào Recycle Bin.\n"
            f"  Đường dẫn: {path}\n"
            f"  Bạn có thể khôi phục từ Recycle Bin nếu cần."
        )
    except PermissionError:
        return f"❌ Không có quyền xóa: {path} (File đang được sử dụng hoặc bị khóa)"
    except Exception as e:
        return f"❌ Lỗi khi xóa: {e}"