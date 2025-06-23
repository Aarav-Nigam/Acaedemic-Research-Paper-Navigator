from crewai import Crew
from agents.roles import get_agents

def run_teaching_crew(topic: str, llm):
    scout, summarizer, qa, insight = get_agents(llm)

    crew = Crew(
        agents=[scout, summarizer, qa, insight],
        tasks=[
            {
                "description": f"Find 5 recent academic papers or blogs about {topic}.",
                "agent": scout,
                "input": topic,
                "expected_output": "List of resources"
            },
            {
                "description": f"Summarize the materials found on {topic}.",
                "agent": summarizer,
                "depends_on": scout,
                "expected_output": "Concise summary and key ideas"
            },
            {
                "description": f"Simulate 3 common student questions about {topic} and answer them.",
                "agent": qa,
                "depends_on": summarizer,
                "expected_output": "Detailed Q&A"
            },
            {
                "description": f"Extract key insights and trends for {topic}.",
                "agent": insight,
                "depends_on": summarizer,
                "expected_output": "Takeaways and future directions"
            },
        ],
        verbose=True,
        return_intermediate_steps=True
    )

    crew_output = crew.kickoff()
    task_outputs = []
    for step in crew_output.tasks_output:
        task_outputs.append({
            "description": step.description,
            "agent": getattr(step, "agent", "Unknown Agent"),
            "output": step.raw  # You could also use step.summary
        })

    return task_outputs
