"""
gui/sidebar.py
Sidebar trái — cây thư mục, yêu thích, và quick-add folder.
"""

import os
import customtkinter as ctk
from pathlib import Path
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

FILE_ICONS = {
    ".pdf":  "󰈦",
    ".docx": "󰈬", ".doc": "󰈬",
    ".xlsx": "󰈛", ".xls": "󰈛",
    ".pptx": "󰈧", ".ppt": "󰈧",
    ".txt":  "󰈙", ".md":  "󰍔",
    ".jpg":  "󰈟", ".jpeg":"󰈟", ".png": "󰈟", ".gif": "󰈟",
    ".mp4":  "󰈫", ".mkv": "󰈫", ".avi": "󰈫",
    ".mp3":  "󰈣", ".wav": "󰈣",
    ".zip":  "󰛫", ".rar": "󰛫", ".7z":  "󰛫",
    ".py":   "󰌠", ".js":  "󰌞", ".html":"󰌝",
    ".exe":  "󰣙",
}

FOLDER_ICON = "📁"
FILE_ICON   = "📄"


class SidebarPanel(ctk.CTkFrame):
    """Panel sidebar với cây thư mục và danh sách yêu thích."""

    def __init__(self, master, app, **kwargs):
        super().__init__(
            master,
            fg_color=SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=BORDER,
            **kwargs
        )
        self.app             = app
        self.on_file_select  = None
        self.on_folder_change = None
        self._favorites      = [
            str(Path.home() / "Downloads"),
            str(Path.home() / "Desktop"),
            str(Path.home() / "Documents"),
        ]
        self._current_folder = str(Path.home() / "Downloads")
        self._expanded       = {}

        self._build()

    def _build(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent", height=36)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,4))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="EXPLORER",
            font=ctk.CTkFont(family="Courier New", size=10, weight="bold"),
            text_color=TEXT_DIM
        ).grid(row=0, column=0, sticky="w")

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.grid(row=0, column=1)

        for icon, tip, cmd in [
            ("+", "Thêm thư mục", self._add_folder),
            ("↺", "Làm mới",     self._refresh),
        ]:
            btn = ctk.CTkButton(
                actions, text=icon, width=24, height=24,
                fg_color="transparent", hover_color=SURFACE2,
                text_color=TEXT_DIM, corner_radius=6,
                font=ctk.CTkFont(size=13),
                command=cmd
            )
            btn.pack(side="left", padx=1)

        # Quick nav — Máy tính
        ctk.CTkLabel(
            self, text="  THIẾT BỊ",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_DIM
        ).grid(row=1, column=0, sticky="w", padx=10, pady=(4,2))

        # Scrollable tree
        self.tree_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=PURPLE_DIM,
        )
        self.tree_scroll.grid(row=2, column=0, sticky="nsew", padx=6, pady=4)

        self._build_tree()

        # Divider
        ctk.CTkFrame(self, height=1, fg_color=BORDER, corner_radius=0).grid(
            row=3, column=0, sticky="ew", padx=10, pady=4
        )

        # Yêu thích
        ctk.CTkLabel(
            self, text="  PINNED",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_DIM
        ).grid(row=4, column=0, sticky="w", padx=10, pady=(0,2))

        self.fav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.fav_frame.grid(row=5, column=0, sticky="ew", padx=6, pady=(0,8))
        self._build_favorites()

    def _build_tree(self):
        """Xây dựng cây thư mục gốc."""
        for w in self.tree_scroll.winfo_children():
            w.destroy()

        home = Path.home()
        roots = [
            ("🖥️  Máy tính này", str(home)),
            ("  📁  Desktop",    str(home / "Desktop")),
            ("  📁  Downloads",  str(home / "Downloads")),
            ("  📁  Documents",  str(home / "Documents")),
            ("  📁  Pictures",   str(home / "Pictures")),
        ]

        for label, path in roots:
            is_active = (path == self._current_folder)
            btn = ctk.CTkButton(
                self.tree_scroll,
                text=label,
                anchor="w",
                height=28,
                fg_color=PURPLE_DIM if is_active else "transparent",
                hover_color=SURFACE2,
                text_color=TEXT if is_active else TEXT_DIM,
                corner_radius=6,
                font=ctk.CTkFont(size=12),
                command=lambda p=path: self._open_folder(p)
            )
            btn.pack(fill="x", pady=1, padx=2)

            # Nếu đang active → hiển thị nội dung folder
            if is_active and Path(path).exists():
                self._render_folder_contents(path, indent=16)

    def _render_folder_contents(self, folder: str, indent: int = 12):
        """Render các file/folder con trong thư mục đang mở."""
        try:
            entries = sorted(
                Path(folder).iterdir(),
                key=lambda x: (x.is_file(), x.name.lower())
            )[:30]  # Giới hạn 30 entries

            for entry in entries:
                if entry.name.startswith("."):
                    continue
                ext  = entry.suffix.lower()
                icon = FOLDER_ICON if entry.is_dir() else "📄"
                name = (entry.name[:22] + "…") if len(entry.name) > 24 else entry.name

                row = ctk.CTkFrame(self.tree_scroll, fg_color="transparent", height=26)
                row.pack(fill="x", pady=0)

                btn = ctk.CTkButton(
                    row,
                    text=f"{icon}  {name}",
                    anchor="w",
                    height=24,
                    fg_color="transparent",
                    hover_color=SURFACE2,
                    text_color=TEXT_DIM,
                    corner_radius=4,
                    font=ctk.CTkFont(size=11),
                    command=lambda e=entry: self._on_entry_click(str(e))
                )
                btn.pack(fill="x", padx=(indent, 2))

        except PermissionError:
            pass

    def _build_favorites(self):
        """Render danh sách thư mục yêu thích."""
        for w in self.fav_frame.winfo_children():
            w.destroy()

        for path in self._favorites:
            name = Path(path).name or path
            btn = ctk.CTkButton(
                self.fav_frame,
                text=f"★  {name}",
                anchor="w",
                height=26,
                fg_color="transparent",
                hover_color=SURFACE2,
                text_color=TEXT_DIM,
                corner_radius=6,
                font=ctk.CTkFont(size=11),
                command=lambda p=path: self._open_folder(p)
            )
            btn.pack(fill="x", pady=1, padx=2)

    def _open_folder(self, path: str):
        """Mở thư mục và cập nhật tree."""
        self._current_folder = path
        self._build_tree()
        if self.on_folder_change:
            self.on_folder_change(path)

    def _on_entry_click(self, path: str):
        """Xử lý click vào file hoặc folder."""
        p = Path(path)
        if p.is_dir():
            self._open_folder(path)
        else:
            if self.on_file_select:
                self.on_file_select(path)

    def _add_folder(self):
        """Thêm thư mục vào danh sách yêu thích qua dialog."""
        dialog = ctk.CTkInputDialog(
            text="Nhập đường dẫn thư mục:",
            title="Thêm thư mục"
        )
        path = dialog.get_input()
        if path and Path(path).exists():
            if path not in self._favorites:
                self._favorites.append(path)
                self._build_favorites()

    def _refresh(self):
        """Làm mới tree."""
        self._build_tree()