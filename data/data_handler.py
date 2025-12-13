# THÀNH VIÊN 4: Cài đặt logic. Bạn có thể dùng thư viện `json` và `datetime`.

def save_graph_to_json(filename, nodes, edges):
    """
    Lưu cấu trúc đồ thị vào file JSON.
    
    Tham số:
        filename (str): Đường dẫn đến file.
        nodes (list): Danh sách các đối tượng Node.
        edges (list): Danh sách các đối tượng Edge.
        
    Trả về:
        bool: True nếu thành công, False nếu thất bại.
    """
    pass

def load_graph_from_json(filename):
    """
    Đọc file JSON.
    
    Tham số:
        filename (str): Đường dẫn đến file.
        
    Trả về:
        tuple: (nodes_data, edges_data) trong đó nodes_data và edges_data là danh sách các dictionary.
    """
    pass

def convert_to_adjacency_matrix(nodes, edges):
    """
    Chuyển đổi đồ thị hiện tại thành chuỗi Ma trận kề để hiển thị.
    
    Tham số:
        nodes (list): Danh sách các đối tượng Node.
        edges (list): Danh sách các đối tượng Edge.
        
    Trả về:
        str: Chuỗi ma trận kề đã được định dạng.
    """
    pass

def convert_to_adjacency_list(nodes, edges):
    """
    Chuyển đổi đồ thị hiện tại thành chuỗi Danh sách kề để hiển thị.
    
    Tham số:
        nodes (list): Danh sách các đối tượng Node.
        edges (list): Danh sách các đối tượng Edge.
        
    Trả về:
        str: Chuỗi danh sách kề đã được định dạng.
    """
    pass

def convert_to_edge_list(nodes, edges):
    """
    Chuyển đổi đồ thị hiện tại thành chuỗi Danh sách cạnh để hiển thị.
    
    Tham số:
        nodes (list): Danh sách các đối tượng Node.
        edges (list): Danh sách các đối tượng Edge.
        
    Trả về:
        str: Chuỗi danh sách cạnh đã được định dạng.
    """
    pass

def format_log(message):
    """
    Thêm dấu thời gian vào chuỗi thông báo.
    
    Tham số:
        message (str): Nội dung thông báo.
        
    Trả về:
        str: Chuỗi đã được định dạng (ví dụ: "[10:00:00] Thông báo").
    """
    pass
