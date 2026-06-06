# providers/base.py

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """
    Lớp cha cho mọi AI provider.
    Local (Ollama), Groq, Gemini đều kế thừa từ đây.
    Mọi provider đều có chung 1 method duy nhất: chat()
    """

    @abstractmethod
    def chat(self, prompt: str) -> str:
        """
        Gửi prompt → nhận response dạng string.
        Đây là method DUY NHẤT dispatcher cần gọi.
        Không quan tâm provider là gì — gọi chat() là xong.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Kiểm tra provider có sẵn sàng không."""
        pass

    @abstractmethod
    def get_label(self) -> str:
        """Tên hiển thị ở GUI."""
        pass