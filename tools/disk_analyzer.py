"""
tools/disk_analyzer.py
Phân tích dung lượng ổ đĩa và các thư mục chiếm nhiều dung lượng nhất.
"""

import os
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


IGNORE_FOLDERS = {
    "appdata", "node_modules", ".git", "__pycache__",
    "venv", ".venv", "env", "$recycle.bin",
    "windows", "system32",
}


def _get_folder_size(folder_path: str) -> tuple[str, int]:
    """Tính tổng dung lượng một thư mục."""
    total = 0
    try:
        for entry in os.scandir(folder_path):
            if entry.is_file(follow_symlinks=False):
                try:
                    total += entry.stat().st_size
                except Exception:
                    pass
            elif entry.is_dir(follow_symlinks=False):
                sub_total, _ = _get_folder_size(entry.path)
                total += sub_total
    except PermissionError:
        pass
    return folder_path, total


def _format_size(size_bytes: int) -> str:
    """Định dạng kích thước sang đơn vị dễ đọc."""
    if size_bytes >= 1 << 30:
        return f"{size_bytes / (1 << 30):.2f} GB"
    elif size_bytes >= 1 << 20:
        return f"{size_bytes / (1 << 20):.1f} MB"
    elif size_bytes >= 1 << 10:
        return f"{size_bytes / (1 << 10):.1f} KB"
    return f"{size_bytes} B"


def disk_analyzer(drive: str = "C:") -> str:
    """
    Phân tích tổng quan dung lượng ổ đĩa và
    liệt kê các thư mục chiếm nhiều dung lượng nhất.

    Args:
        drive: Tên ổ đĩa cần phân tích. Ví dụ: C:, D:

    Returns:
        Báo cáo dung lượng ổ đĩa và top thư mục lớn nhất.
    """
    if not drive:
        return "❌ Vui lòng nhập tên ổ đĩa. Ví dụ: C:, D:"

    drive_clean = drive.strip().upper()
    if ":" not in drive_clean:
        drive_clean = f"{drive_clean}:"
    drive_path = f"{drive_clean}/"

    try:
        total, used, free = shutil.disk_usage(drive_path)
        used_pct = (used / total) * 100

        # Quét các thư mục con cấp 1 bằng đa luồng
        top_dirs = []
        try:
            with os.scandir(drive_path) as entries:
                dirs = [
                    e.path for e in entries
                    if e.is_dir(follow_symlinks=False)
                    and e.name.lower() not in IGNORE_FOLDERS
                    and not e.name.startswith(".")
                ]

            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {executor.submit(_get_folder_size, d): d for d in dirs}
                for future in as_completed(futures):
                    try:
                        path, size = future.result()
                        if size > 0:
                            top_dirs.append((path, size))
                    except Exception:
                        pass
        except PermissionError:
            pass

        top_dirs.sort(key=lambda x: x[1], reverse=True)

        # Tạo progress bar dung lượng
        bar_filled = int(used_pct / 5)
        bar        = "█" * bar_filled + "░" * (20 - bar_filled)

        output = (
            f"📊 Phân tích ổ đĩa {drive_clean}\n"
            f"{'─' * 40}\n"
            f"  Tổng dung lượng : {_format_size(total)}\n"
            f"  Đã sử dụng      : {_format_size(used)} ({used_pct:.1f}%)\n"
            f"  Còn trống       : {_format_size(free)}\n"
            f"  [{bar}] {used_pct:.0f}%\n"
        )

        if top_dirs:
            output += f"\n📁 Top {min(5, len(top_dirs))} thư mục lớn nhất:\n"
            for path, size in top_dirs[:5]:
                output += f"  {_format_size(size):>10}  {path}\n"

        return output

    except Exception as e:
        return f"❌ Không thể phân tích ổ đĩa {drive_clean}: {e}"