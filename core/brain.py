# core/brain.py

import os
import requests
from core.prompt  import build_prompt
from providers    import create_provider
from config       import load_settings


class Brain:
    def __init__(self):
        self.settings = load_settings()
        self.provider = create_provider(self.settings)
        self.username = os.getenv("USERNAME") or os.getenv("USER") or ""

    def reload(self):
        self.settings = load_settings()
        self.provider = create_provider(self.settings)

    def think(self, user_input: str) -> str:
        """Luồng này CHỈ để nhả JSON gọi Tool"""
        prompt = build_prompt(user_input, self.username)
        return self.provider.chat(prompt)

    def is_ready(self) -> tuple[bool, str]:
        if not self.provider.is_available():
            mode = self.settings.get("mode", "local")
            if mode == "local":
                return False, f"❌ Ollama chưa chạy.\nBật lên: ollama serve"
            return False, f"❌ Kết nối {mode.upper()} thất bại. Kiểm tra API Key/Internet."
        return True, ""

    def get_label(self) -> str:
        return self.provider.get_label()

    def summarize(self, content: str) -> str:
        """Luồng tóm tắt thuần túy — Ép trả về văn xuôi tiếng Việt Gen Z mượt mà"""
        system = (
            "Mày là trợ lý tóm tắt văn bản hệ chiến thần của OOFI. "
            "Nhiệm vụ DUY NHẤT: Viết một bài tóm tắt khoảng 3-5 câu bằng tiếng Việt Gen Z tự nhiên, "
            "KHÔNG viết tắt, xưng 'tao' gọi 'mày', lầy lội vừa đủ. "
            "TUYỆT ĐỐI KHÔNG TRẢ VỀ JSON, KHÔNG MỞ MÓC NGOẶC NHỌN. Chỉ viết văn xuôi thuần túy!"
        )
        user = f"Tóm tắt nội dung sau đây cho tao, bắt đầu bằng 'Đây là file nói về...':\n\n{content}"

        mode = self.settings.get("mode", "local")
        if mode == "local":
            # Gọi chat_raw của LocalProvider để truyền mảng messages (System + User)
            return self.provider.chat_raw(system, user)
        else:
            # Đối với Cloud (Gemini/Groq), ta nhồi chung vào một prompt clear sạch sẽ
            full_prompt = f"SYSTEM: {system}\n\nUSER: {user}"
            return self.provider.chat(full_prompt)