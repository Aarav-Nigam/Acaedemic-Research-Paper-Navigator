from langchain.text_splitter import RecursiveCharacterTextSplitter
import fitz  # PyMuPDF

def extract_full_text(path):
    """Extract all text from a PDF file"""
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def chunk_text(text, chunk_size=1000, chunk_overlap=200):
    """Split text into overlapping chunks"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "]
    )
    return splitter.split_text(text)
