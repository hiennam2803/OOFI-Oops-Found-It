# 🗂️ DAMN
### Desktop Agent Managing Nonsense

> *"Your desktop is a mess. DAMN."*

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-black?style=flat-square)](https://ollama.com)
[![Groq](https://img.shields.io/badge/Groq-Cloud%20AI-orange?style=flat-square)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Meme](https://img.shields.io/badge/Meme-100%25-ff69b4?style=flat-square)](.)

---

## 🤔 DAMN là gì?

Bạn có **437 file trên Desktop**. Bạn không biết file nào là gì. Bạn sợ xóa nhầm. Bạn đã như vậy từ năm 2019.

**DAMN** là trợ lý AI quản lý file bằng tiếng Việt — chạy **hoàn toàn trên máy bạn**, không cần internet, không tốn tiền, không phán xét bạn về cái Desktop đó.

```
Bạn:   "Tìm tất cả file PDF trong Downloads tháng này"
DAMN:  "Tìm thấy 12 file. Bạn có muốn tôi dọn chúng không?"
Bạn:   "Ừ dọn đi"
DAMN:  *dọn xong trong 3 giây*
Bạn:   😮
```

---

## ✨ Tính năng

| Tính năng | Mô tả |
|---|---|
| 🔍 **Tìm kiếm** | Tìm file theo tên, loại, ngày tháng |
| ✏️ **Đổi tên** | Đổi tên đơn hoặc hàng loạt |
| 📁 **Phân loại** | Tự động sắp xếp file vào thư mục |
| 🚚 **Di chuyển** | Di chuyển file theo lệnh |
| 📋 **Sao chép** | Copy file đến nơi khác |
| 🗑️ **Xóa** | Xóa có xác nhận, không xóa nhầm |
| 🆕 **Tạo mới** | Tạo file và thư mục |
| 📊 **Thông tin** | Xem dung lượng, ngày tạo |
| 👯 **Trùng lặp** | Tìm và dọn file bị copy nhiều lần |
| 🗜️ **Nén file** | Zip/unzip thoải mái |
| 🕐 **Lịch sử** | Xem file vừa chỉnh sửa gần đây |
| 🧹 **Dọn rác** | Phân tích và dọn dẹp ổ đĩa |
| 📖 **Tóm tắt** | Đọc và tóm tắt PDF, DOCX, TXT |

---

## 🧠 Chọn AI phù hợp với máy bạn

DAMN hỏi bạn 1 lần duy nhất khi cài — sau đó tự nhớ.

### 💻 Chế độ Local (Offline)
> Không cần internet. Không giới hạn câu hỏi. Miễn phí mãi mãi.

| Tier | Model | Tải về | RAM tối thiểu |
|---|---|---|---|
| 🟢 Nhẹ | qwen2.5:1.5b | ~1 GB | 4 GB |
| 🟡 Bình thường | qwen2.5:3b | ~2 GB | 6 GB |
| 🔴 Mạnh | qwen2.5:7b | ~5 GB | 8 GB |

DAMN tự detect RAM máy bạn và gợi ý tier phù hợp. Bạn vẫn có thể tự chọn.

### ☁️ Chế độ Cloud (Groq)
> Cần internet + API key miễn phí. Chạy được máy RAM 2GB. Model 70B nhanh như chớp.

Đăng ký key miễn phí tại [console.groq.com](https://console.groq.com) — 2 phút là xong.

---

## 🚀 Cài đặt

### Yêu cầu
- Python 3.10+
- RAM 4GB+ (Local) hoặc 2GB+ (Cloud)

### Các bước

```bash
# 1. Clone về
git clone https://github.com/your-username/DAMN.git
cd DAMN

# 2. Tạo môi trường ảo
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Cài thư viện
pip install -r requirements.txt

# 4a. Nếu dùng Local — cài Ollama tại ollama.com rồi tải model
ollama pull qwen2.5:7b       # hoặc 3b, 1.5b tùy máy

# 4b. Nếu dùng Cloud — lấy API key tại console.groq.com

# 5. Chạy thôi
python main.py
```

Lần đầu chạy DAMN sẽ hỏi bạn vài câu — chọn xong là dùng được luôn.

---

## 💬 Ví dụ câu lệnh

```
"Tìm tất cả ảnh trong Desktop"
"Đổi tên file abc.docx thành abc_final.docx"
"Phân loại tự động thư mục Downloads"
"Tìm file nào nặng hơn 1GB trong máy"
"Nén thư mục Projects thành zip"
"Tìm file bị trùng trong Photos"
"Tóm tắt file báo cáo tháng 3.pdf"
"Dọn file rác trong ổ C"
"Tạo thư mục Work/2025/Q2 trên Desktop"
```

---

## 🏗️ Cấu trúc dự án

```
DAMN/
├── config/          # Cài đặt, chọn model
├── ai/              # Local (Ollama) + Cloud (Groq)
├── agent/           # Não của app — LangChain Agent
│   └── tools/       # 13 tools thao tác file
├── gui/             # Giao diện
├── tests/           # Test chat terminal
└── main.py
```

---

## 🤝 Đóng góp

DAMN là dự án mã nguồn mở. Mọi đóng góp đều được chào đón:

- 🐛 Tìm thấy bug? Mở Issue
- 💡 Có ý tưởng? Mở Discussion  
- 🔧 Muốn code? Mở Pull Request

---

## 📄 License

MIT — dùng thoải mái, thương mại hay cá nhân đều được.

---

<div align="center">

*"Dọn Desktop không khó. Khó là bạn chưa có DAMN."*

**⭐ Star nếu dự án hữu ích cho bạn**

</div>
