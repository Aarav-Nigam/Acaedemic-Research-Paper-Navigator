# frontend/upload.py

import streamlit as st
from utils.pdf_utils import save_uploaded_pdf, fetch_arxiv_pdf
from backend.process_pdf import process_pdf

def render_upload_ui():
    st.title("📄 Upload or Fetch a Research Paper")

    option = st.radio("Select input type:", ["Upload PDF", "Fetch from arXiv"])

    if option == "Upload PDF":
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_file:
            path = save_uploaded_pdf(uploaded_file)
            st.success(f"PDF saved to: {path}")

    elif option == "Fetch from arXiv":
        arxiv_id = st.text_input("Enter arXiv ID (e.g. 2401.12345)")
        if st.button("Fetch Paper") and arxiv_id:
            path, metadata = fetch_arxiv_pdf(arxiv_id)
            if path:
                st.success(f"Downloaded paper to {path}")
                st.json(metadata)
            else:
                st.error("Failed to fetch paper.")


    # After PDF saved successfully
    if st.button("🔄 Process for Q&A"):
        num_chunks = process_pdf(path, paper_id=uploaded_file.name.split(".")[0])
        st.success(f"Processed! {num_chunks} text chunks embedded.")
