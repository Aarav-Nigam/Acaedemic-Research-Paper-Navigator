
import streamlit as st
from frontend import upload, qa_chat
from frontend import summary, citation_explorer, citation_graph, agents_demo, agent_pipeline
from utils.session_manager import SessionManager
from utils.pdf_utils import cleanup_user_data

# patch_sqlite.py
import sys
import pysqlite3
sys.modules["sqlite3"] = pysqlite3


# Configure page
st.set_page_config(
    page_title="📚 Academic Navigator", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session manager
@st.cache_resource
def get_session_manager():
    manager = SessionManager()
    manager.start_cleanup_service()
    return manager

# Start session management
session_manager = get_session_manager()

pages = {
    "Upload / Fetch Paper": upload.render_upload_ui,
    "Semantic Q&A Chat": qa_chat.render_chat_ui,
    "Auto Summary": summary.render_summary_ui,
    "Citation Extractor & Explorer": citation_explorer.render_citation_ui,
    "Citation Graph": citation_graph.render_citation_graph_ui,
    "Crew Learning": agents_demo.render_agents_ui,
    "Individual Learning": agent_pipeline.render_agent_pipeline_ui
}

def render_session_info():
    """Render session information and controls in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔐 Session Management")
    
    if 'user_session_id' in st.session_state:
        # Show session info
        session_id_display = st.session_state.user_session_id[:8] + "..."
        st.sidebar.info(f"Session: {session_id_display}")
        
        # Show session files count (real-time)
        pdf_count = session_manager.get_pdf_count(st.session_state.user_session_id)
        st.sidebar.text(f"📄 Files: {pdf_count}")
        
        # Show PDF list with remove buttons
        if pdf_count > 0:
            st.sidebar.subheader("📚 Uploaded PDFs")
            pdfs = session_manager.get_session_pdfs(st.session_state.user_session_id)
            
            for pdf in pdfs:
                pdf_display = f"{pdf[:20]}..." if len(pdf) > 20 else pdf
                remove_key = f"remove_{pdf}"
                if st.sidebar.button(f"❌ Remove {pdf_display}", key=remove_key):
                    if session_manager.remove_pdf_from_session(st.session_state.user_session_id, pdf):
                        st.sidebar.success(f"Removed {pdf}")
                        st.rerun()


        
        # Session controls
        col1 = st.sidebar.columns(1)
        
        with col1[0]:
            if st.button("🔄 New Session", help="Start a new session"):
                cleanup_user_data(st.session_state.user_session_id)
                if st.session_state.user_session_id in session_manager.session_pdfs:
                    del session_manager.session_pdfs[st.session_state.user_session_id]
                st.session_state.clear()
                st.rerun()
    else:
        st.sidebar.info("No active session")

def main():
    st.sidebar.title("📚 Academic Navigator")
    
    # Navigation
    choice = st.sidebar.radio("Navigate to:", list(pages.keys()))
    
    # Session info
    render_session_info()
    
    # Render selected page
    try:
        pages[choice]()
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        st.info("Please try refreshing the page or starting a new session.")

if __name__ == "__main__":
    main()
