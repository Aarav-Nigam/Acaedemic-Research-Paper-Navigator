import fitz  # PyMuPDF
import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def extract_references(pdf_path: str, search_sections: List[str] = None) -> List[str]:
    """
    Extract references from a PDF file with improved accuracy.
    
    Args:
        pdf_path: Path to the PDF file
        search_sections: List of section names to search for
    
    Returns:
        List of reference strings
    """
    if search_sections is None:
        search_sections = ["References", "Bibliography", "Works Cited", "Literature Cited"]
    
    try:
        doc = fitz.open(pdf_path)
        references = []
        reference_section_found = False
        reference_text = ""
        
        # First pass: find reference sections
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            # Check if this page contains a reference section
            for section_name in search_sections:
                # Look for section headers
                patterns = [
                    rf"\b{section_name}\b",
                    rf"\b{section_name.upper()}\b",
                    rf"\b{section_name.lower()}\b"
                ]
                
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        reference_section_found = True
                        logger.info(f"Found {section_name} section on page {page_num + 1}")
                        break
                
                if reference_section_found:
                    break
            
            # If we found a reference section, collect text from this page onwards
            if reference_section_found:
                reference_text += text + "\n"
        
        if not reference_section_found:
            logger.warning("No reference section found. Searching entire document...")
            # Fallback: search the entire document
            for page in doc:
                reference_text += page.get_text() + "\n"
        
        doc.close()
        
        # Extract individual references
        references = parse_reference_text(reference_text, search_sections)
        
        return references
        
    except Exception as e:
        logger.error(f"Error extracting references from {pdf_path}: {str(e)}")
        return []

def parse_reference_text(text: str, search_sections: List[str]) -> List[str]:
    """
    Parse reference text to extract individual citations.
    
    Args:
        text: Full text containing references
        search_sections: Section names to help with parsing
    
    Returns:
        List of individual reference strings
    """
    references = []
    
    # Split text into lines
    lines = text.split('\n')
    
    # Find the start of the reference section
    ref_start_idx = 0
    for i, line in enumerate(lines):
        for section_name in search_sections:
            if re.search(rf"\b{section_name}\b", line, re.IGNORECASE):
                ref_start_idx = i + 1
                break
        if ref_start_idx > 0:
            break
    
    # Extract references from the reference section
    ref_lines = lines[ref_start_idx:]
    
    # Method 1: Look for numbered references [1], [2], etc.
    numbered_refs = extract_numbered_references(ref_lines)
    if numbered_refs:
        references.extend(numbered_refs)
    
    # Method 2: Look for author-year patterns
    if not references:
        author_year_refs = extract_author_year_references(ref_lines)
        references.extend(author_year_refs)
    
    # Method 3: Look for DOI/URL patterns
    if not references:
        doi_refs = extract_doi_references(ref_lines)
        references.extend(doi_refs)
    
    # Method 4: Fallback - split by periods and filter
    if not references:
        period_refs = extract_period_separated_references(ref_lines)
        references.extend(period_refs)
    
    # Clean and validate references
    references = clean_references(references)
    
    return references

def extract_numbered_references(lines: List[str]) -> List[str]:
    """Extract references with numbered format like [1], (1), 1., etc."""
    references = []
    current_ref = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line starts with a number pattern
        if re.match(r'^\[\d+\]|\(\d+\)|\d+\.|^\d+\s', line):
            if current_ref:
                references.append(current_ref.strip())
            current_ref = line
        else:
            # Continuation of previous reference
            if current_ref:
                current_ref += " " + line
    
    # Add the last reference
    if current_ref:
        references.append(current_ref.strip())
    
    return references

def extract_author_year_references(lines: List[str]) -> List[str]:
    """Extract references in author-year format."""
    references = []
    current_ref = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Look for author-year pattern at the beginning
        if re.match(r'^[A-Z][a-z]+,?\s+[A-Z]\.?.*\(\d{4}\)', line):
            if current_ref:
                references.append(current_ref.strip())
            current_ref = line
        else:
            if current_ref:
                current_ref += " " + line
    
    if current_ref:
        references.append(current_ref.strip())
    
    return references

def extract_doi_references(lines: List[str]) -> List[str]:
    """Extract references containing DOI or arXiv patterns."""
    references = []
    current_ref = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Look for DOI or arXiv patterns
        if re.search(r'doi:|arxiv:|https?://', line, re.IGNORECASE):
            if current_ref:
                references.append(current_ref.strip())
            current_ref = line
        else:
            if current_ref:
                current_ref += " " + line
            elif re.search(r'\b(19|20)\d{2}\b', line):  # Has a year
                current_ref = line
    
    if current_ref:
        references.append(current_ref.strip())
    
    return references

def extract_period_separated_references(lines: List[str]) -> List[str]:
    """Fallback method: split by periods and filter likely references."""
    text = " ".join(lines)
    
    # Split by periods, but be careful about abbreviations
    sentences = re.split(r'\.(?=\s+[A-Z])', text)
    
    references = []
    for sentence in sentences:
        sentence = sentence.strip()
        
        # Filter likely references
        if (len(sentence) > 50 and  # Reasonable length
            re.search(r'\b(19|20)\d{2}\b', sentence) and  # Contains a year
            (re.search(r'[a-z]\s+[A-Z]', sentence) or  # Contains author-like patterns
             re.search(r'doi:|arxiv:|journal|conference|proceedings', sentence, re.IGNORECASE))):
            references.append(sentence)
    
    return references

def clean_references(references: List[str]) -> List[str]:
    """Clean and validate reference strings."""
    cleaned = []
    
    for ref in references:
        ref = ref.strip()
        
        # Skip if too short or too long
        if len(ref) < 20 or len(ref) > 2000:
            continue
        
        # Skip if doesn't look like a reference
        if not re.search(r'[a-zA-Z]', ref):  # Must contain letters
            continue
        
        # Remove excessive whitespace
        ref = re.sub(r'\s+', ' ', ref)
        
        # Remove common artifacts
        ref = re.sub(r'^\d+\s*', '', ref)  # Remove leading numbers
        ref = re.sub(r'^\[\d+\]\s*', '', ref)  # Remove [1] style prefixes
        
        cleaned.append(ref)
    
    return cleaned
