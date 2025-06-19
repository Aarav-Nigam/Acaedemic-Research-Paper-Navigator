import streamlit as st
from agents.exec_pipeline import (
    run_scout_agent,
    run_summarizer_agent,
    run_qa_agent,
    run_curator_agent
)

def render_agent_pipeline_ui():
    st.title("🧠 Run Individual CrewAI Agents")

    tab1, tab2, tab3, tab4 = st.tabs(["📡 Scout", "📝 Summarizer", "❓ Q&A", "🗺️ Curator"])

    with tab1:
        topic = st.text_input("Topic to scout papers for:", key="scout_topic")
        if st.button("🔍 Run Scout"):
            with st.spinner("Fetching papers..."):
                result = run_scout_agent(topic)
                st.markdown("### Results")
                st.code(result)

    with tab2:
        paper_text = st.text_area("Paste paper content to summarize:", height=300, key="sum_text")
        if st.button("📝 Summarize"):
            with st.spinner("Summarizing..."):
                result = run_summarizer_agent(paper_text)
                st.markdown("### Summary")
                st.code(result)

    with tab3:
        question = st.text_input("Your question:", key="qa_q")
        context = st.text_area("Paper content or context:", height=300, key="qa_ctx")
        if st.button("🤖 Ask Q&A Agent"):
            with st.spinner("Thinking..."):
                result = run_qa_agent(question, context)
                st.markdown("### Answer")
                st.code(result)

    with tab4:
        cur_topic = st.text_input("Topic for citation mapping:", key="cur_map")
        if st.button("🗺️ Generate Citation Map Description"):
            with st.spinner("Curating map..."):
                result = run_curator_agent(cur_topic)
                st.markdown("### Citation Map Description")
                st.code(result)
