from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


from dotenv import load_dotenv
import os

load_dotenv()

os.environ["GROQ_API"] = os.getenv("GROQ_API")

def summarize_text(text, model="gpt-4"):
    llm = ChatGroq(model="qwen-qwq-32b", groq_api_key=os.environ["GROQ_API"], temperature=0.7)

    prompt = PromptTemplate.from_template("""
You are a helpful academic assistant. Given a scientific paper's text, extract the following:
1. 📌 TL;DR summary (3-5 bullet points)
2. 🧠 Key contributions
3. ⚠️ Limitations
4. 📢 Major claims (starting with phrases like "We propose", "Our results show", etc.)

Text:
{text}

Respond clearly using markdown formatting.
""")

    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.run(text=text[:8000])  # Token-safe limit
    return result
