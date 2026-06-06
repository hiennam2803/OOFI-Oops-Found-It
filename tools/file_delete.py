import os
from pathlib import Path
from send2trash import send2trash

def delete_file(path: str) -> str:
    """
    Xóa file hoặc thư mục an toàn bằng cách quăng vào Recycle Bin (Thùng rác).
    Ép hỏi Yes/No trực tiếp trên Terminal để bảo vệ chiến thần.
    """
    if not path:
        return "❌ Đường dẫn trống không hà, đưa cái file mày muốn trảm đây tao xử cho chiến thần!"

    # Thay thế mấy cái placeholder username nếu AI trích xuất bị ngáo
    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    path = path.replace("[username]", username).replace("[YourUsername]", username).replace("{username}", username)
    path = path.strip().strip("'\"")

    target_path = Path(path)

    # CHỐT CHẶN BẢO MẬT BLACKLIST (Cái này mà sai là đi luôn hệ thống!)
    blacklist_paths = [
        str(Path.home()),                                 # Thư mục User gốc (C:/Users/ASUS)
        str(Path.home() / "Desktop"),                     # Toàn bộ Desktop
        str(Path.home() / "Downloads"),                   # Toàn bộ Downloads
        str(Path.home() / "Documents"),                   # Toàn bộ Documents
        os.getenv("WINDIR", "C:\\Windows"),               # Thư mục Windows
        "C:\\", "D:\\", "E:\\"                            # Gốc các ổ đĩa
    ]

    # Chuẩn hóa đường dẫn để so sánh chính xác nhất
    try:
        resolved_path = str(target_path.resolve()).lower()
        for bl_path in blacklist_paths:
            if resolved_path == str(Path(bl_path).resolve()).lower():
                return f"⚠️ [CẢNH BÁO PHÁ HOẠI]: Mày định lừa tao xóa thư mục cốt lõi '{target_path}' hả bưởi? Quên đi nhé, sập nguồn máy tao lấy gì húc tạ!"
    except Exception:
        pass 

    # Kiểm tra sự tồn tại thật sự của file/folder trên ổ cứng
    if not target_path.exists():
        return f"❌ File hoặc thư mục không tồn tại: {path} (Chưa kịp xóa đã bay màu rồi mày ơi)"

    # 🚨 QUẢ CHỐT CHẶN YES/NO BẰNG CƠM - ÉP PHẢI HỎI ĐÉO CHO CHẠY LỤI
    item_type = "Thư mục" if target_path.is_dir() else "File"
    print(f"\n☠️  [TRẢM FILE CẢNH BÁO]: Thằng đệ OOFI đang giơ gươm chuẩn bị xử lý:")
    print(f"➔ Đối tượng trảm: {item_type} '{target_path.name}'")
    print(f"➔ Đường dẫn: {target_path}")
    
    confirm_input = input(f"Mày có chắc chắn muốn tiễn cái {item_type.lower()} này vào Thùng rác không? [y/N]: ").strip().lower()
    if confirm_input not in ("y", "yes", "có"):
        return f"🛑 Đã thu gươm! Chiến thần bảo tha nên {item_type.lower()} vẫn an toàn nha mày!"

    try:
        # Bắn file/folder vào thùng rác bằng tốc độ bàn thờ
        send2trash(str(target_path))
        return f"🗑️ Đã tiễn {item_type} '{target_path.name}' vào Thùng rác thành công rực rỡ!\n➔ Đường dẫn cũ: {path}\nNghe tới đây là thấy nhẹ lòng liền đúng không chiến thần?"

    except PermissionError:
        return f"❌ Không có quyền trảm cái file này rồi mày ơi: {path} (File đang mở hoặc bị hệ thống khóa rồi)"
    except Exception as e:
        return f"❌ Đang tính rút gươm trảm file thì vấp cỏ chấn thương vai: {e}"