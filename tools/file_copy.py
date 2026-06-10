"""
tools/file_copy.py
Sao chép file (hỗ trợ đơn lẻ, batch danh sách, wildcard pattern).
"""

import os
import shutil
import fnmatch
from pathlib import Path
from typing import Union, List


def _normalize_path(path_str: str) -> str:
    """Chuẩn hóa đường dẫn, sửa lỗi 'Download' -> 'Downloads' (chỉ khi là phần riêng)."""
    if not path_str:
        return ""
    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    path_str = path_str.replace("[username]", username).replace("{username}", username)
    path_str = path_str.strip().strip("'\"")
    parts = Path(path_str).parts
    new_parts = []
    for part in parts:
        if part.lower() == "download" and part != "Downloads":
            new_parts.append("Downloads")
        else:
            new_parts.append(part)
    return str(Path(*new_parts))


def _copy_single(src: str, dst: str) -> str:
    src_path = Path(src)
    dst_path = Path(dst)
    if not src_path.exists():
        return f"❌ Nguồn không tồn tại: {src}"
    if not src_path.is_file():
        return f"❌ Chỉ hỗ trợ sao chép file: {src}"
    if dst_path.is_dir() or dst.endswith(("/", "\\")):
        dst_path.mkdir(parents=True, exist_ok=True)
        final_dst = dst_path / src_path.name
    else:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        final_dst = dst_path
    if final_dst.exists():
        stem, suffix = final_dst.stem, final_dst.suffix
        c = 1
        while final_dst.exists():
            final_dst = final_dst.parent / f"{stem}_copy{c}{suffix}"
            c += 1
    try:
        shutil.copy2(str(src_path), str(final_dst))
        return f"📋 Thành công: {src_path.name} → {final_dst.parent.name}/{final_dst.name}"
    except Exception as e:
        return f"❌ Lỗi {src_path.name}: {e}"


def copy_file(
    src: str = "",
    dst: str = "",
    source_path: str = "",
    source_paths: Union[str, List[str]] = None,
    destination_path: str = "",
    pattern: str = "",
    folder: str = "",
    **kwargs
) -> str:
    # Xác định đích
    dest = destination_path or dst
    if not dest:
        return "❌ Vui lòng cung cấp đích (destination_path hoặc dst)."
    dest = _normalize_path(dest)

    # Trường hợp pattern + folder (từ AI có thể dùng)
    if pattern and folder:
        src_folder = _normalize_path(folder)
        src_path = Path(src_folder)
        if not src_path.exists():
            return f"❌ Thư mục không tồn tại: {src_folder}"
        try:
            items = [p for p in src_path.iterdir() if p.is_file() and fnmatch.fnmatch(p.name.lower(), pattern.lower())]
        except PermissionError:
            return f"❌ Không đọc được {src_folder}"
        if not items:
            return f"⚠️ Không tìm thấy file nào khớp pattern '{pattern}' trong '{src_folder}'"
        results = []
        for item in items:
            results.append(_copy_single(str(item), dest))
        return "\n".join(results)

    # Trường hợp source_path có thể chứa wildcard
    sources = source_paths or source_path or src
    if not sources:
        return "❌ Vui lòng cung cấp nguồn (src, source_path, source_paths) hoặc pattern+folder."
    
    if isinstance(sources, str):
        sources = [sources]
    
    results = []
    for src_pattern in sources:
        src_pattern_norm = _normalize_path(src_pattern)
        # Nếu có wildcard, xử lý glob
        if "*" in src_pattern_norm or "?" in src_pattern_norm:
            src_path = Path(src_pattern_norm)
            parent = src_path.parent
            pattern_name = src_path.name
            if not parent.exists():
                results.append(f"❌ Thư mục không tồn tại: {parent}")
                continue
            try:
                items = list(parent.iterdir())
            except PermissionError:
                results.append(f"❌ Không đọc được {parent}")
                continue
            matched = [item for item in items if item.is_file() and fnmatch.fnmatch(item.name.lower(), pattern_name.lower())]
            if not matched:
                results.append(f"⚠️ Không tìm thấy file nào với pattern: {src_pattern_norm}")
                continue
            for item in matched:
                results.append(_copy_single(str(item), dest))
        else:
            # Đường dẫn cụ thể
            results.append(_copy_single(src_pattern_norm, dest))
    
    if not results:
        return "❌ Không có file nào được sao chép"
    return "\n".join(results)