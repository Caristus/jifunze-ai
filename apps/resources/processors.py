import logging
logger = logging.getLogger(__name__)
try:
    import fitz  # PyMuPDF
    HAS_PDF = True
except ImportError:
    fitz = None
    HAS_PDF = False
try:
    import docx  # python-docx
    HAS_DOCX = True
except ImportError:
    docx = None
    HAS_DOCX = False
def extract_text(file_obj) -> str:
    filename = file_obj.name.lower()
    text = ""
    try:
        file_obj.seek(0)  # Ensure pointer is at start (fixes test client issue)
        if filename.endswith(".pdf"):
            if not HAS_PDF: return ""
            with fitz.open(stream=file_obj.read(), filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text()
        elif filename.endswith(".docx"):
            if not HAS_DOCX: return ""
            document = docx.Document(file_obj)
            text = "\n".join(p.text for p in document.paragraphs)
        else:
            text = file_obj.read().decode("utf-8", errors="ignore")
    except Exception as e:
        logger.error("Extraction failed for %s: %s", filename, e)
    return text
def chunk_text(text: str, chunk_size: int = 1000) -> list:
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) > chunk_size:
            if current:
                chunks.append(current.strip())
            current = p
        else:
            current += "\n\n" + p
    if current:
        chunks.append(current.strip())
    return [c for c in chunks if c]
