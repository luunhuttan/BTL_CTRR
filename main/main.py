import customtkinter as ctk
from tkinter import simpledialog
import math
import datetime
import sys
import os

# Add parent directory to path to allow importing from 'data' and 'algorithms'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import separated modules
from graph_objects import Node, Edge
from app_ui import GraphGUI

# --- Configuration ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- Main Application (GUI Controller) ---
class GraphApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Window Setup
        self.title("QUẢN LÝ ĐỒ THỊ")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        # 2. Data Storage
        self.nodes = []
        self.edges = []
        self.node_counter = 1
        self.selected_node = None  # Tracks the first node clicked for edge creation

        # 3. Layout Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 4. Initialize UI via Helper Class
        self.ui = GraphGUI(self)
        
        self.log("Ứng dụng đã khởi động. Sẵn sàng.")

    # --- Core Logic: Logging & Drawing ---

    def log(self, message):
        """Appends a message to the log console with a timestamp."""
        if not hasattr(self, 'log_box'): return
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {message}\n"
        
        self.log_box.configure(state="normal")
        self.log_box.insert("end", full_msg)
        self.log_box.see("end") # Auto-scroll to bottom
        self.log_box.configure(state="disabled")

    def draw_graph(self):
        """Clears and redraws the entire graph."""
        if not hasattr(self, 'canvas'): return
        
        self.canvas.delete("all")
        
        # Draw Edges first (so they appear behind nodes)
        for edge in self.edges:
            edge.draw(self.canvas)
            
        # Draw Nodes
        for node in self.nodes:
            node.draw(self.canvas)
            
        # Highlight selected node if any
        if self.selected_node:
            x, y, r = self.selected_node.x, self.selected_node.y, self.selected_node.radius + 5
            self.canvas.create_oval(x-r, y-r, x+r, y+r, outline="yellow", width=3)

    # --- Interactive Mouse Logic ---

    def on_left_click(self, event):
        x, y = event.x, event.y
        clicked_node = self.get_node_at(x, y)

        if clicked_node:
            # Scenario: Clicked on a Node
            if self.selected_node is None:
                # First click -> Select
                self.selected_node = clicked_node
                self.log(f"Đã chọn Đỉnh {clicked_node.id}. Nhấn vào đỉnh khác để nối.")
            else:
                if self.selected_node == clicked_node:
                    # Clicked same node -> Deselect
                    self.selected_node = None
                    self.log("Đã bỏ chọn đỉnh.")
                else:
                    # Clicked different node -> Create Edge
                    self.add_edge(self.selected_node, clicked_node)
                    self.selected_node = None # Reset selection
        else:
            # Scenario: Clicked on Empty Space -> Create Node
            self.add_node(x, y)
            self.selected_node = None # Ensure selection is cleared
        
        self.draw_graph()

    def on_right_click(self, event):
        x, y = event.x, event.y
        
        # Check Node Hit
        clicked_node = self.get_node_at(x, y)
        if clicked_node:
            new_label = simpledialog.askstring("Đổi tên Đỉnh", f"Nhập tên mới cho Đỉnh {clicked_node.id}:", initialvalue=clicked_node.label)
            if new_label:
                clicked_node.label = new_label
                self.log(f"Đã đổi tên Đỉnh {clicked_node.id} thành '{new_label}'")
                self.draw_graph()
            return

        # Check Edge Hit
        clicked_edge = self.get_edge_at(x, y)
        if clicked_edge:
            new_weight = simpledialog.askinteger("Sửa Trọng số", "Nhập trọng số mới:", initialvalue=clicked_edge.weight)
            if new_weight is not None:
                clicked_edge.weight = new_weight
                self.log(f"Đã cập nhật trọng số cạnh thành {new_weight}")
                self.draw_graph()
            return

    # --- Helper Methods ---

    def get_node_at(self, x, y):
        for node in self.nodes:
            # Euclidean distance check
            dist = math.sqrt((node.x - x)**2 + (node.y - y)**2)
            if dist <= node.radius:
                return node
        return None

    def get_edge_at(self, x, y, threshold=15):
        for edge in self.edges:
            # Check distance to line segment
            # Simplified: Check distance to midpoint for now (easier to click label)
            mid_x = (edge.start_node.x + edge.end_node.x) / 2
            mid_y = (edge.start_node.y + edge.end_node.y) / 2
            dist = math.sqrt((mid_x - x)**2 + (mid_y - y)**2)
            if dist <= threshold:
                return edge
        return None

    def add_node(self, x, y):
        new_node = Node(self.node_counter, x, y)
        self.nodes.append(new_node)
        self.node_counter += 1
        self.log(f"Đỉnh {new_node.id} được tạo tại ({x}, {y})")

    def add_edge(self, start, end):
        # Check for duplicates
        for edge in self.edges:
            if (edge.start_node == start and edge.end_node == end):
                self.log("Cạnh đã tồn tại!")
                return

        new_edge = Edge(start, end)
        self.edges.append(new_edge)
        self.log(f"Đã nối Đỉnh {start.label} với Đỉnh {end.label}")

    def clear_canvas(self):
        self.nodes = []
        self.edges = []
        self.node_counter = 1
        self.selected_node = None
        self.draw_graph()
        self.log("Đã xóa bảng vẽ.")

    # --- Placeholder Methods (For Team Members) ---

    def run_bfs(self):
        self.log("BFS: Tính năng sắp ra mắt (Thành viên 2)...")
        # TODO: Connected to Member 2's code

    def run_dfs(self):
        self.log("DFS: Tính năng sắp ra mắt (Thành viên 2)...")
        # TODO: Connected to Member 2's code

    def run_dijkstra(self):
        self.log("Dijkstra: Tính năng sắp ra mắt (Thành viên 3)...")
        # TODO: Connected to Member 3's code

    def run_prim(self):
        self.log("Prim: Tính năng sắp ra mắt (Thành viên 3)...")
        # TODO: Connected to Member 3's code

    def run_check_bipartite(self):
        self.log("Kiểm tra 2 phía: Tính năng sắp ra mắt (Thành viên 2)...")
        # TODO: Connected to Member 2's code

    def run_kruskal(self):
        self.log("Kruskal: Tính năng sắp ra mắt (Thành viên 3)...")
        # TODO: Connected to Member 3's code

    def run_ford_fulkerson(self):
        self.log("Ford-Fulkerson: Tính năng sắp ra mắt (Thành viên 3)...")
        # TODO: Connected to Member 3's code

    def run_fleury(self):
        self.log("Fleury: Tính năng sắp ra mắt (Thành viên 3/6)...")
        # TODO: Connected to Member 3/6's code

    def run_hierholzer(self):
        self.log("Hierholzer: Tính năng sắp ra mắt (Thành viên 3/6)...")
        # TODO: Connected to Member 3/6's code

    def show_representations(self):
        self.log("Hiện Ma trận/DS kề: Tính năng sắp ra mắt (Thành viên 4)...")
        # TODO: Connected to Member 4's code

    def generate_random(self):
        self.log("Tạo đồ thị ngẫu nhiên: Tính năng sắp ra mắt (Thành viên 4)...")
        # TODO: Connected to Member 4's code

    def save_graph(self):
        self.log("Lưu file: Tính năng sắp ra mắt (Thành viên 5)...")
        # TODO: Connected to Member 5's code

    def load_graph(self):
        self.log("Đọc file: Tính năng sắp ra mắt (Thành viên 5)...")
        # TODO: Connected to Member 5's code

if __name__ == "__main__":
    app = GraphApp()
    app.mainloop()
