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
    import json
    from datetime import datetime

    try:
        nodes_data = []
        for n in nodes:
            nodes_data.append({
                "id": int(n.id),
                "x": float(n.x),
                "y": float(n.y),
                "label": str(n.label) if getattr(n, 'label', None) is not None else str(n.id),
            })

        edges_data = []
        for e in edges:
            try:
                u = int(e.start_node.id)
                v = int(e.end_node.id)
            except Exception:
                # Skip malformed edges
                continue
            edges_data.append({
                "start": u,
                "end": v,
                "weight": int(getattr(e, 'weight', 1)),
            })

        payload = {
            "meta": {"saved_at": datetime.now().isoformat()},
            "nodes": nodes_data,
            "edges": edges_data,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        return True
    except Exception:
        return False

def load_graph_from_json(filename):
    """
    Đọc file JSON.
    
    Tham số:
        filename (str): Đường dẫn đến file.
        
    Trả về:
        tuple: (nodes_data, edges_data) trong đó nodes_data và edges_data là danh sách các dictionary.
    """
    import json
    try:
        with open(filename, "r", encoding="utf-8") as f:
            payload = json.load(f)

        nodes = payload.get("nodes") or []
        edges = payload.get("edges") or []

        # Normalise expected shapes
        nodes_out = []
        for n in nodes:
            if not isinstance(n, dict):
                continue
            nodes_out.append({
                "id": int(n.get("id")),
                "x": float(n.get("x", 0)),
                "y": float(n.get("y", 0)),
                "label": n.get("label", str(n.get("id")))
            })

        edges_out = []
        for e in edges:
            if not isinstance(e, dict):
                continue
            try:
                edges_out.append({
                    "start": int(e.get("start")),
                    "end": int(e.get("end")),
                    "weight": int(e.get("weight", 1)),
                })
            except Exception:
                continue

        return (nodes_out, edges_out)
    except Exception:
        return (None, None)

def convert_to_adjacency_matrix(nodes, edges):
    """
    Chuyển đổi đồ thị hiện tại thành chuỗi Ma trận kề để hiển thị.
    
    Tham số:
        nodes (list): Danh sách các đối tượng Node.
        edges (list): Danh sách các đối tượng Edge.
        
    Trả về:
        str: Chuỗi ma trận kề đã được định dạng.
    """
    # Build index mapping
    ids = sorted([int(n.id) for n in nodes])
    if not ids:
        return ""

    id_to_idx = {nid: i for i, nid in enumerate(ids)}
    n = len(ids)
    mat = [[0 for _ in range(n)] for _ in range(n)]
    for e in edges:
        try:
            u = int(e.start_node.id)
            v = int(e.end_node.id)
            w = int(getattr(e, 'weight', 1))
        except Exception:
            continue
        if u in id_to_idx and v in id_to_idx:
            mat[id_to_idx[u]][id_to_idx[v]] = w

    # Format as string
    header = "    " + " ".join([str(x) for x in ids])
    lines = [header]
    for i, row in enumerate(mat):
        lines.append(f"{ids[i]:>3} " + " ".join(str(x) for x in row))
    return "\n".join(lines)

def convert_to_adjacency_list(nodes, edges):
    """
    Chuyển đổi đồ thị hiện tại thành chuỗi Danh sách kề để hiển thị.
    
    Tham số:
        nodes (list): Danh sách các đối tượng Node.
        edges (list): Danh sách các đối tượng Edge.
        
    Trả về:
        str: Chuỗi danh sách kề đã được định dạng.
    """
    adj = {int(n.id): [] for n in nodes}
    for e in edges:
        try:
            u = int(e.start_node.id)
            v = int(e.end_node.id)
            w = int(getattr(e, 'weight', 1))
        except Exception:
            continue
        if u in adj:
            adj[u].append((v, w))

    lines = []
    for u in sorted(adj.keys()):
        neigh = ", ".join([f"{v}({w})" for v, w in sorted(adj[u])])
        lines.append(f"{u}: {neigh}")
    return "\n".join(lines)

def convert_to_edge_list(nodes, edges):
    """
    Chuyển đổi đồ thị hiện tại thành chuỗi Danh sách cạnh để hiển thị.
    
    Tham số:
        nodes (list): Danh sách các đối tượng Node.
        edges (list): Danh sách các đối tượng Edge.
        
    Trả về:
        str: Chuỗi danh sách cạnh đã được định dạng.
    """
    lines = []
    for e in edges:
        try:
            u = int(e.start_node.id)
            v = int(e.end_node.id)
            w = int(getattr(e, 'weight', 1))
        except Exception:
            continue
        lines.append(f"{u} -> {v} (w={w})")
    return "\n".join(lines)

def format_log(message, level=None):
    """
    Định dạng thông báo ngắn gọn, chuyên nghiệp bằng tiếng Việt.

    Thiết kế:
    - Không in thời gian.
    - Dùng nhãn ngắn (ví dụ: [THÔNG BÁO], [CẢNH BÁO], [LỖI], [THÀNH CÔNG]).
    - Nếu `message` đã bắt đầu bằng một nhãn dạng "[...]", giữ nguyên như là đầu vào đã định dạng.
    - Nếu `message` bắt đầu bằng tiền tố tiếng Việt như "Lỗi:", "Cảnh báo:", sẽ tự động chuyển thành nhãn tương ứng.

    Args:
        message (str): Nội dung thông báo.
        level (str|None): (tùy chọn) mức log mong muốn (ví dụ 'LỖI', 'CẢNH BÁO').

    Returns:
        str: Chuỗi đã định dạng, kết thúc bằng newline.
    """

    msg = str(message).strip()

    # Nếu caller đã truyền một chuỗi đã có định dạng '[...]' ở đầu, giữ nguyên.
    if msg.startswith("[") and "]" in msg.splitlines()[0]:
        out = msg
        if not out.endswith("\n"):
            out += "\n"
        return out

    # Chuẩn hóa nhãn nếu được cung cấp
    def _normalize_level(l):
        if l is None:
            return None
        s = str(l).strip().lower()
        mapping = {
            'ok': 'THÀNH CÔNG', 'success': 'THÀNH CÔNG', 'thành công': 'THÀNH CÔNG',
            'warn': 'CẢNH BÁO', 'warning': 'CẢNH BÁO', 'cảnh báo': 'CẢNH BÁO',
            'error': 'LỖI', 'lỗi': 'LỖI', 'fail': 'LỖI',
            'info': 'THÔNG BÁO', 'thông báo': 'THÔNG BÁO'
        }
        return mapping.get(s, str(l).strip().upper())

    label = _normalize_level(level)

    # Tự động nhận diện tiền tố tiếng Việt trong message (ví dụ "Lỗi:")
    if label is None:
        lowered = msg.lower()
        auto_map = [
            ('lỗi', 'LỖI'),
            ('cảnh báo', 'CẢNH BÁO'),
            ('thành công', 'THÀNH CÔNG'),
            ('thông báo', 'THÔNG BÁO'),
        ]
        for prefix, lab in auto_map:
            if lowered.startswith(prefix) or lowered.startswith(prefix + ':') or lowered.startswith(prefix + ' -'):
                label = lab
                # loại bỏ phần tiền tố để thông điệp gọn hơn
                rest = msg[len(prefix):].lstrip(' :.-—')
                if rest:
                    msg = rest
                break

    if label is None:
        label = 'THÔNG BÁO'

    formatted = f"[{label}] {msg}"
    if not formatted.endswith("\n"):
        formatted += "\n"
    return formatted
