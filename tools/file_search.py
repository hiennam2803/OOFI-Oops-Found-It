# tools/file_search.py

import os
import fnmatch
from pathlib import Path
from datetime import datetime


IGNORE_FOLDERS = {
    "appdata", "node_modules", ".git", "__pycache__",
    "venv", ".venv", "env", "ntuser", "$recycle.bin",
    "windows", "system32", "program files", "program files (x86)",
}


def _smart_pattern(pattern: str) -> str:
    """
    Nếu user gõ thiếu đuôi hoặc tên mờ → tự wrap thành fuzzy match.
    "báo cáo" → "*báo cáo*"
    "*.pdf"   → "*.pdf" (giữ nguyên)
    """
    pattern = pattern.strip().strip("'\"")
    if "." not in pattern and "*" not in pattern:
        return f"*{pattern}*"
    return pattern


def search_files(pattern: str, folder: str = "", max_depth: int = 3) -> str:
    """
    Tìm file theo pattern trong thư mục.
    pattern  : *.pdf | report* | báo cáo (fuzzy tự động)
    folder   : đường dẫn thư mục, mặc định Home
    max_depth: độ sâu tối đa (mặc định 3)
    """
    if not folder:
        folder = str(Path.home())

    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    folder   = folder.replace("[username]", username)
    folder   = folder.replace("[YourUsername]", username)
    folder   = folder.strip().strip("'\"")
    pattern  = _smart_pattern(pattern)

    if not os.path.exists(folder):
        return f"❌ Thư mục không tồn tại: {folder}"

    base_path  = Path(folder)
    base_depth = len(base_path.parts)
    results    = []

    try:
        for root, dirs, files in os.walk(base_path):
            current_depth = len(Path(root).parts) - base_depth

            # Chốt độ sâu
            if current_depth >= max_depth:
                dirs.clear()
                continue

            # Lọc folder rác + folder ẩn
            dirs[:] = [
                d for d in dirs
                if d.lower() not in IGNORE_FOLDERS
                and not d.startswith(".")
            ]

            # Quét file khớp pattern
            for file in files:
                if not fnmatch.fnmatch(file.lower(), pattern.lower()):
                    continue
                file_path = Path(root) / file
                try:
                    stat     = file_path.stat()
                    size_kb  = stat.st_size / 1024
                    modified = datetime.fromtimestamp(
                        stat.st_mtime
                    ).strftime("%d/%m/%Y %H:%M")
                    size_str = (
                        f"{size_kb:.1f} KB"
                        if size_kb < 1024
                        else f"{size_kb / 1024:.1f} MB"
                    )
                    results.append(
                        f"📄 {file_path}  [{size_str}]  Sửa: {modified}"
                    )
                except (PermissionError, FileNotFoundError):
                    continue

    except PermissionError:
        return f"❌ Không có quyền truy cập: {folder}"
    except Exception as e:
        return f"❌ Lỗi: {e}"

    if not results:
        return (
            f"🔍 Không tìm thấy '{pattern}' "
            f"trong '{folder}' (sâu {max_depth} tầng)."
        )

    total  = len(results)
    output = f"✅ Tìm thấy {total} file:\n" + "\n".join(results[:20])
    if total > 20:
        output += f"\n\n... và {total - 20} file khác"
    return output