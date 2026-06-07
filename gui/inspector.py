"""
gui/inspector.py
Panel inspector phải — thông tin file, thao tác nhanh, dung lượng ổ đĩa.
"""

import os
import shutil
import time
import customtkinter as ctk
from pathlib import Path


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

EXT_COLORS = {
    ".pdf":  ("#F87171", "#2D1515"),
    ".docx": ("#60A5FA", "#0F1E2D"),
    ".doc":  ("#60A5FA", "#0F1E2D"),
    ".xlsx": ("#4ADE80", "#0F2015"),
    ".xls":  ("#4ADE80", "#0F2015"),
    ".pptx": ("#FB923C", "#2D1A0F"),
    ".jpg":  ("#A78BFA", "#1A1528"),
    ".jpeg": ("#A78BFA", "#1A1528"),
    ".png":  ("#A78BFA", "#1A1528"),
    ".zip":  ("#FBBF24", "#2D2408"),
    ".py":   ("#2DD4BF", "#0A2020"),
}
DEFAULT_EXT_COLOR = ("#8A87A0", "#1E1B2E")


def _format_size(size_bytes: int) -> str:
    if size_bytes >= 1 << 30:
        return f"{size_bytes / (1 << 30):.2f} GB"
    elif size_bytes >= 1 << 20:
        return f"{size_bytes / (1 << 20):.1f} MB"
    elif size_bytes >= 1 << 10:
        return f"{size_bytes / (1 << 10):.1f} KB"
    return f"{size_bytes} B"


