import streamlit as st
from backend.summarizer import summarize_text
from utils.chunking import extract_full_text

def render_summary_ui():
    st.title("📄 Paper Summary & Key Points")

    path = st.text_input("Path to uploaded PDF:", key="summary_pdf_path")
    if not path:
        st.warning("Enter a valid file path to a PDF you've uploaded.")
        return

    if st.button("🧠 Generate Summary"):
        with st.spinner("Reading and summarizing..."):
            text = extract_full_text(path)
            summary = summarize_text(text)
            st.markdown(summary)
