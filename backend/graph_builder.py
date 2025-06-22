import networkx as nx
from typing import List, Dict, Any, Optional
from collections import defaultdict
import re


def build_citation_graph(main_paper: Dict, citations: List[Dict]) -> nx.DiGraph:
    """
    Legacy function maintained for backward compatibility
    """
    return build_enhanced_citation_graph([main_paper], citations, "force-directed")


def build_enhanced_citation_graph(main_papers: List[Dict], citations: List[Dict], 
                                layout: str = "force-directed") -> nx.DiGraph:
    """
    Build an enhanced citation graph with multiple main papers and advanced features
    
    Args:
        main_papers: List of main paper dictionaries
        citations: List of citation dictionaries
        layout: Layout style for the graph
    
    Returns:
        NetworkX DiGraph with enhanced node and edge attributes
    """
    G = nx.DiGraph()
    
    # Add main paper nodes with enhanced attributes
    for i, paper in enumerate(main_papers):
        main_id = f"main_{i}"
        title = paper.get("title", f"Paper {i+1}")
        
        G.add_node(
            main_id,
            label=title,
            full_title=title,
            year=paper.get("year", "2025"),
            color="#3498db",
            size=25,
            node_type="main",
            authors=paper.get("authors", []),
            venue=paper.get("venue", ""),
            abstract=paper.get("abstract", ""),
            doi=paper.get("doi", ""),
            citation_count=len([c for c in citations if c.get("source_paper", "").replace('.pdf', '') in title])
        )
    
    # Process and deduplicate citations
    processed_citations = process_citations(citations)
    
    # Group citations by source paper for better organization
    citations_by_source = group_citations_by_source(processed_citations, main_papers)
    
    # Add citation nodes and edges
    citation_id_counter = 0
    added_citations = set()  # Track to avoid duplicates
    
    for source_idx, paper_citations in citations_by_source.items():
        main_id = f"main_{source_idx}"
        
        for citation in paper_citations:
            # Create unique identifier for citation to avoid duplicates
            citation_key = create_citation_key(citation)
            
            if citation_key in added_citations:
                # If citation already exists, just add edge from this main paper
                existing_node = find_citation_node(G, citation_key)
                if existing_node:
                    G.add_edge(main_id, existing_node)
                continue
            
            added_citations.add(citation_key)
            cited_id = f"cited_{citation_id_counter}"
            
            # Enhanced citation node attributes
            node_attrs = create_citation_node_attributes(citation, cited_id)
            G.add_node(cited_id, **node_attrs)
            
            # Add edge with metadata
            edge_attrs = create_edge_attributes(citation)
            G.add_edge(main_id, cited_id, **edge_attrs)
            
            citation_id_counter += 1
    
    # Add cross-citations between papers if they exist
    add_cross_citations(G, processed_citations)
    
    # Calculate and add graph metrics
    add_graph_metrics(G)
    
    # Apply layout-specific optimizations
    optimize_for_layout(G, layout)
    
    return G


def process_citations(citations: List[Dict]) -> List[Dict]:
    """
    Process and clean citation data
    
    Args:
        citations: Raw citation list
    
    Returns:
        Processed citation list
    """
    processed = []
    
    for citation in citations:
        # Clean and validate citation data
        cleaned = clean_citation_data(citation)
        
        if validate_citation(cleaned):
            processed.append(cleaned)
    
    # Remove duplicates based on title similarity
    return deduplicate_citations_advanced(processed)


def clean_citation_data(citation: Dict) -> Dict:
    """Clean and standardize citation data"""
    cleaned = citation.copy()
    
    # Clean title
    title = cleaned.get("title", "")
    if title:
        # Remove extra whitespace and normalize
        title = re.sub(r'\s+', ' ', title.strip())
        # Remove common prefixes/suffixes
        title = re.sub(r'^(The|A|An)\s+', '', title, flags=re.IGNORECASE)
        cleaned["title"] = title
    
    # Standardize year
    year = cleaned.get("year")
    if year:
        try:
            if isinstance(year, str):
                year_match = re.search(r'\b(19|20)\d{2}\b', year)
                if year_match:
                    cleaned["year"] = int(year_match.group())
                else:
                    cleaned["year"] = None
            elif isinstance(year, (int, float)):
                year = int(year)
                if 1900 <= year <= 2030:
                    cleaned["year"] = year
                else:
                    cleaned["year"] = None
        except (ValueError, TypeError):
            cleaned["year"] = None
    
    # Clean authors
    authors = cleaned.get("authors", [])
    if authors and isinstance(authors, list):
        cleaned_authors = []
        for author in authors:
            if isinstance(author, dict):
                name = author.get("name", "").strip()
                if name:
                    cleaned_authors.append({"name": name})
            elif isinstance(author, str):
                name = author.strip()
                if name:
                    cleaned_authors.append({"name": name})
        cleaned["authors"] = cleaned_authors
    
    # Clean venue
    venue = cleaned.get("venue", "")
    if venue:
        venue = re.sub(r'\s+', ' ', venue.strip())
        cleaned["venue"] = venue
    
    return cleaned


def validate_citation(citation: Dict) -> bool:
    """Validate that citation has minimum required data"""
    return bool(
        citation.get("title") or 
        citation.get("authors") or 
        (citation.get("raw_text") and len(citation.get("raw_text", "")) > 10)
    )


def deduplicate_citations_advanced(citations: List[Dict]) -> List[Dict]:
    """Advanced deduplication using multiple similarity metrics"""
    from difflib import SequenceMatcher
    
    def calculate_similarity(cit1: Dict, cit2: Dict) -> float:
        """Calculate similarity score between two citations"""
        scores = []
        
        # Title similarity
        title1 = cit1.get("title", "").lower()
        title2 = cit2.get("title", "").lower()
        if title1 and title2:
            title_sim = SequenceMatcher(None, title1, title2).ratio()
            scores.append(title_sim * 0.6)  # Title is most important
        
        # Author similarity
        authors1 = [a.get("name", "").lower() for a in cit1.get("authors", [])]
        authors2 = [a.get("name", "").lower() for a in cit2.get("authors", [])]
        if authors1 and authors2:
            # Check for common authors
            common_authors = set(authors1) & set(authors2)
            author_sim = len(common_authors) / max(len(authors1), len(authors2))
            scores.append(author_sim * 0.3)
        
        # Year similarity
        year1 = cit1.get("year")
        year2 = cit2.get("year")
        if year1 and year2:
            year_sim = 1.0 if year1 == year2 else 0.0
            scores.append(year_sim * 0.1)
        
        return sum(scores) if scores else 0.0
    
    deduplicated = []
    
    for citation in citations:
        is_duplicate = False
        
        for existing in deduplicated:
            similarity = calculate_similarity(citation, existing)
            if similarity > 0.8:  # High similarity threshold
                is_duplicate = True
                # Keep the citation with more complete data
                if count_non_empty_fields(citation) > count_non_empty_fields(existing):
                    deduplicated.remove(existing)
                    deduplicated.append(citation)
                break
        
        if not is_duplicate:
            deduplicated.append(citation)
    
    return deduplicated


def count_non_empty_fields(citation: Dict) -> int:
    """Count non-empty fields in citation"""
    count = 0
    for key, value in citation.items():
        if value:
            if isinstance(value, (list, dict)):
                if value:  # Non-empty list or dict
                    count += 1
            else:
                count += 1
    return count


def group_citations_by_source(citations: List[Dict], main_papers: List[Dict]) -> Dict[int, List[Dict]]:
    """Group citations by their source paper"""
    citations_by_source = defaultdict(list)
    
    for citation in citations:
        source_paper = citation.get("source_paper", "")
        
        # Find matching main paper index
        source_idx = 0  # Default to first paper
        for i, paper in enumerate(main_papers):
            paper_title = paper.get("title", "")
            if source_paper.replace('.pdf', '') in paper_title or paper_title in source_paper:
                source_idx = i
                break
        
        citations_by_source[source_idx].append(citation)
    
    return dict(citations_by_source)


def create_citation_key(citation: Dict) -> str:
    """Create unique key for citation to detect duplicates"""
    title = citation.get("title", "").lower().strip()
    year = citation.get("year", "")
    authors = citation.get("authors", [])
    
    key_parts = []
    
    if title:
        # Use first 50 characters of title
        key_parts.append(title[:50])
    
    if year:
        key_parts.append(str(year))
    
    if authors and isinstance(authors, list) and len(authors) > 0:
        first_author = authors[0]
        if isinstance(first_author, dict):
            author_name = first_author.get("name", "")
        else:
            author_name = str(first_author)
        
        if author_name:
            # Use last name
            last_name = author_name.split()[-1].lower()
            key_parts.append(last_name)
    
    return "|".join(key_parts)


def find_citation_node(G: nx.DiGraph, citation_key: str) -> Optional[str]:
    """Find existing citation node by key"""
    for node_id, attrs in G.nodes(data=True):
        if attrs.get("citation_key") == citation_key:
            return node_id
    return None


def create_citation_node_attributes(citation: Dict, node_id: str) -> Dict:
    """Create comprehensive node attributes for citation"""
    title = citation.get("title", f"Citation {node_id}")
    year = citation.get("year")
    authors = citation.get("authors", [])
    venue = citation.get("venue", "")
    
    # Determine node color based on publication year and other factors
    color_info = determine_node_color(citation)
    
    # Create display label (truncated title)
    display_label = title[:60] + "..." if len(title) > 60 else title
    
    # Calculate influence score based on available metadata
    influence_score = calculate_influence_score(citation)
    
    attrs = {
        "label": display_label,
        "full_title": title,
        "year": year,
        "color": color_info["color"],
        "size": max(8, min(20, 10 + influence_score * 2)),  # Size based on influence
        "node_type": "citation",
        "authors": authors,
        "venue": venue,
        "citation_key": create_citation_key(citation),
        "influence_score": influence_score,
        "raw_text": citation.get("raw_text", ""),
        "doi": citation.get("doi", ""),
        "url": citation.get("url", ""),
        "abstract": citation.get("abstract", ""),
        "citation_count": citation.get("citationCount", 0),
        "reference_count": citation.get("referenceCount", 0)
    }
    
    return attrs


def determine_node_color(citation: Dict) -> Dict[str, str]:
    """Determine node color based on citation attributes"""
    year = citation.get("year")
    citation_count = citation.get("citationCount", 0)
    venue = citation.get("venue", "").lower()
    
    # High-impact venues (simplified list)
    high_impact_venues = [
        "nature", "science", "cell", "nejm", "lancet", "jama",
        "neurips", "icml", "iclr", "aaai", "ijcai", "acl", "emnlp",
        "cvpr", "iccv", "eccv", "siggraph", "chi", "uist"
    ]
    
    is_high_impact = any(venue_name in venue for venue_name in high_impact_venues)
    
    if is_high_impact or citation_count > 100:
        return {"color": "#e74c3c", "category": "high_impact"}  # Red for high impact
    elif isinstance(year, int):
        if year >= 2020:
            return {"color": "#f39c12", "category": "recent"}  # Orange for recent
        elif year >= 2015:
            return {"color": "#27ae60", "category": "moderate"}  # Green for moderate
        elif year >= 2010:
            return {"color": "#3498db", "category": "older"}  # Blue for older
        else:
            return {"color": "#9b59b6", "category": "classic"}  # Purple for classic
    else:
        return {"color": "#95a5a6", "category": "unknown"}  # Gray for unknown


