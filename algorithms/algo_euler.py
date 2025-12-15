"""Thuật toán Euler (Fleury / Hierholzer).

Bao gồm kiểm tra:
- Vô hướng: liên thông (bỏ qua đỉnh bậc 0), bậc chẵn / đúng 2 bậc lẻ
- Có hướng: kiểm tra in-degree/out-degree và (mạnh) liên thông theo điều kiện Euler có hướng

Trả về danh sách id đỉnh theo thứ tự đi qua, hoặc None nếu không tồn tại.
"""


def _build_undirected_adj(nodes, edges):
    adj = {int(node.id): [] for node in nodes}
    for edge in edges:
        u = int(edge.start_node.id)
        v = int(edge.end_node.id)
        if u not in adj:
            adj[u] = []
        if v not in adj:
            adj[v] = []
        adj[u].append(v)
        adj[v].append(u)
    return adj


def _nonzero_degree_vertices(adj):
    return [v for v, nbrs in adj.items() if len(nbrs) > 0]


def _is_connected_ignoring_isolated(adj) -> bool:
    verts = _nonzero_degree_vertices(adj)
    if not verts:
        return True
    start = verts[0]
    visited = set([start])
    stack = [start]
    while stack:
        u = stack.pop()
        for v in adj.get(u, []):
            if v not in visited:
                visited.add(v)
                stack.append(v)
    return all(v in visited for v in verts)


def euler_classification(nodes, edges):
    """Return (kind, start_id).

    kind:
    - "euler"      : có chu trình Euler
    - "semi-euler" : có đường đi Euler (nửa Euler)
    - "none"       : không có
    """
    adj = _build_undirected_adj(nodes, edges)
    if not _is_connected_ignoring_isolated(adj):
        return ("none", None)

    odd = [v for v, nbrs in adj.items() if len(nbrs) % 2 == 1]
    if len(odd) == 0:
        start = next((v for v, nbrs in adj.items() if len(nbrs) > 0), None)
        if start is None:
            # Không có cạnh: coi như chu trình rỗng
            start = int(nodes[0].id) if nodes else None
        return ("euler", start)
    if len(odd) == 2:
        return ("semi-euler", odd[0])
    return ("none", None)


def _build_directed_adj(nodes, edges):
    adj = {int(node.id): [] for node in nodes}
    radj = {int(node.id): [] for node in nodes}
    indeg = {int(node.id): 0 for node in nodes}
    outdeg = {int(node.id): 0 for node in nodes}

    for edge in edges:
        u = int(edge.start_node.id)
        v = int(edge.end_node.id)
        if u not in adj:
            adj[u] = []
            radj[u] = []
            indeg[u] = 0
            outdeg[u] = 0
        if v not in adj:
            adj[v] = []
            radj[v] = []
            indeg[v] = 0
            outdeg[v] = 0
        adj[u].append(v)
        radj[v].append(u)
        outdeg[u] += 1
        indeg[v] += 1

    return adj, radj, indeg, outdeg


def _nonzero_degree_vertices_directed(indeg, outdeg):
    verts = []
    for v in set(indeg.keys()) | set(outdeg.keys()):
        if indeg.get(v, 0) + outdeg.get(v, 0) > 0:
            verts.append(v)
    return verts


def _dfs_reach(start, adj, extra_edge=None):
    """Return visited set in directed graph from start.

    extra_edge: optional tuple (a, b) treated as an additional directed edge a->b.
    """
    visited = set()
    stack = [start]
    while stack:
        u = stack.pop()
        if u in visited:
            continue
        visited.add(u)
        for v in adj.get(u, []):
            if v not in visited:
                stack.append(v)
        if extra_edge is not None and u == extra_edge[0]:
            v = extra_edge[1]
            if v not in visited:
                stack.append(v)
    return visited


def _is_strongly_connected_on_vertices(adj, radj, vertices, start, extra_edge=None):
    if not vertices:
        return True
    if start not in vertices:
        return False

    visited_fwd = _dfs_reach(start, adj, extra_edge=extra_edge)
    # reverse extra edge is b->a in reverse graph
    extra_rev = None
    if extra_edge is not None:
        extra_rev = (extra_edge[1], extra_edge[0])
    visited_rev = _dfs_reach(start, radj, extra_edge=extra_rev)
    return all(v in visited_fwd and v in visited_rev for v in vertices)


