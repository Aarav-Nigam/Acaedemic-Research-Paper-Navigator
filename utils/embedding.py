from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

from dotenv import load_dotenv
import os

load_dotenv()

os.environ["HF_TOKEN"] = os.getenv("HUGGINGFACE_TOKEN")

def get_embedding_model():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def save_embeddings(chunks_with_metadata, user_session_id):
    """Save embeddings for user session with metadata"""
    VECTOR_DIR = os.path.join("data", "temp_sessions", user_session_id, "vectors")
    os.makedirs(VECTOR_DIR, exist_ok=True)
    
    # Convert chunks with metadata to Document objects
    documents = []
    for chunk_data in chunks_with_metadata:
        if isinstance(chunk_data, dict):
            doc = Document(
                page_content=chunk_data["content"],
                metadata={
                    "source": chunk_data["source"],
                    "pdf_path": chunk_data.get("pdf_path", "")
                }
            )
        else:
            # Fallback for plain text chunks
            doc = Document(page_content=chunk_data)
        documents.append(doc)
    
    embedding_model = get_embedding_model()
    vectordb = Chroma.from_documents(
        documents, 
        embedding_model, 
        persist_directory=VECTOR_DIR
    )
    return vectordb