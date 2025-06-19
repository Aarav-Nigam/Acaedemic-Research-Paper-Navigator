from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from dotenv import load_dotenv
import os

load_dotenv()

os.environ["HF_TOKEN"] = os.getenv("HUGGINGFACE_TOKEN")

VECTOR_DIR = "data/vectors"

def get_embedding_model():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def save_embeddings(chunks, paper_id):
    os.makedirs(VECTOR_DIR, exist_ok=True)
    db_path = os.path.join(VECTOR_DIR, paper_id)
    
    embedding_model = get_embedding_model()
    vectordb = Chroma.from_texts(chunks, embedding_model, persist_directory=db_path)
    return vectordb
