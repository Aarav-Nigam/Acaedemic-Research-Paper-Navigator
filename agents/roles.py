from crewai import Agent

def get_agents(llm):
    """
    Creates and returns a tuple of CrewAI agents:
    Scout Agent, Summarizer Agent, Q&A Agent, and Map Curator Agent.
    Each agent is assigned a clear role, goal, and backstory.
    """

    # Agent 1: Scout Agent
    # Purpose: Find relevant academic papers from arXiv or other sources
    scout_agent = Agent(
        role="Scout Agent",
        goal="Identify and fetch the most relevant academic papers for a given research topic or keyword.",
        backstory=(
            "A highly experienced academic researcher who knows how to efficiently navigate arXiv, "
            "Semantic Scholar, and other APIs to find papers that are most relevant and recent. "
            "Has a keen understanding of keywords, citation trends, and domain relevance."
        ),
        tools=[],  # You can add tools like arXiv API wrappers here
        verbose=True,
        llm=llm
    )

    # Agent 2: Summarizer Agent
    # Purpose: Generate concise summaries and TL;DR for selected papers
    summarizer_agent = Agent(
        role="Summarizer Agent",
        goal="Summarize research papers, extract their key findings, and present clear TL;DR sections.",
        backstory=(
            "A scientific writer trained in reading and distilling academic content quickly. "
            "Can parse complex scientific language into digestible points without losing meaning. "
            "Useful for researchers and students needing quick insights into papers."
        ),
        tools=[],  # Add tools for text summarization or PDF parsing if available
        verbose=True,
        llm=llm
    )

    # Agent 3: Q&A Agent
    # Purpose: Answer questions related to specific papers using a RAG pipeline
    qa_agent = Agent(
        role="Q&A Agent",
        goal="Provide detailed, context-aware answers to user questions based on specific research papers.",
        backstory=(
            "An expert in natural language understanding and retrieval-augmented generation. "
            "Combines retrieval techniques and language models to answer complex questions about academic content."
        ),
        tools=[],  # Optionally include vector store or retrieval tools
        verbose=True,
        llm=llm
    )

# Agent 4: Insight Generator Agent
    insight_agent = Agent(
        role="Insight Generator",
        goal="Generate key insights, emerging trends, and challenges from a set of academic papers.",
        backstory=(
            "A research analyst with expertise in identifying patterns across academic literature. "
            "Highlights new trends, common challenges, and noteworthy research directions."
        ),
        tools=[],  # Could later integrate NLP/statistical tools
        verbose=True,
        llm=llm
    )

    return scout_agent, summarizer_agent, qa_agent, insight_agent
