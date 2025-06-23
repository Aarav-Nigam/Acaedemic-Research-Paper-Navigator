# agents_ui.py
import streamlit as st
from agents.exec_pipeline import (
    run_scout_agent,
    run_summarizer_agent,
    run_qa_agent,
    run_insight_agent
)

def render_agent_pipeline_ui():
    st.title("🤖 CrewAI Agent Pipeline")
    st.caption("Multi-agent system for academic research. Choose a tab to get started.")

    tab1, tab2, tab3, tab4 = st.tabs(["📡 Scout", "📝 Summarizer", "❓ Q&A", "💡 Insight Generator"])

    # SCOUT
    with tab1:
        st.subheader("📡 Scout Papers")
        topic = st.text_input("Enter a research topic", placeholder="e.g., Vision-Language Models in Robotics")

        if st.button("🔍 Search"):
            with st.spinner("🚀 Scouting papers..."):
                result = run_scout_agent(topic)
                st.success("✅ Papers fetched!")

                view = st.radio("Display format:", ["📄 Rendered", "📜 Code"], horizontal=True)
                if view == "📄 Rendered":
                    st.markdown(result, unsafe_allow_html=True)
                else:
                    st.code(result)

                st.download_button("📥 Download Paper List", result.raw, file_name="scouted_papers.md")

    # SUMMARIZER
    with tab2:
        st.subheader("📝 Summarize Paper Content")
        paper_text = st.text_area("Paste full paper text below:", height=350)

        if st.button("📃 Summarize"):
            with st.spinner("🧠 Reading paper..."):
                result = run_summarizer_agent(paper_text)
                st.success("✅ Summary ready!")

                with st.expander("📄 View Summary"):
                    st.markdown(result, unsafe_allow_html=True)

                st.download_button("📥 Download Summary", result.raw, file_name="summary.md")

    # QA
    with tab3:
        st.subheader("❓ Ask a Question About a Paper")
        question = st.text_input("Your research question", placeholder="e.g., What is the core contribution?")
        context = st.text_area("Paste the paper content or summary:", height=300)

        if st.button("🤖 Ask Agent"):
            with st.spinner("💬 Thinking..."):
                result = run_qa_agent(question, context)
                st.success("✅ Answer generated!")

                with st.expander("🧾 View Answer"):
                    st.markdown(result, unsafe_allow_html=True)

                st.download_button("📥 Download Answer", result.raw, file_name="qa_answer.md")

    # INSIGHT
    with tab4:
        st.subheader("💡 Generate Research Insights")
        summaries = st.text_area("Paste paper summaries or key points:", height=300)

        if st.button("💡 Generate Insights"):
            with st.spinner("🔍 Analyzing..."):
                result = run_insight_agent(summaries)
                st.success("✅ Insights ready!")

                with st.expander("📊 View Insights"):
                    st.markdown(result, unsafe_allow_html=True)

                st.download_button("📥 Download Insights", result.raw, file_name="insights.md")
