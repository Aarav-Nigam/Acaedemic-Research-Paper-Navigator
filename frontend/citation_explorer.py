import streamlit as st
from backend.citation_processor import get_citation_metadata

def render_citation_ui():
    st.title("🔗 Citation Extractor & Explorer")

    path = st.text_input("Enter PDF path:", key="citation_path")
    if not path:
        return

    if st.button("📚 Extract Citations"):
        with st.spinner("Parsing and enriching..."):
            citations = get_citation_metadata(path)
            for i, ref in enumerate(citations):
                st.markdown(f"**{i+1}. {ref.get('title', '')}**")
                st.markdown(f"- Authors: {', '.join([a['name'] for a in ref.get('authors', [])])}")
                st.markdown(f"- Year: {ref.get('year', 'N/A')}")
                st.markdown("---")
