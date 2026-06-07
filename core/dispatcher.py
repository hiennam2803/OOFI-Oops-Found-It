"""
core/dispatcher.py
Dispatcher — nhận JSON từ AI, kiểm tra an toàn, và thực thi tool.

3 lớp bảo vệ:
  Lớp 1: Blacklist — chặn đường dẫn vào thư mục hệ thống.
  Lớp 2: Confirmation — trả flag cho GUI xác nhận trước khi thực thi.
  Lớp 3: send2trash — xóa an toàn qua Recycle Bin (trong file_delete.py).
"""

import json
import re
from pathlib import Path


# ── Lớp 1: Blacklist đường dẫn hệ thống ─────────────────
SYSTEM_BLACKLIST = [
    "c:\\windows",
    "c:\\program files",
    "c:\\program files (x86)",
    "c:\\system32",
]

# ── Lớp 2: Tool yêu cầu xác nhận người dùng ─────────────
DESTRUCTIVE_TOOLS = {
    "delete_file",
    "move_file",
    "organize_files",
    "rename_file",
}


def is_path_safe(target_path: str, user_blacklist: list[str] | None = None) -> bool:
    """
    Kiểm tra đường dẫn không nằm trong vùng bị chặn.
    Chuẩn hóa về absolute path trước khi so sánh để tránh bypass
    bằng relative path (../Windows) hoặc khác dấu gạch chéo.

    Args:
        target_path  : Đường dẫn cần kiểm tra.
        user_blacklist: Danh sách thư mục bổ sung do người dùng tự thêm.

    Returns:
        True nếu đường dẫn an toàn, False nếu bị chặn.
    """
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
        # Đường dẫn không hợp lệ → chặn an toàn
        return False


def parse_response(response: str) -> dict:
    """
    Parse JSON từ response của AI.
    Xử lý các trường hợp AI trả về JSON không sạch (có markdown, text thừa).

    Args:
        response: Chuỗi response thô từ AI provider.

    Returns:
        Dict đã parse. Trả về parse_error nếu không parse được.
    """
    cleaned = response.strip()

    # Loại bỏ markdown code block nếu có
    if cleaned.startswith("```"):
        parts   = cleaned.split("```")
        cleaned = parts[1] if len(parts) > 1 else cleaned
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    # Thử parse trực tiếp
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Tìm JSON trong text nếu AI thêm text thừa bên ngoài
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
        "message": f"Không thể parse JSON từ response: {response[:150]}",
    }


def dispatch(
    parsed: dict,
    user_blacklist: list[str] | None = None,
    confirmed: bool = False,
) -> dict:
    """
    Kiểm tra an toàn và thực thi tool.

    Args:
        parsed        : Dict đã parse từ response AI.
        user_blacklist: Danh sách thư mục bổ sung do người dùng tự thêm.
        confirmed     : True nếu người dùng đã xác nhận qua GUI popup.

    Returns:
        Dict kết quả:
        - {"success": True,  "result": "..."}             — thực thi thành công
        - {"success": False, "result": "..."}             — lỗi hoặc bị chặn
        - {"success": False, "need_confirm": True, ...}   — cần xác nhận từ GUI
    """
    if user_blacklist is None:
        user_blacklist = []

    tool    = parsed.get("tool", "unknown")
    params  = parsed.get("params", {})
    message = parsed.get("message", "")

    # Tool không xác định hoặc ngoài chủ đề
    if tool in ("unknown", "off_topic", "parse_error"):
        return {"success": False, "result": message}

    # Lớp 1: Kiểm tra tất cả đường dẫn trong params
    for value in params.values():
        if isinstance(value, str) and ("/" in value or "\\" in value):
            if not is_path_safe(value, user_blacklist):
                return {
                    "success": False,
                    "result":  f"❌ Thao tác bị từ chối: đường dẫn nằm trong vùng bảo vệ.\n  Đường dẫn: {value}",
                }

    # Lớp 2: Tool phá hủy cần xác nhận từ GUI
    if tool in DESTRUCTIVE_TOOLS and not confirmed:
        return {
            "success":      False,
            "need_confirm": True,
            "tool":         tool,
            "params":       params,
            "message":      message,
            "result":       message,
        }

    return _run_tool(tool, params, message)


def _run_tool(tool: str, params: dict, message: str = "") -> dict:
    """
    Import và gọi tool function tương ứng.
    Sử dụng lazy import để giảm thời gian khởi động.

    Args:
        tool   : Tên tool cần thực thi.
        params : Tham số truyền vào tool.
        message: Thông điệp mô tả từ AI (dùng làm fallback).

    Returns:
        Dict {"success": bool, "result": str}
    """
    try:
        result = _dispatch_tool(tool, params, message)
        return {"success": True, "result": result}
    except TypeError as e:
        return {
            "success": False,
            "result":  f"❌ Tham số không hợp lệ cho tool '{tool}': {e}",
        }
    except Exception as e:
        return {
            "success": False,
            "result":  f"❌ Lỗi thực thi tool '{tool}': {e}",
        }


def _dispatch_tool(tool: str, params: dict, message: str) -> str:
    """Ánh xạ tên tool → function call tương ứng."""

    if tool == "search_files":
        from tools.file_search import search_files
        return search_files(**params)

    elif tool == "rename_file":
        from tools.file_rename import rename_file
        path_val = (
            params.get("path")
            or params.get("file_path")
            or params.get("src")
        )
        new_name_val = (
            params.get("new_name")
            or params.get("new")
            or params.get("target_name")
            or params.get("name")
        )
        # Fallback: trích xuất tên mới từ message nếu AI không điền vào params
        if not new_name_val and message:
            match = re.search(
                r"(?:thành|sang|to)\s+([^\s]+)", message, re.IGNORECASE
            )
            if match:
                new_name_val = match.group(1).strip().strip("'\"`.")
        return rename_file(path=path_val, new_name=new_name_val)

    elif tool == "organize_files":
        from tools.file_organizer import organize_files
        return organize_files(**params)

    elif tool == "move_file":
        from tools.file_move import move_file
        src = params.get("src") or params.get("path") or params.get("source")
        dst = params.get("dst") or params.get("destination") or params.get("target")
        return move_file(src=src, dst=dst)

    elif tool == "copy_file":
        from tools.file_copy import copy_file
        src = params.get("src") or params.get("path") or params.get("source")
        dst = params.get("dst") or params.get("destination") or params.get("target")
        return copy_file(src=src, dst=dst)

    elif tool == "delete_file":
        from tools.file_delete import delete_file
        return delete_file(**params)

    elif tool == "create_file":
        from tools.file_create import create_file
        path_val    = params.get("path") or params.get("file_path")
        content_val = params.get("content") or params.get("text") or params.get("data") or ""
        # Fallback: trích xuất nội dung từ message nếu AI không điền vào params
        if not content_val and message:
            match = re.search(
                r"(?:nội\s+dung|với\s+nội\s+dung|chứa)\s+(.+)",
                message, re.IGNORECASE
            )
            if match:
                content_val = match.group(1).strip().strip("'\"`.")
        return create_file(path=path_val, content=content_val)

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

    else:
        return f"❌ Tool không tồn tại: '{tool}'"