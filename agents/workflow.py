from crewai import Crew
from agents.roles import get_agents

def run_demo_crew(llm):
    scout, summarizer, qa, curator = get_agents(llm)

    crew = Crew(
        agents=[scout, summarizer, qa, curator],
        tasks=[
            {
                "description": "Scout for 5 recent academic papers on LLM Interpretability.",
                "agent": scout,
                "input": "LLM Interpretability",
                "expected_output": "List of 5 recent arXiv papers"
            },
            {
                "description": "Summarize the 5 papers retrieved by the Scout Agent.",
                "agent": summarizer,
                "depends_on": scout,
                "expected_output": "Summary of those 5 papers"
            },
            {
                "description": "Answer common questions about the summarized papers.",
                "agent": qa,
                "depends_on": summarizer,
                "expected_output": "Answers to 3 common questions about LLM interpretability"
            },
            {
                "description": "Create a citation graph based on the papers found by the Scout Agent.",
                "agent": curator,
                "depends_on": scout,
                "expected_output": "Citation graph of those 5 papers"
            }
        ],
        verbose=True
    )

    result = crew.kickoff()
    return result
