from flask import Flask, render_template, request, jsonify
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import os

app = Flask(__name__)

def solve_max_flow(nodes, arcs, source, sink):
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    
    for source_node, target_node, capacity in arcs:
        G.add_edge(source_node, target_node, capacity=capacity)
    
    flow_value, flow_dict = nx.maximum_flow(G, source, sink)
    
    flow_values = []
    for source_node, target_dict in flow_dict.items():
        for target_node, flow in target_dict.items():
            if flow > 0:
                flow_values.append([source_node, target_node, flow])
    
    return flow_values, flow_value

def create_graph_image(nodes, arcs, flow_values=None):
    G = nx.DiGraph()
    
    for node in nodes:
        G.add_node(node)
    
    for source, target, capacity in arcs:
        if flow_values:
            flow = 0
            for f in flow_values:
                if f[0] == source and f[1] == target:
                    flow = f[2]
                    break
            
            G.add_edge(source, target, capacity=capacity, flow=flow, 
                      label=f"{flow:.1f}/{capacity}")
        else:
            G.add_edge(source, target, capacity=capacity, 
                      label=f"0/{capacity}")
    
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)
    
    node_colors = []
    for node in G.nodes():
        if node == nodes[0]:
            node_colors.append('lightgreen')
        elif node == nodes[-1]:
            node_colors.append('lightcoral')
        else:
            node_colors.append('lightblue')
    
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color=node_colors)
    
    if flow_values:
        edges = list(G.edges(data=True))
        edge_colors = []
        widths = []
        for u, v, d in edges:
            ratio = d.get('flow', 0) / d['capacity'] if d['capacity'] > 0 else 0
            edge_colors.append((ratio, 0, 1-ratio))
            widths.append(1 + 3 * ratio)
        
        nx.draw_networkx_edges(G, pos, width=widths, edge_color=edge_colors, 
                              arrowsize=20, edgelist=[(u, v) for u, v, _ in edges])
    else:
        nx.draw_networkx_edges(G, pos, width=2, edge_color='black', 
                              arrowsize=20)
    
    nx.draw_networkx_labels(G, pos, font_size=14, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'label'))
    
    plt.title("Max Flow Network")
    plt.axis('off')
    
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close()
    
    return base64.b64encode(img.getvalue()).decode()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    data = request.json
    nodes = data['nodes']
    arcs = data['arcs']
    source = data['source']
    sink = data['sink']
    
    if not nodes or not arcs or not source or not sink:
        return jsonify({
            'error': 'Missing required inputs'
        }), 400
    
    if source not in nodes or sink not in nodes:
        return jsonify({
            'error': 'Source or sink node not in node list'
        }), 400
    
    try:
        flow_values, max_flow_value = solve_max_flow(nodes, arcs, source, sink)
        graph_image = create_graph_image(nodes, arcs, flow_values)
        
        return jsonify({
            'max_flow': float(max_flow_value),
            'flow_values': flow_values,
            'graph_image': graph_image
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Use environment variable for port with a default of 5000
    port = int(os.environ.get('PORT', 5000))
    # In production, don't use debug mode
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug) 