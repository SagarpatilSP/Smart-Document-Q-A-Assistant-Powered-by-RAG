import pdfplumber
import re

import pdfplumber

def pdf_to_text(pdf_file):
    pages = []
    with pdfplumber.open(pdf_file) as pdf:
        for i, p in enumerate(pdf.pages):
            page_text = p.extract_text() or ""
            pages.append({
                "page": i + 1,
                "text": page_text
            })
    return pages

def clean_text(text):
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

def chunk_text(pages, chunk_size=1200, overlap=200):

    chunks = []

    for page in pages:
        text = clean_text(page["text"])
        page_no = page["page"]

        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()

            if len(chunk) > 30:
                chunks.append({
                    "page": page_no,
                    "text": chunk
                })

            start = end - overlap
            if start < 0:
                start = 0

    return chunks