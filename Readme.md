
# 📚 Academic Research Paper Navigator

> *"Chat with papers, map ideas, and accelerate your lit review."*

## 🚀 Overview

**Academic Research Paper Navigator** is an intelligent assistant for researchers, students, and academic professionals. It allows users to upload or fetch research papers (PDFs or arXiv links), get auto-generated summaries, visualize citation-based idea maps, and interact with papers using semantic Q\&A—all while curating personal insights over time.

### 🔍 Core Features

* **📄 Paper Ingestion**

  * Upload PDFs or fetch directly from [arXiv API](https://arxiv.org/help/api/index).
  * Extract metadata (title, authors, abstract, publication date).
  * Identify and highlight sections (Abstract, Methodology, Results, etc.) using NLP heuristics.

* **🧠 Semantic Search + Q\&A (via RAG)**

  * Build a vector index from paper content using **ChromaDB** or **FAISS**.
  * Ask research-specific questions (e.g., "What is the main contribution?" or "How does it compare with XYZ?").
  * Uses **LangChain** with models like **OpenAI GPT**, **Mistral**, or **Phi-3** for reasoning.

* **🗺️ Citation-Based Mind Mapping**

  * Extract citations using **PyMuPDF** or **Grobid**.
  * Construct a **temporal knowledge graph** using **NetworkX** and visualize it with **PyVis**, **D3.js**, or **Mermaid.js**.
  * Highlight thematic clusters (e.g., foundational papers vs. recent breakthroughs).

* **👥 CrewAI Agents for Modular Research Tasks**

  * 📚 **Literature Scout Agent**: Fetches related papers based on topic keywords.
  * 📝 **Summarizer Agent**: Generates concise TL;DR, highlights limitations, and contributions.
  * 🤖 **Q\&A Tutor Agent**: Answers technical questions from paper using semantic retrieval.
  * 🧠 **Insight Archivist Agent**: Stores personalized notes and highlights.
  * 🔄 **Updater Agent**: Checks for newer papers or citations weekly (like a mini research digest).

* **🧑‍🎓 Personalization**

  * Users can embed their own notes and have the system learn from preferences (e.g., preferred topics, authors).
  * Track "read" vs "to-read" papers.
  * Tagging system for organizing ideas, authors, journals.

* **🧪 Experimental Features**

  * Claim extraction using factuality-check LLMs (extracting statements like "We propose..." or "Our results show\...").
  * Paper-to-slide generator: Convert key content into a presentation outline (using markdown/PPTX generation).
  * GPT/phi-based dialogue agents simulating the paper’s authors or peer reviewers.

---

## 🔧 Tech Stack

| Area                | Tools                                                                                   |
| ------------------- | --------------------------------------------------------------------------------------- |
| **Frontend**        | Streamlit                                                                               |
| **PDF Parsing**     | PyMuPDF / pdfminer.six / Grobid                                                         |
| **Paper Fetching**  | arXiv API, Semantic Scholar API (for metadata enrichment)                               |
| **RAG Pipeline**    | LangChain, ChromaDB / FAISS, HuggingFace Embeddings                                     |
| **LLMs**            | OpenAI GPT-4, Mistral, Phi-3, Mixtral                                                   |
| **Agent Framework** | CrewAI                                                                                  |
| **Visualization**   | NetworkX, PyVis, Mermaid.js, D3.js                                                      |
| **Storage**         | Local Storage                                                                           |
| **Deployment**      | Streamlit Community Cloud                                                               |

---

## 💡 Use Cases

| User                        | Scenario                                                                                                        |
| --------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 🎓 **Graduate Student**     | Needs a quick grasp of a dozen papers for a seminar next week. Uses summarizer + mind maps to identify overlap. |
| 📖 **Undergrad Researcher** | Uses Q\&A agent to ask "Why does this method outperform BERT?" in a dense NLP paper.                            |
| 🔬 **Postdoc**              | Tracks a topic over time—uses the citation mind map to watch how ideas evolve over years.                       |
| 🧑‍🏫 **Professor**         | Uses it as a tool to recommend curated readings to students and maintain annotated collections.                 |
| ✍️ **Science Communicator** | Auto-generates summaries + slides for recent papers for public-friendly newsletters.                            |

---

## 💡 Future Additions (Stretch Goals)

* 🌐 **Multilingual Paper Support** — Translate and process papers in languages like Chinese, German.
* 🧩 **Plugin Ecosystem** — Enable users to contribute modules (e.g., “Compare 2 papers”, “Detect novelty”, etc).
* 📥 **BibTeX Import** — Bulk fetch and process from .bib files.
* 📊 **Methodology Visualizer** — Parse and visualize methods or experimental setups.
* 🔍 **Paper Similarity Explorer** — "Find me 10 papers like this" based on embedding distance.

---

## 🆓 Philosophy & License

The tool is designed to remain **free** for students, researchers, and the broader academic community. MIT license or AGPL preferred to ensure future openness. You are encouraged to contribute or fork it to suit niche use cases!

---

# ⚡️ Project Status & Implementation Notes

This project is an early-stage prototype focused on core research paper navigation features. The following reflects what is currently implemented and used:

- **PDF Upload & Metadata Extraction:**  
  Users can upload PDFs. Metadata (title, authors, abstract) is extracted using **PyMuPDF** and basic regex heuristics.

- **arXiv Fetching:**  
  Fetching via [arXiv API](https://arxiv.org/help/api/index) is supported for metadata and PDF download.

- **Section Highlighting:**  
  Basic section detection (Abstract, Introduction, etc.) is implemented using simple text matching.

- **Semantic Search & Q\&A:**  
  A minimal **RAG** pipeline is set up using **ChromaDB** for vector storage and **OpenAI GPT-3.5** for Q\&A.  
  (No support yet for Mistral, Phi-3, or HuggingFace models.)

- **Citation Extraction:**  
  Citations are extracted from PDFs using **PyMuPDF**.  
  (No Grobid integration yet.)

- **Visualization:**  
  Citation graphs are visualized using **NetworkX** and **PyVis**.  
  (No D3.js or Mermaid.js support yet.)

- **Agents:**  
  Modular agent logic is planned but not yet implemented.  
  (No CrewAI integration yet.)

- **Personalization:**  
  Users can add notes and tag papers.  
  (No learning from preferences or advanced tracking.)

- **Experimental Features:**  
  Not yet implemented (e.g., claim extraction, slide generator, dialogue agents).

- **Tech Stack Used:**  
  - **Frontend:** Streamlit  
  - **PDF Parsing:** PyMuPDF  
  - **Paper Fetching:** arXiv API  
  - **RAG Pipeline:** ChromaDB, OpenAI GPT-3.5  
  - **Visualization:** NetworkX, PyVis  
  - **Storage:** Local file system  
  - **Deployment:** Streamlit Community Cloud

**Note:**  
Many features listed below are aspirational or in-progress. See issues and roadmap for current development status.