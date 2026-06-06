"""
tools/file_compress.py
Nén và giải nén file ZIP bằng threading để không treo giao diện.
"""

import os
import zipfile
import threading
from pathlib import Path


def compress_files(path: str, action: str = "zip") -> str:
    """
    Nén hoặc giải nén file/thư mục.

    Args:
        path  : Đường dẫn file hoặc thư mục cần xử lý.
        action: 'zip' để nén, 'unzip' để giải nén.

    Returns:
        Thông báo kết quả.
    """
    if not path:
        return "❌ Vui lòng cung cấp đường dẫn file hoặc thư mục."

    target = Path(path.strip().strip("'\""))
    if not target.exists():
        return f"❌ Đường dẫn không tồn tại: {path}"

    action = action.lower().strip()

    if action == "zip":
        return _zip(target)
    elif action == "unzip":
        return _unzip(target)
    else:
        return "❌ Hành động không hợp lệ. Chỉ hỗ trợ 'zip' hoặc 'unzip'."


def _zip(target: Path) -> str:
    """Nén file hoặc thư mục thành ZIP."""
    zip_path = (
        target.with_suffix(".zip")
        if target.is_file()
        else target.parent / f"{target.name}.zip"
    )

    result   = {"status": ""}
    progress = {"current": 0, "total": 0}

    def _worker():
        try:
            if target.is_file():
                files = [target]
            else:
                files = [f for f in target.rglob("*") if f.is_file()]

            progress["total"] = len(files)

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for i, f in enumerate(files):
                    arcname = f.relative_to(target.parent)
                    zf.write(f, arcname)
                    progress["current"] = i + 1

            result["status"] = "ok"
        except Exception as e:
            result["status"] = f"error:{e}"

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    thread.join(timeout=300)  # Timeout 5 phút

    if thread.is_alive():
        return "❌ Quá trình nén vượt quá thời gian cho phép (5 phút)."
    if result["status"].startswith("error:"):
        return f"❌ Lỗi khi nén: {result['status'][6:]}"

    size = zip_path.stat().st_size / (1024 * 1024)
    return (
        f"📦 Nén thành công {progress['total']} file.\n"
        f"  Đầu ra : {zip_path}\n"
        f"  Kích thước: {size:.2f} MB"
    )


def _unzip(target: Path) -> str:
    """Giải nén file ZIP."""
    if target.suffix.lower() != ".zip":
        return f"❌ File không phải định dạng ZIP: {target.name}"

    extract_dir = target.parent / target.stem

    try:
        with zipfile.ZipFile(target, "r") as zf:
            total = len(zf.namelist())
            extract_dir.mkdir(parents=True, exist_ok=True)
            zf.extractall(extract_dir)

        return (
            f"📂 Giải nén thành công {total} file.\n"
            f"  Thư mục đầu ra: {extract_dir}"
        )
    except zipfile.BadZipFile:
        return f"❌ File ZIP bị hỏng hoặc không đúng định dạng: {target.name}"
    except Exception as e:
        return f"❌ Lỗi khi giải nén: {e}"