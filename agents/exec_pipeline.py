from crewai import LLM
from agents.roles import get_agents

import os
from dotenv import load_dotenv

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API")
llm = LLM(model="groq/gemma2-9b-it")


def run_scout_agent(topic):
    scout, *_ = get_agents(llm)
    return scout.kickoff(f"Search for 5 recent arXiv papers on {topic}")

def run_summarizer_agent(paper_content):
    _, summarizer, *_ = get_agents(llm)
    return summarizer.kickoff(f"Summarize this paper:\n\n{paper_content}")

def run_qa_agent(question, context):
    *_, qa, _ = get_agents(llm)
    return qa.kickoff(f"Answer the question: '{question}' based on:\n\n{context}")

def run_curator_agent(topic):
    *_, curator = get_agents(llm)
    return curator.kickoff(f"Build a citation graph for papers on {topic}")
