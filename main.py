
import streamlit as st
from frontend import upload, qa_chat
from frontend import summary, citation_explorer, citation_graph, agents_demo, agent_pipeline

pages = {
    "Upload / Fetch Paper": upload.render_upload_ui,
    "Semantic Q&A Chat": qa_chat.render_chat_ui,
    "Auto Summary": summary.render_summary_ui,
    "Citation Extractor & Explorer": citation_explorer.render_citation_ui,
    "Citation Graph": citation_graph.render_citation_graph_ui,
    "Agents Demo": agents_demo.render_agents_ui,
    "Agent Pipeline": agent_pipeline.render_agent_pipeline_ui
}


def main():
    st.sidebar.title("📚 Academic Navigator")
    choice = st.sidebar.radio("Go to:", list(pages.keys()))
    pages[choice]()

if __name__ == "__main__":
    main()
