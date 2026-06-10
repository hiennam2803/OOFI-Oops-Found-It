"""
tools/file_rename.py
Đổi tên file/thư mục (đơn lẻ, batch theo mapping, batch theo pattern, batch regex).
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Union


def _normalize_path(path_str: str) -> Path:
    """Chuẩn hóa đường dẫn, sửa lỗi viết thường download -> Downloads."""
    path_str = path_str.strip().strip("'\"")
    if os.name == 'nt':
        path_str = path_str.replace('/', '\\')
    path_obj = Path(path_str)
    if not path_obj.exists():
        parent = path_obj.parent
        name = path_obj.name
        if name.lower() == "download":
            corrected = parent / "Downloads"
            if corrected.exists():
                return corrected
        if name.upper() == "DOWNLOAD":
            corrected = parent / "Downloads"
            if corrected.exists():
                return corrected
    return path_obj.resolve() if path_obj.exists() else path_obj


def _rename_single(path: str, new_name: str) -> str:
    target = Path(path)
    if not target.exists():
        target = _normalize_path(path)
        if not target.exists():
            return f"❌ Không tìm thấy: {path}"
    if target.is_file() and not Path(new_name).suffix:
        new_name = new_name + target.suffix
    final_dst = target.parent / new_name
    if final_dst.exists() and final_dst != target:
        stem, suffix = final_dst.stem, final_dst.suffix
        counter = 1
        while final_dst.exists():
            final_dst = target.parent / f"{stem}_v{counter}{suffix}"
            counter += 1
    try:
        old_name = target.name
        os.rename(str(target), str(final_dst))
        item_type = "Thư mục" if target.is_dir() else "File"
        return f"✏️ Đổi tên {item_type.lower()} thành công.\n  Tên cũ: {old_name}\n  Tên mới: {final_dst.name}"
    except PermissionError:
        return f"❌ Không có quyền đổi tên: {path}"
    except Exception as e:
        return f"❌ Lỗi: {e}"


def _rename_batch_map(folder_path: str, new_names: List[Dict[str, str]]) -> str:
    folder = _normalize_path(folder_path)
    if not folder.exists():
        return f"❌ Thư mục không tồn tại: {folder_path}"
    if not folder.is_dir():
        return f"❌ Không phải thư mục: {folder}"
    renamed = []
    errors = []
    for item in new_names:
        old = item.get("old_name")
        new = item.get("new_name")
        if not old or not new:
            errors.append(f"Thiếu key: {item}")
            continue
        old_path = folder / old
        if not old_path.exists():
            errors.append(f"{old}: không tồn tại trong {folder}")
            continue
        new_path = folder / new
        if new_path.exists() and new_path != old_path:
            stem, suffix = new_path.stem, new_path.suffix
            counter = 1
            while new_path.exists():
                new_path = folder / f"{stem}_v{counter}{suffix}"
                counter += 1
        try:
            os.rename(str(old_path), str(new_path))
            renamed.append(f"{old} → {new_path.name}")
        except Exception as e:
            errors.append(f"{old}: {e}")
    if not renamed:
        return f"❌ Không có mục nào được đổi tên trong {folder}.\n" + ("\nLỗi: " + ", ".join(errors) if errors else "")
    result = f"📁 Đã đổi tên {len(renamed)} mục trong '{folder}':\n" + "\n".join(renamed)
    if errors:
        result += f"\n⚠️ Lỗi: {', '.join(errors)}"
    return result


def _rename_batch_regex(folder_path: str, pattern_regex: str, replacement: Union[str, callable]) -> str:
    """Đổi tên batch dùng regex pattern."""
    folder = _normalize_path(folder_path)
    if not folder.exists():
        return f"❌ Thư mục không tồn tại: {folder_path}"
    if not folder.is_dir():
        return f"❌ Không phải thư mục: {folder}"
    try:
        items = list(folder.iterdir())
    except PermissionError:
        return f"❌ Không đọc được {folder}"
    renamed = []
    errors = []
    try:
        regex = re.compile(pattern_regex, re.IGNORECASE)
    except re.error as e:
        return f"❌ Regex không hợp lệ: {pattern_regex} - {e}"
    for item in items:
        new_name = regex.sub(replacement, item.name)
        if new_name == item.name:
            continue
        new_path = folder / new_name
        if new_path.exists() and new_path != item:
            stem, suffix = new_path.stem, new_path.suffix
            c = 1
            while new_path.exists():
                new_path = folder / f"{stem}_v{c}{suffix}"
                c += 1
        try:
            os.rename(str(item), str(new_path))
            renamed.append(f"{item.name} → {new_path.name}")
        except Exception as e:
            errors.append(f"{item.name}: {e}")
    if not renamed:
        return f"🔍 Không có mục nào thay đổi với regex '{pattern_regex}' trong '{folder}'."
    result = f"📁 Đã đổi tên {len(renamed)} mục trong '{folder}':\n" + "\n".join(renamed[:20])
    if len(renamed) > 20:
        result += f"\n... và {len(renamed)-20} mục khác"
    if errors:
        result += f"\n⚠️ Lỗi: {', '.join(errors[:5])}"
    return result


def rename_file(
    path: str = "",
    new_name: str = "",
    folder_path: str = "",
    pattern: str = "",
    replacement: str = "",
    folder_pattern: str = "",
    new_folder_name_prefix: str = "",
    old_prefix: str = "",
    new_prefix: str = "",
    new_names: Optional[List[Dict[str, str]]] = None,
    username: str = "",
    **kwargs
) -> str:
    """
    Đổi tên file/thư mục.

    Hỗ trợ:
    - Single: path + new_name
    - Batch mapping: folder_path + new_names
    - Batch pattern (wildcard): folder_path + pattern + replacement
    - Batch regex (folder_pattern + new_folder_name_prefix): thay "haha" -> "huhu"
    """
    real_username = username or os.getenv("USERNAME") or os.getenv("USER") or ""
    default_downloads = str(Path.home() / "Downloads")

    # 1. Xử lý batch regex với folder_pattern + new_folder_name_prefix
    if folder_pattern and new_folder_name_prefix:
        # Nếu không có folder_path, mặc định là Downloads
        folder = _normalize_path(folder_path) if folder_path else _normalize_path(default_downloads)
        if not folder.exists():
            return f"❌ Thư mục không tồn tại: {folder_path or default_downloads}"
        if not folder.is_dir():
            return f"❌ Không phải thư mục: {folder}"
        # Lấy tất cả thư mục con
        try:
            items = [item for item in folder.iterdir() if item.is_dir()]
        except PermissionError:
            return f"❌ Không đọc được {folder}"
        renamed = []
        errors = []
        # Thay thế literal "haha" -> "huhu", "haha1" -> "huhu1"
        for item in items:
            old_name = item.name
            new_name = old_name.replace("haha", "huhu").replace("haha1", "huhu1")
            if new_name == old_name:
                continue
            new_path = folder / new_name
            if new_path.exists():
                stem, suffix = new_path.stem, new_path.suffix
                c = 1
                while new_path.exists():
                    new_path = folder / f"{stem}_v{c}{suffix}"
                    c += 1
            try:
                os.rename(str(item), str(new_path))
                renamed.append(f"{old_name} → {new_path.name}")
            except Exception as e:
                errors.append(f"{old_name}: {e}")
        if not renamed:
            return f"🔍 Không tìm thấy thư mục nào chứa 'haha' hoặc 'haha1' trong '{folder}'."
        result = f"📁 Đã đổi tên {len(renamed)} thư mục trong '{folder}':\n" + "\n".join(renamed)
        if errors:
            result += f"\n⚠️ Lỗi: {', '.join(errors)}"
        return result

    # 2. Batch mapping
    if folder_path and new_names and isinstance(new_names, list):
        folder_path = folder_path.replace("[username]", real_username).replace("{username}", real_username)
        return _rename_batch_map(folder_path, new_names)

    # 3. Batch wildcard (pattern) hoặc regex
    if folder_path and pattern and replacement:
        folder_path = folder_path.replace("[username]", real_username).replace("{username}", real_username)
        # Heuristic: nếu pattern chứa '.*' hoặc '.+' hoặc '^' hoặc '$' -> coi là regex thuần
        if re.search(r'\.\*|\.\+|[\^\$]', pattern):
            regex_pattern = pattern  # dùng trực tiếp, không escape
        else:
            # Xử lý wildcard chuẩn: không escape dấu * và ?
            STAR = "___STAR___"
            QMARK = "___QMARK___"
            temp = pattern.replace("*", STAR).replace("?", QMARK)
            escaped = re.escape(temp)
            regex_pattern = escaped.replace(STAR, ".*").replace(QMARK, ".")
        return _rename_batch_regex(folder_path, regex_pattern, replacement)

    # 4. Single
    if path and new_name:
        path = path.replace("[username]", real_username).replace("{username}", real_username)
        return _rename_single(path, new_name)

    return "❌ Không xác định được chế độ rename. Hãy cung cấp folder_pattern+new_folder_name_prefix (rename batch) hoặc path+new_name (đơn lẻ)."