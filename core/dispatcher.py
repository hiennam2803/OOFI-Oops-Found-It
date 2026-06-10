"""
core/dispatcher.py
Dispatcher — nhận JSON từ AI, kiểm tra an toàn, và thực thi tool.
"""

import json
import re
from pathlib import Path

SYSTEM_BLACKLIST = [
    "c:\\windows",
    "c:\\program files",
    "c:\\program files (x86)",
    "c:\\system32",
]

DESTRUCTIVE_TOOLS = {
    "delete_file",
    "move_file",
    "organize_files",
    "rename_file",
}

def is_path_safe(target_path: str, user_blacklist: list[str] | None = None) -> bool:
    if user_blacklist is None:
        user_blacklist = []
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
        return False

def parse_response(response: str) -> dict:
    cleaned = response.strip()
    if cleaned.startswith("```"):
        parts = cleaned.split("```")
        cleaned = parts[1] if len(parts) > 1 else cleaned
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(cleaned[start:end])
        except Exception:
            pass
    return {
        "tool": "parse_error",
        "params": {},
        "confirm": False,
        "message": f"Không thể parse JSON từ response: {response[:150]}",
    }

def dispatch(
    parsed: dict,
    user_blacklist: list[str] | None = None,
    confirmed: bool = False,
) -> dict:
    if user_blacklist is None:
        user_blacklist = []
    tool = parsed.get("tool", "unknown")
    params = parsed.get("params", {})
    message = parsed.get("message", "")

    if tool == "reply":
        return {"success": True, "result": message}

    if tool in ("unknown", "off_topic", "parse_error"):
        return {"success": False, "result": message}

    for value in params.values():
        if isinstance(value, str) and ("/" in value or "\\" in value):
            if not is_path_safe(value, user_blacklist):
                return {
                    "success": False,
                    "result": f"❌ Thao tác bị từ chối: đường dẫn nằm trong vùng bảo vệ.\n  Đường dẫn: {value}",
                }

    if tool in DESTRUCTIVE_TOOLS and not confirmed:
        return {
            "success": False,
            "need_confirm": True,
            "tool": tool,
            "params": params,
            "message": message,
            "result": message,
        }

    return _run_tool(tool, params, message)

def _run_tool(tool: str, params: dict, message: str = "") -> dict:
    try:
        result = _dispatch_tool(tool, params, message)
        return {"success": True, "result": result}
    except TypeError as e:
        return {"success": False, "result": f"❌ Tham số không hợp lệ: {e}"}
    except Exception as e:
        return {"success": False, "result": f"❌ Lỗi thực thi: {e}"}

def _dispatch_tool(tool: str, params: dict, message: str) -> str:
    if tool == "search_files":
        from tools.file_search import search_files
        return search_files(**params)
    elif tool == "rename_file":
        from tools.file_rename import rename_file
        path_val = params.get("path") or params.get("file_path") or params.get("src")
        new_name_val = params.get("new_name") or params.get("new") or params.get("target_name") or params.get("name")
        folder_path_val = params.get("folder_path") or params.get("folder")
        pattern_val = params.get("pattern")
        replacement_val = params.get("replacement")
        folder_pattern_val = params.get("folder_pattern")
        new_folder_name_prefix_val = params.get("new_folder_name_prefix")
        username_val = params.get("username")
        if not new_name_val and message:
            match = re.search(r"(?:thành|sang|to)\s+([^\s]+)", message, re.IGNORECASE)
            if match:
                new_name_val = match.group(1).strip().strip("'\"`.")
        return rename_file(
            path=path_val,
            new_name=new_name_val,
            folder_path=folder_path_val,
            pattern=pattern_val,
            replacement=replacement_val,
            folder_pattern=folder_pattern_val,
            new_folder_name_prefix=new_folder_name_prefix_val,
            username=username_val,
        )
    elif tool == "organize_files":
        from tools.file_organizer import organize_files
        return organize_files(**params)
    elif tool == "move_file":
        from tools.file_move import move_file
        # Truyền toàn bộ params để file_move tự xử lý source_paths, destination_path, src, dst...
        return move_file(**params)
    elif tool == "copy_file":
        from tools.file_copy import copy_file
        return copy_file(**params)
    elif tool == "delete_file":
        from tools.file_delete import delete_file
        return delete_file(**params)
    elif tool == "create_file":
        from tools.file_create import create_file
        return create_file(**params)
    elif tool == "file_info":
        from tools.file_info import file_info
        return file_info(**params)
    elif tool == "find_duplicates":
        from tools.file_duplicate import find_duplicates
        return find_duplicates(**params)
    elif tool == "compress_files":
        from tools.file_compress import compress_files
        return compress_files(**params)
    elif tool == "file_history":
        from tools.file_history import file_history
        return file_history(**params)
    elif tool == "disk_analyzer":
        from tools.disk_analyzer import disk_analyzer
        return disk_analyzer(**params)
    elif tool == "summarize_file":
        from tools.summarizer import summarize_file
        return summarize_file(**params)
    elif tool == "help":
        return (
            "🎯 OOFI (Oops, Found It!) — Trợ lý quản lý file thông minh\n"
            "─────────────────────────────────────────────────────────────\n"
            "📁 Các chức năng chính:\n"
            "  • Tìm kiếm file theo tên, đuôi\n"
            "  • Đổi tên, di chuyển, sao chép, xóa file (an toàn qua Recycle Bin)\n"
            "  • Tạo file/thư mục mới với nội dung tùy chỉnh\n"
            "  • Tóm tắt nội dung tài liệu (PDF, DOCX, TXT)\n"
            "  • Dọn dẹp thư mục, phân loại file tự động\n"
            "  • Phân tích dung lượng ổ đĩa\n"
            "  • Tìm file trùng lặp, nén/giải nén ZIP\n"
            "  • Xem lịch sử file mới chỉnh sửa\n"
            "  • Xem thông tin chi tiết file\n"
            "─────────────────────────────────────────────────────────────\n"
            "💬 Hãy hỏi tôi bất cứ điều gì về quản lý file!"
        )
    else:
        return f"❌ Tool không tồn tại: '{tool}'"