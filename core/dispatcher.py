# core/dispatcher.py

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
    # Nếu chạy trên terminal mà gặp tool nguy hiểm và chưa confirm -> hỏi trực tiếp luôn!
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

    # Đã vượt qua kiểm tra hoặc đồng ý chạy -> Nện luôn!
    return _run_tool(tool, params)


def _run_tool(tool: str, params: dict) -> dict:
    """Import và gọi tool tương ứng chạy thật dưới ổ cứng."""
    try:
        if tool == "search_files":
            from tools.file_search import search_files
            result = search_files(**params)

        elif tool == "rename_file":
            from tools.file_rename import rename_file
            result = rename_file(**params)

        elif tool == "organize_files":
            from tools.file_organizer import organize_files
            result = organize_files(**params)

        elif tool == "move_file":
            from tools.file_move import move_file
            result = move_file(**params)

        elif tool == "copy_file":
            from tools.file_copy import copy_file
            result = copy_file(**params)

        elif tool == "delete_file":
            from tools.file_delete import delete_file
            result = delete_file(**params)

        elif tool == "create_file":
            from tools.file_create import create_file
            result = create_file(**params)

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