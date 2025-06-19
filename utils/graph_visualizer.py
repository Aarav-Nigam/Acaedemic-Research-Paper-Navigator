from pyvis.network import Network
import streamlit.components.v1 as components

def render_graph(G, height="600px"):
    net = Network(height=height, bgcolor="#ffffff", font_color="black", directed=True)
    for node_id, attr in G.nodes(data=True):
        net.add_node(
            node_id,
            label=attr.get("label", ""),
            title=f"{attr.get('label', '')} ({attr.get('year', 'N/A')})",
            color=attr.get("color", "#97c2fc")
        )

    for source, target in G.edges():
        net.add_edge(source, target)

    net.set_options("""
    {
    "nodes": {
        "shape": "dot",
        "size": 12,
        "font": { "size": 12 }
    },
    "edges": {
        "arrows": { "to": { "enabled": true } },
        "smooth": true
    },
    "physics": {
        "enabled": true,
        "solver": "forceAtlas2Based"
    }
    }
    """)


    net.save_graph("data/citation_graph.html")
    HtmlFile = open("data/citation_graph.html", "r", encoding="utf-8")
    components.html(HtmlFile.read(), height=650, scrolling=True)
