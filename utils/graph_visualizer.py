from pyvis.network import Network
import streamlit.components.v1 as components
import streamlit as st
import networkx as nx
import tempfile
import os

def render_graph(G, height="600px", layout="force-directed"):
    """
    Render a citation graph with simplified approach for better compatibility
    """
    
    # Check if graph is empty
    if len(G.nodes) == 0:
        st.warning("Graph is empty. No nodes to display.")
        return
    
    st.write(f"Rendering graph with {len(G.nodes)} nodes and {len(G.edges)} edges")
    
    # Create simple network
    net = Network(
        height=height,
        width="100%",
        bgcolor="#ffffff",
        font_color="black",
        directed=True
    )
    
    # Disable physics initially for faster rendering
    net.toggle_physics(False)
    
    # Add nodes with simple styling
    for node_id, attr in G.nodes(data=True):
        node_type = attr.get("node_type", "citation")
        
        # Simple color scheme
        if node_type == "main":
            color = "#3498db"
            size = 25
        else:
            color = "#e74c3c" 
            size = 15
            
        # Simple tooltip
        title = f"{attr.get('label', str(node_id))}\nYear: {attr.get('year', 'N/A')}"
        
        # Add node with minimal parameters
        try:
            net.add_node(
                str(node_id),
                label=str(attr.get("label", str(node_id))[:20]),
                color=color,
                size=size,
                title=title
            )
        except TypeError:
            # Fallback for different pyvis versions
            net.add_node(
                n_id=str(node_id),
                label=str(attr.get("label", str(node_id))[:20]),
                color=color,
                size=size,
                title=title
            )
    
    # Add edges with simple styling
    for source, target, edge_data in G.edges(data=True):
        try:
            net.add_edge(str(source), str(target))
        except TypeError:
            # Fallback for different pyvis versions
            net.add_edge(source=str(source), to=str(target))
    
    # Set minimal options
    net.set_options("""
    var options = {
      "physics": {
        "enabled": true,
        "stabilization": {"iterations": 100}
      }
    }
    """)
    
    # Save to temporary file
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp_file:
            net.save_graph(tmp_file.name)
            temp_path = tmp_file.name
        
        # Read and display
        with open(temp_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Simple modification to ensure it displays
        html_content = html_content.replace(
            '<div id="mynetworkid"',
            '<div id="mynetworkid" style="border: 1px solid #ccc;"'
        )
        
        # Display with exact height
        components.html(html_content, height=int(height.replace('px', '')) + 50)
        
        # Clean up
        os.unlink(temp_path)
        
        st.success("Graph rendered successfully!")
        
    except Exception as e:
        st.error(f"Error rendering graph: {e}")
        st.write("Trying alternative approach...")
        
        # Alternative: Generate HTML directly
        render_simple_html_graph(G)

def render_simple_html_graph(G):
    """Fallback method using simple HTML/JS"""
    
    nodes_data = []
    edges_data = []
    
    for node_id, attr in G.nodes(data=True):
        nodes_data.append({
            'id': str(node_id),
            'label': str(attr.get('label', str(node_id))[:20]),
            'color': '#3498db' if attr.get('node_type') == 'main' else '#e74c3c'
        })
    
    for source, target in G.edges():
        edges_data.append({'from': str(source), 'to': str(target)})
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style type="text/css">
            #mynetworkid {{
                width: 100%;
                height: 600px;
                border: 1px solid lightgray;
            }}
        </style>
    </head>
    <body>
        <div id="mynetworkid"></div>
        <script type="text/javascript">
            var nodes = new vis.DataSet({nodes_data});
            var edges = new vis.DataSet({edges_data});
            var container = document.getElementById('mynetworkid');
            var data = {{
                nodes: nodes,
                edges: edges
            }};
            var options = {{
                physics: {{
                    enabled: true,
                    stabilization: {{iterations: 100}}
                }}
            }};
            var network = new vis.Network(container, data, options);
        </script>
    </body>
    </html>
    """
    
    components.html(html_content, height=650)

def create_test_graph():
    """Create a simple test graph"""
    G = nx.DiGraph()
    
    # Add test nodes
    G.add_node(1, label="Main Paper", node_type="main", year=2023)
    G.add_node(2, label="Citation 1", node_type="citation", year=2022)
    G.add_node(3, label="Citation 2", node_type="citation", year=2021)
    G.add_node(4, label="Citation 3", node_type="citation", year=2020)
    
    # Add test edges
    G.add_edge(1, 2)
    G.add_edge(1, 3)
    G.add_edge(1, 4)
    G.add_edge(2, 3)
    
    return G

# Streamlit test interface
if __name__ == "__main__":
    st.title("Citation Graph Visualization Debug")
    
    st.write("Testing graph visualization...")
    
    # Debug info
    try:
        import pyvis
        st.write(f"Pyvis version: {pyvis.__version__}")
    except:
        st.write("Could not determine pyvis version")
    
    # Create and display test graph
    test_graph = create_test_graph()
    st.write(f"Created test graph with {len(test_graph.nodes)} nodes and {len(test_graph.edges)} edges")
    
    # Test buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Render with Pyvis"):
            render_graph(test_graph)
    
    with col2:
        if st.button("Render with Simple HTML"):
            render_simple_html_graph(test_graph)
    
    # Show graph structure
    with st.expander("Graph Structure"):
        st.write("Nodes:", list(test_graph.nodes(data=True)))
        st.write("Edges:", list(test_graph.edges(data=True)))