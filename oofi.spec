# -*- mode: python ; coding: utf-8 -*-
#
# Build:  pyinstaller oofi.spec
# Output: dist/OOFI.exe  (Windows, --onefile)
#
# Lưu ý:
#   - Model AI (Ollama) KHÔNG được bundle vào exe — người dùng tự "ollama pull".
#   - settings.json vẫn đọc/ghi ở ~/.oofi/ (logic đã có trong config/settings.py),
#     không nằm trong exe nên không mất khi cập nhật version mới.
#   - Nếu bạn thêm thư viện đọc PDF/DOCX cho summarize_file (ví dụ PyPDF2,
#     python-docx, pdfplumber...) mà bị lỗi "ModuleNotFoundError" khi chạy exe,
#     thêm tên package đó vào hiddenimports dưới đây.

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

hiddenimports = (
    ["uvicorn.logging",
     "uvicorn.loops",
     "uvicorn.loops.auto",
     "uvicorn.protocols",
     "uvicorn.protocols.http",
     "uvicorn.protocols.http.auto",
     "uvicorn.protocols.websockets",
     "uvicorn.protocols.websockets.auto",
     "uvicorn.lifespan",
     "uvicorn.lifespan.on",
     "webview",
     "send2trash",
     ]
    + collect_submodules("core")
    + collect_submodules("config")
    + collect_submodules("providers")
    + collect_submodules("tools")
)

a = Analysis(
    ["run_desktop.py"],
    pathex=["."],
    binaries=[],
    datas=[
        ("webapp/static", "static"),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="OOFI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,   # đổi thành True tạm thời nếu cần xem log lỗi khi debug build
    icon=None,       # trỏ tới "assets/oofi.ico" nếu bạn có icon riêng
)
