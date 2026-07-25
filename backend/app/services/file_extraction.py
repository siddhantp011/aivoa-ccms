"""
Lightweight text extraction for uploaded complaint documents.
Per the assignment, production-grade OCR/parsing is explicitly NOT required -
this handles the common cases (PDF, DOCX, TXT, EML/plain email text) well enough
to feed the LangGraph extraction node.
"""
import io
from email import message_from_bytes
from fastapi import UploadFile


async def extract_text_from_upload(file: UploadFile) -> str:
    content = await file.read()
    name = (file.filename or "").lower()

    if name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if name.endswith(".docx"):
        from docx import Document
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)

    if name.endswith(".eml"):
        msg = message_from_bytes(content)
        if msg.is_multipart():
            parts = [p.get_payload(decode=True) for p in msg.walk() if p.get_content_type() == "text/plain"]
            return "\n".join(p.decode(errors="ignore") for p in parts if p)
        return (msg.get_payload(decode=True) or b"").decode(errors="ignore")

    # .txt or unknown - best effort decode
    return content.decode(errors="ignore")
