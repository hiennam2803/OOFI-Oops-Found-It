# tools/summarizer.py

from pathlib import Path


# ── Đọc file ──────────────────────────────────────────────

def _read_txt(path: Path) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _read_pdf(path: Path) -> str:
    try:
        import fitz
        doc  = fitz.open(str(path))
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text
    except Exception as e:
        return f"[Lỗi đọc PDF: {e}]"


def _read_docx(path: Path) -> str:
    try:
        from docx import Document
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        return f"[Lỗi đọc DOCX: {e}]"


def _extract_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return _read_pdf(path)
    elif ext in (".docx", ".doc"):
        return _read_docx(path)
    elif ext in (".txt", ".md", ".py", ".js", ".json", ".log", ".csv"):
        return _read_txt(path)
    else:
        return f"[Định dạng '{ext}' chưa hỗ trợ]"


# ── Tách chunks ───────────────────────────────────────────

def _split_chunks(text: str, max_words: int = 1200) -> list[str]:
    """Tăng lên 1200 từ để giảm số lần gọi AI Local, tăng tốc độ x3 lần!"""
    words  = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunks.append(" ".join(words[i:i + max_words]))
    return chunks


def _summarize_local(text: str, brain) -> str:
    """Thuật toán Map-Reduce tối ưu tốc độ bàn thờ cho máy húc tạ"""
    chunks = _split_chunks(text, max_words=1200)

    if len(chunks) == 1:
        return brain.summarize(chunks[0])

    # Giai đoạn Map
    mini_summaries = []
    for chunk in chunks:
        # Gọi trực tiếp hàm suy luận văn xuôi, bỏ qua cơ chế JSON của chat thông thường
        mini = brain.summarize(chunk)
        if not mini.startswith("{"):  # Phòng thủ nếu AI ngáo nhả JSON
            mini_summaries.append(mini)

    # Giai đoạn Reduce
    combined = "\n".join(mini_summaries)
    return brain.summarize(combined)


def _summarize_cloud(text: str, brain) -> str:
    """Hệ Cloud chơi bài bốc thẳng nguyên con — Thả cửa cho Gemini nuốt trọn gói"""
    mode = brain.settings.get("mode", "cloud")
    
    if mode == "gemini":
        # Gemini có context window 1 triệu token ➔ Nuốt sạch sành sanh không cắt gọt!
        return brain.summarize(text)
    else:
        # Groq (Llama 3 8B) giới hạn 8k token ➔ Cắt khoảng 6000 từ cho an toàn
        return brain.summarize(text[:25000])


def summarize_file(path: str, brain=None) -> str:
    file_path = Path(path.strip().strip("'\""))

    if not file_path.exists():
        return f"❌ File không tồn tại: {file_path}"
    if not file_path.is_file():
        return f"❌ Đây không phải file: {file_path}"

    size_mb = file_path.stat().st_size / (1024 * 1024)
    if size_mb > 50:
        return f"❌ File quá nặng ({size_mb:.1f} MB). Giới hạn gánh tạ là 50 MB thôi mày!"

    text = _extract_text(file_path)

    if text.startswith("["):
        return text
    if not text.strip():
        return "❌ Cái này mà sai là đi luôn, file trống không có chữ nào để tao đọc hết!"

    if brain is None:
        return f"📄 FILE: {file_path.name}\n{text[:500]}"

    mode = brain.settings.get("mode", "local")
    if mode == "local":
        return _summarize_local(text, brain)
    else:
        return _summarize_cloud(text, brain)