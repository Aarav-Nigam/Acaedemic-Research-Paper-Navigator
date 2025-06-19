from utils.chunking import extract_full_text, chunk_text
from utils.embedding import save_embeddings

def process_pdf(path, paper_id):
    text = extract_full_text(path)
    chunks = chunk_text(text)
    db = save_embeddings(chunks, paper_id)
    return len(chunks)
