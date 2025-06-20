from utils.chunking import extract_full_text, chunk_text
from utils.embedding import save_embeddings

def process_pdf(path, paper_id, user_session_id):
    """Process PDF with user session context"""
    text = extract_full_text(path)
    chunks = chunk_text(text)
    # Pass user_session_id to save_embeddings for isolated storage
    db = save_embeddings(chunks, paper_id, user_session_id)
    return len(chunks)