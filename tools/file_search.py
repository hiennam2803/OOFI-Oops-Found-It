import os
import fnmatch
import time
from pathlib import Path
from datetime import datetime

# Danh sách folder rác hệ thống chặn quét để đỡ tốn sức RAM
IGNORE_FOLDERS = {
    "appdata", "node_modules", ".git", "__pycache__",
    "venv", ".venv", "env", "ntuser", "$recycle.bin",
    "windows", "system32", "program files", "program files (x86)",
}

# BỘ NHỚ ĐỆM CHIẾN THẦN (CACHE)
# Lưu cấu trúc: {(folder, pattern, max_depth): (timestamp, results_list)}
_SEARCH_CACHE = {}
CACHE_TTL = 15  # Hết hạn sau 15 giây. Trong 15s này gõ lại lệnh là ra kết quả trong 0 giây!

def _smart_pattern(pattern: str) -> str:
    """Tự động chuyển thành fuzzy match nếu user gõ thiếu."""
    pattern = pattern.strip().strip("'\"")
    if "." not in pattern and "*" not in pattern:
        return f"*{pattern}*"
    return pattern

def _fast_scan(base_path: Path, pattern: str, max_depth: int) -> list[str]:
    """Thuật toán dùng os.scandir tăng tốc độ cào cấu ổ cứng gấp 5 lần os.walk"""
    results = []
    base_depth = len(base_path.parts)
    
    # Dùng hàng đợi (Queue) để tự duyệt cây thư mục theo độ sâu, tối ưu hơn os.walk
    queue = [(base_path, 0)]
    
    while queue:
        current_dir, current_depth = queue.pop(0)
        
        # Chốt chặn độ sâu tối đa
        if current_depth >= max_depth:
            continue
            
        try:
            # os.scandir trả về các DirEntry, húp thông tin cực nhanh không tốn RAM
            with os.scandir(current_dir) as entries:
                for entry in entries:
                    name_lower = entry.name.lower()
                    
                    # Bộ lọc folder rác + folder ẩn ẩn hiện hiện
                    if entry.is_dir():
                        if name_lower not in IGNORE_FOLDERS and not entry.name.startswith("."):
                            queue.append((Path(entry.path), current_depth + 1))
                            
                    # Khớp file thì bốc thông tin luôn
                    elif entry.is_file():
                        if fnmatch.fnmatch(name_lower, pattern.lower()):
                            try:
                                stat = entry.stat()
                                size_kb = stat.st_size / 1024
                                modified = datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M")
                                size_str = (
                                    f"{size_kb:.1f} KB"
                                    if size_kb < 1024
                                    else f"{size_kb / 1024:.1f} MB"
                                )
                                results.append(f"📄 {entry.path}  [{size_str}]  Sửa: {modified}")
                            except (PermissionError, FileNotFoundError):
                                continue
                                
        except (PermissionError, FileNotFoundError):
            continue  # Gặp folder cấm là quay xe ngay
            
    return results

def search_files(pattern: str, folder: str = "", max_depth: int = 3) -> str:
    """
    Tìm file hệ chiến thần siêu tốc độ.
    Tự động ăn Cache nếu tìm lại câu lệnh cũ trong vòng 15 giây.
    """
    t_start = time.time() # Bấm giờ xem chạy mất bao nhiêu mili-giây
    
    if not folder:
        folder = str(Path.home())

    username = os.getenv("USERNAME") or os.getenv("USER") or ""
    folder = folder.replace("[username]", username).replace("[YourUsername]", username)
    folder = folder.strip().strip("'\"")
    pattern = _smart_pattern(pattern)

    if not os.path.exists(folder):
        return f"❌ Thư mục không tồn tại: {folder}"

    base_path = Path(folder)
    cache_key = (str(base_path), pattern, max_depth)
    now = time.time()

    # KIỂM TRA BỘ NHỚ ĐỆM (CACHE HIT)
    if cache_key in _SEARCH_CACHE:
        cache_time, cached_results = _SEARCH_CACHE[cache_key]
        if now - cache_time < CACHE_TTL:
            t_delta = (time.time() - t_start) * 1000
            total = len(cached_results)
            output = f"⚡ [CACHE ULTIMATE] Tìm thấy {total} file ({t_delta:.1f} ms):\n" + "\n".join(cached_results[:20])
            if total > 20:
                output += f"\n\n... và {total - 20} file khác"
            return output

    # CHẠY QUÉT THẬT BẰNG ĐỘNG CƠ TURBO OS.SCANDIR
    try:
        results = _fast_scan(base_path, pattern, max_depth)
    except Exception as e:
        return f"❌ Lỗi: {e}"

    # Ghi lại vào Cache để lần sau húp cho mượt
    _SEARCH_CACHE[cache_key] = (now, results)

    if not results:
        return f"🔍 Không tìm thấy '{pattern}' trong '{folder}' (sâu {max_depth} tầng)."

    t_delta = (time.time() - t_start) * 1000
    total = len(results)
    output = f"✅ [TURBO SCAN] Tìm thấy {total} file ({t_delta:.1f} ms):\n" + "\n".join(results[:20])
    if total > 20:
        output += f"\n\n... và {total - 20} file khác"
    return output