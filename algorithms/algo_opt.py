# THÀNH VIÊN 3: Cài đặt logic bên trong các hàm này. Nhớ sử dụng `edge.weight` để tính toán.
import main.graph_objects as go

def dijkstra(nodes, edges, start_id, end_id):
    """
    Tìm đường đi ngắn nhất giữa hai đỉnh sử dụng thuật toán Dijkstra.
    
    Tham số:
        nodes (list): Danh sách các đối tượng Node.
        edges (list): Danh sách các đối tượng Edge.
        start_id (int): ID của đỉnh bắt đầu.
        end_id (int): ID của đỉnh đích.
        
    Trả về:
        tuple: (path_list_of_ids, total_weight)
            - path_list_of_ids (list): Danh sách các ID đỉnh biểu diễn đường đi ngắn nhất.
            - total_weight (int/float): Tổng trọng số dọc theo đường đi.
    """
    node_ids = go.g_node_ids(nodes)
    start = int(start_id)
    end = int(end_id)

    if start not in node_ids or end not in node_ids:
        return ([], float('inf'))

    adj = go.g_build_directed_adj(edges)
    dist = {node_id: float('inf') for node_id in node_ids}
    prev = {node_id: None for node_id in node_ids}

    dist[start] = 0
    heap = [(0, start)]

    while heap:
        current_dist, u = go.g_heapq.heappop(heap)
        if current_dist != dist[u]:
            continue
        if u == end:
            break

        for v, w, _edge in adj.get(u, []):
            if v not in node_ids:
                continue
            new_dist = current_dist + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                go.g_heapq.heappush(heap, (new_dist, v))

    if dist[end] == float('inf'):
        return ([], float('inf'))

    # Reconstruct path
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        if cur == start:
            break
        cur = prev[cur]

    if not path or path[-1] != start:
        return ([], float('inf'))

    path.reverse()
    return (path, dist[end])


def dijkstra_trace(nodes, edges, start_id, end_id):
    """Dijkstra variant that also returns a step-by-step trace for visualization.

    Returns:
        tuple: (path_list_of_ids, total_weight, trace)

    Trace events are tuples:
        ("settle", u, dist_u)     when node u is popped/settled
        ("relax", u, v, new_dist) when edge u->v relaxes dist[v]
    """
    node_ids = go.g_node_ids(nodes)
    start = int(start_id)
    end = int(end_id)

    if start not in node_ids or end not in node_ids:
        return ([], float('inf'), [])

    adj = go.g_build_directed_adj(edges)
    dist = {node_id: float('inf') for node_id in node_ids}
    prev = {node_id: None for node_id in node_ids}

    dist[start] = 0
    heap = [(0, start)]
    trace = []
    settled = set()

    while heap:
        current_dist, u = go.g_heapq.heappop(heap)
        if current_dist != dist[u]:
            continue
        if u in settled:
            continue
        settled.add(u)
        trace.append(("settle", u, current_dist))
        if u == end:
            break

        for v, w, _edge in adj.get(u, []):
            if v not in node_ids:
                continue
            new_dist = current_dist + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                go.g_heapq.heappush(heap, (new_dist, v))
                trace.append(("relax", u, v, new_dist))

    if dist[end] == float('inf'):
        return ([], float('inf'), trace)
    # Reconstruct path
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        if cur == start:
            break
        cur = prev[cur]

    if not path or path[-1] != start:
        return ([], float('inf'), trace)

    path.reverse()
    return (path, dist[end], trace)

def prim(nodes, edges):
    """
    Tìm Cây khung nhỏ nhất (MST) sử dụng thuật toán Prim.
    
    Tham số:
        nodes (list): Danh sách các đối tượng Node.
        edges (list): Danh sách các đối tượng Edge.
        
    Trả về:
        list: Danh sách các đối tượng Edge (hoặc tuple biểu diễn kết nối) tạo thành MST.
    """
    node_ids = sorted(go.g_node_ids(nodes))
    if not node_ids:
        return []

    adj = go.g_build_undirected_adj(edges)
    visited = set()
    mst_edges = []

    def run_from(start):
        visited.add(start)
        heap = []
        for v, w, edge in adj.get(start, []):
            if v not in visited:
                go.g_heapq.heappush(heap, (w, start, v, edge))

        while heap:
            w, u, v, edge = go.g_heapq.heappop(heap)
            if v in visited:
                continue
            visited.add(v)
            mst_edges.append(edge)
            for nxt, nxt_w, nxt_edge in adj.get(v, []):
                if nxt not in visited:
                    go.g_heapq.heappush(heap, (nxt_w, v, nxt, nxt_edge))

    # If disconnected, return a spanning forest
    for start in node_ids:
        if start not in visited:
            run_from(start)

    return mst_edges


