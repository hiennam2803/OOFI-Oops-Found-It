"""
tools/file_copy.py
Sao chép file với shutil.copy2 (giữ nguyên metadata gốc).
"""

import os
import shutil
from pathlib import Path


def copy_file(src: str, dst: str) -> str:
    """
    Sao chép file đến thư mục hoặc đường dẫn đích.
    Tự động xử lý trùng tên bằng cách thêm hậu tố _copy{n}.

    Args:
        src: Đường dẫn file nguồn.
        dst: Đường dẫn thư mục đích hoặc file đích.

    Returns:
        Thông báo kết quả.
    """
    if not src or not dst:
        return "❌ Vui lòng cung cấp đường dẫn nguồn và đích."

    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    src = src.replace("[username]", username).replace("{username}", username).strip().strip("'\"")
    dst = dst.replace("[username]", username).replace("{username}", username).strip().strip("'\"")

    src_path = Path(src)
    dst_path = Path(dst)

    if not src_path.exists():
        return f"❌ File nguồn không tồn tại: {src}"
    if not src_path.is_file():
        return "❌ Chỉ hỗ trợ sao chép file đơn lẻ, không hỗ trợ thư mục."

    # Xác định đường dẫn đích cuối cùng
    if dst_path.is_dir() or dst.endswith("/") or dst.endswith("\\"):
        dst_path.mkdir(parents=True, exist_ok=True)
        final_dst = dst_path / src_path.name
    else:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        final_dst = dst_path

    # Xử lý trùng tên
    if final_dst.exists():
        stem, suffix = final_dst.stem, final_dst.suffix
        counter = 1
        while final_dst.exists():
            final_dst = final_dst.parent / f"{stem}_copy{counter}{suffix}"
            counter  += 1

    try:
        shutil.copy2(str(src_path), str(final_dst))
        return (
            f"📋 Sao chép thành công.\n"
            f"  Nguồn : {src}\n"
            f"  Đích  : {final_dst}"
        )
    except PermissionError:
        return f"❌ Không có quyền truy cập: {src}"
    except Exception as e:
        return f"❌ Lỗi khi sao chép: {e}"