class InspectorPanel(ctk.CTkFrame):
    """Panel inspector bên phải."""

    def __init__(self, master, app, **kwargs):
        super().__init__(
            master,
            fg_color=SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=BORDER,
            **kwargs
        )
        self.app          = app
        self._current_file = None
        self._build()

    def _build(self):
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        ctk.CTkLabel(
            self, text="INSPECTOR",
            font=ctk.CTkFont(family="Courier New", size=10, weight="bold"),
            text_color=TEXT_DIM
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10,6))

        # File card
        self.file_card = ctk.CTkFrame(
            self, fg_color=SURFACE2, corner_radius=10,
            border_width=1, border_color=BORDER
        )
        self.file_card.grid(row=1, column=0, sticky="ew", padx=8, pady=(0,4))

        self._build_empty_card()

        # Quick actions
        self._build_actions()

        # Disk usage
        self._build_disk()

    def _build_empty_card(self):
        """Hiện trạng thái trống khi chưa chọn file."""
        for w in self.file_card.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self.file_card,
            text="⊛\n\nChọn một file\nđể xem thông tin",
            font=ctk.CTkFont(size=12),
            text_color=BORDER,
            justify="center"
        ).pack(pady=24)

    def _build_file_card(self, path: str):
        """Hiển thị thông tin file được chọn."""
        for w in self.file_card.winfo_children():
            w.destroy()

        p   = Path(path)
        ext = p.suffix.lower()
        fg_color, bg_color = EXT_COLORS.get(ext, DEFAULT_EXT_COLOR)

        # File icon badge
        icon_frame = ctk.CTkFrame(
            self.file_card,
            width=44, height=44,
            fg_color=bg_color,
            corner_radius=10,
            border_width=1,
            border_color=fg_color + "55"
        )
        icon_frame.pack(anchor="w", padx=12, pady=(12,6))
        icon_frame.pack_propagate(False)

        ctk.CTkLabel(
            icon_frame,
            text=ext.upper().replace(".", "") or "FILE",
            font=ctk.CTkFont(family="Courier New", size=10, weight="bold"),
            text_color=fg_color
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Tên file
        name = p.name
        if len(name) > 28:
            name = name[:25] + "…"
        ctk.CTkLabel(
            self.file_card, text=name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT,
            anchor="w"
        ).pack(fill="x", padx=12, pady=(0,2))

        # Path
        folder = str(p.parent)
        if len(folder) > 32:
            folder = "…" + folder[-30:]
        ctk.CTkLabel(
            self.file_card, text=folder,
            font=ctk.CTkFont(size=10),
            text_color=TEXT_DIM,
            anchor="w"
        ).pack(fill="x", padx=12, pady=(0,8))

        # Divider
        ctk.CTkFrame(
            self.file_card, height=1, fg_color=BORDER, corner_radius=0
        ).pack(fill="x", padx=8)

        # Metadata
        try:
            stat     = p.stat()
            size     = _format_size(stat.st_size)
            modified = time.strftime("%d/%m/%Y %H:%M", time.localtime(stat.st_mtime))
            writable = "Đọc/Ghi" if os.access(p, os.W_OK) else "Chỉ đọc"
        except Exception:
            size, modified, writable = "—", "—", "—"

        meta_items = [
            ("⚖", "Kích thước", size),
            ("🗓", "Sửa đổi",   modified),
            ("🔐", "Quyền",     writable),
        ]

        for icon, label, value in meta_items:
            row = ctk.CTkFrame(self.file_card, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=3)

            ctk.CTkLabel(
                row, text=f"{icon}  {label}",
                font=ctk.CTkFont(size=11),
                text_color=TEXT_DIM, width=90, anchor="w"
            ).pack(side="left")

            ctk.CTkLabel(
                row, text=value,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=TEXT, anchor="e"
            ).pack(side="right")

        ctk.CTkFrame(
            self.file_card, height=8, fg_color="transparent"
        ).pack()

    def _build_actions(self):
        """Panel thao tác nhanh."""
        act_frame = ctk.CTkFrame(self, fg_color="transparent")
        act_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=4)

        ctk.CTkLabel(
            act_frame, text="THAO TÁC NHANH",
            font=ctk.CTkFont(family="Courier New", size=10, weight="bold"),
            text_color=TEXT_DIM
        ).pack(anchor="w", pady=(0,6))

        actions = [
            ("✨ Tóm tắt",   PURPLE,   self._action_summarize),
            ("✏️ Đổi tên",   SURFACE2, self._action_rename),
            ("🚚 Di chuyển", SURFACE2, self._action_move),
            ("📋 Sao chép",  SURFACE2, self._action_copy),
            ("🗜 Nén ZIP",   SURFACE2, self._action_compress),
            ("🗑 Xóa",       "#2D1515", self._action_delete),
        ]

        grid = ctk.CTkFrame(act_frame, fg_color="transparent")
        grid.pack(fill="x")

        for i, (label, color, cmd) in enumerate(actions):
            btn = ctk.CTkButton(
                grid, text=label,
                height=30, width=110,
                fg_color=color,
                hover_color=PURPLE_DIM if color == PURPLE else BORDER,
                text_color=TEXT if color != SURFACE2 else TEXT_DIM,
                corner_radius=8,
                font=ctk.CTkFont(size=11),
                border_width=1,
                border_color=BORDER,
                command=cmd
            )
            btn.grid(row=i//2, column=i%2, padx=3, pady=2, sticky="ew")

        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

    def _build_disk(self):
        """Panel dung lượng ổ đĩa."""
        disk_outer = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=BORDER,
        )
        disk_outer.grid(row=3, column=0, sticky="nsew", padx=8, pady=(4,8))

        ctk.CTkLabel(
            disk_outer, text="DUNG LƯỢNG Ổ ĐĨA",
            font=ctk.CTkFont(family="Courier New", size=10, weight="bold"),
            text_color=TEXT_DIM
        ).pack(anchor="w", pady=(0,8))

        # Quét các ổ đĩa
        drives = self._get_drives()
        colors = [PURPLE, TEAL, AMBER, GREEN]

        for i, (drive, total, used, free) in enumerate(drives):
            pct   = int(used / total * 100) if total > 0 else 0
            color = colors[i % len(colors)]

            card = ctk.CTkFrame(
                disk_outer, fg_color=SURFACE2,
                corner_radius=8, border_width=1, border_color=BORDER
            )
            card.pack(fill="x", pady=3)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=10, pady=(8,4))

            ctk.CTkLabel(
                top, text=f"💾  {drive}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=TEXT
            ).pack(side="left")

            ctk.CTkLabel(
                top, text=f"{pct}%",
                font=ctk.CTkFont(family="Courier New", size=11),
                text_color=color
            ).pack(side="right")

            # Progress bar
            bar_bg = ctk.CTkFrame(card, height=4, fg_color=BORDER, corner_radius=999)
            bar_bg.pack(fill="x", padx=10, pady=(0,4))

            bar_fill = ctk.CTkFrame(
                bar_bg, height=4,
                fg_color=color,
                corner_radius=999
            )
            bar_fill.place(relx=0, rely=0, relwidth=pct/100, relheight=1)

            ctk.CTkLabel(
                card,
                text=f"{_format_size(used)} / {_format_size(total)}  ·  còn {_format_size(free)}",
                font=ctk.CTkFont(size=10),
                text_color=TEXT_DIM
            ).pack(anchor="w", padx=10, pady=(0,8))

    def _get_drives(self) -> list:
        """Lấy danh sách ổ đĩa và dung lượng."""
        drives = []
        if os.name == "nt":
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    try:
                        total, used, free = shutil.disk_usage(drive)
                        drives.append((f"{letter}:", total, used, free))
                    except Exception:
                        pass
        else:
            try:
                total, used, free = shutil.disk_usage("/")
                drives.append(("/", total, used, free))
            except Exception:
                pass
        return drives[:4]

    # ── Public API ────────────────────────────────────────

    def load_file(self, path: str):
        """Load thông tin file vào inspector."""
        self._current_file = path
        self._build_file_card(path)

    # ── Quick action handlers ─────────────────────────────

    def _action_summarize(self):
        if not self._current_file:
            return
        cmd = f"Tóm tắt file {self._current_file}"
        self.app.chat.add_message("user", cmd)
        self.app.send_command(cmd)

    def _action_rename(self):
        if not self._current_file:
            return
        dialog = ctk.CTkInputDialog(
            text=f"Tên mới cho '{Path(self._current_file).name}':",
            title="Đổi tên file"
        )
        new_name = dialog.get_input()
        if new_name:
            cmd = f"Đổi tên file {self._current_file} thành {new_name}"
            self.app.chat.add_message("user", cmd)
            self.app.send_command(cmd)

    def _action_move(self):
        if not self._current_file:
            return
        dialog = ctk.CTkInputDialog(
            text="Di chuyển đến thư mục:",
            title="Di chuyển file"
        )
        dst = dialog.get_input()
        if dst:
            cmd = f"Di chuyển file {self._current_file} đến {dst}"
            self.app.chat.add_message("user", cmd)
            self.app.send_command(cmd)

    def _action_copy(self):
        if not self._current_file:
            return
        dialog = ctk.CTkInputDialog(
            text="Sao chép đến thư mục:",
            title="Sao chép file"
        )
        dst = dialog.get_input()
        if dst:
            cmd = f"Sao chép file {self._current_file} đến {dst}"
            self.app.chat.add_message("user", cmd)
            self.app.send_command(cmd)

    def _action_compress(self):
        if not self._current_file:
            return
        cmd = f"Nén file {self._current_file} thành zip"
        self.app.chat.add_message("user", cmd)
        self.app.send_command(cmd)

    def _action_delete(self):
        if not self._current_file:
            return
        cmd = f"Xóa file {self._current_file}"
        self.app.chat.add_message("user", cmd)
        self.app.send_command(cmd)