import streamlit as st
from agents.workflow import run_teaching_crew
from crewai import LLM
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API")
llm = LLM(model="groq/gemma2-9b-it")

def render_agents_ui():
    st.title("🎓 CrewAI Teaching Assistant")
    st.caption("Let a team of agents teach you any topic in an organized, interactive format.")

    topic = st.text_input("📘 What would you like to learn about?", placeholder="e.g., Graph Neural Networks")

    if st.button("🚀 Teach Me!"):
        if not topic:
            st.warning("Please enter a topic.")
            return

        st.markdown("---")
        st.info("👥 Agents are working... you'll see updates as each completes.")

        # Run crew + show progress
        progress = st.progress(0)
        task_outputs = run_teaching_crew(topic, llm)


        st.success("✅ All agents have finished their tasks.")
        st.markdown("### 🧾 Your Personalized Learning Module")

        full_text = ""
        total_tasks = len(task_outputs)
        for i, step in enumerate(task_outputs):
            progress.progress((i + 1) / total_tasks)    
            
            with st.expander(f"🧠 Task {i+1}: {step['description']} ({step['agent']})"):
                st.markdown(step["output"], unsafe_allow_html=True)
                full_text += f"### {step['description']} ({step['agent']})\n\n{step['output']}\n\n"

        st.download_button("📥 Download Full Lesson", full_text, file_name=f"learn_{topic.replace(' ', '_')}.md")

        st.markdown("---")
        st.markdown("👋 **Tip:** Try entering more specific or niche topics for better results.")
