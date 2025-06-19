import fitz  # PyMuPDF
import re

def extract_references(pdf_path):
    doc = fitz.open(pdf_path)
    references = []

    # Look for "References" or "Bibliography" section
    found = False
    for page in doc:
        text = page.get_text()
        if "references" in text.lower() or "bibliography" in text.lower():
            found = True
        if found:
            lines = text.split("\n")
            for line in lines:
                if re.search(r"\[\d+\]|\d{4}|doi|arxiv", line, re.IGNORECASE):
                    references.append(line.strip())

    return references
