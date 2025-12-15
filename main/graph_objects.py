import tkinter as tk
import math
import heapq
from collections import deque

# --- Global Helpers for Algorithms ---
g_heapq = heapq
g_deque = deque

def g_node_ids(nodes):
    return [n.id for n in nodes]

def g_build_directed_adj(edges):
    adj = {}
    for edge in edges:
        u = edge.start_node.id
        v = edge.end_node.id
        w = edge.weight
        if u not in adj: adj[u] = []
        adj[u].append((v, w, edge))
    return adj

def g_build_undirected_adj(edges):
    adj = {}
    for edge in edges:
        u = edge.start_node.id
        v = edge.end_node.id
        w = edge.weight
        
        if u not in adj: adj[u] = []
        adj[u].append((v, w, edge))
        
        if v not in adj: adj[v] = []
        adj[v].append((u, w, edge))
    return adj

class Node:
    def __init__(self, id, x, y, label=None):
        self.id = int(id)
        self.x = float(x)
        self.y = float(y)
        self.label = label if label else str(id)
        self.radius = 20
        self.color = "#3B8ED0"  # Modern Blue/Cyan
        self.text_color = "white"

    def draw(self, canvas):
        x0, y0 = self.x - self.radius, self.y - self.radius
        x1, y1 = self.x + self.radius, self.y + self.radius
        
        # Vẽ hình tròn với viền sạch sẽ
        canvas.create_oval(x0, y0, x1, y1, fill=self.color, outline="white", width=2)
        
        # Vẽ nhãn ở giữa
        canvas.create_text(self.x, self.y, text=self.label, fill=self.text_color, font=("Roboto", 12, "bold"))

class Edge:
    def __init__(self, start_node, end_node, weight=1):
        self.start_node = start_node
        self.end_node = end_node
        self.weight = int(weight)
        self.color = "gray70"

    def draw(self, canvas, is_directed=True, show_weight=True, curve_offset=0):
        # Tính toán điểm đầu và điểm cuối
        start_x, start_y = self.start_node.x, self.start_node.y
        end_x, end_y = self.end_node.x, self.end_node.y
        
        # Tính toán vector để rút ngắn đoạn thẳng sao cho mũi tên hiển thị rõ (không bị đỉnh che mất)
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Rút ngắn bằng bán kính đỉnh (20) + một khoảng đệm nhỏ
            shorten_len = self.end_node.radius + 2 
            ratio = shorten_len / distance
            end_x = end_x - dx * ratio
            end_y = end_y - dy * ratio
        
        # Vẽ đường (thẳng hoặc cong). Nếu có 2 chiều (u->v và v->u) thì dùng cong để khỏi chồng lên nhau.
        arrow_opt = tk.LAST if is_directed else None

        if curve_offset:
            # Dùng đường cong bậc 2: start -> control -> end
            dx = end_x - start_x
            dy = end_y - start_y
            dist = math.sqrt(dx**2 + dy**2) or 1.0
            # vector pháp tuyến đơn vị
            nx = -dy / dist
            ny = dx / dist
            mx = (start_x + end_x) / 2
            my = (start_y + end_y) / 2
            cx = mx + nx * curve_offset
            cy = my + ny * curve_offset

            canvas.create_line(
                start_x,
                start_y,
                cx,
                cy,
                end_x,
                end_y,
                fill=self.color,
                width=2,
                smooth=True,
                arrow=arrow_opt,
            )

            # Midpoint gần đúng tại t=0.5 của Bezier bậc 2
            mid_x = (start_x + 2 * cx + end_x) / 4
            mid_y = (start_y + 2 * cy + end_y) / 4
        else:
            canvas.create_line(
                start_x,
                start_y,
                end_x,
                end_y,
                fill=self.color,
                width=2,
                smooth=True,
                arrow=arrow_opt,
            )
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2

        if show_weight:
            text = str(self.weight)
            canvas.create_rectangle(mid_x - 10, mid_y - 10, mid_x + 10, mid_y + 10, fill="#2b2b2b", outline="")
            canvas.create_text(mid_x, mid_y, text=text, fill="gray90", font=("Roboto", 10))
