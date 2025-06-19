import requests

def fetch_metadata_from_semantic_scholar(title_or_doi):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={title_or_doi}&limit=1&fields=title,authors,year,citationCount,externalIds"
    try:
        res = requests.get(url)
        data = res.json()
        if data.get("data"):
            return data["data"][0]
    except:
        return None
