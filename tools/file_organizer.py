import os
import shutil
from pathlib import Path

# BẢN ĐỒ ĐỊNH DẠNG TỐI THƯỢNG (Phân loại bằng RAM, tốc độ mili-giây)
EXTENSION_MAP = {
    # Nhóm tài liệu, đồ án
    ".pdf": "Documents",
    ".docx": "Documents",
    ".doc": "Documents",
    ".xlsx": "Documents",
    ".xls": "Documents",
    ".pptx": "Documents",
    ".ppt": "Documents",
    ".txt": "Documents",
    ".md": "Documents",
    # Nhóm ảnh chiến thần
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".svg": "Images",
    # Nhóm bộ cài, file nén
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".exe": "Programs",
    ".msi": "Programs",
    # Nhóm Code (Dân lập trình)
    ".py": "Code",
    ".js": "Code",
    ".html": "Code",
    ".css": "Code",
    ".json": "Code",
    # Nhóm giải trí, nhạc, video
    ".mp3": "Media",
    ".mp4": "Media",
    ".mkv": "Media",
}

def organize_files(folder: str) -> str:
    """
    Tự động quét và gom tất cả các file bừa bộn vào các thư mục chức năng.
    Tốc độ xử lý: Bàn thờ (Dưới 0.1 giây cho cả trăm file).
    """
    if not folder:
        return "❌ Thư mục trống không, đưa đường dẫn đây tao dọn cho mày chiến thần ơi!"

    # Thay username nếu con AI trích xuất có placeholder
    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    folder = folder.replace("[username]", username).replace("[YourUsername]", username).replace("{username}", username)
    folder = folder.strip().strip("'\"")

    target_path = Path(folder)

    if not target_path.exists():
        return f"❌ Thư mục không tồn tại: {folder}"
    if not target_path.is_dir():
        return f"❌ Đây là cái file chứ có phải thư mục đâu mà bắt tao dọn: {folder}"

    moved_count = 0
    skipped_count = 0
    report = []

    try:
        # Dùng os.scandir để húp danh sách file với tốc độ bàn thờ
        with os.scandir(target_path) as entries:
            for entry in entries:
                # CHỈ xử lý FILE ở tầng ngoài cùng, KHÔNG đụng vào các FOLDER sẵn có
                if entry.is_file():
                    file_path = Path(entry.path)
                    ext = file_path.suffix.lower()

                    # Nếu đuôi file nằm trong bản đồ tối thượng thì tiến hành hốt xác
                    if ext in EXTENSION_MAP:
                        sub_folder_name = EXTENSION_MAP[ext]
                        dest_folder = target_path / sub_folder_name

                        # Nếu thư mục con chưa tồn tại (ví dụ chưa có folder Images) -> tạo luôn
                        dest_folder.mkdir(exist_ok=True)

                        dest_file_path = dest_folder / file_path.name

                        # Xử lý trùng tên file: Nếu trùng thì đắp thêm hậu tố để không bị ghi đè mất file gốc
                        if dest_file_path.exists():
                            stem = file_path.stem
                            suffix = file_path.suffix
                            counter = 1
                            while dest_file_path.exists():
                                dest_file_path = dest_folder / f"{stem}_copy{counter}{suffix}"
                                counter += 1

                        # Thực hiện di chuyển file bằng shutil.move (nhanh vờ cờ lờ)
                        shutil.move(str(file_path), str(dest_file_path))
                        moved_count += 1
                    else:
                        skipped_count += 1

    except PermissionError:
        return f"❌ Không có quyền truy cập để dọn dẹp thư mục này: {folder}"
    except Exception as e:
        return f"❌ Đang dọn thì vấp cỏ chấn thương vai: {e}"

    if moved_count == 0:
        return f"🧹 Folder '{target_path.name}' sạch bong kin kít rồi mày ơi, không có file rác nào cần gom!"

    output = f"✅ Đã dọn dẹp xong folder '{target_path.name}' với tốc độ bàn thờ!\n"
    output += f"➔ Gom thành công: {moved_count} file vào các thư mục tương ứng.\n"
    if skipped_count > 0:
        output += f"➔ Bỏ qua: {skipped_count} file lạ không rõ danh tính.\n"
    output += "\nCái này mà sai là đi luôn, nhìn ổ cứng gọn gàng thấy sáng ra liền đúng không chiến thần!"
    return output