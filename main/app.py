import customtkinter as ctk
from tkinter import simpledialog, Menu
import math
import datetime
import sys
import os

# Add parent directory to path to allow importing from 'data' and 'algorithms'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Remove the script directory from sys.path to avoid 'main.py' shadowing 'main' package
try:
    sys.path.remove(os.path.dirname(__file__))
except ValueError:
    pass

# Import separated modules
from main.graph_objects import Node, Edge
from main.app_ui import GraphGUI
from custom.algorithm_runner import AlgorithmRunner
from algorithms.algo_traversal import bfs, dfs, check_bipartite
from data.generator import RandomGraphGenerator
from data.data_handler import format_log, save_graph_to_json, load_graph_from_json, convert_to_adjacency_list, convert_to_adjacency_matrix, convert_to_edge_list
from tkinter import filedialog

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
        self.is_directed = True # Default to directed graph

        # 3. Layout Configuration
        self.grid_columnconfigure(0, weight=0) # Sidebar (fixed width)
        self.grid_columnconfigure(1, weight=1) # Canvas (expands)
        self.grid_columnconfigure(2, weight=0) # Right Panel (fixed width)
        self.grid_rowconfigure(0, weight=1)

        # 4. Initialize UI via Helper Class
        self.ui = GraphGUI(self)
        self.algo_runner = AlgorithmRunner(self)
        
        self.log("Ứng dụng đã khởi động. Sẵn sàng.", level='THÔNG BÁO')

    # --- Core Logic: Logging & Drawing ---

    def log(self, message, level=None):
        """Appends a message to the log console."""
        # Use centralized formatter to produce concise, professional Vietnamese logs
        full_msg = format_log(message, level)

        # Prefer card-based container if available
        if hasattr(self, 'log_container'):
            try:
                # Parse label and message text from formatted string: "[LABEL] text"
                first = full_msg.splitlines()[0]
                if first.startswith('[') and ']' in first:
                    parsed_label = first.split(']')[0].lstrip('[').strip()
                    parsed_text = first.split('] ', 1)[1] if '] ' in first else first.split(']', 1)[1].strip()
                else:
                    parsed_label = (level or 'THÔNG BÁO').upper()
                    parsed_text = first
                self.add_log_card(parsed_text, parsed_label)
            except Exception:
                # If anything fails, fallback to textbox if present
                if hasattr(self, 'log_box'):
                    self.log_box.configure(state="normal")
                    self.log_box.insert("end", full_msg)
                    self.log_box.see("end")
                    self.log_box.configure(state="disabled")
        else:
            if not hasattr(self, 'log_box'): return
            self.log_box.configure(state="normal")
            self.log_box.insert("end", full_msg)
            self.log_box.see("end") # Auto-scroll to bottom
            self.log_box.configure(state="disabled")

    def clear_log(self):
        """Clears the log console."""
        # Clear card-based container if present
        if hasattr(self, 'log_container'):
            try:
                for w in list(self.log_container.winfo_children()):
                    w.destroy()
                return
            except Exception:
                pass

        if not hasattr(self, 'log_box'): return
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def add_log_card(self, message, level=None):
        """Create a small rounded card in the log container showing the message and icon/color by level."""
        if not hasattr(self, 'log_container'):
            return

        # Color & icon mapping
        cmap = {
            'THÔNG BÁO': ('#3498db', 'ℹ️'),
            'THÀNH CÔNG': ('#2ecc71', '✅'),
            'CẢNH BÁO': ('#f1c40f', '⚠️'),
            'LỖI': ('#e74c3c', '❌'),
            'THUẬT TOÁN': ('#8e44ad', '⚙️')
        }
        col, icon = cmap.get(level, ('#7f8c8d', 'ℹ️'))

        # Card frame
        card = ctk.CTkFrame(self.log_container, fg_color="#2b2b2b", corner_radius=8, border_width=1)
        card.grid_columnconfigure(2, weight=1)
        # place card in column 0 so it expands to full container width
        card.grid(sticky="ew", padx=6, pady=6, column=0)

        # Left colored bar (use Tk frame for solid color)
        try:
            left_bar = tk.Frame(card, width=6, bg=col)
            left_bar.grid(row=0, column=0, rowspan=2, sticky="nsw", padx=(0,6))
        except Exception:
            pass

        # Icon
        lbl_icon = ctk.CTkLabel(card, text=icon, width=28, height=28, text_color=col, anchor="center", font=ctk.CTkFont(size=14))
        lbl_icon.grid(row=0, column=1, sticky="nw", padx=(0,6), pady=6)

        # Message label (strip trailing newline)
        txt = str(message).rstrip('\n')
        lbl_msg = ctk.CTkLabel(card, text=txt, anchor="w", justify="left", wraplength=1, text_color="#e0e0e0")
        lbl_msg.grid(row=0, column=2, sticky="nsew", padx=(0,6), pady=6)

        # Adjust wraplength after layout so long messages wrap to available width
        def _apply_wrap():
            try:
                # ensure geometry is calculated
                self.log_container.update_idletasks()
                w = self.log_container.winfo_width() or getattr(self.log_container, '_canvas', None) and self.log_container._canvas.winfo_width() or 300
                # subtract margins/columns (left icon + paddings)
                wrap = max(int(w - 120), 80)
                lbl_msg.configure(wraplength=wrap)
            except Exception:
                pass

        # schedule immediate adjust and ensure future resizes update wraps
        try:
            _apply_wrap()
            if not hasattr(self, '_log_wrap_bound') or not self._log_wrap_bound:
                self._log_wrap_bound = True
                try:
                    self.log_container.bind('<Configure>', lambda e: self._update_log_wraps())
                except Exception:
                    pass
        except Exception:
            pass

        # Small level caption (optional)
        try:
            lbl_level = ctk.CTkLabel(card, text=f"{level}", anchor="e", text_color="gray60", font=ctk.CTkFont(size=10))
            lbl_level.grid(row=1, column=2, sticky="se", padx=(0,6), pady=(0,6))
        except Exception:
            pass

        # Try to scroll to bottom of the scrollable frame
        try:
            if hasattr(self.ui.log_container, 'yview_moveto'):
                self.ui.log_container.yview_moveto(1.0)
            elif hasattr(self.log_container, '_canvas'):
                self.log_container._canvas.yview_moveto(1.0)
        except Exception:
            pass

    def _update_log_wraps(self):
        """Recompute wraplength for all message labels inside log cards when container resizes."""
        try:
            self.log_container.update_idletasks()
            w = self.log_container.winfo_width() or getattr(self.log_container, '_canvas', None) and self.log_container._canvas.winfo_width() or 300
            wrap = max(int(w - 120), 80)
            for card in self.log_container.winfo_children():
                for child in card.winfo_children():
                    try:
                        # update CTkLabel instances (message labels)
                        if isinstance(child, ctk.CTkLabel):
                            # heuristic: update labels that likely are messages (justify left)
                            if getattr(child, 'configure', None):
                                child.configure(wraplength=wrap)
                    except Exception:
                        continue
        except Exception:
            pass

    def draw_graph(self):
        """Clears and redraws the entire graph."""
        if not hasattr(self, 'canvas'): return
        
        self.canvas.delete("all")
        
        # Draw Edges first (so they appear behind nodes)
        for edge in self.edges:
            edge.draw(self.canvas, self.is_directed)
            
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
                self.log(f"Đã chọn Đỉnh {clicked_node.id}. Nhấn vào đỉnh khác để nối.", level='THÔNG BÁO')
            else:
                if self.selected_node == clicked_node:
                    # Clicked same node -> Deselect
                    self.selected_node = None
                    self.log("Đã bỏ chọn đỉnh.", level='THÔNG BÁO')
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
        self.clicked_node = self.get_node_at(x, y)
        if self.clicked_node:
            # Create context menu for Node
            menu = Menu(self, tearoff=0)
            menu.add_command(label="Đổi tên", command=self.rename_node_action)
            menu.add_command(label="Xóa đỉnh", command=self.delete_node_action)
            menu.tk_popup(event.x_root, event.y_root)
            return

        # Check Edge Hit
        clicked_edge = self.get_edge_at(x, y)
        if clicked_edge:
            new_weight = simpledialog.askinteger("Sửa Trọng số", "Nhập trọng số mới:", initialvalue=clicked_edge.weight)
            if new_weight is not None:
                clicked_edge.weight = new_weight
                self.log(f"Đã cập nhật trọng số cạnh thành {new_weight}", level='THÀNH CÔNG')
                self.draw_graph()
            return

    def rename_node_action(self):
        if self.clicked_node:
            new_label = simpledialog.askstring("Đổi tên Đỉnh", f"Nhập tên mới cho Đỉnh {self.clicked_node.id}:", initialvalue=self.clicked_node.label)
            if new_label:
                self.clicked_node.label = new_label
                self.log(f"Đã đổi tên Đỉnh {self.clicked_node.id} thành '{new_label}'", level='THÀNH CÔNG')
                self.draw_graph()
            self.clicked_node = None

    def delete_node_action(self):
        if self.clicked_node:
            self.delete_node(self.clicked_node)
            self.clicked_node = None

    def delete_node(self, node):
        # Remove edges connected to node
        self.edges = [e for e in self.edges if e.start_node != node and e.end_node != node]
        # Remove node
        self.nodes.remove(node)
        # Clear selection if it was selected
        if self.selected_node == node:
            self.selected_node = None
        
        self.log(f"Đã xóa Đỉnh {node.id}", level='THÔNG BÁO')
        self.draw_graph()

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
        self.log(f"Đỉnh {new_node.id} được tạo tại ({x}, {y})", level='THÀNH CÔNG')

    def add_edge(self, start, end):
        # Check for duplicates
        for edge in self.edges:
            if (edge.start_node == start and edge.end_node == end):
                self.log("Cạnh đã tồn tại!", level='CẢNH BÁO')
                return

        new_edge = Edge(start, end)
        self.edges.append(new_edge)
        self.log(f"Đã nối Đỉnh {start.label} với Đỉnh {end.label}", level='THÀNH CÔNG')

    def clear_canvas(self):
        if hasattr(self, 'algo_runner'):
            self.algo_runner.cancel_animation()
        self.nodes = []
        self.edges = []
        self.node_counter = 1
        self.selected_node = None
        self.draw_graph()
        self.log("Đã xóa bảng vẽ.", level='THÔNG BÁO')

    def toggle_directed(self):
        self.is_directed = not self.is_directed
        mode = "Có hướng" if self.is_directed else "Vô hướng"
        self.log(f"Đã chuyển sang chế độ đồ thị: {mode}", level='THÔNG BÁO')
        self.draw_graph()

    # --- Placeholder Methods (For Team Members) ---

    def run_bfs(self):
        self.algo_runner.run_bfs()

    def run_dfs(self):
        self.algo_runner.run_dfs()

    def run_dijkstra(self):
        self.algo_runner.run_dijkstra()

    def run_prim(self):
        self.algo_runner.run_prim()

    def run_check_bipartite(self):
        self.algo_runner.run_check_bipartite()

    def run_kruskal(self):
        self.algo_runner.run_kruskal()

    def run_ford_fulkerson(self):
        self.algo_runner.run_ford_fulkerson()

    def run_fleury(self):
        self.log("Fleury: Tính năng sắp ra mắt (Thành viên 3/6)...", level='THÔNG BÁO')
        # TODO: Connected to Member 3/6's code

    def run_hierholzer(self):
        self.log("Hierholzer: Tính năng sắp ra mắt (Thành viên 3/6)...", level='THÔNG BÁO')
        # TODO: Connected to Member 3/6's code

    def show_representations(self):
        self.log("Hiện Ma trận/DS kề: Tính năng sắp ra mắt (Thành viên 4)...", level='THÔNG BÁO')
        # TODO: Connected to Member 4's code

    def generate_random(self):
        num_nodes = simpledialog.askinteger("Tạo ngẫu nhiên", "Nhập số lượng đỉnh (5-20):", minvalue=5, maxvalue=20)
        if not num_nodes:
            return

        self.clear_canvas()
        
        # Get canvas dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 100: width = 800 # Fallback if not rendered yet
        if height < 100: height = 600

        generator = RandomGraphGenerator()
        node_data, edge_data = generator.generate_random_graph(num_nodes, width, height)

        # Create Nodes
        for nid, x, y in node_data:
            self.nodes.append(Node(nid, x, y))
        self.node_counter = num_nodes + 1

        # Create Edges
        node_map = {n.id: n for n in self.nodes}
        for u_id, v_id, w in edge_data:
            if u_id in node_map and v_id in node_map:
                self.edges.append(Edge(node_map[u_id], node_map[v_id], w))

        self.draw_graph()
        self.log(f"Đã tạo đồ thị ngẫu nhiên với {len(self.nodes)} đỉnh và {len(self.edges)} cạnh.", level='THÀNH CÔNG')

    def save_graph(self):
        # Save current graph to a JSON file (asks user for path)
        if not self.nodes:
            self.log("Không có đồ thị để lưu.", level='CẢNH BÁO')
            return

        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], initialfile="graph.json")
        if not path:
            return

        ok = save_graph_to_json(path, self.nodes, self.edges)
        if ok:
            self.log(f"Đã lưu file: {os.path.basename(path)}", level='THÀNH CÔNG')
        else:
            self.log(f"Không lưu được file: {os.path.basename(path)}", level='LỖI')

    def load_graph(self):
        # Load graph from a JSON file (asks user for path)
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return

        nodes_data, edges_data = load_graph_from_json(path)
        if nodes_data is None:
            self.log(f"Không đọc được file: {os.path.basename(path)}", level='LỖI')
        # Log panel state and default size
        self.log_collapsed = False
        self._right_panel_width = 300
        self.grid_columnconfigure(3, minsize=self._right_panel_width)
        self._grip_dragging = False
        self._grip_start_x = None
        self._grip_start_width = None


        # Clear existing
        if hasattr(self, 'algo_runner'):
            self.algo_runner.cancel_animation()
        self.nodes = []
        self.edges = []

        # Recreate nodes
        for nd in nodes_data:
            try:
                nid = int(nd.get('id'))
                x = float(nd.get('x', 100))
                y = float(nd.get('y', 100))
                label = nd.get('label', str(nid))
                self.nodes.append(Node(nid, x, y, label))
            except Exception:
                continue


    # --- Log panel control (collapse / resize) ---
    def toggle_log(self):
        """Collapse or expand the right log panel."""
        if not hasattr(self, 'ui'):
            return

        if self.log_collapsed:
            # expand
            self.ui.right_panel.grid()
            self.ui.grip.grid()
            self.grid_columnconfigure(3, minsize=self._right_panel_width)
            try:
                self.ui.btn_toggle_log.configure(text='◀')
            except Exception:
                pass
            self.log_collapsed = False
        else:
            # collapse
            # remember current width
            try:
                info = self.ui.right_panel.winfo_width()
                if info > 50:
                    self._right_panel_width = info
            except Exception:
                pass
            self.ui.right_panel.grid_remove()
            self.ui.grip.grid_remove()
            self.grid_columnconfigure(3, minsize=0)
            try:
                self.ui.btn_toggle_log.configure(text='▶')
            except Exception:
                pass
            self.log_collapsed = True

    def start_grip_drag(self, event):
        self._grip_dragging = True
        # record absolute x
        self._grip_start_x = event.x_root
        self._grip_start_width = self.ui.right_panel.winfo_width()

    def grip_drag(self, event):
        if not self._grip_dragging:
            return
        try:
            dx = event.x_root - self._grip_start_x
            # moving mouse left (negative dx) increases width; adjust sign
            new_w = max(120, int(self._grip_start_width - dx))
            self._right_panel_width = new_w
            self.grid_columnconfigure(3, minsize=new_w)
            try:
                self.ui.right_panel.configure(width=new_w)
            except Exception:
                pass
        except Exception:
            pass

    def end_grip_drag(self, event):
        self._grip_dragging = False
        self._grip_start_x = None
        self._grip_start_width = None
        node_map = {int(n.id): n for n in self.nodes}

        # Recreate edges
        for ed in edges_data:
            try:
                u = int(ed.get('start'))
                v = int(ed.get('end'))
                w = int(ed.get('weight', 1))
                if u in node_map and v in node_map:
                    self.edges.append(Edge(node_map[u], node_map[v], w))
            except Exception:
                continue

        # Update counter
        max_id = max([int(n.id) for n in self.nodes], default=0)
        self.node_counter = max_id + 1

        self.draw_graph()
        self.log(f"Đã đọc file: {os.path.basename(path)} ({len(self.nodes)} đỉnh, {len(self.edges)} cạnh)", level='THÀNH CÔNG')

if __name__ == "__main__":
    app = GraphApp()
    app.mainloop()
