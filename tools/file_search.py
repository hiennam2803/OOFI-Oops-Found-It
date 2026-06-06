"""
tools/file_search.py
Tìm kiếm file với tốc độ tối ưu bằng os.scandir + cache + fuzzy match.
"""

import os
import fnmatch
import time
from pathlib import Path
from datetime import datetime


# Thư mục hệ thống bỏ qua khi quét để tăng tốc
IGNORE_FOLDERS = {
    "appdata", "node_modules", ".git", "__pycache__",
    "venv", ".venv", "env", "ntuser", "$recycle.bin",
    "windows", "system32", "program files", "program files (x86)",
}

# Bộ nhớ đệm: {(folder, pattern, max_depth): (timestamp, results)}
_SEARCH_CACHE: dict = {}
CACHE_TTL = 15  # Giây


def _smart_pattern(pattern: str) -> str:
    """
    Chuyển đổi pattern thành fuzzy match nếu người dùng
    không nhập đuôi file hoặc ký tự wildcard.
    Ví dụ: 'báo cáo' → '*báo cáo*'
    """
    pattern = pattern.strip().strip("'\"")
    if "." not in pattern and "*" not in pattern:
        return f"*{pattern}*"
    return pattern


def _scan(base_path: Path, pattern: str, max_depth: int) -> list[str]:
    """
    Quét thư mục bằng os.scandir (nhanh hơn os.walk ~5x).
    Dùng hàng đợi BFS để kiểm soát độ sâu chính xác.
    """
    results = []
    queue   = [(base_path, 0)]

    while queue:
        current_dir, depth = queue.pop(0)
        if depth >= max_depth:
            continue

        try:
            with os.scandir(current_dir) as entries:
                for entry in entries:
                    name_lower = entry.name.lower()
                    if entry.is_dir(follow_symlinks=False):
                        if (
                            name_lower not in IGNORE_FOLDERS
                            and not entry.name.startswith(".")
                        ):
                            queue.append((Path(entry.path), depth + 1))

                    elif entry.is_file(follow_symlinks=False):
                        if fnmatch.fnmatch(name_lower, pattern.lower()):
                            try:
                                stat     = entry.stat()
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
                                    f"📄 {entry.path}  [{size_str}]  Sửa: {modified}"
                                )
                            except (PermissionError, FileNotFoundError):
                                continue
        except (PermissionError, FileNotFoundError):
            continue

    return results


def search_files(pattern: str, folder: str = "", max_depth: int = 3) -> str:
    """
    Tìm file theo pattern trong thư mục chỉ định.

    Args:
        pattern  : Pattern tìm kiếm. Ví dụ: *.pdf, report*, báo cáo
        folder   : Đường dẫn thư mục. Mặc định: thư mục Home
        max_depth: Độ sâu quét tối đa. Mặc định: 3 tầng

    Returns:
        Chuỗi kết quả danh sách file tìm thấy.
    """
    t_start  = time.time()

    if not folder:
        folder = str(Path.home())

    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    folder   = folder.replace("[username]", username).replace("[YourUsername]", username)
    folder   = folder.strip().strip("'\"")
    pattern  = _smart_pattern(pattern)

    if not os.path.exists(folder):
        return f"❌ Thư mục không tồn tại: {folder}"

    base_path = Path(folder)
    cache_key = (str(base_path), pattern, max_depth)
    now       = time.time()

    # Kiểm tra cache
    if cache_key in _SEARCH_CACHE:
        cache_time, cached = _SEARCH_CACHE[cache_key]
        if now - cache_time < CACHE_TTL:
            elapsed = (time.time() - t_start) * 1000
            total   = len(cached)
            output  = f"⚡ [Cache] Tìm thấy {total} file ({elapsed:.0f}ms):\n" + "\n".join(cached[:20])
            if total > 20:
                output += f"\n\n... và {total - 20} file khác"
            return output

    # Quét thật
    try:
        results = _scan(base_path, pattern, max_depth)
    except Exception as e:
        return f"❌ Lỗi khi quét: {e}"

    # Lưu cache
    _SEARCH_CACHE[cache_key] = (now, results)

    if not results:
        return (
            f"🔍 Không tìm thấy '{pattern}' "
            f"trong '{folder}' (độ sâu {max_depth} tầng)."
        )

    elapsed = (time.time() - t_start) * 1000
    total   = len(results)
    output  = f"✅ Tìm thấy {total} file ({elapsed:.0f}ms):\n" + "\n".join(results[:20])
    if total > 20:
        output += f"\n\n... và {total - 20} file khác"
    return output