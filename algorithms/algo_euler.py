# THÀNH VIÊN 3/6: Cài đặt logic bên trong các hàm này.

class FleuryEuler:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.adj = self.build_list()
    #Tạo danh sách kề từ Node và Edge
    def build_list(self):
        adj = {node.id: [] for node in self.nodes}
        for edge in self.edges:
            u = edge.start_node.id
            v = edge.end_node.id
            adj[u].append(v)
            adj[v].append(u) #vo huong 
        return adj
    #Kiem tra chu trinh Euler
    def has_euler(self):
        adj = self.build_list()
        for i in self.adj:
            if len(self.adj[i]) % 2 != 0:
                return False
        return True
    #Kiem tra canh cau
    def is_bridge(self, u , v):
        #xoa tam canh u-v
        self.adj[u].remove(v)
        self.adj[v].remove(u)

        visited = set()

        def dfs(x):
            visited.add(x)
            for nxt in self.adj[x]:
                if nxt not in visited:
                    dfs(nxt)
        dfs(u)

        self.adj[u].append(v)
        self.adj[v].append(u)

        return v not in visited


    def fleury_algorithm(self):
        """
        Finds an Eulerian Path or Circuit using Fleury's Algorithm.
        
        Args:
            nodes (list): List of Node objects.
            edges (list): List of Edge objects.
            
        Returns:
            list: A list of Node IDs representing the Eulerian path/circuit.
            Returns None if no such path exists.
        """
        if not self.has_euler():
            return None

        start = self.nodes[0].id
        curr = start 
        path = [curr]

        while self.adj[curr]:
            for nxt in list(self.adj[curr]):
                # Chi tranh cau neu con lua chon khac
                if len(self.adj[curr]) == 1 or not self.is_bridge(curr, nxt):
                    self.adj[curr].remove(nxt)
                    self.adj[nxt].remove(curr)
                    path.append(nxt)
                    curr = nxt
                    break
        return path 
    
class HierholzerEuler:
    def __init__(self, nodes, edges, logger = None):
        self.nodes = nodes
        self.edges = edges
        self.log = logger if logger else print

    def build_adj_list(self):
        adj = {node.id: [] for node in self.nodes}

        for edge in self.edges:
            u = edge.start_node.id
            v = edge.end_node.id
            adj[u].append(v)
            adj[v].append(u) #vo huong
        return adj
    
    def has_euler_circuit(self):
        adj = self.build_adj_list()

        for v in adj:
            if len(adj[v]) % 2 != 0:
                return False 
        return True 
    
    def hierholzer_algorithm(self):
        """
        Finds an Eulerian Circuit using Hierholzer's Algorithm.
        
        Args:
            nodes (list): List of Node objects.
            edges (list): List of Edge objects.
            
        Returns:
            list: A list of Node IDs representing the Eulerian circuit.
            Returns None if no such circuit exists.
        """
        if not self.has_euler_circuit():
            self.log("Do thi khong co chu trinh euler (ton tai dinh bac le)")
            return None
        
        adj = self.build_adj_list()
        stack = []
        circuit = []

        start = self.nodes[0].id
        curr = start
        self.log(f"Ton tai chu trinh Euler. Bat dau tai dinh {start}")

        while stack or adj[curr]:
            if not adj[curr]:
                circuit.append(curr)
                curr = stack.pop()
            else:
                stack.append(curr)
                nxt = adj[curr].pop()
                adj[nxt].remove(curr)
                curr = nxt
        circuit.append(curr)
        circuit.reverse()

        return circuit

def fleury_algorithm(nodes, edges):
    return FleuryEuler(nodes, edges).fleury_algorithm()

def hierholzer_algorithm(nodes, edges):
    return HierholzerEuler(nodes, edges).hierholzer_algorithm()
