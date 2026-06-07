"""
gui/app.py
Cửa sổ chính của OOFI — khởi tạo layout 3 cột và quản lý state toàn app.
"""

import sys
import os
import threading
import customtkinter as ctk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core        import Brain, dispatch, parse_response
from config      import load_settings, save_settings, detect_recommended_tier


# ── Theme ──────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Màu sắc chủ đạo OOFI
PURPLE      = "#7C6FF7"
PURPLE_DIM  = "#4A437A"
PURPLE_BG   = "#1E1B2E"
SURFACE     = "#252235"
SURFACE2    = "#2D2A42"
BORDER      = "#3A3650"
TEXT        = "#E8E6F0"
TEXT_DIM    = "#8A87A0"
GREEN       = "#4ADE80"
RED         = "#F87171"
AMBER       = "#FBBF24"


class OOFIApp(ctk.CTk):
    """Cửa sổ chính của ứng dụng OOFI."""

    def __init__(self):
        super().__init__()

        self.title("OOFI — Oops, Found It!")
        self.geometry("1200x700")
        self.minsize(900, 600)
        self.configure(fg_color=PURPLE_BG)

        # Khởi tạo Brain
        self._setup_brain()

        # Import các panel
        from gui.sidebar      import SidebarPanel
        from gui.chat_panel   import ChatPanel
        from gui.inspector    import InspectorPanel

        # Layout chính
        self.grid_columnconfigure(0, weight=0, minsize=220)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0, minsize=260)
        self.grid_rowconfigure(0, weight=0)  # Titlebar
        self.grid_rowconfigure(1, weight=1)  # Main
        self.grid_rowconfigure(2, weight=0)  # Statusbar

        # Titlebar
        self._build_titlebar()

        # 3 Panel chính
        self.sidebar   = SidebarPanel(self, app=self)
        self.chat      = ChatPanel(self, app=self)
        self.inspector = InspectorPanel(self, app=self)

        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=(8,0), pady=4)
        self.chat.grid(row=1, column=1, sticky="nsew", padx=4, pady=4)
        self.inspector.grid(row=1, column=2, sticky="nsew", padx=(0,8), pady=4)

        # Statusbar
        self._build_statusbar()

        # Gắn callback
        self.sidebar.on_file_select   = self._on_file_select
        self.sidebar.on_folder_change = self._on_folder_change

    # ── Setup Brain ───────────────────────────────────────

    def _setup_brain(self):
        """Khởi tạo Brain — tự setup nếu là lần đầu chạy."""
        settings = load_settings()
        if settings.get("first_run", True):
            settings["mode"]       = "local"
            settings["local_tier"] = detect_recommended_tier()
            settings["first_run"]  = False
            save_settings(settings)
        try:
            self.brain = Brain()
        except Exception as e:
            self.brain = None
            print(f"[Brain] Lỗi khởi tạo: {e}")

    # ── Titlebar ──────────────────────────────────────────

    def _build_titlebar(self):
        bar = ctk.CTkFrame(self, height=44, fg_color=SURFACE, corner_radius=0)
        bar.grid(row=0, column=0, columnspan=3, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)
        bar.grid_propagate(False)

        # Logo
        logo = ctk.CTkLabel(
            bar, text="⊛ OOFI",
            font=ctk.CTkFont(family="Courier New", size=15, weight="bold"),
            text_color=PURPLE
        )
        logo.grid(row=0, column=0, padx=16, pady=12)

        # Provider badge
        label = self.brain.get_label() if self.brain else "Chưa kết nối"
        self.provider_badge = ctk.CTkLabel(
            bar, text=f"  {label}  ",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_DIM,
            fg_color=SURFACE2,
            corner_radius=999,
        )
        self.provider_badge.grid(row=0, column=0, padx=(110, 0), pady=12)

        # Window controls
        ctrl_frame = ctk.CTkFrame(bar, fg_color="transparent")
        ctrl_frame.grid(row=0, column=2, padx=12, pady=8)

        for symbol, color, cmd in [
            ("─", TEXT_DIM, self.iconify),
            ("□", TEXT_DIM, lambda: self.state("zoomed")),
            ("✕", RED,      self.destroy),
        ]:
            btn = ctk.CTkButton(
                ctrl_frame, text=symbol, width=28, height=22,
                fg_color="transparent", hover_color=SURFACE2,
                text_color=color, corner_radius=4,
                font=ctk.CTkFont(size=12), command=cmd
            )
            btn.pack(side="left", padx=2)

    # ── Statusbar ─────────────────────────────────────────

    def _build_statusbar(self):
        bar = ctk.CTkFrame(self, height=26, fg_color=SURFACE, corner_radius=0)
        bar.grid(row=2, column=0, columnspan=3, sticky="ew")
        bar.grid_propagate(False)

        segs = [
            ("●", GREEN,    "Ollama online"),
            ("⌘", PURPLE,   self.brain.get_label() if self.brain else "—"),
            ("📁", TEXT_DIM, "Downloads"),
            ("≡", TEXT_DIM, "Sẵn sàng"),
        ]

        for icon, color, text in segs:
            seg = ctk.CTkFrame(bar, fg_color="transparent")
            seg.pack(side="left", padx=12, pady=3)
            ctk.CTkLabel(
                seg, text=icon, text_color=color,
                font=ctk.CTkFont(size=11)
            ).pack(side="left", padx=(0,4))
            ctk.CTkLabel(
                seg, text=text, text_color=TEXT_DIM,
                font=ctk.CTkFont(size=11)
            ).pack(side="left")

        # Version
        ctk.CTkLabel(
            bar, text="v0.1.0-dev",
            text_color=BORDER,
            font=ctk.CTkFont(size=10)
        ).pack(side="right", padx=12)

    # ── Callbacks ─────────────────────────────────────────

    def _on_file_select(self, file_path: str):
        """Khi người dùng click file trong sidebar."""
        self.inspector.load_file(file_path)

    def _on_folder_change(self, folder_path: str):
        """Khi người dùng chuyển thư mục trong sidebar."""
        pass

    def send_command(self, user_input: str):
        """Gửi lệnh từ chat input — chạy trong thread riêng."""
        if not user_input.strip():
            return
        if not self.brain:
            self.chat.add_message("oofi", "❌ Brain chưa được khởi tạo.")
            return

        def _worker():
            raw     = self.brain.think(user_input)
            parsed  = parse_response(raw)
            tool    = parsed.get("tool", "")

            # Xử lý help — AI tự trả lời tự nhiên
            if tool == "help":
                reply = self.brain.provider.chat_raw(
                    system=(
                        "Bạn là OOFI — trợ lý AI quản lý file thông minh. "
                        "Tính cách thân thiện, tự nhiên, hài hước nhẹ. "
                        "Trả lời bằng tiếng Việt thuần túy, không dùng JSON."
                    ),
                    user=user_input
                )
                self.after(0, lambda: self.chat.add_message("oofi", reply))
                return

            # Destructive tool — yêu cầu confirm
            if parsed.get("confirm") and tool not in ("unknown", "off_topic"):
                self.after(0, lambda: self._ask_confirm(parsed))
                return

            result = dispatch(parsed, confirmed=True)

            # Summarize — truyền brain vào
            if tool == "summarize_file" and result.get("success"):
                text    = result["result"]
                summary = self.brain.summarize(text)
                self.after(0, lambda: self.chat.add_message("oofi", summary))
                return

            msg = result.get("result", "Không có kết quả.")
            self.after(0, lambda: self.chat.add_message("oofi", msg))

        self.chat.show_typing()
        threading.Thread(target=_worker, daemon=True).start()

    def _ask_confirm(self, parsed: dict):
        """Hiện popup xác nhận cho destructive tools."""
        msg  = parsed.get("message", "Thao tác này có thể thay đổi file.")
        tool = parsed.get("tool", "")

        dialog = ctk.CTkToplevel(self)
        dialog.title("Xác nhận")
        dialog.geometry("400x180")
        dialog.configure(fg_color=SURFACE)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="⚠️  Xác nhận thao tác",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=AMBER
        ).pack(pady=(20, 8))

        ctk.CTkLabel(
            dialog, text=msg,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_DIM,
            wraplength=340
        ).pack(pady=4)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=16)

        def _confirm():
            dialog.destroy()
            result = dispatch(parsed, confirmed=True)
            self.chat.add_message("oofi", result.get("result", "Lỗi."))

        def _cancel():
            dialog.destroy()
            self.chat.add_message("oofi", "🛑 Đã hủy thao tác.")

        ctk.CTkButton(
            btn_frame, text="Xác nhận", width=120,
            fg_color=RED, hover_color="#DC2626",
            command=_confirm
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_frame, text="Hủy", width=100,
            fg_color=SURFACE2, hover_color=BORDER,
            command=_cancel
        ).pack(side="left", padx=8)


def run():
    app = OOFIApp()
    app.mainloop()


if __name__ == "__main__":
    run()