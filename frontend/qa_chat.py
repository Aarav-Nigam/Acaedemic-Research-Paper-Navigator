import streamlit as st
from backend.qa_pipeline import load_retriever, build_qa_chain
from utils.session_manager import session_manager
import os
from backend.process_pdf import process_pdf

def render_chat_ui():
    st.title("💬 Ask Questions About Your Paper")
    
     # Process PDF button (only show if we have PDFs)
    current_pdfs = session_manager.get_session_pdfs(st.session_state.user_session_id)
    if current_pdfs:
        st.subheader("📚 Available PDFs for Processing")
        
        # Show all PDFs with process buttons
        for pdf_name in current_pdfs:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.text(f"📄 {pdf_name}")
            with col2:
                if st.button(f"🔄 Process", key=f"process_{pdf_name}"):
                    try:
                        user_dir = os.path.join("data", "temp_sessions", st.session_state.user_session_id)
                        pdf_path = os.path.join(user_dir, "pdfs", pdf_name)
                        paper_id = pdf_name.split(".")[0]
                        num_chunks = process_pdf(pdf_path, paper_id=paper_id, user_session_id=st.session_state.user_session_id)
                        st.success(f"Processed {pdf_name}! {num_chunks} text chunks embedded.")
                    except Exception as e:
                        st.error(f"Processing failed: {str(e)}")
            with col3:
                if st.button(f"🗑️ Remove", key=f"remove_upload_{pdf_name}"):
                    if session_manager.remove_pdf_from_session(st.session_state.user_session_id, pdf_name):
                        st.success(f"Removed {pdf_name}")
                        st.rerun()
    
    # Show summary
    pdf_count = session_manager.get_pdf_count(st.session_state.user_session_id)
    if pdf_count > 0:
        st.info(f"📊 Current session has {pdf_count} PDF(s) uploaded")
    else:
        st.info("📭 No PDFs in current session")

    paper_id = st.text_input("Enter paper ID used in upload:", key="chat_paper_id")
    if not paper_id:
        st.warning("Please enter a paper ID.")
        return

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    retriever = load_retriever(paper_id)
    qa_chain = build_qa_chain(retriever)

    query = st.text_input("Ask a question:", key="user_question")

    if st.button("Ask") and query:
        with st.spinner("Thinking..."):
            result = qa_chain.invoke({"question": query, "chat_history": st.session_state.chat_history})
            st.session_state.chat_history.append((query, result["answer"]))
            st.success(result)

    st.markdown("---")
    st.subheader("📝 Conversation History")
    for i, (q, a) in enumerate(st.session_state.chat_history):
        st.markdown(f"**Q{i+1}:** {q}")
        st.markdown(f"> {a}")
