from utils.citations import extract_references
from utils.metadata_enrich import fetch_metadata_from_semantic_scholar
import logging
from typing import List, Dict, Any
import time


# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def get_citation_metadata(pdf_path: str, max_citations: int = 20, 
                         include_metadata: bool = True, 
                         search_sections: List[str] = None) -> List[Dict[str, Any]]:
    """
    Extract and enrich citation metadata from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        max_citations: Maximum number of citations to process
        include_metadata: Whether to enrich with external metadata
        search_sections: List of section names to search for citations
    
    Returns:
        List of citation dictionaries with metadata
    """
    if search_sections is None:
        search_sections = ["References", "Bibliography"]
    
    try:
        logger.info(f"Extracting references from {pdf_path}")
        raw_refs = extract_references(pdf_path, search_sections=search_sections)
        
        if not raw_refs:
            logger.warning("No references found in the PDF")
            return []
        
        logger.info(f"Found {len(raw_refs)} raw references")
        
        # Limit the number of citations to process
        raw_refs = raw_refs[:max_citations]
        enriched = []
        
        for i, ref in enumerate(raw_refs):
            logger.info(f"Processing citation {i+1}/{len(raw_refs)}")
            
            citation_data = {
                "raw_text": ref,
                "processed_index": i + 1
            }
            
            if include_metadata:
                try:
                    # Add a small delay to respect API rate limits
                    if i > 0:
                        time.sleep(0.5)
                    
                    metadata = fetch_metadata_from_semantic_scholar(ref)
                    if metadata:
                        citation_data.update(metadata)
                        logger.info(f"Enriched citation {i+1} with metadata")
                    else:
                        # Try to extract basic info from raw text if API fails
                        basic_info = extract_basic_citation_info(ref)
                        citation_data.update(basic_info)
                        logger.warning(f"Could not enrich citation {i+1}, using basic extraction")
                        
                except Exception as e:
                    logger.error(f"Error enriching citation {i+1}: {str(e)}")
                    # Fallback to basic extraction
                    basic_info = extract_basic_citation_info(ref)
                    citation_data.update(basic_info)
            else:
                # Just extract basic info without external API calls
                basic_info = extract_basic_citation_info(ref)
                citation_data.update(basic_info)
            
            enriched.append(citation_data)
        
        logger.info(f"Successfully processed {len(enriched)} citations")
        return enriched
        
    except Exception as e:
        logger.error(f"Error processing citations from {pdf_path}: {str(e)}")
        raise

def extract_basic_citation_info(citation_text: str) -> Dict[str, Any]:
    """
    Extract basic information from a citation string using regex patterns.
    
    Args:
        citation_text: Raw citation text
    
    Returns:
        Dictionary with basic citation information
    """
    import re
    
    info = {
        "title": "",
        "authors": [],
        "year": None,
        "venue": ""
    }
    
    # Try to extract year (4-digit number, typically in parentheses or at start/end)
    year_pattern = r'\b(19|20)\d{2}\b'
    year_match = re.search(year_pattern, citation_text)
    if year_match:
        try:
            info["year"] = int(year_match.group())
        except ValueError:
            pass
    
    # Try to extract title (usually in quotes or after authors before year)
    title_patterns = [
        r'"([^"]+)"',  # Quoted title
        r"'([^']+)'",  # Single quoted title
        r'\.([^.]+)\.',  # Between periods
    ]
    
    for pattern in title_patterns:
        title_match = re.search(pattern, citation_text)
        if title_match:
            potential_title = title_match.group(1).strip()
            # Filter out obviously non-title text
            if len(potential_title) > 10 and not re.match(r'^\d+$', potential_title):
                info["title"] = potential_title
                break
    
    # If no title found, try to extract the first substantial part
    if not info["title"]:
        # Remove common prefixes and split by periods
        cleaned = re.sub(r'^\[\d+\]\s*', '', citation_text)  # Remove [1] style prefixes
        parts = cleaned.split('.')
        for part in parts:
            part = part.strip()
            if len(part) > 20 and not re.match(r'^\d{4}$', part):  # Not just a year
                info["title"] = part
                break
    
    # Try to extract authors (usually at the beginning, before title or year)
    # This is more complex and error-prone, so we'll do a simple extraction
    author_part = citation_text.split('.')[0] if '.' in citation_text else citation_text[:100]
    # Remove citation numbers and clean up
    author_part = re.sub(r'^\[\d+\]\s*', '', author_part)
    
    # Look for comma-separated names (simplified)
    if ',' in author_part and len(author_part) < 200:  # Reasonable length for author list
        potential_authors = [name.strip() for name in author_part.split(',')]
        # Filter out obviously non-author text
        authors = []
        for author in potential_authors[:5]:  # Limit to first 5 potential authors
            if len(author) > 1 and not re.search(r'\d{4}', author):  # No years in author names
                authors.append({"name": author})
        if authors:
            info["authors"] = authors
    
    # Extract venue/journal (this is quite challenging from raw text)
    # Look for common journal patterns
    venue_patterns = [
        r'(?:In |in )?([A-Z][^,\.]+(?:Journal|Conference|Proceedings|Review|Letters))',
        r'(?:In |in )?([A-Z][^,\.]+(?:ACM|IEEE|Nature|Science))',
    ]
    
    for pattern in venue_patterns:
        venue_match = re.search(pattern, citation_text)
        if venue_match:
            info["venue"] = venue_match.group(1).strip()
            break
    
    return info

def validate_citation_data(citation: Dict[str, Any]) -> bool:
    """
    Validate that a citation has minimum required data.
    
    Args:
        citation: Citation dictionary
    
    Returns:
        True if citation has valid data
    """
    return bool(
        citation.get("title") or 
        citation.get("authors") or 
        citation.get("raw_text")
    )

def deduplicate_citations(citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate citations based on title similarity.
    
    Args:
        citations: List of citation dictionaries
    
    Returns:
        Deduplicated list of citations
    """
    from difflib import SequenceMatcher
    
    def similar(a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio() > 0.85
    
    deduplicated = []
    
    for citation in citations:
        title = citation.get("title", "")
        if not title:
            deduplicated.append(citation)
            continue
        
        is_duplicate = False
        for existing in deduplicated:
            existing_title = existing.get("title", "")
            if existing_title and similar(title, existing_title):
                is_duplicate = True
                break
        
        if not is_duplicate:
            deduplicated.append(citation)
    
    return deduplicated