def directed_euler_classification(nodes, edges):
    """Return (kind, start_id, end_id) for directed Euler.

    kind:
    - "euler"      : có chu trình Euler có hướng
    - "semi-euler" : có đường đi Euler có hướng
    - "none"       : không có
    """
    if not nodes:
        return ("none", None, None)

    adj, radj, indeg, outdeg = _build_directed_adj(nodes, edges)
    vertices = _nonzero_degree_vertices_directed(indeg, outdeg)

    if not edges:
        # Không có cạnh: coi như chu trình rỗng tại 1 đỉnh
        nid = int(nodes[0].id)
        return ("euler", nid, nid)

    start = None
    end = None
    for v in vertices:
        diff = outdeg.get(v, 0) - indeg.get(v, 0)
        if diff == 1:
            if start is not None:
                return ("none", None, None)
            start = v
        elif diff == -1:
            if end is not None:
                return ("none", None, None)
            end = v
        elif diff == 0:
            continue
        else:
            return ("none", None, None)

    if start is None and end is None:
        # Euler circuit candidate
        start = next((v for v in vertices if outdeg.get(v, 0) > 0), None)
        if start is None:
            return ("none", None, None)
        if not _is_strongly_connected_on_vertices(adj, radj, vertices, start):
            return ("none", None, None)
        return ("euler", start, start)

    if start is None or end is None:
        return ("none", None, None)

    # Euler trail candidate: check strong connectivity after adding edge end->start
    if not _is_strongly_connected_on_vertices(adj, radj, vertices, start, extra_edge=(end, start)):
        return ("none", None, None)
    return ("semi-euler", start, end)


def _hierholzer_directed(nodes, edges):
    kind, start, _end = directed_euler_classification(nodes, edges)
    if kind == "none" or start is None:
        return None

    adj, _radj, _indeg, _outdeg = _build_directed_adj(nodes, edges)
    # Work on a copy because we'll consume edges
    adj = {k: list(v) for k, v in adj.items()}

    stack = [int(start)]
    path = []
    while stack:
        v = stack[-1]
        if adj.get(v):
            u = adj[v].pop()
            stack.append(u)
        else:
            path.append(stack.pop())

    path.reverse()
    # Must use all edges exactly once
    if len(path) != len(edges) + 1:
        return None
    return path


class FleuryEuler:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.adj = _build_undirected_adj(nodes, edges)

    def _is_bridge(self, u, v):
        # Nếu có nhiều cạnh song song u-v thì không phải cầu (loại bỏ 1 cạnh vẫn còn đường trực tiếp)
        if self.adj[u].count(v) > 1:
            return False

        # Xóa tạm 1 cạnh u-v
        self.adj[u].remove(v)
        self.adj[v].remove(u)

        visited = set([u])
        stack = [u]
        while stack:
            x = stack.pop()
            for nxt in self.adj.get(x, []):
                if nxt not in visited:
                    visited.add(nxt)
                    stack.append(nxt)

        # Khôi phục cạnh
        self.adj[u].append(v)
        self.adj[v].append(u)

        return v not in visited

    def fleury_algorithm(self):
        kind, start = euler_classification(self.nodes, self.edges)
        if kind == "none" or start is None:
            return None

        # Làm việc trên bản sao adjacency vì thuật toán sẽ xóa cạnh
        self.adj = {k: list(v) for k, v in self.adj.items()}
        curr = int(start)
        path = [curr]

        while self.adj.get(curr):
            neighbors = list(self.adj[curr])
            chosen = None
            for nxt in neighbors:
                # Tránh đi qua cầu nếu còn lựa chọn khác
                if len(self.adj[curr]) == 1 or not self._is_bridge(curr, nxt):
                    chosen = nxt
                    break
            if chosen is None:
                # Fallback (không nên xảy ra)
                chosen = neighbors[0]

            # Xóa đúng 1 cạnh curr-chosen
            self.adj[curr].remove(chosen)
            self.adj[chosen].remove(curr)
            curr = chosen
            path.append(curr)

        # Đảm bảo đã dùng hết cạnh
        if any(self.adj[v] for v in self.adj):
            return None
        return path


class HierholzerEuler:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges

    def hierholzer_algorithm(self):
        kind, start = euler_classification(self.nodes, self.edges)
        if kind == "none" or start is None:
            return None

        adj = _build_undirected_adj(self.nodes, self.edges)
        # Làm việc trên bản sao
        adj = {k: list(v) for k, v in adj.items()}

        stack = [int(start)]
        circuit = []
        while stack:
            v = stack[-1]
            if adj.get(v):
                u = adj[v].pop()
                adj[u].remove(v)
                stack.append(u)
            else:
                circuit.append(stack.pop())

        circuit.reverse()
        # Đảm bảo đã dùng hết cạnh
        if any(adj[v] for v in adj):
            return None
        return circuit


def fleury_algorithm(nodes, edges, directed: bool = False):
    if directed:
        # Fleury cho đồ thị có hướng khá phức tạp; dùng Hierholzer để đảm bảo đúng.
        return _hierholzer_directed(nodes, edges)
    return FleuryEuler(nodes, edges).fleury_algorithm()


def hierholzer_algorithm(nodes, edges, directed: bool = False):
    if directed:
        return _hierholzer_directed(nodes, edges)
    return HierholzerEuler(nodes, edges).hierholzer_algorithm()
