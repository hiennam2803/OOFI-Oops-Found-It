"""
tools/file_history.py
Xem lịch sử các file được chỉnh sửa gần đây trong thư mục.
"""

import os
import time
from pathlib import Path


def file_history(folder: str = "", days: int = 7) -> str:
    """
    Liệt kê các file được chỉnh sửa trong N ngày gần đây.

    Args:
        folder: Đường dẫn thư mục cần xem lịch sử. Mặc định: Home.
        days  : Số ngày nhìn lại. Mặc định: 7 ngày.

    Returns:
        Danh sách file được sắp xếp theo thời gian chỉnh sửa mới nhất.
    """
    if not folder:
        folder = str(Path.home())

    target = Path(folder.strip().strip("'\""))
    if not target.exists() or not target.is_dir():
        return f"❌ Thư mục không tồn tại: {folder}"

    now        = time.time()
    cutoff     = int(days) * 86400
    recent     = []

    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            fp = Path(root) / f
            try:
                mtime = fp.stat().st_mtime
                if (now - mtime) < cutoff:
                    time_str = time.strftime("%d/%m/%Y %H:%M", time.localtime(mtime))
                    recent.append((mtime, f"  [{time_str}]  {fp}"))
            except Exception:
                continue

    if not recent:
        return f"📭 Không có file nào được chỉnh sửa trong {days} ngày qua."

    recent.sort(key=lambda x: x[0], reverse=True)
    lines  = "\n".join(item[1] for item in recent[:20])
    total  = len(recent)
    output = f"📜 Lịch sử chỉnh sửa trong {days} ngày qua ({total} file):\n{lines}"
    if total > 20:
        output += f"\n\n... và {total - 20} file khác"
    return output