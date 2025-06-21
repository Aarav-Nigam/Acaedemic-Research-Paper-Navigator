from utils.chunking import extract_full_text, chunk_text
from utils.embedding import save_embeddings

def process_pdf(path, paper_id, user_session_id):
    """Process PDF with user session context"""
    text = extract_full_text(path)
    chunks = chunk_text(text)
    # Pass user_session_id to save_embeddings for isolated storage
    db = save_embeddings(chunks, paper_id, user_session_id)
    return len(chunks)

def process_pdfs_batch(pdf_paths, pdf_names, user_session_id):
    """Process multiple PDFs and combine them into a single vector database"""
    all_chunks = []
    
    for pdf_path, pdf_name in zip(pdf_paths, pdf_names):
        # Extract text from each PDF
        text = extract_full_text(pdf_path)
        chunks = chunk_text(text)
        
        # Add metadata to chunks to identify source PDF
        for chunk in chunks:
            chunk_with_metadata = {
                "content": chunk,
                "source": pdf_name,
                "pdf_path": pdf_path
            }
            all_chunks.append(chunk_with_metadata)
    
    # Save all chunks to a single vector database for this user session
    db = save_embeddings(all_chunks, user_session_id)
    return len(all_chunks)