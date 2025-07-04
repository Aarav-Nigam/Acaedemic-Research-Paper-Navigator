from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from utils.embedding import get_embedding_model

from dotenv import load_dotenv
import os

load_dotenv()

os.environ["GROQ_API"] = os.getenv("GROQ_API")

def load_retriever(user_session_id):
    """Load retriever for user session"""
    vectordb = Chroma(
        persist_directory = os.path.join("data", "temp_sessions", user_session_id, "vectors"),
        embedding_function=get_embedding_model()
    )
    return vectordb.as_retriever()

def build_qa_chain(retriever):
    llm = ChatGroq(
        model="qwen-qwq-32b", 
        groq_api_key=os.environ["GROQ_API"],
        temperature=0.7
    )
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain

