from utils.citations import extract_references
from utils.metadata_enrich import fetch_metadata_from_semantic_scholar

def get_citation_metadata(pdf_path):
    raw_refs = extract_references(pdf_path)
    enriched = []

    for ref in raw_refs[:10]:  # limit to top 10 for speed
        metadata = fetch_metadata_from_semantic_scholar(ref)
        if metadata:
            enriched.append(metadata)
        else:
            enriched.append({"title": ref})  # fallback

    return enriched
