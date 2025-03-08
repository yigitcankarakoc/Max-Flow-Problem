import networkx as nx

def solve_max_flow(nodes, arcs, capacities, source, sink):
    """
    Solve a max flow problem using NetworkX.
    
    Parameters:
    - nodes: List of node names
    - arcs: List of tuples (source, target, capacity)
    - source: Source node
    - sink: Sink node
    
    Returns:
    - flow_values: Dictionary mapping arcs to optimal flow values
    - max_flow_value: The maximum flow value
    """
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    
    for source_node, target_node, capacity in arcs:
        G.add_edge(source_node, target_node, capacity=capacity)
    
    flow_value, flow_dict = nx.maximum_flow(G, source, sink)
    
    flow_values = []
    for source_node, target_dict in flow_dict.items():
        for target_node, flow in target_dict.items():
            flow_values.append([source_node, target_node, flow])
    
    return flow_values, flow_value
