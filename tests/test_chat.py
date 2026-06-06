import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core        import Brain, dispatch, parse_response
from config      import load_settings, save_settings, detect_recommended_tier


def setup():
    print("=" * 55)
    print("   OOFI — Test Chat Terminal Full Option Nitro")
    print("=" * 55)

    settings = load_settings()

    if settings.get("first_run", True):
        print("\n⚙️  Lần đầu chạy — chọn chế độ AI:")
        print("  1. Local  (Ollama)")
        print("  2. Groq   (Cloud)")
        print("  3. Gemini (Cloud)")
        print("   Chọn [1/2/3, mặc định 1]: ").strip() or "1"

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
    print("💡 DANH SÁCH THỬ NGHIỆM CHIẾN THẦN (FULL TOOL):")
    print("   • Tìm file:      'Tìm tất cả file PDF trong Downloads'")
    print("   • Tóm tắt:       'Tóm tắt file C:/Users/ASUS/Downloads/Tài liệu.txt'")
    print("   • Dọn dẹp:       'Dọn dẹp folder C:/Users/ASUS/Downloads giùm tao'")
    print("   • Xóa file:      'Xóa file C:/Users/ASUS/Downloads/rác.txt'")
    print("   • Di chuyển:     'Di chuyển file C:/Users/ASUS/Downloads/ảnh.jpg ra Desktop'")
    print("   • Sao chép:      'Copy file C:/Users/ASUS/Downloads/bài_tập.pdf sang Desktop'")
    print("   • Đổi tên:       'Đổi tên file C:/Users/ASUS/Downloads/rác.txt thành Mật_Thư.txt'")
    print("   • Tạo mới:       'Tạo file C:/Users/ASUS/Downloads/lich_tap_ta.txt với nội dung húc tạ 65kg'")
    print("   • Phân tích ổ:   'Kiểm tra dung lượng ổ C:'")
    print("   • Check trùng:   'Tìm file trùng nội dung trong thư mục Downloads'")
    print("   • Nén file:      'Nén file C:/Users/ASUS/Downloads/lich_tap_ta.txt'")
    print("   • Giải nén:      'Giải nén file C:/Users/ASUS/Downloads/lich_tap_ta.zip'")
    print("   • Soi thông tin: 'Xem thông tin chi tiết file C:/Users/ASUS/Downloads/lich_tap_ta.txt'")
    print("   • Lịch sử sửa:   'Xem các file mới chỉnh sửa gần đây trong Downloads'")
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

            # Nếu AI phát hiện câu hỏi ngoài lề hoặc đùa giỡn, in câu trả lời ra luôn
            if parsed.get("tool") in ("off_topic", "unknown", "parse_error"):
                print(f"\n🤖 OOFI: {parsed.get('message')}")
                continue

            # Bước 3 — Gửi cho Dispatcher gọi hàm Python chạy dưới ổ cứng
            print("\n⚙️  Hệ thống đang thực thi lệnh dưới nền...")
            result = dispatch(parsed)

            # Bước 4 — Điều phối hiển thị kết quả theo từng Tool riêng biệt (Full Giáp Chức Năng)
            current_tool = parsed.get("tool")

            if current_tool == "summarize_file" and result.get("success"):
                print("\n🤔 Đang tóm tắt văn bản...")
                summary = brain.summarize(result["result"])
                print(f"\n✅ Tóm tắt từ chiến thần:\n{summary}")
                
            elif current_tool == "organize_files":
                print(f"\n🧹 Kết quả dọn dẹp:\n{result.get('result', '')}")
                
            elif current_tool == "delete_file":
                print(f"\n🗑️ Kết quả xử lý xóa file:\n{result.get('result', '')}")
                
            elif current_tool == "move_file":
                print(f"\n🚚 Kết quả di chuyển file:\n{result.get('result', '')}")
                
            elif current_tool == "copy_file":
                print(f"\n📋 Kết quả sao chép file:\n{result.get('result', '')}")
                
            elif current_tool == "rename_file":
                print(f"\n✏️ Kết quả đổi tên:\n{result.get('result', '')}")
                
            elif current_tool == "create_file":
                print(f"\n📄 Kết quả tạo mới:\n{result.get('result', '')}")

            elif current_tool == "disk_analyzer":
                print(f"\n📊 Kết quả phân tích ổ đĩa:\n{result.get('result', '')}")

            elif current_tool == "find_duplicates":
                print(f"\n🔍 Kết quả quét file trùng nội dung:\n{result.get('result', '')}")

            elif current_tool == "compress_files":
                print(f"\n📦 Kết quả nén hoặc giải nén:\n{result.get('result', '')}")

            elif current_tool == "file_info":
                print(f"\n🔎 Kết quả soi cấu trúc chỉ số file:\n{result.get('result', '')}")

            elif current_tool == "file_history":
                print(f"\n📜 Kết quả tra cứu lịch sử chỉnh sửa:\n{result.get('result', '')}")
                
            else:
                # Các tool tìm kiếm hoặc phát sinh khác hiển thị ở đây
                print(f"\n✅ Kết quả thực thi:\n{result.get('result', '')}")

        except KeyboardInterrupt:
            print("\n👋 Tạm biệt!")
            break
        except Exception as e:
            print(f"\n❌ Lỗi hệ thống: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    run()