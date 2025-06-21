import requests
import time
import logging
from typing import Dict, Any, Optional, List
import urllib.parse

logger = logging.getLogger(__name__)

class SemanticScholarAPI:
    """Enhanced Semantic Scholar API client with rate limiting and retry logic."""
    
    def __init__(self):
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_interval = 0.1  # Minimum time between requests (100ms)
    
    def _rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_interval:
            time.sleep(self.min_interval - time_since_last)
        self.last_request_time = time.time()
    
    def search_paper(self, query: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Search for a paper using Semantic Scholar API.
        
        Args:
            query: Search query (title, DOI, or other identifier)
            max_retries: Maximum number of retry attempts
        
        Returns:
            Paper metadata or None if not found
        """
        # Clean and encode the query
        query = query.strip()
        if not query:
            return None
        
        # Try different search strategies
        search_strategies = [
            self._search_by_title,
            self._search_by_doi,
            self._search_by_partial_title
        ]
        
        for strategy in search_strategies:
            try:
                result = strategy(query, max_retries)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Search strategy failed: {str(e)}")
                continue
        
        return None
    
    def _search_by_title(self, query: str, max_retries: int) -> Optional[Dict[str, Any]]:
        """Search by full title."""
        # Extract potential title from the query
        title = self._extract_title(query)
        if not title or len(title) < 10:
            return None
        
        return self._make_search_request(title, max_retries)
    
    def _search_by_doi(self, query: str, max_retries: int) -> Optional[Dict[str, Any]]:
        """Search by DOI if present."""
        import re
        doi_match = re.search(r'10\.\d{4,}[^\s]*', query)
        if doi_match:
            doi = doi_match.group()
            return self._make_search_request(f"DOI:{doi}", max_retries)
        return None
    
    def _search_by_partial_title(self, query: str, max_retries: int) -> Optional[Dict[str, Any]]:
        """Search by partial title (first few words)."""
        title = self._extract_title(query)
        if not title:
            return None
        
        # Take first 5-8 words for partial search
        words = title.split()[:6]
        partial_title = " ".join(words)
        
        if len(partial_title) > 15:  # Ensure minimum length
            return self._make_search_request(partial_title, max_retries)
        return None
    
    def _extract_title(self, citation_text: str) -> str:
        """Extract title from citation text."""
        import re
        
        
        # Common title patterns
        title_patterns = [
            r'"([^"]+)"',  # Double quoted title
            r"'([^']+)'",  # Single quoted title
            r'\.([^.]{20,})\.',  # Between periods, reasonable length
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, citation_text)
            if match:
                title = match.group(1).strip()
                # Filter out years and other non-title text
                if not re.match(r'^\d{4}', title) and len(title) > 10:
                    return title
        
        # Fallback: try to extract from the beginning after author names
        parts = citation_text.split('.')
        for part in parts[1:3]:  # Skip first part (likely authors), check next 2
            part = part.strip()
            if 20 < len(part) < 200 and not re.search(r'^\d{4}', part):
                return part
        
        return ""
    
    def _make_search_request(self, query: str, max_retries: int) -> Optional[Dict[str, Any]]:
        """Make the actual API request with retry logic."""
        fields = "title,authors,year,citationCount,externalIds,venue,abstract,url"
        encoded_query = urllib.parse.quote(query)
        url = f"{self.base_url}/paper/search?query={encoded_query}&limit=1&fields={fields}"
        
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("data") and len(data["data"]) > 0:
                        paper = data["data"][0]
                        return self._format_paper_data(paper)
                elif response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.warning(f"API request failed with status {response.status_code}")
                    break
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                break
        
        return None
    
    def _format_paper_data(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """Format paper data from API response."""
        formatted = {
            "title": paper.get("title", ""),
            "authors": paper.get("authors", []),
            "year": paper.get("year"),
            "citationCount": paper.get("citationCount", 0),
            "externalIds": paper.get("externalIds", {}),
            "venue": paper.get("venue", ""),
            "abstract": paper.get("abstract", ""),
            "url": paper.get("url", "")
        }
        
        # Clean up authors format
        if formatted["authors"]:
            formatted["authors"] = [
                {"name": author.get("name", "")} for author in formatted["authors"]
                if author.get("name")
            ]
        
        return formatted

# Global API instance
_semantic_scholar_api = SemanticScholarAPI()

def fetch_metadata_from_semantic_scholar(citation_text: str) -> Optional[Dict[str, Any]]:
    """
    Fetch metadata for a citation from Semantic Scholar.
    
    Args:
        citation_text: Raw citation text
    
    Returns:
        Paper metadata or None if not found
    """
    try:
        return _semantic_scholar_api.search_paper(citation_text)
    except Exception as e:
        logger.error(f"Error fetching metadata: {str(e)}")
        return None

def batch_fetch_metadata(citations: List[str], max_concurrent: int = 5) -> List[Optional[Dict[str, Any]]]:
    """
    Fetch metadata for multiple citations with controlled concurrency.
    
    Args:
        citations: List of citation texts
        max_concurrent: Maximum concurrent requests
    
    Returns:
        List of metadata dictionaries (or None for failed requests)
    """
    import concurrent.futures
    import threading
    
    results = []
    
    # Process in batches to control concurrency
    batch_size = max_concurrent
    for i in range(0, len(citations), batch_size):
        batch = citations[i:i + batch_size]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            future_to_citation = {
                executor.submit(fetch_metadata_from_semantic_scholar, citation): citation
                for citation in batch
            }
            
            for future in concurrent.futures.as_completed(future_to_citation):
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error processing citation: {str(e)}")
                    results.append(None)
        
        # Add delay between batches
        if i + batch_size < len(citations):
            time.sleep(1)
    
    return results