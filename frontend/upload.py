
import streamlit as st
import os
import atexit
import shutil
from utils.pdf_utils import save_uploaded_pdf, fetch_arxiv_pdf, cleanup_user_data
from backend.process_pdf import process_pdf
import time
from utils.session_manager import session_manager

def get_user_session_dir():
    """Get or create user-specific directory based on session state"""
    if 'user_session_id' not in st.session_state:
        import uuid
        st.session_state.user_session_id = str(uuid.uuid4())
    
    user_dir = os.path.join("data", "temp_sessions", st.session_state.user_session_id)
    pdf_dir = os.path.join(user_dir, "pdfs")
    os.makedirs(pdf_dir, exist_ok=True)
    return user_dir

def register_cleanup():
    """Register cleanup function to run when session ends"""
    if 'cleanup_registered' not in st.session_state:
        st.session_state.cleanup_registered = True
        
        # Register cleanup for when the script ends
        def cleanup_on_exit():
            if 'user_session_id' in st.session_state:
                cleanup_user_data(st.session_state.user_session_id)
        
        atexit.register(cleanup_on_exit)

def render_upload_ui():
    st.title("📄 Upload or Fetch a Research Paper")
    
    # Register cleanup and get user directory
    register_cleanup()
    user_dir = get_user_session_dir()
    
    # Add cleanup button for manual cleanup
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🗑️ Clear Session"):
            cleanup_user_data(st.session_state.user_session_id)
            if st.session_state.user_session_id in session_manager.session_pdfs:
                del session_manager.session_pdfs[st.session_state.user_session_id]
            st.session_state.clear()
            st.rerun()
    
    option = st.radio("Select input type:", ["Upload PDF", "Fetch from arXiv"])
    
    path = None
    paper_id = None
    
    if option == "Upload PDF":
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_file:
            # Save to pdfs subdirectory
            path = save_uploaded_pdf(uploaded_file, user_dir)
            paper_id = uploaded_file.name.split(".")[0]
            
            # Track in session manager
            session_manager.add_pdf_to_session(st.session_state.user_session_id, uploaded_file.name)
            
            st.success(f"PDF saved to user session")
            st.rerun()  # Refresh to update file count
            
    elif option == "Fetch from arXiv":
        arxiv_id = st.text_input("Enter arXiv ID (e.g. 2401.12345)")
        if st.button("Fetch Paper") and arxiv_id:
            path, metadata = fetch_arxiv_pdf(arxiv_id, user_dir)
            if path:
                paper_id = arxiv_id
                pdf_name = os.path.basename(path)
                
                # Track in session manager  
                session_manager.add_pdf_to_session(st.session_state.user_session_id, pdf_name)
                
                st.success(f"Downloaded paper to user session")
                st.json(metadata)
                time.sleep(3)
                st.rerun()  # Refresh to update file count
                st.json(metadata)
            else:
                st.error("Failed to fetch paper.")
    