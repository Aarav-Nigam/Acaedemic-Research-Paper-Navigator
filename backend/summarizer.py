
# Updated backend/summarizer.py
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

def summarize_text(text, custom_prompt=""):
    """Generate summary using Groq API with optional custom prompt"""
    try:
        llm = ChatGroq(
            model="qwen/qwen/qwen3-32b",
            groq_api_key=os.getenv("GROQ_API"),
            temperature=0.3
        )
        
        base_prompt = f"""
        {custom_prompt if custom_prompt else 'Please provide a comprehensive summary of the following document(s).'}
        
        Focus on:
        1. Main topics and themes
        2. Key findings and insights
        3. Important conclusions
        4. Significant data or results
        
        Document(s) to summarize:
        {text[:8000]}  # Limit text to avoid token limits
        """
        
        response = llm.invoke(base_prompt)
        return response.content
        
    except Exception as e:
        return f"Error generating summary: {str(e)}"