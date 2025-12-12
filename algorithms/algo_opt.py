# MEMBER 3: Implement the logic inside these functions. Remember to use `edge.weight` for calculations.

def dijkstra(nodes, edges, start_id, end_id):
    """
    Finds the shortest path between two nodes using Dijkstra's algorithm.
    
    Args:
        nodes (list): List of Node objects.
        edges (list): List of Edge objects.
        start_id (int): The ID of the starting node.
        end_id (int): The ID of the destination node.
        
    Returns:
        tuple: (path_list_of_ids, total_weight)
            - path_list_of_ids (list): List of node IDs representing the shortest path.
            - total_weight (int/float): The sum of weights along the path.
    """
    pass

def prim(nodes, edges):
    """
    Finds the Minimum Spanning Tree (MST) using Prim's algorithm.
    
    Args:
        nodes (list): List of Node objects.
        edges (list): List of Edge objects.
        
    Returns:
        list: A list of Edge objects (or tuples representing connections) that form the MST.
    """
    pass

def kruskal(nodes, edges):
    """
    Finds the Minimum Spanning Tree (MST) using Kruskal's algorithm.
    
    Args:
        nodes (list): List of Node objects.
        edges (list): List of Edge objects.
        
    Returns:
        list: A list of Edge objects that form the MST.
    """
    pass

def ford_fulkerson(nodes, edges, source_id, sink_id):
    """
    Finds the Maximum Flow using the Ford-Fulkerson algorithm.
    
    Args:
        nodes (list): List of Node objects.
        edges (list): List of Edge objects.
        source_id (int): The ID of the source node.
        sink_id (int): The ID of the sink node.
        
    Returns:
        tuple: (max_flow_value, flow_network)
            - max_flow_value (int): The maximum flow.
            - flow_network (list): List of edges with assigned flow values.
    """
    pass
