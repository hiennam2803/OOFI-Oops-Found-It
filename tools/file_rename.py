"""
tools/file_rename.py
Đổi tên file hoặc thư mục với xử lý tự động trùng tên.
"""

import os
from pathlib import Path


def rename_file(path: str, new_name: str) -> str:
    """
    Đổi tên file hoặc thư mục.
    Tự động giữ lại đuôi file gốc nếu new_name không có đuôi.
    Tự động xử lý trùng tên bằng hậu tố _v{n}.

    Args:
        path    : Đường dẫn file hoặc thư mục cần đổi tên.
        new_name: Tên mới (chỉ cần tên, không cần đường dẫn đầy đủ).

    Returns:
        Thông báo kết quả.
    """
    if not path or not new_name:
        return "❌ Vui lòng cung cấp đường dẫn và tên mới."

    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    path     = path.replace("[username]", username).replace("{username}", username).strip().strip("'\"")
    new_name = new_name.strip().strip("'\"")

    target = Path(path)
    if not target.exists():
        return f"❌ Không tìm thấy: {path}"

    # Giữ lại đuôi file gốc nếu new_name không có đuôi
    if target.is_file() and not Path(new_name).suffix:
        new_name = new_name + target.suffix

    final_dst = target.parent / new_name

    # Xử lý trùng tên
    if final_dst.exists() and final_dst != target:
        stem, suffix = final_dst.stem, final_dst.suffix
        counter = 1
        while final_dst.exists():
            final_dst = target.parent / f"{stem}_v{counter}{suffix}"
            counter  += 1

    try:
        old_name = target.name
        os.rename(str(target), str(final_dst))
        item_type = "Thư mục" if target.is_dir() else "File"
        return (
            f"✏️ Đổi tên {item_type.lower()} thành công.\n"
            f"  Tên cũ: {old_name}\n"
            f"  Tên mới: {final_dst.name}"
        )
    except PermissionError:
        return f"❌ Không có quyền đổi tên: {path} (File đang được sử dụng)"
    except Exception as e:
        return f"❌ Lỗi khi đổi tên: {e}"