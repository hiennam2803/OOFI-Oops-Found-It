"""
providers/base.py
Abstract base class cho tất cả AI provider.
Local (Ollama), Groq, Gemini đều kế thừa từ đây.
"""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """
    Giao diện chung cho mọi AI provider.
    Dispatcher chỉ cần gọi chat() mà không cần biết
    provider cụ thể là gì (Local, Groq hay Gemini).
    """

    @abstractmethod
    def chat(self, prompt: str) -> str:
        """
        Gửi prompt và nhận response dạng string thuần túy.
        Đây là method duy nhất dispatcher sử dụng.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Kiểm tra provider có sẵn sàng không.
        Local: Ollama đang chạy và model đã tải.
        Cloud: Có internet và API key hợp lệ.
        """
        pass

    @abstractmethod
    def get_label(self) -> str:
        """
        Nhãn hiển thị trên giao diện.
        Ví dụ: '💻 Local · qwen2.5:3b · CPU'
        """
        pass