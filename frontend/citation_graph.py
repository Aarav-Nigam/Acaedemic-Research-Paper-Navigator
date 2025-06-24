import streamlit as st
from backend.citation_processor import get_citation_metadata
from backend.graph_builder import build_enhanced_citation_graph

from utils.graph_visualizer import render_graph
from utils.session_manager import session_manager
import os
from typing import List, Dict, Any

def render_citation_graph_ui():
    """Enhanced UI for building citation graphs from multiple PDFs"""
    
    # Page header with improved styling
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; margin-bottom: 2rem; color: white;">
        <h1 style="margin: 0; font-size: 2.5rem;">📊 Citation Graph Builder</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">
            Visualize citation networks from your research papers
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get available PDFs for current session
    current_pdfs = session_manager.get_session_pdfs(st.session_state.user_session_id)
    
    if not current_pdfs:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background-color: #f8f9fa; 
                    border-radius: 10px; border-left: 4px solid #17a2b8;">
            <h3 style="color: #17a2b8; margin-bottom: 1rem;">📭 No PDFs Available</h3>
            <p style="color: #6c757d; font-size: 1.1rem;">
                Please upload PDFs first to build citation graphs.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Configuration Section
    with st.expander("⚙️ Graph Configuration", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            max_citations = st.slider(
                "📊 Max Citations per PDF", 
                min_value=5, 
                max_value=50, 
                value=20,
                help="Limit citations to improve graph readability"
            )
        
        with col2:
            include_metadata = st.checkbox(
                "🔍 Enrich with Metadata", 
                value=True,
                help="Fetch additional metadata from Semantic Scholar"
            )
        
        with col3:
            graph_layout = st.selectbox(
                "🎨 Layout Style",
                ["Force-directed", "Hierarchical", "Circular"],
                help="Choose graph visualization layout"
            )
    
    # PDF Selection Section
    st.markdown("### 📚 Select Research Papers")
    
    # Initialize selected PDFs in session state
    if "selected_graph_pdfs" not in st.session_state:
        st.session_state.selected_graph_pdfs = []
    
    # Create columns for better layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # PDF selection with enhanced checkboxes
        selected_pdfs = []
        
        # Select All / None buttons
        subcol1, subcol2, subcol3 = st.columns([1, 1, 4])
        with subcol1:
            if st.button("✅ Select All", key="select_all_graph"):
                st.session_state.selected_graph_pdfs = current_pdfs.copy()
                st.rerun()
        
        with subcol2:
            if st.button("❌ Clear All", key="clear_all_graph"):
                st.session_state.selected_graph_pdfs = []
                st.rerun()
        
        # Display PDFs with enhanced styling
        for i, pdf_name in enumerate(current_pdfs):
            # Create a more appealing checkbox layout
            is_selected = st.checkbox(
                f"📄 **{pdf_name}**", 
                value=pdf_name in st.session_state.selected_graph_pdfs,
                key=f"select_graph_{pdf_name}_{i}",
                help=f"Include {pdf_name} in citation graph"
            )
            
            if is_selected and pdf_name not in selected_pdfs:
                selected_pdfs.append(pdf_name)
            elif not is_selected and pdf_name in st.session_state.selected_graph_pdfs:
                st.session_state.selected_graph_pdfs.remove(pdf_name)
    
    with col2:
        # PDF count and info
        if selected_pdfs:
            st.markdown(f"""

            <div style="background-color: rgba(40, 167, 69, 0.1); color: inherit; padding: 1rem; border-radius: 8px; text-align: center;">
                <h4 style="color: #28a745; margin: 0;">Selected PDFs</h4>
                <p style="font-size: 2rem; margin: 0.5rem 0; color: #28a745;">{len(selected_pdfs)}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: rgba(255, 193, 7, 0.1); color: inherit; padding: 1rem; border-radius: 8px; text-align: center;">
                <h4 style="color: #856404; margin: 0;">No PDFs Selected</h4>
                <p style="color: #856404; margin: 0.5rem 0;">Select papers above</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.session_state.selected_graph_pdfs = selected_pdfs
    
    if not selected_pdfs:
        st.warning("⚠️ Please select at least one PDF to build a citation graph.")
        return
    
    # Selected PDFs summary with better styling
    st.markdown("### 📊 Selected Papers Summary")
    
    # Create expandable summary
    with st.expander(f"📋 View Selected Papers ({len(selected_pdfs)})", expanded=False):
        for i, pdf_name in enumerate(selected_pdfs, 1):
            st.markdown(f"**{i}.** 📄 {pdf_name}")
    
    # Graph Generation Section
    st.markdown("### 🚀 Generate Citation Graph")
    
    # Enhanced generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button(
            "🔄 Build Citation Graph", 
            type="primary",
            use_container_width=True,
            help="Process selected PDFs and create interactive citation network"
        )
    
    if generate_button:
        try:
            with st.spinner("🔄 Building citation graph..."):
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                all_citations = []
                
                # Process each selected PDF
                for i, pdf_name in enumerate(selected_pdfs):
                    status_text.text(f"Processing {pdf_name}...")
                    progress_bar.progress((i + 1) / len(selected_pdfs))
                    
                    try:
                        # Get full path for PDF
                        pdf_path = os.path.join("data", "temp_sessions", st.session_state.user_session_id,"pdfs", pdf_name)

                        # Extract citations
                        citations = get_citation_metadata(
                            pdf_path, 
                            max_citations=max_citations,
                            include_metadata=include_metadata
                        )
                        
                        # Add source paper info to each citation
                        for citation in citations:
                            citation["source_paper"] = pdf_name
                        
                        all_citations.extend(citations)
                        
                    except Exception as e:
                        st.error(f"❌ Error processing {pdf_name}: {str(e)}")
                        continue
                
                status_text.text("Building graph visualization...")
                
                if all_citations:
                    # Build the graph
                    main_papers = [{"title": pdf.replace('.pdf', ''), "year": "2025"} 
                                 for pdf in selected_pdfs]
                    
                    G = build_enhanced_citation_graph(main_papers, all_citations, graph_layout)
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Display graph statistics
                    display_graph_statistics(G, all_citations, selected_pdfs)
                    
                    # Render the interactive graph
                    st.markdown("### 🌐 Interactive Citation Network")
                    render_graph(G, height="700px", layout=graph_layout.lower())
                    
                    # Export options
                    st.markdown("### 📥 Export Options")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("💾 Save as HTML"):
                            st.success("Graph saved to data/citation_graph.html")
                    
                    with col2:
                        if st.button("📊 Export Data"):
                            export_citation_data(all_citations, selected_pdfs)
                    
                    with col3:
                        if st.button("🖼️ Generate Report"):
                            generate_citation_report(G, all_citations, selected_pdfs)
                
                else:
                    st.warning("⚠️ No citations found in the selected PDFs.")
                    
        except Exception as e:
            st.error(f"❌ Error building citation graph: {str(e)}")


def display_graph_statistics(G, citations: List[Dict], selected_pdfs: List[str]):
    """Display statistics about the citation graph"""
    
    st.markdown("### 📈 Graph Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Source Papers", len(selected_pdfs))
    
    with col2:
        st.metric("📄 Total Citations", len(citations))
    
    with col3:
        st.metric("🔗 Graph Nodes", G.number_of_nodes())
    
    with col4:
        st.metric("➡️ Graph Edges", G.number_of_edges())
    
    # Year distribution
    years = [c.get("year") for c in citations if isinstance(c.get("year"), int)]
    if years:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("📅 Newest Citation", max(years))
        
        with col2:
            st.metric("📅 Oldest Citation", min(years))

def export_citation_data(citations: List[Dict], selected_pdfs: List[str]):
    """Export citation data as downloadable file"""
    import json
    import pandas as pd
    
    # Prepare data for export
    export_data = {
        "source_papers": selected_pdfs,
        "citations": citations,
        "export_timestamp": st.session_state.get("current_time", "N/A")
    }
    
    # Convert to JSON
    json_data = json.dumps(export_data, indent=2, default=str)
    
    st.download_button(
        label="📥 Download Citation Data (JSON)",
        data=json_data,
        file_name="citation_data.json",
        mime="application/json"
    )

def generate_citation_report(G, citations: List[Dict], selected_pdfs: List[str]):
    """Generate a comprehensive citation report"""
    
    st.markdown("### 📋 Citation Analysis Report")
    
    # Summary statistics
    total_citations = len(citations)
    unique_years = len(set(c.get("year") for c in citations if c.get("year")))
    
    report = f"""
    ## Citation Network Analysis Report
    
    **Generated on:** {st.session_state.get("current_time", "N/A")}
    
    ### Overview
    - **Source Papers:** {len(selected_pdfs)}
    - **Total Citations:** {total_citations}
    - **Unique Publication Years:** {unique_years}
    - **Graph Density:** {G.number_of_edges() / (G.number_of_nodes() * (G.number_of_nodes() - 1)) if G.number_of_nodes() > 1 else 0:.3f}
    
    ### Source Papers
    """
    
    for i, pdf in enumerate(selected_pdfs, 1):
        report += f"{i}. {pdf}\n"
    
    st.markdown(report)
    
    # Make report downloadable
    st.download_button(
        label="📥 Download Full Report",
        data=report,
        file_name="citation_report.md",
        mime="text/markdown"
    )