"""
tools/file_create.py
Tạo file hoặc thư mục mới (hỗ trợ batch).
"""

import os
from pathlib import Path
from typing import Union, List


def _normalize_path(path_str: str) -> str:
    """Chuẩn hóa đường dẫn, sửa lỗi 'Download' -> 'Downloads' chỉ khi là một phần riêng biệt."""
    if not path_str:
        return ""
    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    path_str = path_str.replace("[username]", username).replace("{username}", username)
    path_str = path_str.strip().strip("'\"")
    
    # Tách đường dẫn thành các phần (ví dụ: C:, Users, ASUS, Download)
    parts = Path(path_str).parts
    new_parts = []
    for part in parts:
        # Nếu phần này là "Download" (không phân biệt hoa thường) và không phải "Downloads" thì sửa
        if part.lower() == "download" and part != "Downloads":
            new_parts.append("Downloads")
        else:
            new_parts.append(part)
    # Ghép lại thành đường dẫn chuẩn
    normalized = str(Path(*new_parts))
    return normalized


def _create_single(path: str, content: str = "", is_folder: bool = False) -> str:
    target = Path(path)
    try:
        # Tạo thư mục nếu is_folder=True hoặc không có đuôi mở rộng hoặc kết thúc bằng dấu /
        if is_folder or not target.suffix or path.endswith(("/", "\\")):
            if target.exists():
                return f"⚠️ Thư mục đã tồn tại: {path}"
            target.mkdir(parents=True, exist_ok=True)
            return f"📁 Tạo thư mục: {path}"
        else:
            if target.exists():
                return f"⚠️ File đã tồn tại: {path}"
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
            return f"📄 Tạo file: {path} ({len(content)} ký tự)"
    except PermissionError:
        return f"❌ Không có quyền tạo: {path}"
    except Exception as e:
        return f"❌ Lỗi tạo {path}: {e}"


def create_file(
    path: str = "",
    content: str = "",
    is_folder: bool = False,
    file_paths: Union[str, List[str]] = None,
    paths: Union[str, List[str]] = None,
    **kwargs
) -> str:
    """
    Tạo file hoặc thư mục. Hỗ trợ:
      - Single: path + content (tùy chọn)
      - Batch: file_paths (list) hoặc paths (list)
    """
    # Xác định danh sách đường dẫn cần tạo
    targets = file_paths or paths
    if targets is None:
        if not path:
            return "❌ Vui lòng cung cấp 'path' (tạo đơn) hoặc 'file_paths' (tạo batch)."
        targets = [path]
    elif isinstance(targets, str):
        targets = [targets]
    elif not isinstance(targets, list):
        return "❌ file_paths phải là string hoặc list."

    results = []
    for p in targets:
        norm_path = _normalize_path(p)
        res = _create_single(norm_path, content, is_folder)
        results.append(res)
    if not results:
        return "❌ Không có mục nào được tạo."
    return "\n".join(results)