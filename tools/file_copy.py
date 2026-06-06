import os
import shutil
from pathlib import Path

def copy_file(src: str, dst: str) -> str:
    """
    Sao chép file siêu tốc độ, giữ nguyên meta-data gốc.
    src: Đường dẫn file gốc cần sao chép.
    dst: Đường dẫn thư mục đích hoặc file đích mới.
    """
    if not src or not dst:
        return "❌ Thiếu đường dẫn gốc hoặc đích rồi chiến thần ơi, đưa đủ đây tao copy cho!"

    # Khử mấy cái placeholder tào lao của AI nếu có
    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    src = src.replace("[username]", username).replace("{username}", username).strip().strip("'\"")
    dst = dst.replace("[username]", username).replace("{username}", username).strip().strip("'\"")

    src_path = Path(src)
    dst_path = Path(dst)

    if not src_path.exists():
        return f"❌ File gốc không tồn tại thì sao chép kiểu gì mày: {src}"
    if not src_path.is_file():
        return f"❌ Tool này chỉ chơi hệ sao chép file lẻ thôi, không chơi cả folder nha chiến thần: {src}"

    # Nếu dst là một thư mục (ví dụ: C:/Users/ASUS/Desktop) -> tự đắp tên file gốc vào
    if dst_path.is_dir() or dst.endswith("/") or dst.endswith("\\"):
        dst_path.mkdir(exist_ok=True, parents=True)
        final_dst = dst_path / src_path.name
    else:
        # Nếu dst là một đường dẫn file đầy đủ mới (ví dụ: D:/Target/FileNew.pdf)
        dst_path.parent.mkdir(exist_ok=True, parents=True)
        final_dst = dst_path

    # Xử lý trùng tên: Nếu file đích đã có sẵn -> Đắp thêm hậu tố copy để không ghi đè mất file cũ
    if final_dst.exists():
        stem = final_dst.stem
        suffix = final_dst.suffix
        counter = 1
        while final_dst.exists():
            final_dst = final_dst.parent / f"{stem}_copy{counter}{suffix}"
            counter += 1

    try:
        # Nện lệnh sao chép hệ bàn thờ
        shutil.copy2(str(src_path), str(final_dst))
        return f"📋 Sao chép file thành công rực rỡ với tốc độ bàn thờ!\n➔ Từ: {src}\n➔ Đến: {final_dst}\nCái này mà sai là đi luôn, nhìn mượt vờ cờ lờ đúng không mày!"
    except PermissionError:
        return f"❌ Không có quyền sao chép file này rồi: {src} (File bị khóa hoặc folder đích cấm ghi)"
    except Exception as e:
        return f"❌ Đang copy thì vấp cỏ chấn thương vai: {e}"