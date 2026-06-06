import json
import os
from pathlib import Path

# ── Blacklist hệ thống ────────────────────────────────────
SYSTEM_BLACKLIST = [
    "c:\\windows",
    "c:\\program files",
    "c:\\program files (x86)",
    "c:\\system32",
]

# ── Tools có tính phá hủy — bắt buộc confirm ─────────────
DESTRUCTIVE_TOOLS = [
    "delete_file",
    "move_file",
    "organize_files",
    "rename_file",
]


def is_path_safe(target_path: str, user_blacklist: list = []) -> bool:
    """Lớp 1 — kiểm tra đường dẫn có nằm trong vùng cấm không."""
    try:
        resolved = str(Path(target_path).resolve()).lower()

        for banned in SYSTEM_BLACKLIST:
            banned_clean = str(Path(banned).resolve()).lower()
            if resolved.startswith(banned_clean):
                return False

        for banned in user_blacklist:
            try:
                banned_clean = str(Path(banned).resolve()).lower()
                if resolved.startswith(banned_clean):
                    return False
            except Exception:
                continue

        return True
    except Exception:
        return False  # Đường dẫn lạ → block luôn


def parse_response(response: str) -> dict:
    """Parse JSON từ response AI, dọn sạch rác markdown."""
    cleaned = response.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end   = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(cleaned[start:end])
            except Exception:
                pass
        return {
            "tool":    "parse_error",
            "params":  {},
            "confirm": False,
            "message": f"AI trả về không đúng JSON: {response[:100]}"
        }


def dispatch(parsed: dict, user_blacklist: list = []) -> dict:
    """
    Nhận JSON đã parse → kiểm tra an toàn → hỏi confirm trên terminal nếu cần → gọi tool.
    """
    tool    = parsed.get("tool", "unknown")
    params  = parsed.get("params", {})
    confirm = parsed.get("confirm", False)
    message = parsed.get("message", "")

    # Tool không xác định
    if tool in ("unknown", "off_topic", "parse_error"):
        return {"success": False, "result": message}

    # Lớp 1 — kiểm tra an toàn đường dẫn
    for key, value in params.items():
        if isinstance(value, str) and ("/" in value or "\\" in value):
            if not is_path_safe(value, user_blacklist):
                return {
                    "success": False,
                    "result":  f"❌ Đường dẫn bị chặn (vùng cấm): {value}"
                }

    # Lớp 2 — CỨU NGHẼN CHO BẢN TEST TERMINAL NÈ MÀY!
    if tool in DESTRUCTIVE_TOOLS and not confirm:
        print(f"\n⚠️  [OOFI CẢNH BÁO]: Lệnh này có thể thay đổi ổ cứng của mày!")
        print(f"➔ Hành động: {message or tool}")
        print(f"➔ Tham số: {params}")
        user_choice = input("Mày có chắc chắn muốn nện lệnh này không? [y/N]: ").strip().lower()
        
        if user_choice not in ("y", "yes", "có"):
            return {
                "success": False,
                "result": "🛑 Chiến thần đã hủy lệnh, an toàn là trên hết mày ơi!"
            }

    # Đã vượt qua kiểm tra hoặc đồng ý chạy -> Nện luôn! (Bơm thêm message vào đuôi)
    return _run_tool(tool, params, message)


