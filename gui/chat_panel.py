"""
gui/chat_panel.py
Panel chat chính — hiển thị lịch sử hội thoại, input, quick actions.
"""

import customtkinter as ctk
from datetime import datetime


PURPLE     = "#7C6FF7"
PURPLE_DIM = "#4A437A"
PURPLE_BG  = "#1E1B2E"
SURFACE    = "#252235"
SURFACE2   = "#2D2A42"
BORDER     = "#3A3650"
TEXT       = "#E8E6F0"
TEXT_DIM   = "#8A87A0"
GREEN      = "#4ADE80"
RED        = "#F87171"
AMBER      = "#FBBF24"
TEAL       = "#2DD4BF"

QUICK_CMDS = [
    ("🔍", "Tìm kiếm",  "Tìm "),
    ("✨", "Dọn dẹp",   "Dọn dẹp và phân loại thư mục Downloads"),
    ("👯", "Trùng lặp", "Tìm file trùng lặp trong Downloads"),
    ("💿", "Ổ đĩa",    "Phân tích dung lượng ổ đĩa C:"),
    ("🕐", "Lịch sử",  "Xem file chỉnh sửa trong 7 ngày qua"),
]


class ChatPanel(ctk.CTkFrame):
    """Panel chat chính của OOFI."""

    def __init__(self, master, app, **kwargs):
        super().__init__(
            master,
            fg_color=SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=BORDER,
            **kwargs
        )
        self.app           = app
        self._typing_shown = False
        self._build()
        self._add_welcome()

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        self._build_header()

        # Messages area
        self.msg_area = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=PURPLE_DIM,
        )
        self.msg_area.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)
        self.msg_area.grid_columnconfigure(0, weight=1)

        # Quick actions
        self._build_quickbar()

        # Input
        self._build_input()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=38)
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10,0))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="⊛  Chat",
            font=ctk.CTkFont(family="Courier New", size=13, weight="bold"),
            text_color=TEXT
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            header, text="✕ Xóa lịch sử",
            width=100, height=24,
            fg_color="transparent",
            hover_color=SURFACE2,
            text_color=TEXT_DIM,
            corner_radius=6,
            font=ctk.CTkFont(size=11),
            command=self._clear_history
        ).grid(row=0, column=1)

    def _build_quickbar(self):
        bar = ctk.CTkFrame(self, fg_color=SURFACE2, corner_radius=8, height=34)
        bar.grid(row=2, column=0, sticky="ew", padx=8, pady=(0,4))

        for icon, label, cmd_text in QUICK_CMDS:
            btn = ctk.CTkButton(
                bar,
                text=f"{icon} {label}",
                height=26,
                fg_color="transparent",
                hover_color=PURPLE_DIM,
                text_color=TEXT_DIM,
                corner_radius=6,
                font=ctk.CTkFont(size=11),
                command=lambda t=cmd_text: self._quick_send(t)
            )
            btn.pack(side="left", padx=4, pady=4)

    def _build_input(self):
        input_frame = ctk.CTkFrame(self, fg_color=SURFACE2, corner_radius=10)
        input_frame.grid(row=3, column=0, sticky="ew", padx=8, pady=(0,8))
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_box = ctk.CTkTextbox(
            input_frame,
            height=56,
            fg_color="transparent",
            text_color=TEXT,
            font=ctk.CTkFont(size=13),
            wrap="word",
            border_width=0,
        )
        self.input_box.grid(row=0, column=0, sticky="ew", padx=10, pady=6)
        self.input_box.insert("0.0", "Nhập lệnh hoặc hỏi OOFI...")
        self.input_box.configure(text_color=TEXT_DIM)
        self.input_box.bind("<FocusIn>",  self._on_focus_in)
        self.input_box.bind("<FocusOut>", self._on_focus_out)
        self.input_box.bind("<Return>",   self._on_enter)
        self.input_box.bind("<Shift-Return>", lambda e: None)

        btn_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        btn_row.grid(row=1, column=0, sticky="ew", padx=8, pady=(0,6))

        ctk.CTkLabel(
            btn_row,
            text="Enter ↵ gửi   Shift+Enter xuống dòng",
            text_color=BORDER,
            font=ctk.CTkFont(size=10)
        ).pack(side="left")

        self.send_btn = ctk.CTkButton(
            btn_row,
            text="Gửi  ↗",
            width=80, height=28,
            fg_color=PURPLE,
            hover_color=PURPLE_DIM,
            text_color="white",
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._send
        )
        self.send_btn.pack(side="right")

    # ── Messages ──────────────────────────────────────────

    def _add_welcome(self):
        """Hiện tin nhắn chào mừng."""
        self.add_message(
            "oofi",
            "Xin chào! Tôi là OOFI ⊛\n\n"
            "Tôi có thể giúp bạn tìm, dọn, đổi tên, tóm tắt "
            "và quản lý file trên máy tính.\n\n"
            "Thử gõ: \"Tìm tất cả file PDF trong Downloads\" 🚀"
        )

    def add_message(self, sender: str, text: str):
        """Thêm tin nhắn vào chat."""
        self._remove_typing()

        row = len(self.msg_area.winfo_children())

        wrapper = ctk.CTkFrame(self.msg_area, fg_color="transparent")
        wrapper.grid(row=row, column=0, sticky="ew", pady=4, padx=2)
        wrapper.grid_columnconfigure(1, weight=1)

        is_user = sender == "user"

        # Avatar
        avatar_text = "You" if is_user else "OO"
        avatar_color = PURPLE if not is_user else SURFACE2
        avatar = ctk.CTkLabel(
            wrapper,
            text=avatar_text,
            width=32, height=32,
            fg_color=avatar_color,
            corner_radius=999,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="white" if not is_user else TEXT_DIM,
        )

        # Bubble
        bubble_color = SURFACE2 if not is_user else PURPLE_DIM
        text_color   = TEXT     if not is_user else "#D4D0F8"

        bubble = ctk.CTkFrame(
            wrapper,
            fg_color=bubble_color,
            corner_radius=10,
            border_width=1,
            border_color=BORDER if not is_user else PURPLE_DIM,
        )

        msg_label = ctk.CTkLabel(
            bubble,
            text=text,
            anchor="w",
            justify="left",
            wraplength=380,
            font=ctk.CTkFont(size=13),
            text_color=text_color,
        )
        msg_label.pack(padx=10, pady=8)

        # Timestamp
        ts = datetime.now().strftime("%H:%M")
        ts_label = ctk.CTkLabel(
            wrapper,
            text=ts,
            font=ctk.CTkFont(size=10),
            text_color=BORDER,
        )

        if is_user:
            ts_label.grid(row=0, column=0, sticky="e", padx=(0,4), pady=(16,0))
            bubble.grid(row=0, column=1, sticky="e", padx=(60,0))
            avatar.grid(row=0, column=2, sticky="n", padx=(6,2))
        else:
            avatar.grid(row=0, column=0, sticky="n", padx=(2,6))
            bubble.grid(row=0, column=1, sticky="w", padx=(0,60))
            ts_label.grid(row=0, column=2, sticky="w", padx=(4,0), pady=(16,0))

        # Scroll xuống cuối
        self.after(50, lambda: self.msg_area._parent_canvas.yview_moveto(1.0))

    def show_typing(self):
        """Hiện indicator đang xử lý."""
        if self._typing_shown:
            return
        self._typing_shown = True

        row = len(self.msg_area.winfo_children())
        self._typing_frame = ctk.CTkFrame(self.msg_area, fg_color="transparent")
        self._typing_frame.grid(row=row, column=0, sticky="w", pady=4, padx=2)

        indicator = ctk.CTkFrame(
            self._typing_frame,
            fg_color=SURFACE2,
            corner_radius=10,
            border_width=1,
            border_color=BORDER
        )
        indicator.pack(side="left", padx=(38,0))

        self._dots_label = ctk.CTkLabel(
            indicator,
            text="⊛  Đang xử lý",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_DIM,
        )
        self._dots_label.pack(padx=12, pady=8)

        self._animate_dots(0)
        self.after(50, lambda: self.msg_area._parent_canvas.yview_moveto(1.0))

    def _animate_dots(self, count: int):
        """Animation dots cho typing indicator."""
        if not self._typing_shown:
            return
        dots = "⊛" * (count % 3 + 1)
        try:
            self._dots_label.configure(text=f"{dots}  Đang xử lý")
            self.after(400, lambda: self._animate_dots(count + 1))
        except Exception:
            pass

    def _remove_typing(self):
        """Xóa typing indicator."""
        if self._typing_shown:
            try:
                self._typing_frame.destroy()
            except Exception:
                pass
            self._typing_shown = False

    # ── Input handlers ────────────────────────────────────

    def _on_focus_in(self, event):
        current = self.input_box.get("0.0", "end").strip()
        if current == "Nhập lệnh hoặc hỏi OOFI...":
            self.input_box.delete("0.0", "end")
            self.input_box.configure(text_color=TEXT)

    def _on_focus_out(self, event):
        if not self.input_box.get("0.0", "end").strip():
            self.input_box.insert("0.0", "Nhập lệnh hoặc hỏi OOFI...")
            self.input_box.configure(text_color=TEXT_DIM)

    def _on_enter(self, event):
        self._send()
        return "break"

    def _send(self):
        text = self.input_box.get("0.0", "end").strip()
        if not text or text == "Nhập lệnh hoặc hỏi OOFI...":
            return
        self.input_box.delete("0.0", "end")
        self.add_message("user", text)
        self.app.send_command(text)

    def _quick_send(self, text: str):
        """Gửi lệnh nhanh từ quickbar."""
        self.input_box.delete("0.0", "end")
        self.input_box.configure(text_color=TEXT)
        self.input_box.insert("0.0", text)
        if not text.endswith(" "):
            self._send()

    def _clear_history(self):
        """Xóa toàn bộ lịch sử chat."""
        for widget in self.msg_area.winfo_children():
            widget.destroy()
        self._typing_shown = False
        self._add_welcome()