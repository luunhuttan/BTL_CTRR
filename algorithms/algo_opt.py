# THÀNH VIÊN 3: Cài đặt logic bên trong các hàm này. Nhớ sử dụng `edge.weight` để tính toán.

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
    pass

def prim(nodes, edges):
    """
    Tìm Cây khung nhỏ nhất (MST) sử dụng thuật toán Prim.
    
    Tham số:
        nodes (list): Danh sách các đối tượng Node.
        edges (list): Danh sách các đối tượng Edge.
        
    Trả về:
        list: Danh sách các đối tượng Edge (hoặc tuple biểu diễn kết nối) tạo thành MST.
    """
    pass

def kruskal(nodes, edges):
    """
    Tìm Cây khung nhỏ nhất (MST) sử dụng thuật toán Kruskal.
    
    Tham số:
        nodes (list): Danh sách các đối tượng Node.
        edges (list): Danh sách các đối tượng Edge.
        
    Trả về:
        list: Danh sách các đối tượng Edge tạo thành MST.
    """
    pass

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
    pass
