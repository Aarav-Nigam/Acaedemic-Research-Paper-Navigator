import networkx as nx

def build_citation_graph(main_paper, citations):
    G = nx.DiGraph()

    # Add main paper node
    main_id = "main"
    G.add_node(main_id, label=main_paper["title"], year=main_paper.get("year", "N/A"), color="#1f77b4")

    # Add cited papers as nodes
    for i, cited in enumerate(citations):
        cited_id = f"cited_{i}"
        title = cited.get("title", f"Paper {i}")
        year = cited.get("year", "N/A")
        color = "#ff7f0e"
        G.add_node(cited_id, label=title, year=year, color=color)
        G.add_edge(main_id, cited_id)

    return G