def prim_trace(nodes, edges):
    """Prim variant that also returns a step-by-step trace for visualization.

    Returns:
        tuple: (mst_edges, trace)

    Trace events are tuples:
        ("start", start_node_id)
        ("consider", edge)  popped from heap
        ("accept", edge)    added to MST
    """
    node_ids = sorted(go.g_node_ids(nodes))
    if not node_ids:
        return ([], [])

    adj = go.g_build_undirected_adj(edges)
    visited = set()
    mst_edges = []
    trace = []

    def run_from(start):
        trace.append(("start", int(start)))
        visited.add(start)
        heap = []
        for v, w, edge in adj.get(start, []):
            if v not in visited:
                go.g_heapq.heappush(heap, (w, start, v, edge))

        while heap:
            w, u, v, edge = go.g_heapq.heappop(heap)
            trace.append(("consider", edge))
            if v in visited:
                continue
            visited.add(v)
            mst_edges.append(edge)
            trace.append(("accept", edge))
            for nxt, nxt_w, nxt_edge in adj.get(v, []):
                if nxt not in visited:
                    go.g_heapq.heappush(heap, (nxt_w, v, nxt, nxt_edge))

    for start in node_ids:
        if start not in visited:
            run_from(start)

    return (mst_edges, trace)

def kruskal(nodes, edges):
    """
    Tìm Cây khung nhỏ nhất (MST) sử dụng thuật toán Kruskal.
    
    Tham số:
        nodes (list): Danh sách các đối tượng Node.
        edges (list): Danh sách các đối tượng Edge.
        
    Trả về:
        list: Danh sách các đối tượng Edge tạo thành MST.
    """
    node_ids = sorted(go.g_node_ids(nodes))
    if not node_ids:
        return []

    parent = {x: x for x in node_ids}
    rank = {x: 0 for x in node_ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra = find(a)
        rb = find(b)
        if ra == rb:
            return False
        if rank[ra] < rank[rb]:
            parent[ra] = rb
        elif rank[ra] > rank[rb]:
            parent[rb] = ra
        else:
            parent[rb] = ra
            rank[ra] += 1
        return True

    # Treat edges as undirected for MST
    sorted_edges = sorted(edges, key=lambda e: e.weight)
    mst_edges = []
    for edge in sorted_edges:
        u = int(edge.start_node.id)
        v = int(edge.end_node.id)
        if u not in parent or v not in parent:
            continue
        if union(u, v):
            mst_edges.append(edge)

    return mst_edges


def kruskal_trace(nodes, edges):
    """Kruskal variant that also returns a step-by-step trace for visualization.

    Returns:
        tuple: (mst_edges, trace)

    Trace events are tuples:
        ("consider", edge)
        ("accept", edge)
        ("reject", edge)
    """
    node_ids = sorted(go.g_node_ids(nodes))
    if not node_ids:
        return ([], [])

    parent = {x: x for x in node_ids}
    rank = {x: 0 for x in node_ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra = find(a)
        rb = find(b)
        if ra == rb:
            return False
        if rank[ra] < rank[rb]:
            parent[ra] = rb
        elif rank[ra] > rank[rb]:
            parent[rb] = ra
        else:
            parent[rb] = ra
            rank[ra] += 1
        return True

    sorted_edges = sorted(edges, key=lambda e: e.weight)
    mst_edges = []
    trace = []

    for edge in sorted_edges:
        u = int(edge.start_node.id)
        v = int(edge.end_node.id)
        if u not in parent or v not in parent:
            continue
        trace.append(("consider", edge))
        if union(u, v):
            mst_edges.append(edge)
            trace.append(("accept", edge))
        else:
            trace.append(("reject", edge))

    return (mst_edges, trace)

def ford_fulkerson(nodes, edges, source_id, sink_id):
    """
    Tìm Luồng cực đại sử dụng thuật toán Ford-Fulkerson.
    
    Tham số:
        nodes (list): Danh sách các đối tượng Node.
        edges (list): Danh sách các đối tượng Edge.
        source_id (int): ID của đỉnh nguồn.
        sink_id (int): ID của đỉnh đích.
        
    Trả về:
        tuple: (max_flow_value, flow_network)
            - max_flow_value (int): Giá trị luồng cực đại.
            - flow_network (list): Danh sách các cạnh với giá trị luồng đã gán.
    """
    node_ids = go.g_node_ids(nodes)
    source = int(source_id)
    sink = int(sink_id)
    if source not in node_ids or sink not in node_ids:
        return (0, [])

    # Edmonds-Karp (BFS) implementation with explicit residual edges.
    # Supports parallel edges by representing each original edge as its own arc.
    graph = {node_id: [] for node_id in node_ids}

    # Each residual edge is stored in a list attached to graph[u] as dict:
    # {'to': v, 'rev': index_of_reverse_edge_in_graph[v], 'cap': remaining_capacity}
    original_arc_ref = []  # (u, idx_in_graph_u, original_capacity)

    def add_edge(u, v, capacity):
        fwd = {'to': v, 'rev': len(graph[v]), 'cap': capacity}
        rev = {'to': u, 'rev': len(graph[u]), 'cap': 0}
        graph[u].append(fwd)
        graph[v].append(rev)
        return (u, len(graph[u]) - 1)

    for edge in edges:
        u = int(edge.start_node.id)
        v = int(edge.end_node.id)
        cap = int(edge.weight)
        if u not in graph or v not in graph:
            continue
        if cap < 0:
            cap = 0
        u_ref, idx_ref = add_edge(u, v, cap)
        original_arc_ref.append((u_ref, idx_ref, cap))

    def bfs():
        parent = {node_id: None for node_id in node_ids}  # node_id -> (prev_node, edge_index)
        q = go.g_deque([source])
        parent[source] = (source, None)
        while q:
            u = q.popleft()
            for i, e in enumerate(graph[u]):
                v = e['to']
                if parent[v] is None and e['cap'] > 0:
                    parent[v] = (u, i)
                    if v == sink:
                        return parent
                    q.append(v)
        return None

    max_flow = 0
    while True:
        parent = bfs()
        if parent is None:
            break

        # Find bottleneck
        path_flow = float('inf')
        v = sink
        while v != source:
            u, ei = parent[v]
            e = graph[u][ei]
            path_flow = min(path_flow, e['cap'])
            v = u

        if path_flow == 0 or path_flow == float('inf'):
            break

        # Augment
        v = sink
        while v != source:
            u, ei = parent[v]
            e = graph[u][ei]
            rev = graph[v][e['rev']]
            e['cap'] -= path_flow
            rev['cap'] += path_flow
            v = u

        max_flow += int(path_flow)

    # Attach per-edge flow on the original edge objects.
    flow_network = []
    for edge, (u, idx, original_cap) in zip(edges, original_arc_ref):
        remaining = graph[u][idx]['cap']
        flow_value = original_cap - remaining
        try:
            setattr(edge, 'flow', int(flow_value))
        except Exception:
            pass
        flow_network.append(edge)

    return (max_flow, flow_network)


def ford_fulkerson_trace(nodes, edges, source_id, sink_id):
    """Ford-Fulkerson (Edmonds-Karp) variant with trace events for visualization.

    Returns:
        tuple: (max_flow_value, flow_network, trace)

    Trace events are tuples:
        ("augment", path_pairs, bottleneck, max_flow_after)
    where path_pairs is a list of (u, v) along the augmenting path in residual graph.
    """
    node_ids = go.g_node_ids(nodes)
    source = int(source_id)
    sink = int(sink_id)
    if source not in node_ids or sink not in node_ids:
        return (0, [], [])

    graph = {node_id: [] for node_id in node_ids}
    original_arc_ref = []  # (u, idx_in_graph_u, original_capacity)

    def add_edge(u, v, capacity):
        fwd = {'to': v, 'rev': len(graph[v]), 'cap': capacity}
        rev = {'to': u, 'rev': len(graph[u]), 'cap': 0}
        graph[u].append(fwd)
        graph[v].append(rev)
        return (u, len(graph[u]) - 1)

    for edge in edges:
        u = int(edge.start_node.id)
        v = int(edge.end_node.id)
        cap = int(edge.weight)
        if u not in graph or v not in graph:
            continue
        if cap < 0:
            cap = 0
        u_ref, idx_ref = add_edge(u, v, cap)
        original_arc_ref.append((u_ref, idx_ref, cap))

    def bfs():
        parent = {node_id: None for node_id in node_ids}  # node_id -> (prev_node, edge_index)
        q = go.g_deque([source])
        parent[source] = (source, None)
        while q:
            u = q.popleft()
            for i, e in enumerate(graph[u]):
                v = e['to']
                if parent[v] is None and e['cap'] > 0:
                    parent[v] = (u, i)
                    if v == sink:
                        return parent
                    q.append(v)
        return None

    trace = []
    max_flow = 0
    while True:
        parent = bfs()
        if parent is None:
            break

        # Find bottleneck and collect path
        path_flow = float('inf')
        path_pairs = []
        v = sink
        while v != source:
            u, ei = parent[v]
            e = graph[u][ei]
            path_flow = min(path_flow, e['cap'])
            path_pairs.append((int(u), int(v)))
            v = u

        if path_flow == 0 or path_flow == float('inf'):
            break

        path_pairs.reverse()

        # Augment
        v = sink
        while v != source:
            u, ei = parent[v]
            e = graph[u][ei]
            rev = graph[v][e['rev']]
            e['cap'] -= path_flow
            rev['cap'] += path_flow
            v = u

        max_flow += int(path_flow)
        trace.append(("augment", path_pairs, int(path_flow), int(max_flow)))

    flow_network = []
    for edge, (u, idx, original_cap) in zip(edges, original_arc_ref):
        remaining = graph[u][idx]['cap']
        flow_value = original_cap - remaining
        try:
            setattr(edge, 'flow', int(flow_value))
        except Exception:
            pass
        flow_network.append(edge)

    return (max_flow, flow_network, trace)
