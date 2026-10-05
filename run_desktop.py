"""
run_desktop.py
Entry point khi chạy OOFI như app desktop (dev hoặc .exe đã đóng gói).

- Chạy uvicorn (FastAPI) ngầm trong 1 thread daemon.
- Mở giao diện qua pywebview (giống app desktop thật, không có thanh địa chỉ).
- Nếu pywebview không có sẵn (ví dụ môi trường không hỗ trợ WebView2),
  fallback sang mở trình duyệt mặc định tới http://127.0.0.1:PORT.

Chạy thử ở dev:
    python run_desktop.py

Đóng gói exe:
    pyinstaller oofi.spec
"""

import socket
import sys
import threading
import time
from pathlib import Path

# Đảm bảo project root nằm trong sys.path (quan trọng khi chạy từ .exe)
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import uvicorn


APP_TITLE = "OOFI — Oops, Found It!"
PREFERRED_PORT = 8756


def _port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) != 0


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _run_server(port: int):
    from webapp.main import app  # import ở đây để tránh side-effect khi chưa cần

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


def _wait_until_ready(url: str, timeout_s: float = 15.0) -> bool:
    import urllib.request

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=0.5)
            return True
        except Exception:
            time.sleep(0.2)
    return False


def main():
    port = PREFERRED_PORT if _port_is_free(PREFERRED_PORT) else _find_free_port()
    url = f"http://127.0.0.1:{port}"

    server_thread = threading.Thread(target=_run_server, args=(port,), daemon=True)
    server_thread.start()

    _wait_until_ready(url)

    try:
        import webview  # pywebview

        webview.create_window(
            APP_TITLE,
            url,
            width=1080,
            height=740,
            min_size=(760, 520),
        )
        webview.start()
    except ImportError:
        # Fallback: không có pywebview -> mở trình duyệt mặc định
        import webbrowser

        webbrowser.open(url)
        print(f"OOFI đang chạy tại {url}")
        print("Đóng cửa sổ terminal này (Ctrl+C) để dừng server.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
