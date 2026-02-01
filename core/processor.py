import pdfplumber
import re

def pdf_to_text(pdf_file):
    txt = []
    with pdfplumber.open(pdf_file) as pdf:
        for p in pdf.pages:
            page_text = p.extract_text() or ""
            txt.append(page_text)
    return "\n".join(txt)

def clean_text(text):
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

def chunk_text(text, chunk_size=1200, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start = end - overlap
        if start < 0:
            start = 0
    return [c for c in chunks if len(c) > 30]