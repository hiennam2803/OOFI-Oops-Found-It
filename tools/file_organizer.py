"""
tools/file_organizer.py
Phân loại file tự động theo bản đồ định dạng cứng.
AI chỉ kích hoạt lệnh — Python quyết định phân loại để đảm bảo chính xác 100%.
"""

import os
import shutil
from pathlib import Path


# Bản đồ phân loại file — cứng trong code, không phụ thuộc AI
EXTENSION_MAP: dict[str, str] = {
    # Tài liệu
    ".pdf": "Documents", ".docx": "Documents", ".doc": "Documents",
    ".xlsx": "Documents", ".xls": "Documents", ".pptx": "Documents",
    ".ppt": "Documents",  ".txt": "Documents",  ".md": "Documents",
    ".odt": "Documents",  ".rtf": "Documents",
    # Hình ảnh
    ".jpg": "Images",  ".jpeg": "Images", ".png": "Images",
    ".gif": "Images",  ".svg":  "Images", ".webp": "Images",
    ".bmp": "Images",  ".ico":  "Images",
    # Video
    ".mp4": "Videos", ".mkv": "Videos", ".avi": "Videos",
    ".mov": "Videos",  ".wmv": "Videos",
    # Âm thanh
    ".mp3": "Audio", ".wav": "Audio", ".flac": "Audio",
    ".aac": "Audio", ".ogg": "Audio",
    # Lưu trữ
    ".zip": "Archives", ".rar": "Archives", ".7z": "Archives",
    ".tar": "Archives", ".gz":  "Archives",
    # Phần mềm
    ".exe": "Programs", ".msi": "Programs", ".dmg": "Programs",
    # Mã nguồn
    ".py": "Code", ".js": "Code",   ".ts": "Code",
    ".html": "Code", ".css": "Code", ".java": "Code",
    ".cpp": "Code",  ".c":   "Code", ".json": "Code",
}


def organize_files(folder: str) -> str:
    """
    Phân loại tất cả file trong thư mục vào các thư mục con theo định dạng.
    Chỉ xử lý file ở tầng ngoài cùng, không đệ quy vào thư mục con.

    Args:
        folder: Đường dẫn thư mục cần dọn dẹp.

    Returns:
        Báo cáo số file đã phân loại.
    """
    if not folder:
        return "❌ Vui lòng cung cấp đường dẫn thư mục."

    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    folder   = folder.replace("[username]", username).replace("[YourUsername]", username)
    folder   = folder.replace("{username}", username).strip().strip("'\"")

    target = Path(folder)
    if not target.exists():
        return f"❌ Thư mục không tồn tại: {folder}"
    if not target.is_dir():
        return f"❌ Đây không phải thư mục: {folder}"

    moved     = 0
    skipped   = 0
    moved_log: list[str] = []

    try:
        with os.scandir(target) as entries:
            for entry in entries:
                if not entry.is_file():
                    continue

                fp  = Path(entry.path)
                ext = fp.suffix.lower()

                if ext not in EXTENSION_MAP:
                    skipped += 1
                    continue

                dest_folder = target / EXTENSION_MAP[ext]
                dest_folder.mkdir(exist_ok=True)
                dest_file   = dest_folder / fp.name

                # Xử lý trùng tên
                if dest_file.exists():
                    stem, suffix = fp.stem, fp.suffix
                    counter = 1
                    while dest_file.exists():
                        dest_file = dest_folder / f"{stem}_copy{counter}{suffix}"
                        counter  += 1

                shutil.move(str(fp), str(dest_file))
                moved_log.append(f"  {fp.name}  →  {EXTENSION_MAP[ext]}/")
                moved += 1

    except PermissionError:
        return f"❌ Không có quyền truy cập thư mục: {folder}"
    except Exception as e:
        return f"❌ Lỗi khi phân loại: {e}"

    if moved == 0:
        return f"✅ Thư mục '{target.name}' đã gọn gàng, không có file nào cần phân loại."

    output = (
        f"✅ Phân loại hoàn tất thư mục '{target.name}'.\n"
        f"  Đã di chuyển: {moved} file\n"
        f"  Bỏ qua      : {skipped} file (định dạng không xác định)\n\n"
        f"Chi tiết:\n" + "\n".join(moved_log[:15])
    )
    if moved > 15:
        output += f"\n  ... và {moved - 15} file khác"
    return output