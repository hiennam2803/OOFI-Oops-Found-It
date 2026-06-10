"""
tools/file_organizer.py
Phân loại file tự động theo bản đồ định dạng cứng.
AI chỉ kích hoạt lệnh — Python quyết định phân loại để đảm bảo chính xác 100%.
Hỗ trợ: folder (str) hoặc folder_path (str), tham số force (bool) để bỏ qua kiểm tra an toàn.
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

# Các thư mục tuyệt đối không bao giờ được dọn (để tránh tai nạn)
FORBIDDEN_PATHS = [
    "C:\\", "D:\\", "/", "/home", "/etc", "/usr", "/bin", "/sbin",
    "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)"
]

# Dấu hiệu nhận biết thư mục dự án (nếu tồn tại, sẽ yêu cầu force=True)
PROJECT_MARKERS = ['.git', '.svn', '.hg', 'setup.py', 'pyproject.toml', 'package.json', 'composer.json', 'Cargo.toml']


def organize_files(folder: str = "", folder_path: str = "", force: bool = False, **kwargs) -> str:
    """
    Phân loại tất cả file trong thư mục theo định dạng (dựa trên EXTENSION_MAP).
    Chỉ xử lý file ở tầng ngoài cùng, không đệ quy.

    Tham số:
        folder / folder_path: đường dẫn thư mục cần dọn.
        force: nếu True, bỏ qua các kiểm tra an toàn (forbidden paths, project markers).
    """
    # Xác định đường dẫn đích
    target_path = folder or folder_path
    if not target_path:
        return "❌ Vui lòng cung cấp thư mục (folder hoặc folder_path)."

    # Thay thế username nếu có
    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    target_path = target_path.replace("[username]", username).replace("{username}", username)
    target_path = target_path.strip().strip("'\"")

    target = Path(target_path)
    if not target.exists():
        return f"❌ Thư mục không tồn tại: {target_path}"
    if not target.is_dir():
        return f"❌ Đây không phải thư mục: {target_path}"

    # === Kiểm tra an toàn ===
    abs_path = str(target.resolve()).lower()
    for forbidden in FORBIDDEN_PATHS:
        if abs_path == forbidden.lower() or abs_path.startswith(forbidden.lower() + os.sep):
            if not force:
                return f"❌ Thư mục '{target}' nằm trong danh sách cấm vì lý do an toàn. Dùng force=True nếu thực sự muốn."
            break

    # Phát hiện dự án
    markers_found = []
    for marker in PROJECT_MARKERS:
        if (target / marker).exists():
            markers_found.append(marker)
    if markers_found and not force:
        return (f"⚠️ Thư mục '{target.name}' có dấu hiệu là dự án (tìm thấy: {', '.join(markers_found)}). "
                f"Sẽ KHÔNG tự động dọn dẹp để tránh hỏng cấu trúc. Dùng force=True nếu vẫn muốn dọn.")

    # === Tiến hành phân loại ===
    moved = 0
    skipped = 0
    moved_log: list[str] = []

    try:
        with os.scandir(target) as entries:
            for entry in entries:
                if not entry.is_file():
                    continue

                fp = Path(entry.path)
                ext = fp.suffix.lower()
                if ext not in EXTENSION_MAP:
                    skipped += 1
                    continue

                dest_folder = target / EXTENSION_MAP[ext]
                dest_folder.mkdir(exist_ok=True)
                dest_file = dest_folder / fp.name

                # Xử lý trùng tên
                if dest_file.exists():
                    stem, suffix = fp.stem, fp.suffix
                    counter = 1
                    while dest_file.exists():
                        dest_file = dest_folder / f"{stem}_copy{counter}{suffix}"
                        counter += 1

                shutil.move(str(fp), str(dest_file))
                moved_log.append(f"  {fp.name}  →  {EXTENSION_MAP[ext]}/")
                moved += 1

    except PermissionError:
        return f"❌ Không có quyền truy cập thư mục: {target}"
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