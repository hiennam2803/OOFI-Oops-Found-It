"""
tools/summarizer.py
Tóm tắt tài liệu PDF, DOCX, TXT bằng thuật toán Map-Reduce.
- Local model: Chia nhỏ text → tóm tắt từng phần → gộp lại
- Cloud model: Gửi nguyên văn bản (context window lớn)
"""

from pathlib import Path


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
    except ImportError:
        return "[Lỗi: Cần cài pymupdf — pip install pymupdf]"
    except Exception as e:
        return f"[Lỗi đọc PDF: {e}]"


def _read_docx(path: Path) -> str:
    try:
        from docx import Document
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except ImportError:
        return "[Lỗi: Cần cài python-docx — pip install python-docx]"
    except Exception as e:
        return f"[Lỗi đọc DOCX: {e}]"


def _extract_text(path: Path) -> str:
    """Trích xuất text từ file theo định dạng."""
    ext = path.suffix.lower()
    if ext == ".pdf":
        return _read_pdf(path)
    elif ext in (".docx", ".doc"):
        return _read_docx(path)
    elif ext in (".txt", ".md", ".py", ".js", ".ts", ".json", ".log", ".csv"):
        return _read_txt(path)
    return f"[Định dạng '{ext}' chưa được hỗ trợ]"


def _split_chunks(text: str, max_words: int = 600) -> list[str]:
    """Tách text thành các đoạn theo số từ."""
    words  = text.split()
    return [
        " ".join(words[i : i + max_words])
        for i in range(0, len(words), max_words)
    ]


def _summarize_local(text: str, brain) -> str:
    """
    Thuật toán Map-Reduce cho local model (1.5b/3b).

    Map   : Tóm tắt từng đoạn nhỏ 600 từ độc lập.
    Reduce: Gộp tất cả tóm tắt nhỏ → tóm tắt tổng thể.

    Ưu điểm: Tránh quá tải context window, kết quả chính xác hơn.
    """
    chunks = _split_chunks(text, max_words=600)

    if len(chunks) == 1:
        # File ngắn — gọi AI một lần duy nhất
        return brain.summarize(chunks[0])

    # Map phase
    mini_summaries = []
    for i, chunk in enumerate(chunks, 1):
        print(f"   Đang xử lý phần {i}/{len(chunks)}...")
        summary = brain.summarize(chunk)
        # Bỏ qua nếu AI trả về JSON thay vì text (phòng ngừa)
        if summary and not summary.strip().startswith("{"):
            mini_summaries.append(summary)

    if not mini_summaries:
        return "❌ Không thể tóm tắt nội dung file."

    # Reduce phase
    combined = "\n\n".join(mini_summaries)
    return brain.summarize(combined)


def _summarize_cloud(text: str, brain) -> str:
    """
    Tóm tắt bằng cloud model với context window lớn.
    - Gemini 2.5 Flash: 1,000,000 token — gửi toàn bộ
    - Groq Llama 3.3 70B: 128,000 token — giới hạn ~25,000 ký tự
    """
    mode = brain.settings.get("mode", "cloud")
    if mode == "gemini":
        return brain.summarize(text)
    else:
        return brain.summarize(text[:25000])


def summarize_file(path: str, brain=None) -> str:
    """
    Đọc và tóm tắt nội dung file tài liệu.

    Args:
        path : Đường dẫn đầy đủ đến file.
        brain: Brain object để gọi AI. Nếu None, trả về text thô.

    Returns:
        Bản tóm tắt 3-5 câu bằng tiếng Việt.
    """
    file_path = Path(path.strip().strip("'\""))

    if not file_path.exists():
        return f"❌ File không tồn tại: {file_path}"
    if not file_path.is_file():
        return f"❌ Đây không phải file: {file_path}"

    size_mb = file_path.stat().st_size / (1024 * 1024)
    if size_mb > 50:
        return f"❌ File quá lớn ({size_mb:.1f} MB). Giới hạn tối đa 50 MB."

    text = _extract_text(file_path)

    if text.startswith("["):
        return text
    if not text.strip():
        return "❌ File trống hoặc không đọc được nội dung."

    # Fallback nếu không có brain (dùng cho unit test)
    if brain is None:
        return f"📄 {file_path.name}\n{text[:500]}"

    mode = brain.settings.get("mode", "local")
    if mode == "local":
        return _summarize_local(text, brain)
    else:
        return _summarize_cloud(text, brain)