# MEMBER 2: Implement the logic inside these functions. Do not change the function names or arguments.
from collections import deque


# hàm phụ tạo danh sách kề để tra cứu nhanh
def get_adjacency_list(nodes, edges, directed=True):
    """
    Helper function to build an adjacency map from the list of nodes and edges.
    Returns dict: node_id -> sorted list of neighbor ids.
    """

    # If the GUI attaches direction mode onto edges, prefer that over the
    # function argument so BFS/DFS automatically match the current mode.
    # Important: only override when the caller requests directed traversal.
    # (check_bipartite passes directed=False and should remain undirected.)
    try:
        if directed and edges and hasattr(edges[0], "is_directed"):
            directed = bool(getattr(edges[0], "is_directed"))
    except Exception:
        pass

    adj = {node.id: [] for node in nodes}
    for edge in edges:
        u, v = edge.start_node.id, edge.end_node.id
        if u in adj:
            adj[u].append(v)
        if not directed and v in adj:
            adj[v].append(u)

    for u in adj:
        adj[u].sort()

    return adj


def bfs(nodes, edges, start_id):
    if not nodes:
        return []

    adj = get_adjacency_list(nodes, edges, directed=True)
    if start_id not in adj:
        return []

    visited = set([start_id])
    result = []
    queue = deque([start_id])

    while queue:
        current = queue.popleft()
        result.append(current)
        for neighbor in adj.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return result


def dfs(nodes, edges, start_id):
    if not nodes:
        return []

    adj = get_adjacency_list(nodes, edges, directed=True)
    if start_id not in adj:
        return []

    visited = set()
    result = []

    def _dfs_from(root_id):
        stack = [root_id]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            result.append(current)

            # push neighbors in reverse order so that smallest neighbor is visited first
            for neighbor in reversed(adj.get(current, [])):
                if neighbor not in visited:
                    stack.append(neighbor)

    # Traverse from the requested start node first.
    _dfs_from(start_id)

    # Then traverse any remaining (unreachable/disconnected) vertices.
    for node_id in sorted(adj.keys()):
        if node_id not in visited:
            _dfs_from(node_id)

    return result


def check_bipartite(nodes, edges):
    """Returns (is_bipartite, color_map). color_map maps node_id -> 0/1.
    If not bipartite, color_map contains colors up to the conflict point.
    """
    adj = get_adjacency_list(nodes, edges, directed=False)
    color = {}

    for node in nodes:
        if node.id in color:
            continue

        queue = deque([node.id])
        color[node.id] = 0

        while queue:
            u = queue.popleft()
            for v in adj.get(u, []):
                if v not in color:
                    color[v] = 1 - color[u]
                    queue.append(v)
                elif color[v] == color[u]:
                    return (False, color)

    return (True, color)
