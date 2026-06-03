import sys
# Ép Terminal Windows in ra tiếng Việt không bị lỗi font
sys.stdout.reconfigure(encoding='utf-8')

from langchain_ollama import OllamaLLM

print("=== HỆ THỐNG TRÒ CHUYỆN OFFLINE CÙNG QWEN 2.5 ===")
print("Gõ 'exit' hoặc 'quit' để dừng cuộc trò chuyện nha mầy.\n")

try:
    # Kết nối tới con não Qwen 2.5 offline
    llm = OllamaLLM(model="qwen2.5:7b")
    print("🤖 AI: Sẵn sàng rồi! Muốn nói gì nói đi mầy...")

    while True:
        # Cho mày nhập câu hỏi
        user_input = input("\n[Mày gõ]: ")
        
        # Nếu gõ exit thì thoát vòng lặp
        if user_input.lower() in ['exit', 'quit']:
            print("🤖 AI: Biến đây, đi húc tạ tiếp đây mầy!")
            break
            
        if not user_input.strip():
            continue

        print("🤖 AI đang tải não để trả lời... Chờ tí...")
        
        # Gửi câu hỏi cho AI và nhận câu trả lời
        response = llm.invoke(user_input)
        
        print(f"\n[AI trả lời]: {response}")

except Exception as e:
    print(f"\nQuát đờ phúc! Bị lỗi rồi mày ơi: {e}")