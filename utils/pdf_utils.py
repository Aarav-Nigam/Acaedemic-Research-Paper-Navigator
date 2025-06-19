import os
import fitz  # PyMuPDF
import requests
import arxiv
from datetime import datetime

PDF_DIR = "data/pdfs"

def save_uploaded_pdf(uploaded_file):
    os.makedirs(PDF_DIR, exist_ok=True)
    path = os.path.join(PDF_DIR, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.read())
    return path

def fetch_arxiv_pdf(arxiv_id):
    try:
        search = arxiv.Search(id_list=[arxiv_id])
        result = next(search.results())

        pdf_url = result.pdf_url
        metadata = {
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "abstract": result.summary,
            "published": result.published.strftime("%Y-%m-%d")
        }

        response = requests.get(pdf_url)
        filename = f"{arxiv_id}.pdf"
        path = os.path.join(PDF_DIR, filename)
        with open(path, "wb") as f:
            f.write(response.content)

        return path, metadata

    except Exception as e:
        print("ArXiv fetch error:", e)
        return None, None

def extract_metadata(path):
    """Basic metadata extraction using PyMuPDF"""
    doc = fitz.open(path)
    text = doc[0].get_text() if doc.page_count > 0 else ""
    metadata = doc.metadata
    return {
        "title": metadata.get("title", ""),
        "authors": metadata.get("author", ""),
        "first_page_text": text[:1000]  # first 1000 chars
    }
