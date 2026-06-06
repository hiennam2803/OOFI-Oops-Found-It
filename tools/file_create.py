"""
tools/file_create.py
Tạo file hoặc thư mục mới, bao gồm cả các thư mục cha chưa tồn tại.
"""

import os
from pathlib import Path


def create_file(path: str, content: str = "", is_folder: bool = False) -> str:
    """
    Tạo file hoặc thư mục tại đường dẫn chỉ định.

    Args:
        path     : Đường dẫn file hoặc thư mục cần tạo.
        content  : Nội dung khởi tạo nếu tạo file (tùy chọn).
        is_folder: True nếu muốn tạo thư mục thay vì file.

    Returns:
        Thông báo kết quả.
    """
    if not path:
        return "❌ Vui lòng cung cấp đường dẫn."

    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    path     = path.replace("[username]", username).replace("{username}", username)
    path     = path.strip().strip("'\"")

    target = Path(path)

    try:
        # Tạo thư mục
        if is_folder or not target.suffix or path.endswith(("/", "\\")):
            if target.exists():
                return f"⚠️ Thư mục đã tồn tại: {path}"
            target.mkdir(parents=True, exist_ok=True)
            return f"📁 Tạo thư mục thành công: {path}"

        # Tạo file
        if target.exists():
            return f"⚠️ File đã tồn tại: {path}"

        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)

        return (
            f"📄 Tạo file thành công.\n"
            f"  Đường dẫn : {path}\n"
            f"  Nội dung  : {len(content)} ký tự"
        )
    except PermissionError:
        return f"❌ Không có quyền tạo tại: {path}"
    except Exception as e:
        return f"❌ Lỗi khi tạo: {e}"