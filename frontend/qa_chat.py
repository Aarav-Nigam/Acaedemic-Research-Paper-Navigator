import streamlit as st
from backend.qa_pipeline import load_retriever, build_qa_chain
from utils.session_manager import session_manager
import os
import re
from backend.process_pdf import process_pdfs_batch

def parse_llm_response(response):
    """Parse LLM response to separate thinking and final answer"""
    if not response:
        return {"thinking": "", "answer": ""}
    
    # Extract thinking content from <think> tags
    think_match = re.search(r'<think>(.*?)</think>', response, flags=re.DOTALL | re.IGNORECASE)
    thinking_content = think_match.group(1).strip() if think_match else ""
    
    # Extract the answer part (everything outside <think> tags)
    answer_content = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL | re.IGNORECASE)
    answer_content = answer_content.strip()
    
    # If no answer content found outside think tags, use the original response
    if not answer_content and not thinking_content:
        answer_content = response
    
    return {
        "thinking": thinking_content,
        "answer": answer_content
    }

def render_chat_ui():
    st.title("💬 Ask Questions About Your Papers")
    
    # Get available PDFs for current session
    current_pdfs = session_manager.get_session_pdfs(st.session_state.user_session_id)
    
    if not current_pdfs:
        st.info("📭 No PDFs in current session. Please upload PDFs first.")
        return
    
    # PDF Selection Section
    st.subheader("📚 Select PDFs for Q&A")
    
    # Initialize selected PDFs in session state
    if "selected_pdfs" not in st.session_state:
        st.session_state.selected_pdfs = []
    
    # PDF selection with checkboxes
    selected_pdfs = []
    for pdf_name in current_pdfs:
        if st.checkbox(f"📄 {pdf_name}", key=f"select_{pdf_name}"):
            selected_pdfs.append(pdf_name)
    
    st.session_state.selected_pdfs = selected_pdfs
    
    if not selected_pdfs:
        st.warning("Please select at least one PDF to ask questions about.")
        return
    
    # Show selected PDFs summary
    st.info(f"📊 Selected {len(selected_pdfs)} PDF(s): {', '.join(selected_pdfs)}")
    
    # Initialize vector database for selected PDFs
    if st.button("🔄 Build Knowledge Base", type="primary"):
        if selected_pdfs:
            with st.spinner("Building knowledge base from selected PDFs..."):
                try:
                    user_dir = os.path.join("data", "temp_sessions", st.session_state.user_session_id)
                    pdf_paths = [os.path.join(user_dir, "pdfs", pdf_name) for pdf_name in selected_pdfs]
                    
                    num_chunks = process_pdfs_batch(
                        pdf_paths=pdf_paths,
                        pdf_names=selected_pdfs,
                        user_session_id=st.session_state.user_session_id
                    )
                    
                    st.success(f"✅ Knowledge base built! Processed {num_chunks} text chunks from {len(selected_pdfs)} PDFs.")
                    st.session_state.knowledge_base_ready = True
                    
                except Exception as e:
                    st.error(f"❌ Failed to build knowledge base: {str(e)}")
                    st.session_state.knowledge_base_ready = False
    
    # Check if knowledge base is ready
    if not st.session_state.get("knowledge_base_ready", False):
        st.warning("⚠️ Please build the knowledge base first by clicking the button above.")
        return
    
    st.markdown("---")
    
    # Q&A Section
    st.subheader("💭 Ask Questions")
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Load retriever and QA chain
    try:
        retriever = load_retriever(user_session_id=st.session_state.user_session_id)
        qa_chain = build_qa_chain(retriever)
        
        query = st.chat_input("Ask a question about your selected papers:")
        
        if query:
            # Display user question immediately
            with st.chat_message("user"):
                st.markdown(query)
            with st.spinner("🤔 Thinking..."):
                try:
                    result = qa_chain.invoke({"question": query, "chat_history": st.session_state.chat_history})
                    
                    # Parse the response to separate thinking and answer
                    parsed_response = parse_llm_response(result["answer"])
                    
                    # Store the clean answer in chat history
                    clean_answer = parsed_response["answer"] if parsed_response["answer"] else result["answer"]
                    st.session_state.chat_history.append((query, clean_answer))
                    
                    # Display thinking process if available
                    if parsed_response["thinking"]:
                        st.markdown("### 🧠 **Model's Reasoning Process**")
                        with st.container():
                            st.markdown(
                                f"""
                                <div style='background-color: rgba(31, 119, 180, 0.1); color: inherit; padding: 15px; border-radius: 10px; border-left: 4px solid #1f77b4; margin: 10px 0;'>
                                    <strong>💭 Thinking:</strong><br>
                                    {parsed_response["thinking"].replace(chr(10), '<br>')}
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                    
                    # Display the final answer
                    st.markdown("### ✅ **Answer**")
                    with st.chat_message("assistant"):
                        st.markdown(clean_answer)
                    
                    # Show source documents if available
                    if "source_documents" in result and result["source_documents"]:
                        st.markdown("### 📋 **Source Documents**")
                        
                        # Create tabs for different sources
                        source_tabs = st.tabs([f"📄 Source {i+1}" for i in range(min(3, len(result["source_documents"])))])
                        
                        for i, (tab, doc) in enumerate(zip(source_tabs, result["source_documents"][:3])):
                            with tab:
                                source_metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                                source_name = source_metadata.get('source', f'Document {i+1}')
                                
                                st.markdown(f"**📄 From: {source_name}**")
                                
                                # Display content in a nice box
                                st.markdown(
                                    f"""
                                    <div style='background-color: rgba(40, 167, 69, 0.1); color: inherit; padding: 15px; border-radius: 10px; border-left: 4px solid #28a745; margin: 10px 0;'>
                                        {doc.page_content[:400]}{'...' if len(doc.page_content) > 400 else ''}
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                
                                if len(doc.page_content) > 400:
                                    with st.expander("Show full content"):
                                        st.text(doc.page_content)
                                
                except Exception as e:
                    st.error(f"❌ Error processing question: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error loading knowledge base: {str(e)}")
        st.session_state.knowledge_base_ready = False
    
    # Conversation History in Enhanced Format
    if st.session_state.chat_history:
        st.markdown("---")
        st.subheader("📝 Conversation History")
        
        # Display chat history with expandable sections
        for i, (q, a) in enumerate(reversed(st.session_state.chat_history[-10:])):  # Show last 10 conversations
            conversation_num = len(st.session_state.chat_history) - i
            
            # Create an expandable conversation section
            with st.expander(f"💬 Conversation #{conversation_num}: {q[:60]}{'...' if len(q) > 60 else ''}", expanded=(i == 0)):
                # User question
                st.markdown("**👤 You asked:**")
                st.markdown(
                    f"""
                    <div style='background-color: rgba(33, 150, 243, 0.1); color: inherit; padding: 10px; border-radius: 8px; margin: 5px 0;'>
                        {q}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Assistant answer
                st.markdown("**🤖 Assistant:**")
                st.markdown(
                    f"""
                    <div style='background-color: rgba(139, 195, 74, 0.1); color: inherit; padding: 10px; border-radius: 8px; margin: 5px 0;'>
                        {a}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    # Clear session button with confirmation
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🗑️ Clear Knowledge Base", type="secondary"):
            st.session_state.confirm_clear = True
    
    with col2:
        if st.button("📊 Session Stats", type="secondary"):
            # Show session statistics
            vector_path = os.path.join("data", "vectors", st.session_state.user_session_id)
            vector_exists = os.path.exists(vector_path)
            
            st.info(f"""
            **Session Statistics:**
            - Total PDFs: {len(current_pdfs)}
            - Selected PDFs: {len(st.session_state.get('selected_pdfs', []))}
            - Knowledge Base: {'✅ Built' if st.session_state.get('knowledge_base_ready', False) else '❌ Not Built'}
            - Chat History: {len(st.session_state.get('chat_history', []))} messages
            - Vector DB: {'✅ Exists' if vector_exists else '❌ Not Found'}
            """)
    
    # Confirmation dialog for clearing
    if st.session_state.get("confirm_clear", False):
        st.warning("⚠️ Are you sure you want to clear the knowledge base and chat history?")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("✅ Yes, Clear Everything", type="primary"):
                # Clear vector database
                vector_path = os.path.join("data", "vectors", st.session_state.user_session_id)
                if os.path.exists(vector_path):
                    import shutil
                    shutil.rmtree(vector_path)
                
                # Clear session state
                st.session_state.chat_history = []
                st.session_state.knowledge_base_ready = False
                st.session_state.selected_pdfs = []
                st.session_state.confirm_clear = False
                
                st.success("✅ Knowledge base and chat history cleared!")
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.confirm_clear = False
                st.rerun()


# Updated backend/qa_pipeline.py
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
        persist_directory=f"data/vectors/{user_session_id}",
        embedding_function=get_embedding_model()
    )
    return vectordb.as_retriever()

def build_qa_chain(retriever):
    llm = ChatGroq(
        model="qwen/qwen3-32b", 
        groq_api_key=os.environ["GROQ_API"],
        temperature=0.7
    )
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain


# Updated backend/process_pdf.py
from utils.chunking import extract_full_text, chunk_text
from utils.embedding import save_embeddings

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


# Updated utils/embedding.py
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

from dotenv import load_dotenv
import os

load_dotenv()

os.environ["HF_TOKEN"] = os.getenv("HUGGINGFACE_TOKEN")

VECTOR_DIR = "data/vectors"

def get_embedding_model():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def save_embeddings(chunks_with_metadata, user_session_id):
    """Save embeddings for user session with metadata"""
    os.makedirs(VECTOR_DIR, exist_ok=True)
    db_path = os.path.join(VECTOR_DIR, user_session_id)
    
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
        persist_directory=db_path
    )
    return vectordb