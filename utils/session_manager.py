import os
import time
import threading
from utils.pdf_utils import cleanup_old_sessions

class SessionManager:
    """Manages user sessions and periodic cleanup"""
    
    def __init__(self, cleanup_interval_minutes=60, max_session_age_hours=24):
        self.cleanup_interval = cleanup_interval_minutes * 60
        self.max_session_age = max_session_age_hours
        self.cleanup_thread = None
        self.running = False
        self.session_pdfs = {}  # Track PDFs per session
    
    def start_cleanup_service(self):
        """Start background cleanup service"""
        if not self.running:
            self.running = True
            self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.cleanup_thread.start()
    
    def stop_cleanup_service(self):
        """Stop background cleanup service"""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join()
    
    def _cleanup_loop(self):
        """Background cleanup loop"""
        while self.running:
            try:
                cleanup_old_sessions(self.max_session_age)
            except Exception as e:
                print(f"Cleanup error: {e}")
            time.sleep(self.cleanup_interval)
    
    def get_session_pdfs(self, session_id):
        """Get list of PDFs for a session"""
        user_dir = os.path.join("data", "temp_sessions", session_id)
        pdf_dir = os.path.join(user_dir, "pdfs")
        
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir, exist_ok=True)
            return []
        
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        return sorted(pdf_files)
    
    def add_pdf_to_session(self, session_id, pdf_name):
        """Track a new PDF in the session"""
        if session_id not in self.session_pdfs:
            self.session_pdfs[session_id] = set()
        self.session_pdfs[session_id].add(pdf_name)
    
    def remove_pdf_from_session(self, session_id, pdf_name):
        """Remove PDF from session tracking and filesystem"""
        user_dir = os.path.join("data", "temp_sessions", session_id)
        pdf_path = os.path.join(user_dir, "pdfs", pdf_name)
        
        # Remove from filesystem
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        
        # Remove from tracking
        if session_id in self.session_pdfs and pdf_name in self.session_pdfs[session_id]:
            self.session_pdfs[session_id].remove(pdf_name)
        
        return True
    
    def get_pdf_count(self, session_id):
        """Get current PDF count for session"""
        return len(self.get_session_pdfs(session_id))

# Initialize session manager
session_manager = SessionManager()
session_manager.start_cleanup_service()