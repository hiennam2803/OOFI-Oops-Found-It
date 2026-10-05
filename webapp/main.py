"""
webapp/main.py
FastAPI app cho OOFI — chỉ là lớp API/UI, KHÔNG chứa logic nghiệp vụ.
Toàn bộ logic thật (AI, an toàn đường dẫn, thực thi tool) nằm ở
core/brain.py và core/dispatcher.py — file này chỉ gọi vào đó.

Chạy dev:
    uvicorn webapp.main:app --reload

Chạy production (được run_desktop.py gọi khi đóng gói .exe):
    uvicorn.run(app, host="127.0.0.1", port=PORT)
"""

import sys
import traceback
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

# ── Import các module core đã có sẵn (KHÔNG sửa) ──────────────
from core.brain import Brain
from core.dispatcher import parse_response, dispatch
from config.settings import load_settings, save_settings
from config.model import (
    LOCAL_MODELS,
    CLOUD_MODELS,
    get_ram_gb,
    detect_recommended_tier,
)
from providers.groq import GroqProvider
from providers.gemini import GeminiProvider


# ── Resource path (tương thích PyInstaller --onefile) ─────────
def resource_path(*parts: str) -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent
    return base.joinpath(*parts)


STATIC_DIR = resource_path("static")

app = FastAPI(title="OOFI API")

# Brain là singleton trong process — giữ provider đã khởi tạo,
# tránh phải tạo lại mỗi request (đặc biệt tốn kém với local Ollama).
brain = Brain()


# ── Schemas request ─────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str


class ConfirmRequest(BaseModel):
    tool: str
    params: dict = {}
    message: str = ""


class SettingsUpdateRequest(BaseModel):
    # Cho phép partial update — field nào không gửi thì giữ nguyên.
    mode: str | None = None
    local_tier: str | None = None
    groq_model: str | None = None
    gemini_model: str | None = None
    groq_api_key: str | None = None
    gemini_api_key: str | None = None
    ollama_url: str | None = None
    user_blacklist: list[str] | None = None
    theme: str | None = None
    language: str | None = None
    first_run: bool | None = None


# ── Middleware bắt lỗi chung — không để UI nhận HTML 500 ──────
@app.middleware("http")
async def catch_unhandled_errors(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "result": f"❌ Lỗi server: {e}"},
        )


# ── /api/chat ───────────────────────────────────────────────
@app.post("/api/chat")
async def api_chat(req: ChatRequest):
    """
    Gửi câu lệnh người dùng → Brain.think() (gọi AI) → dispatcher.dispatch().
    Nếu tool thuộc nhóm phá hủy, dispatch() tự trả need_confirm=True —
    trả thẳng cho client, không tự confirm.
    """
    raw = await run_in_threadpool(brain.think, req.message)
    parsed = parse_response(raw)
    user_blacklist = brain.settings.get("user_blacklist", [])
    result = await run_in_threadpool(dispatch, parsed, user_blacklist, False)
    return result


# ── /api/confirm ────────────────────────────────────────────
@app.post("/api/confirm")
async def api_confirm(req: ConfirmRequest):
    """
    Xác nhận thực thi hành động phá hủy. Giữ nguyên tool/params/message
    gốc do /api/chat trả về trước đó — KHÔNG gọi lại AI.
    """
    parsed = {
        "tool": req.tool,
        "params": req.params,
        "confirm": True,
        "message": req.message,
    }
    user_blacklist = brain.settings.get("user_blacklist", [])
    result = await run_in_threadpool(dispatch, parsed, user_blacklist, True)
    return result


# ── /api/help — gọi trực tiếp tool help, không qua AI ─────────
@app.post("/api/help")
async def api_help():
    parsed = {"tool": "help", "params": {}, "confirm": False, "message": ""}
    result = await run_in_threadpool(dispatch, parsed, [], False)
    return result


# ── /api/status — trạng thái provider hiện tại ────────────────
@app.get("/api/status")
async def api_status():
    ready, reason = brain.is_ready()
    return {
        "ready": ready,
        "reason": reason,
        "label": brain.get_label(),
        "mode": brain.settings.get("mode", "local"),
    }


# ── /api/settings — đọc / ghi cấu hình ────────────────────────
@app.get("/api/settings")
async def api_get_settings():
    return load_settings()


@app.post("/api/settings")
async def api_update_settings(req: SettingsUpdateRequest):
    current = load_settings()
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    current.update(updates)
    save_settings(current)
    # Provider có thể đã đổi (mode, tier, api key...) → khởi tạo lại.
    brain.reload()
    ready, reason = brain.is_ready()
    return {
        "success": True,
        "settings": current,
        "status": {"ready": ready, "reason": reason, "label": brain.get_label()},
    }


# ── /api/meta — thông tin tĩnh để render màn hình Settings ────
@app.get("/api/meta")
async def api_meta():
    return {
        "local_tiers": LOCAL_MODELS,
        "cloud_models": CLOUD_MODELS,
        "ram_gb": get_ram_gb(),
        "recommended_tier": detect_recommended_tier(),
        "signup_urls": {
            "groq": GroqProvider.get_signup_url(),
            "gemini": GeminiProvider.get_signup_url(),
        },
    }


# ── Static frontend (mount SAU CÙNG để không nuốt route /api/*) ─
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
