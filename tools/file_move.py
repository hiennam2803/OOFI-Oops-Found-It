import os
import shutil
import fnmatch
from pathlib import Path

def _normalize_path(path_str: str) -> str:
    if not path_str:
        return ""
    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    path_str = path_str.replace("[username]", username).replace("{username}", username)
    path_str = path_str.strip().strip("'\"")
    # Chỉ sửa khi path không tồn tại và có "Download" nhưng không phải "Downloads"
    # Tránh thay "Downloads" thành "Downloadss"
    if "Download" in path_str:
        # Tách phần cuối để kiểm tra
        p = Path(path_str)
        # Nếu path có wildcard, lấy phần cha
        if "*" in path_str or "?" in path_str:
            parent = p.parent
            if not parent.exists() and "Download" in str(parent) and "Downloads" not in str(parent):
                # Thay thế "Download" thành "Downloads" trong phần cha
                new_parent = str(parent).replace("Download", "Downloads")
                path_str = path_str.replace(str(parent), new_parent)
        else:
            if not p.exists() and "Download" in path_str and "Downloads" not in path_str:
                path_str = path_str.replace("Download", "Downloads")
    return path_str

def move_file(source_path: str = "", destination_path: str = "", **kwargs) -> str:
    src = source_path
    dst = destination_path
    if not src or not dst:
        return "❌ Vui lòng cung cấp source_path và destination_path"
    src = _normalize_path(src)
    dst = _normalize_path(dst)

    dst_path = Path(dst)
    dst_path.mkdir(parents=True, exist_ok=True)

    # Xử lý wildcard
    if "*" in src or "?" in src:
        src_path = Path(src)
        parent = src_path.parent
        pattern = src_path.name
        if not parent.exists():
            return f"❌ Thư mục không tồn tại: {parent}"
        try:
            items = list(parent.iterdir())
        except PermissionError:
            return f"❌ Không đọc được {parent}"
        matched = [item for item in items if fnmatch.fnmatch(item.name.lower(), pattern.lower())]
        if not matched:
            return f"⚠️ Không tìm thấy mục nào với pattern: {src}"
        moved = []
        for item in matched:
            final = dst_path / item.name
            if final.exists():
                stem, suffix = item.stem, item.suffix
                c = 1
                while final.exists():
                    final = dst_path / f"{stem}_moved{c}{suffix}"
                    c += 1
            try:
                shutil.move(str(item), str(final))
                moved.append(f"  ✓ {item.name}")
            except Exception as e:
                moved.append(f"  ✗ {item.name} — {e}")
        if not moved:
            return "❌ Không có mục nào được di chuyển"
        return f"🚚 Di chuyển {len(moved)} mục đến {dst}:\n" + "\n".join(moved)

    # File/thư mục đơn
    src_path = Path(src)
    if not src_path.exists():
        return f"❌ Không tìm thấy: {src}"
    final = dst_path / src_path.name
    if final.exists():
        stem, suffix = src_path.stem, src_path.suffix
        c = 1
        while final.exists():
            final = dst_path / f"{stem}_moved{c}{suffix}"
            c += 1
    try:
        shutil.move(str(src_path), str(final))
        return f"🚚 Di chuyển thành công:\n  {src} → {final}"
    except Exception as e:
        return f"❌ Lỗi: {e}"