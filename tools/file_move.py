"""
tools/file_move.py
Di chuyển file hoặc thư mục với shutil.move.
Tự động xử lý trùng tên và kiểm tra đường dẫn hợp lệ.
"""

import os
import shutil
from pathlib import Path


def move_file(src: str, dst: str) -> str:
    """
    Di chuyển file hoặc thư mục đến vị trí mới.

    Args:
        src: Đường dẫn nguồn (file hoặc thư mục).
        dst: Đường dẫn thư mục đích hoặc file đích mới.

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
        return f"❌ Nguồn không tồn tại: {src}"

    # Xác định đường dẫn đích cuối cùng
    if dst_path.is_dir() or dst.endswith("/") or dst.endswith("\\"):
        dst_path.mkdir(parents=True, exist_ok=True)
        final_dst = dst_path / src_path.name
    else:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        final_dst = dst_path

    # Xử lý trùng tên
    if final_dst.exists() and final_dst != src_path:
        stem, suffix = final_dst.stem, final_dst.suffix
        counter = 1
        while final_dst.exists():
            final_dst = final_dst.parent / f"{stem}_moved{counter}{suffix}"
            counter  += 1

    try:
        shutil.move(str(src_path), str(final_dst))
        return (
            f"🚚 Di chuyển thành công.\n"
            f"  Nguồn : {src}\n"
            f"  Đích  : {final_dst}"
        )
    except PermissionError:
        return f"❌ Không có quyền di chuyển: {src}"
    except Exception as e:
        return f"❌ Lỗi khi di chuyển: {e}"