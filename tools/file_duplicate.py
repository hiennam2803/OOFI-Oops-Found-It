"""
tools/file_duplicate.py
Tìm file trùng lặp bằng thuật toán 3 bước + multiprocessing.
Thuật toán: size → quick hash (head+tail) → full hash
"""

import os
import hashlib
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed


IGNORE_FOLDERS = {
    "appdata", "node_modules", ".git", "__pycache__",
    "venv", ".venv", "env", "$recycle.bin",
}


def _quick_hash(path_str: str) -> tuple[str, str] | None:
    """
    Tính hash nhanh bằng cách đọc 1KB đầu + 1KB cuối.
    Dùng cho bước 2 — loại bỏ 99.9% file không trùng.
    """
    try:
        size   = os.path.getsize(path_str)
        chunk  = min(1024, size)
        hasher = hashlib.md5()
        with open(path_str, "rb") as f:
            hasher.update(f.read(chunk))
            if size > chunk:
                f.seek(-chunk, 2)
                hasher.update(f.read(chunk))
        return path_str, hasher.hexdigest()
    except Exception:
        return None


def _full_hash(path_str: str) -> tuple[str, str] | None:
    """
    Tính hash toàn bộ file.
    Chỉ chạy khi bước 1 và 2 đã lọc xong — tránh lãng phí I/O.
    """
    try:
        hasher = hashlib.md5()
        with open(path_str, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return path_str, hasher.hexdigest()
    except Exception:
        return None


def find_duplicates(folder: str) -> str:
    """
    Tìm các file trùng nội dung trong thư mục.

    Args:
        folder: Đường dẫn thư mục cần kiểm tra.

    Returns:
        Báo cáo danh sách file trùng lặp.
    """
    if not folder:
        return "❌ Vui lòng cung cấp đường dẫn thư mục."

    target = Path(folder.strip().strip("'\""))
    if not target.exists() or not target.is_dir():
        return f"❌ Thư mục không tồn tại: {folder}"

    # Bước 1: Thu thập file và nhóm theo kích thước
    size_groups: dict[int, list[str]] = defaultdict(list)
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d.lower() not in IGNORE_FOLDERS]
        for f in files:
            try:
                fp   = os.path.join(root, f)
                size = os.path.getsize(fp)
                if size > 0:
                    size_groups[size].append(fp)
            except Exception:
                continue

    # Chỉ giữ nhóm có từ 2 file trở lên (nghi vấn trùng)
    candidates = [
        fp for files in size_groups.values()
        if len(files) > 1
        for fp in files
    ]

    if not candidates:
        return "✅ Không tìm thấy file nào trùng lặp."

    # Bước 2: Quick hash song song bằng multiprocessing
    quick_groups: dict[str, list[str]] = defaultdict(list)
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(_quick_hash, fp): fp for fp in candidates}
        for future in as_completed(futures):
            result = future.result()
            if result:
                path_str, h = result
                quick_groups[h].append(path_str)

    # Chỉ giữ nhóm quick hash trùng
    quick_candidates = [
        fp for files in quick_groups.values()
        if len(files) > 1
        for fp in files
    ]

    if not quick_candidates:
        return "✅ Không tìm thấy file nào trùng nội dung."

    # Bước 3: Full hash song song
    full_groups: dict[str, list[str]] = defaultdict(list)
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(_full_hash, fp): fp for fp in quick_candidates}
        for future in as_completed(futures):
            result = future.result()
            if result:
                path_str, h = result
                full_groups[h].append(path_str)

    # Tổng hợp kết quả
    report_lines = []
    total_dupes  = 0
    for files in full_groups.values():
        if len(files) > 1:
            report_lines.append(f"📌 [Gốc]  {files[0]}")
            for dup in files[1:]:
                report_lines.append(f"    └── [Trùng] {dup}")
                total_dupes += 1

    if not report_lines:
        return "✅ Không tìm thấy file nào trùng nội dung."

    return (
        f"🔍 Phát hiện {total_dupes} file trùng lặp:\n\n"
        + "\n".join(report_lines)
    )