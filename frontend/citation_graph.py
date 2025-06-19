import streamlit as st
from backend.citation_processor import get_citation_metadata
from backend.graph_builder import build_citation_graph
from utils.graph_visualizer import render_graph

def render_citation_graph_ui():
    st.title("📊 Citation Graph Builder")

    path = st.text_input("PDF path:", key="graph_pdf_path")
    if not path:
        return

    if st.button("🔄 Generate Citation Graph"):
        with st.spinner("Building graph..."):
            citations = get_citation_metadata(path)

            main_paper = {
                "title": "Main Paper",
                "year": "2025"
            }

            G = build_citation_graph(main_paper, citations)
            render_graph(G)
