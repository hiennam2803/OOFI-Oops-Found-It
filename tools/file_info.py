"""
tools/file_info.py
Xem thông tin chi tiết của file hoặc thư mục bằng path.stat().
Không cần gọi AI — xử lý thuần Python trong <1ms.
"""

import os
import time
from pathlib import Path


def _format_size(size_bytes: int) -> str:
    if size_bytes >= 1 << 30:
        return f"{size_bytes / (1 << 30):.2f} GB"
    elif size_bytes >= 1 << 20:
        return f"{size_bytes / (1 << 20):.1f} MB"
    elif size_bytes >= 1 << 10:
        return f"{size_bytes / (1 << 10):.1f} KB"
    return f"{size_bytes} B"


def file_info(path: str) -> str:
    """
    Trả về thông tin chi tiết của file hoặc thư mục.

    Args:
        path: Đường dẫn file hoặc thư mục cần xem thông tin.

    Returns:
        Thông tin bao gồm tên, loại, kích thước, ngày tạo, ngày sửa, quyền truy cập.
    """
    if not path:
        return "❌ Vui lòng cung cấp đường dẫn."

    target = Path(path.strip().strip("'\""))
    if not target.exists():
        return f"❌ Không tìm thấy: {path}"

    try:
        stat      = target.stat()
        item_type = "Thư mục" if target.is_dir() else "File"
        ext       = target.suffix if target.is_file() else "—"
        writable  = "Đọc/Ghi" if os.access(target, os.W_OK) else "Chỉ đọc"
        created   = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(stat.st_ctime))
        modified  = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(stat.st_mtime))

        return (
            f"🔎 Thông tin chi tiết\n"
            f"{'─' * 35}\n"
            f"  Tên          : {target.name}\n"
            f"  Loại         : {item_type}\n"
            f"  Định dạng    : {ext}\n"
            f"  Kích thước   : {_format_size(stat.st_size)}\n"
            f"  Ngày tạo     : {created}\n"
            f"  Sửa đổi lần cuối: {modified}\n"
            f"  Quyền truy cập : {writable}\n"
            f"  Đường dẫn đầy đủ: {target.resolve()}"
        )
    except Exception as e:
        return f"❌ Không thể đọc thông tin: {e}"