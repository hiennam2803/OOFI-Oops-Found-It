# tests/test_chat.py

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core        import Brain, dispatch, parse_response
from config      import load_settings, save_settings, detect_recommended_tier


def setup():
    print("=" * 55)
    print("   OOFI — Test Chat Terminal")
    print("=" * 55)

    settings = load_settings()

    if settings.get("first_run", True):
        print("\n⚙️  Lần đầu chạy — chọn chế độ AI:")
        print("  1. Local  (Ollama)")
        print("  2. Groq   (Cloud)")
        print("  3. Gemini (Cloud)")
        choice = input("\nChọn [1/2/3, mặc định 1]: ").strip() or "1"

        if choice == "2":
            key = input("Groq API Key (gsk_...): ").strip()
            settings["mode"]         = "groq"
            settings["groq_api_key"] = key

        elif choice == "3":
            key = input("Gemini API Key (AIza...): ").strip()
            settings["mode"]           = "gemini"
            settings["gemini_api_key"] = key

        else:
            tier = detect_recommended_tier()
            print(f"\n💻 Local — tier khuyến nghị: {tier}")
            settings["mode"]       = "local"
            settings["local_tier"] = tier

        settings["first_run"] = False
        save_settings(settings)

    return settings


def run():
    setup()

    print("\n🧠 Khởi tạo Brain...")
    brain = Brain()

    ok, err = brain.is_ready()
    if not ok:
        print(err)
        sys.exit(1)

    print(f"✅ Sẵn sàng! [{brain.get_label()}]")
    print("─" * 55)
    print("💡 Thử:")
    print("   • Tìm tất cả file PDF trong Downloads")
    print("   • Tóm tắt file C:/Users/ASUS/Downloads/NHÓM 4_TRIỂN KHAI WEBSITE TRÊN CLOUD.pdf")
    print("─" * 55)

    while True:
        try:
            user_input = input("\n🧑 Bạn: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q", "thoát"):
                print("👋 Tạm biệt!")
                break

            print("\n🤔 Đang xử lý...")

            # Bước 1 — AI suy nghĩ nhả JSON để gọi Tool
            raw = brain.think(user_input)
            print(f"\n📦 JSON từ AI:\n{raw}")

            # Bước 2 — Parse JSON thành dict
            parsed = parse_response(raw)
            print(f"\n🔍 Parsed: {parsed}")

            # Nếu AI phát hiện câu hỏi ngoài lề (off_topic), in câu trả lời ra luôn
            if parsed.get("tool") == "off_topic" or parsed.get("tool") == "unknown":
                print(f"\n🤖 OOFI: {parsed.get('message')}")
                continue

            # Bước 3 — Gửi cho Dispatcher gọi hàm Python chạy ngầm dưới ổ cứng
            result = dispatch(parsed)

            # Bước 4 — Nếu là lệnh summarize_file và trích xuất text thành công
            if parsed.get("tool") == "summarize_file" and result.get("success"):
                print("\n🤔 Đang tóm tắt văn bản...")
                # GỌI ĐÚNG HÀM TÓM TẮT THUỒN TÚY KHÔNG JSON NÈ MÀY!
                summary = brain.summarize(result["result"])
                print(f"\n✅ Tóm tắt từ chiến thần:\n{summary}")
            else:
                # Các tool khác hiển thị kết quả bình thường
                print(f"\n✅ Kết quả:\n{result.get('result', '')}")

        except KeyboardInterrupt:
            print("\n👋 Tạm biệt!")
            break
        except Exception as e:
            print(f"\n❌ Lỗi hệ thống: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    run()