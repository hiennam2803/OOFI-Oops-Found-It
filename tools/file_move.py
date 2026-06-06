import os
import subprocess
from pathlib import Path

def move_file(src: str, dst: str) -> str:
    """
    Di chuyển file/folder với tốc độ bàn thờ bằng cách gọi thẳng Robocopy của Windows.
    Chấp cả file nặng vài chục GB xuyên ổ đĩa!
    """
    if not src or not dst:
        return "❌ Đưa thiếu đường dẫn đi và đến rồi, đưa đủ đây tao bốc vác cho chiến thần!"

    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    src = src.replace("[username]", username).replace("{username}", username).strip().strip("'\"")
    dst = dst.replace("[username]", username).replace("{username}", username).strip().strip("'\"")

    src_path = Path(src)
    dst_path = Path(dst)

    if not src_path.exists():
        return f"❌ Đối tượng gốc đéo tồn tại để mà di chuyển: {src}"

    # Chuẩn hóa đường dẫn đích
    if dst_path.is_dir() or dst.endswith("/") or dst.endswith("\\"):
        dst_path.mkdir(exist_ok=True, parents=True)
        final_dst_dir = dst_path
        file_name = src_path.name if src_path.is_file() else ""
    else:
        dst_path.parent.mkdir(exist_ok=True, parents=True)
        final_dst_dir = dst_path.parent
        file_name = dst_path.name

    try:
        # TRƯỜNG HỢP 1: DI CHUYỂN NGUYÊN CẢ FOLDER TRỌNG TẢI NẶNG
        if src_path.is_dir():
            # /MOVE: Di chuyển cả folder và xóa gốc
            # /E: Gom hết folder con kể cả folder trống
            # /MT:32: Mở 32 luồng CPU cùng bốc vác một lúc, tốc độ giật cục luôn!
            cmd = f'robocopy "{src_path}" "{final_dst_dir}" /E /MOVE /MT:32 /R:1 /W:1'
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"🚚 [ROBOCOPY MULTI-THREAD]: Đã bốc vác nguyên thư mục '{src_path.name}' sang chỗ mới với tốc độ bàn thờ!\n➔ Đến: {final_dst_dir}"

        # TRƯỜNG HỢP 2: DI CHUYỂN FILE LẺ
        else:
            # Nếu trùng tên ở chỗ mới -> Đổi tên an toàn chứ không cho đè chết file cũ
            check_dst = final_dst_dir / (file_name or src_path.name)
            if check_dst.exists():
                stem = check_dst.stem
                suffix = check_dst.suffix
                counter = 1
                while check_dst.exists():
                    file_name = f"{stem}_moved_copy{counter}{suffix}"
                    check_dst = final_dst_dir / file_name
                    counter += 1
            else:
                file_name = file_name or src_path.name

            # Robocopy di chuyển file lẻ: gốc_dir đích_dir file_name /MOV
            cmd = f'robocopy "{src_path.parent}" "{final_dst_dir}" "{src_path.name}" /MOV /MOV /R:1 /W:1'
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Nếu mày muốn đổi tên file lẻ lúc di chuyển sang chỗ mới
            if file_name != src_path.name:
                os.rename(str(final_dst_dir / src_path.name), str(final_dst_dir / file_name))

            return f"🚚 [ROBOCOPY NITRO]: Đã sút file '{file_name}' sang chỗ mới xuyên ổ đĩa trong chớp mắt!\n➔ Đến: {final_dst_dir / file_name}"

    except Exception as e:
        return f"❌ Định bật Nitro Robocopy nhưng bị vấp cỏ chấn thương vai: {e}"