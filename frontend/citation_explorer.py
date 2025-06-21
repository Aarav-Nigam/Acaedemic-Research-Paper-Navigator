import streamlit as st
from backend.citation_processor import get_citation_metadata
from utils.session_manager import session_manager
import os

def render_citation_ui():
    st.title("🔗 Citation Extractor & Explorer")
    
    # Get available PDFs for current session
    current_pdfs = session_manager.get_session_pdfs(st.session_state.user_session_id)
    
    if not current_pdfs:
        st.info("📭 No PDFs in current session. Please upload PDFs first.")
        return
    
    # PDF Selection Section
    st.subheader("📚 Select PDF for Citation Extraction")
    
    # Single PDF selection for citation extraction
    selected_pdf = st.selectbox(
        "Choose a PDF to extract citations from:",
        options=["Select a PDF..."] + current_pdfs,
        key="citation_pdf_select"
    )
    
    if selected_pdf == "Select a PDF...":
        st.warning("Please select a PDF to extract citations from.")
        return
    
    # Show selected PDF info
    st.info(f"📄 Selected: {selected_pdf}")
    
    # Citation extraction settings
    with st.expander("⚙️ Extraction Settings", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            max_citations = st.slider("Max citations to process", 5, 100, 20)
            include_metadata = st.checkbox("Enrich with metadata", value=True)
        with col2:
            search_sections = st.multiselect(
                "Search in sections:",
                ["References", "Bibliography", "Works Cited", "Literature Cited"],
                default=["References", "Bibliography"]
            )
    
    # Extract citations button
    if st.button("📚 Extract Citations", type="primary"):
        user_dir = os.path.join("data", "temp_sessions", st.session_state.user_session_id)
        pdf_path = os.path.join(user_dir, "pdfs", selected_pdf)
        
        if not os.path.exists(pdf_path):
            st.error(f"❌ PDF file not found: {selected_pdf}")
            return
        
        with st.spinner("🔍 Extracting and enriching citations..."):
            try:
                citations = get_citation_metadata(
                    pdf_path, 
                    max_citations=max_citations,
                    include_metadata=include_metadata,
                    search_sections=search_sections
                )
                
                if not citations:
                    st.warning("⚠️ No citations found in the selected PDF.")
                    return
                
                # Store citations in session state
                st.session_state.extracted_citations = citations
                st.session_state.citation_source_pdf = selected_pdf
                
                st.success(f"✅ Successfully extracted {len(citations)} citations!")
                
            except Exception as e:
                st.error(f"❌ Error extracting citations: {str(e)}")
                return
    
    # Display extracted citations
    if 'extracted_citations' in st.session_state and st.session_state.extracted_citations:
        st.markdown("---")
        st.subheader(f"📋 Citations from {st.session_state.get('citation_source_pdf', 'PDF')}")
        
        # Citation display options
        col1, col2, col3 = st.columns(3)
        with col1:
            display_mode = st.radio("Display mode:", ["Detailed", "Compact"], horizontal=True)
        with col2:
            sort_by = st.selectbox("Sort by:", ["Order", "Year", "Citations", "Title"])
        with col3:
            filter_year = st.selectbox("Filter by year:", ["All"] + list(range(2024, 1980, -1)))
        
        citations = st.session_state.extracted_citations.copy()
        
        # Apply filters and sorting
        if filter_year != "All":
            citations = [c for c in citations if c.get('year') == filter_year]
        
        if sort_by == "Year":
            citations.sort(key=lambda x: x.get('year', 0), reverse=True)
        elif sort_by == "Citations":
            citations.sort(key=lambda x: x.get('citationCount', 0), reverse=True)
        elif sort_by == "Title":
            citations.sort(key=lambda x: x.get('title', '').lower())
        
        # Display citations
        for i, ref in enumerate(citations):
            with st.container():
                if display_mode == "Detailed":
                    # Detailed view with expandable sections
                    title = ref.get('title', 'Unknown Title')
                    authors = ref.get('authors', [])
                    year = ref.get('year', 'N/A')
                    citation_count = ref.get('citationCount', 0)
                    
                    # Main citation card
                    st.markdown(
                        f"""
                        <div style='background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 4px solid #007bff; margin: 10px 0;'>
                            <h4 style='margin-bottom: 10px; color: #007bff;'>{i+1}. {title}</h4>
                            <p style='margin: 5px 0;'><strong>👥 Authors:</strong> {', '.join([a.get('name', str(a)) if isinstance(a, dict) else str(a) for a in authors]) if authors else 'N/A'}</p>
                            <p style='margin: 5px 0;'><strong>📅 Year:</strong> {year}</p>
                            <p style='margin: 5px 0;'><strong>📊 Citations:</strong> {citation_count}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Additional details in expander
                    with st.expander(f"🔍 More details for citation {i+1}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if ref.get('externalIds'):
                                st.markdown("**🔗 External IDs:**")
                                for id_type, id_value in ref['externalIds'].items():
                                    if id_value:
                                        if id_type == 'DOI':
                                            st.markdown(f"- DOI: [{id_value}](https://doi.org/{id_value})")
                                        elif id_type == 'ArXiv':
                                            st.markdown(f"- ArXiv: [{id_value}](https://arxiv.org/abs/{id_value})")
                                        else:
                                            st.markdown(f"- {id_type}: {id_value}")
                        
                        with col2:
                            if ref.get('venue'):
                                st.markdown(f"**📖 Venue:** {ref['venue']}")
                            if ref.get('abstract'):
                                st.markdown("**📝 Abstract:**")
                                st.text_area("", ref['abstract'][:500] + "..." if len(ref['abstract']) > 500 else ref['abstract'], height=100, key=f"abstract_{i}")
                        
                        # Raw reference text if available
                        if ref.get('raw_text'):
                            st.markdown("**📄 Raw Reference:**")
                            st.code(ref['raw_text'], language="text")
                
                else:
                    # Compact view
                    title = ref.get('title', 'Unknown Title')
                    authors = ref.get('authors', [])
                    year = ref.get('year', 'N/A')
                    citation_count = ref.get('citationCount', 0)
                    
                    author_names = ', '.join([a.get('name', str(a)) if isinstance(a, dict) else str(a) for a in authors[:3]]) if authors else 'N/A'
                    if len(authors) > 3:
                        author_names += f" +{len(authors)-3} more"
                    
                    st.markdown(
                        f"""
                        <div style='background-color: #ffffff; padding: 10px; border-radius: 8px; border: 1px solid #dee2e6; margin: 5px 0;'>
                            <strong>{i+1}. {title}</strong><br>
                            <small>👥 {author_names} | 📅 {year} | 📊 {citation_count} citations</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
        # Export options
        st.markdown("---")
        st.subheader("📤 Export Citations")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Copy as Text"):
                text_output = []
                for i, ref in enumerate(citations):
                    title = ref.get('title', 'Unknown Title')
                    authors = ', '.join([a.get('name', str(a)) if isinstance(a, dict) else str(a) for a in ref.get('authors', [])])
                    year = ref.get('year', 'N/A')
                    text_output.append(f"{i+1}. {title}\nAuthors: {authors}\nYear: {year}\n")
                
                full_text = "\n".join(text_output)
                st.text_area("📋 Copy this text:", full_text, height=200)
        
        with col2:
            if st.button("📊 Generate Report"):
                # Generate citation statistics
                total_citations = len(citations)
                years = [ref.get('year') for ref in citations if ref.get('year') and isinstance(ref.get('year'), int)]
                avg_year = sum(years) / len(years) if years else 0
                total_paper_citations = sum([ref.get('citationCount', 0) for ref in citations])
                
                st.markdown(
                    f"""
                    ### 📊 Citation Analysis Report
                    - **Total Citations Found:** {total_citations}
                    - **Average Publication Year:** {avg_year:.1f}
                    - **Total Citation Count:** {total_paper_citations:,}
                    - **Most Cited Paper:** {max(citations, key=lambda x: x.get('citationCount', 0)).get('title', 'N/A') if citations else 'N/A'}
                    """
                )
        
        with col3:
            if st.button("🗑️ Clear Citations"):
                if 'extracted_citations' in st.session_state:
                    del st.session_state.extracted_citations
                if 'citation_source_pdf' in st.session_state:
                    del st.session_state.citation_source_pdf
                st.rerun()