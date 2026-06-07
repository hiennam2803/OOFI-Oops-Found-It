"""
core/brain.py
Brain — lớp điều phối trung tâm của OOFI.
Nhận câu lệnh người dùng, gửi cho AI provider,
trả về response thô để dispatcher xử lý.
"""

import os
from core.prompt import build_prompt
from providers   import create_provider
from config      import load_settings


class Brain:
    """
    Lớp trung tâm kết nối người dùng với AI provider.

    Luồng chính:
        User input → think() → AI provider → raw JSON string → dispatcher

    Luồng tóm tắt:
        File text → summarize() → AI provider (system prompt riêng) → tóm tắt văn xuôi
    """

    def __init__(self):
        self.settings = load_settings()
        self.provider = create_provider(self.settings)
        self.username = os.getenv("USERNAME") or os.getenv("USER") or ""

    def reload(self):
        """
        Tải lại settings và khởi tạo provider mới.
        Gọi khi người dùng thay đổi provider trong Settings.
        """
        self.settings = load_settings()
        self.provider = create_provider(self.settings)

    def think(self, user_input: str) -> str:
        """
        Nhận câu lệnh người dùng, gửi tới AI provider.
        Trả về chuỗi JSON thô để dispatcher parse và thực thi.

        Args:
            user_input: Câu lệnh từ người dùng.

        Returns:
            Chuỗi JSON thô từ AI. Dispatcher tự parse.
        """
        prompt = build_prompt(user_input, self.username)
        return self.provider.chat(prompt)

    def summarize(self, content: str) -> str:
        """
        Tóm tắt nội dung văn bản với system prompt riêng biệt.
        Tách khỏi think() để tránh model trả về JSON thay vì văn xuôi.

        Args:
            content: Đoạn text cần tóm tắt.

        Returns:
            Bản tóm tắt 3-5 câu bằng ngôn ngữ tự nhiên.
        """
        system = (
            "Bạn là trợ lý tóm tắt tài liệu. "
            "Nhiệm vụ duy nhất: viết bản tóm tắt 3-5 câu bằng tiếng Việt, "
            "ngắn gọn và súc tích. "
            "Bắt đầu bằng 'Đây là tài liệu về...'. "
            "Tuyệt đối không trả về JSON hay bất kỳ định dạng có cấu trúc nào. "
            "Chỉ viết văn xuôi thuần túy."
        )
        user = f"Tóm tắt nội dung sau:\n\n{content}"

        mode = self.settings.get("mode", "local")
        if mode == "local":
            # Dùng /api/chat với system prompt tách biệt
            # để model không bị ảnh hưởng bởi JSON system prompt mặc định
            return self.provider.chat_raw(system, user)
        else:
            # Cloud providers: gộp system và user vào một prompt rõ ràng
            return self.provider.chat(f"{system}\n\n{user}")

    def is_ready(self) -> tuple[bool, str]:
        """
        Kiểm tra provider có sẵn sàng không.

        Returns:
            (True, "")          nếu provider sẵn sàng.
            (False, "lý do")    nếu không sẵn sàng.
        """
        if not self.provider.is_available():
            mode = self.settings.get("mode", "local")
            if mode == "local":
                pull_cmd = getattr(self.provider, "get_pull_command", lambda: "")()
                return False, (
                    f"❌ Ollama chưa chạy hoặc model chưa được tải.\n"
                    f"Khởi động Ollama: ollama serve\n"
                    f"Tải model: {pull_cmd}"
                )
            return False, (
                f"❌ Không kết nối được {mode.upper()}. "
                f"Kiểm tra kết nối internet và API Key trong Settings."
            )
        return True, ""

    def get_label(self) -> str:
        """Trả về nhãn provider hiện tại để hiển thị trên giao diện."""
        return self.provider.get_label()