def _run_tool(tool: str, params: dict, message: str = "") -> dict:
    """Import và gọi tool tương ứng chạy thật dưới ổ cứng."""
    try:
        if tool == "search_files":
            from tools.file_search import search_files
            result = search_files(**params)

        elif tool == "rename_file":
            from tools.file_rename import rename_file
            
            # Bốc đường dẫn cũ
            path_val = params.get("path") or params.get("file_path") or params.get("src")
            
            # 1. Thử bốc tên mới trong params trước như bình thường
            new_name_val = params.get("new_name") or params.get("new") or params.get("target_name") or params.get("name")
            
            # 2. 🚨 QUẢ KÈO SIÊU CHIẾN THẦN: Nếu AI ngáo đá đéo nhả new_name vào params nhưng lại viết ở message
            if not new_name_val and message:
                import re
                # Dùng Regex hệ bàn thờ quét xem có chữ "thành [Tên_Mới]" hoặc "sang [Tên_Mới]" không
                match = re.search(r'(?:thành|sang|to)\s+([^\s]+)', message, re.IGNORECASE)
                if match:
                    new_name_val = match.group(1).strip().strip("'\"`•.")
            
            # Vả thẳng vào hàm, chấp tất cả các thể loại AI lười biếng
            result = rename_file(path=path_val, new_name=new_name_val)

        elif tool == "organize_files":
            from tools.file_organizer import organize_files
            result = organize_files(**params)

        elif tool == "move_file":
            from tools.file_move import move_file
            # Bọc lót khôn ngoan phòng hờ AI nhả key bậy bạ cho lệnh Di chuyển
            src_val = params.get("src") or params.get("path") or params.get("source") or params.get("file_path")
            dst_val = params.get("dst") or params.get("destination") or params.get("target") or params.get("to")
            result = move_file(src=src_val, dst=dst_val)

        elif tool == "copy_file":
            from tools.file_copy import copy_file
            # Bọc lót khôn ngoan phòng hờ AI nhả key bậy bạ cho lệnh Sao chép
            src_val = params.get("src") or params.get("path") or params.get("source") or params.get("file_path")
            dst_val = params.get("dst") or params.get("destination") or params.get("target") or params.get("to")
            result = copy_file(src=src_val, dst=dst_val)

        elif tool == "delete_file":
            from tools.file_delete import delete_file
            result = delete_file(**params)

        elif tool == "create_file":
            from tools.file_create import create_file
            
            # Bốc đường dẫn file
            path_val = params.get("path") or params.get("file_path")
            
            # 1. Thử bốc nội dung trong params trước như bình thường
            content_val = params.get("content") or params.get("text") or params.get("data")
            
            # 2. 🚨 BIỆN PHÁP CHIẾN THẦN: Nếu AI lười biếng giấu nội dung ở message ngoài tai
            if not content_val and message:
                import re
                # Quét xem có chữ "nội dung [Đoạn_Văn_Bản]" hoặc "chứa [Đoạn_Văn_Bản]" không
                match = re.search(r'(?:nội\s+dung|với\s+nội\s+dung|chứa)\s+(.+)', message, re.IGNORECASE)
                if match:
                    content_val = match.group(1).strip().strip("'\"`•.")
            
            # Nếu cuối cùng vẫn đéo có gì thì mới cho bằng chuỗi rỗng
            if not content_val:
                content_val = ""
                
            # Vả thẳng vào hàm, chấp luôn mọi thể loại AI ngáo đá
            result = create_file(path=path_val, content=content_val)
        elif tool == "file_info":
            from tools.file_info import file_info
            result = file_info(**params)

        elif tool == "find_duplicates":
            from tools.file_duplicate import find_duplicates
            result = find_duplicates(**params)

        elif tool == "compress_files":
            from tools.file_compress import compress_files
            result = compress_files(**params)

        elif tool == "file_history":
            from tools.file_history import file_history
            result = file_history(**params)

        elif tool == "disk_analyzer":
            from tools.disk_analyzer import disk_analyzer
            result = disk_analyzer(**params)

        elif tool == "summarize_file":
            from tools.summarizer import summarize_file
            result = summarize_file(**params)

        else:
            result = f"❌ Tool không tồn tại: {tool}"

        return {"success": True, "result": result}

    except TypeError as e:
        return {"success": False, "result": f"❌ Tham số sai cấu trúc: {e}"}
    except Exception as e:
        return {"success": False, "result": f"❌ Lỗi thực thi dưới nền: {e}"}