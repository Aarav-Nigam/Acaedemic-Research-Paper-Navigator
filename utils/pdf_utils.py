import os
import fitz  # PyMuPDF
import requests
import arxiv
import shutil
import re
from datetime import datetime

def save_uploaded_pdf(uploaded_file, user_dir):
    """Save uploaded PDF to user-specific directory"""
    pdf_dir = os.path.join(user_dir, "pdfs")
    os.makedirs(pdf_dir, exist_ok=True)
    
    path = os.path.join(pdf_dir, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.read())
    return path

def sanitize_filename(name):
    """Sanitize the filename to remove or replace invalid characters."""
    # Remove characters that are not allowed in filenames
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    # Optionally, replace spaces with underscores
    name = name.strip().replace(" ", "_")
    return name

def fetch_arxiv_pdf(arxiv_id, user_dir):
    """Fetch PDF from arXiv and save to user-specific directory with paper title as filename"""
    try:
        search = arxiv.Search(id_list=[arxiv_id])
        result = next(search.results())


        pdf_url = result.pdf_url or f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        
        metadata = {
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "abstract": result.summary,
            "published": result.published.strftime("%Y-%m-%d")
        }

        response = requests.get(pdf_url)
        response.raise_for_status()

        paper_name = sanitize_filename(result.title)
        filename = f"{paper_name}.pdf"
        pdf_dir = os.path.join(user_dir, "pdfs")
        os.makedirs(pdf_dir, exist_ok=True)
        path = os.path.join(pdf_dir, filename)
        
        with open(path, "wb") as f:
            f.write(response.content)
        
        return path, metadata

    except Exception as e:
        print("ArXiv fetch error:", e)
        return None, None


def extract_metadata(path):
    """Basic metadata extraction using PyMuPDF"""
    doc = fitz.open(path)
    text = doc[0].get_text() if doc.page_count > 0 else ""
    metadata = doc.metadata
    return {
        "title": metadata.get("title", ""),
        "authors": metadata.get("author", ""),
        "first_page_text": text[:1000]  # first 1000 chars
    }

def cleanup_user_data(user_session_id):
    """Clean up all data for a specific user session"""
    user_dir = os.path.join("data", "temp_sessions", user_session_id)
    if os.path.exists(user_dir):
        try:
            shutil.rmtree(user_dir)
            print(f"Cleaned up user session: {user_session_id}")
        except Exception as e:
            print(f"Error cleaning up user session {user_session_id}: {e}")

def cleanup_old_sessions(max_age_hours=24):
    """Clean up sessions older than max_age_hours"""
    sessions_dir = os.path.join("data", "temp_sessions")
    if not os.path.exists(sessions_dir):
        return
    
    import time
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for session_id in os.listdir(sessions_dir):
        session_path = os.path.join(sessions_dir, session_id)
        if os.path.isdir(session_path):
            # Check if session is older than max_age
            creation_time = os.path.getctime(session_path)
            if current_time - creation_time > max_age_seconds:
                try:
                    shutil.rmtree(session_path)
                    print(f"Cleaned up old session: {session_id}")
                except Exception as e:
                    print(f"Error cleaning up old session {session_id}: {e}")

