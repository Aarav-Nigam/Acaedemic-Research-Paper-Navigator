import streamlit as st
from agents.workflow import run_demo_crew
from crewai import  LLM



import os
from dotenv import load_dotenv
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API")
llm = LLM(model="groq/gemma2-9b-it")


def render_agents_ui():
    st.title("🤖 CrewAI Multi-Agent Research Assistant")

    if st.button("🚀 Run CrewAI Demo"):
        with st.spinner("Running agents..."):
            
            output = run_demo_crew(llm)
            st.markdown("### ✅ Output from Crew")
            st.code(output)