def calculate_influence_score(citation: Dict) -> float:
    """Calculate influence score for sizing nodes"""
    score = 0.0
    
    # Citation count factor
    citation_count = citation.get("citationCount", 0)
    if citation_count > 0:
        score += min(5.0, citation_count / 20)  # Max 5 points from citations
    
    # Recency factor
    year = citation.get("year")
    if isinstance(year, int):
        current_year = 2025
        age = current_year - year
        if age <= 5:
            score += 2.0  # Recent papers get bonus
        elif age <= 10:
            score += 1.0
    
    # Venue prestige factor
    venue = citation.get("venue", "").lower()
    high_impact_venues = ["nature", "science", "cell", "neurips", "icml", "cvpr"]
    if any(v in venue for v in high_impact_venues):
        score += 2.0
    
    # Author count factor (more authors might indicate larger collaboration)
    authors = citation.get("authors", [])
    if len(authors) > 5:
        score += 1.0
    
    return min(10.0, score)  # Cap at 10


def create_edge_attributes(citation: Dict) -> Dict:
    """Create edge attributes with metadata"""
    return {
        "citation_type": "direct",
        "confidence": 1.0,
        "source_paper": citation.get("source_paper", ""),
        "context": citation.get("context", ""),
        "page_number": citation.get("page_number", "")
    }


def add_cross_citations(G: nx.DiGraph, citations: List[Dict]):
    """Add edges between citations if they cite each other"""
    # This is a placeholder for more advanced cross-citation detection
    # In a full implementation, you would:
    # 1. Compare citation titles/DOIs
    # 2. Use external APIs to find cross-references
    # 3. Add edges between citing papers
    pass


def add_graph_metrics(G: nx.DiGraph):
    """Add graph-level metrics to nodes"""
    try:
        # Calculate centrality measures
        in_degree_centrality = nx.in_degree_centrality(G)
        out_degree_centrality = nx.out_degree_centrality(G)
        
        # Add centrality to node attributes
        for node_id in G.nodes():
            G.nodes[node_id]["in_degree_centrality"] = in_degree_centrality.get(node_id, 0)
            G.nodes[node_id]["out_degree_centrality"] = out_degree_centrality.get(node_id, 0)
            
    except Exception as e:
        # If centrality calculation fails, continue without it
        pass


def optimize_for_layout(G: nx.DiGraph, layout: str):
    """Apply layout-specific optimizations"""
    if layout.lower() == "hierarchical":
        # For hierarchical layout, assign levels
        assign_hierarchical_levels(G)
    elif layout.lower() == "circular":
        # For circular layout, group similar nodes
        assign_circular_groups(G)
    # Force-directed doesn't need special optimization


def assign_hierarchical_levels(G: nx.DiGraph):
    """Assign hierarchical levels to nodes for better layout"""
    # Main papers at level 0
    for node_id, attrs in G.nodes(data=True):
        if attrs.get("node_type") == "main":
            G.nodes[node_id]["level"] = 0
        else:
            G.nodes[node_id]["level"] = 1


def assign_circular_groups(G: nx.DiGraph):
    """Assign groups for circular layout based on attributes"""
    for node_id, attrs in G.nodes(data=True):
        if attrs.get("node_type") == "main":
            G.nodes[node_id]["group"] = "main"
        else:
            # Group by publication year decade
            year = attrs.get("year")
            if isinstance(year, int):
                decade = (year // 10) * 10
                G.nodes[node_id]["group"] = f"{decade}s"
            else:
                G.nodes[node_id]["group"] = "unknown"


def get_graph_statistics(G: nx.DiGraph) -> Dict:
    """Calculate comprehensive graph statistics"""
    stats = {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "main_papers": len([n for n, attr in G.nodes(data=True) if attr.get("node_type") == "main"]),
        "citations": len([n for n, attr in G.nodes(data=True) if attr.get("node_type") == "citation"]),
        "density": nx.density(G),
        "is_connected": nx.is_weakly_connected(G),
    }
    
    # Year distribution
    years = [attr.get("year") for _, attr in G.nodes(data=True) 
             if isinstance(attr.get("year"), int)]
    
    if years:
        stats.update({
            "year_range": (min(years), max(years)),
            "median_year": sorted(years)[len(years)//2],
            "unique_years": len(set(years))
        })
    
    return stats