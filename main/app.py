import customtkinter as ctk
import tkinter as tk
from tkinter import simpledialog, Menu
import math
import datetime
import sys
import os
from tkinter import TclError

# Add parent directory to path to allow importing from 'data' and 'algorithms'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Remove the script directory from sys.path to avoid 'main.py' shadowing 'main' package
try:
    sys.path.remove(os.path.dirname(__file__))
except ValueError:
    pass

# Import separated modules
from main.graph_objects import Node, Edge
from custom.app_ui import GraphGUI
from custom.algorithm_runner import AlgorithmRunner
from algorithms.algo_traversal import bfs, dfs, check_bipartite
from data.generator import RandomGraphGenerator
from data.data_handler import format_log, save_graph_to_json, load_graph_from_json, convert_to_adjacency_list, convert_to_adjacency_matrix, convert_to_edge_list
from tkinter import filedialog

# --- Configuration ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def _patch_customtkinter_ctkbutton_anchor():
    """Compatibility patch for some CustomTkinter versions on newer Python.

    Symptom: periodic DPI scaling callback crashes with
    AttributeError: 'CTkButton' object has no attribute '_anchor'
    coming from customtkinter CTkButton._create_grid().

    This patch makes _set_scaling() resilient by ensuring _anchor exists.
    """

    try:
        btn_cls = getattr(ctk, "CTkButton", None)
        if btn_cls is None:
            return
        original = getattr(btn_cls, "_set_scaling", None)
        if original is None:
            return
        if getattr(btn_cls, "__btl_anchor_patch__", False):
            return

        def _set_scaling_safe(self, *args, **kwargs):
            if not hasattr(self, "_anchor"):
                try:
                    self._anchor = getattr(self, "anchor", "center")
                except Exception:
                    self._anchor = "center"
            try:
                return original(self, *args, **kwargs)
            except (AttributeError, TclError):
                # Ignore scaling updates on partially destroyed widgets.
                return None

        btn_cls._set_scaling = _set_scaling_safe
        btn_cls.__btl_anchor_patch__ = True
    except Exception:
        # Never block app startup due to a compatibility patch.
        return


_patch_customtkinter_ctkbutton_anchor()

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
        self.show_weights = True

        # Drag state (node / edge)
        self._press_x = None
        self._press_y = None
        self._press_node = None
        self._press_edge = None
        self._dragging_mode = None  # None | 'node' | 'edge'
        self._did_drag = False

        # Prevent after()-based animation loops from keeping the app alive
        self._closing = False
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # 3. Layout Configuration
        self.grid_columnconfigure(0, weight=0) # Sidebar (fixed width)
        self.grid_columnconfigure(1, weight=1) # Canvas (expands)
        self.grid_columnconfigure(2, weight=0) # Right Panel (fixed width)
        self.grid_rowconfigure(0, weight=1)

        # 4. Initialize UI via Helper Class
        self.ui = GraphGUI(self)
        self.algo_runner = AlgorithmRunner(self)
        
        self.log("Ứng dụng đã khởi động. Sẵn sàng.", level='THÔNG BÁO')

    def on_close(self):
        """Safely stop animations and close the window."""
        self._closing = True
        try:
            if hasattr(self, 'algo_runner') and self.algo_runner is not None:
                self.algo_runner.cancel_animation()
        except Exception:
            pass
        try:
            self.quit()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass

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
                try:
                    self.after(0, self._refresh_log_scrollregion)
                except Exception:
                    pass
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
            'THÀNH CÔNG': ("#2ecc92", '✅'),
            'CẢNH BÁO': ('#f1c40f', '⚠️'),
            'LỖI': ('#e74c3c', '❌'),
            'THUẬT TOÁN': ('#8e44ad', '⚙️')
        }
        col, icon = cmap.get(level, ('#7f8c8d', 'ℹ️'))

        # Card frame
        card = ctk.CTkFrame(self.log_container, fg_color="#2b2b2b", corner_radius=6)
        card.grid_columnconfigure(1, weight=1)
        card.grid(sticky="ew", padx=5, pady=3, column=0)

        # Keep scrollregion in sync as cards change height (wrap/resize)
        try:
            card.bind('<Configure>', lambda e: self.after(0, self._refresh_log_scrollregion))
        except Exception:
            pass

        # Icon
        lbl_icon = ctk.CTkLabel(card, text=icon, width=30, text_color=col, font=ctk.CTkFont(size=16))
        lbl_icon.grid(row=0, column=0, sticky="nw", padx=(5,0), pady=5)

        # Message label
        txt = str(message).rstrip('\n')
        lbl_msg = ctk.CTkLabel(card, text=txt, anchor="w", justify="left", text_color="#e0e0e0", font=ctk.CTkFont(size=12))
        lbl_msg.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Tag the label for easier identification in _update_log_wraps
        lbl_msg.is_log_message = True

        # Bind configure event to update wraps
        if not hasattr(self, '_log_wrap_bound') or not self._log_wrap_bound:
            self._log_wrap_bound = True
            try:
                self.log_container.bind('<Configure>', lambda e: self._update_log_wraps())
            except Exception:
                pass

        # Initial wrap update
        self.after(10, self._update_log_wraps)

        # Ensure scroll range grows with new content
        self.after(20, self._refresh_log_scrollregion)

        # Auto-scroll to bottom
        self.after(50, self._scroll_log_to_bottom)

    def _get_log_canvas(self):
        """Return the underlying canvas used by CTkScrollableFrame if available."""
        if not hasattr(self, 'log_container'):
            return None
        return getattr(self.log_container, '_parent_canvas', None) or getattr(self.log_container, '_canvas', None)

    def _refresh_log_scrollregion(self):
        """Force-update scrollregion so the scrollbar can reach all log cards."""
        try:
            if not hasattr(self, 'log_container'):
                return
            self.log_container.update_idletasks()
            canvas = self._get_log_canvas()
            if canvas is None:
                return
            bbox = canvas.bbox('all')
            if bbox is None:
                return
            canvas.configure(scrollregion=bbox)
        except Exception:
            pass

    def _scroll_log_to_bottom(self):
        try:
            self.log_container.update_idletasks()
            self._refresh_log_scrollregion()
            # For CTkScrollableFrame, we need to scroll the parent canvas
            if hasattr(self.log_container, '_parent_canvas'):
                self.log_container._parent_canvas.yview_moveto(1.0)
            elif hasattr(self.log_container, '_canvas'):
                self.log_container._canvas.yview_moveto(1.0)
        except Exception:
            pass

    def _update_log_wraps(self):
        """Recompute wraplength for all message labels inside log cards when container resizes."""
        try:
            self.log_container.update_idletasks()
            # Calculate available width
            w = 0
            if hasattr(self.log_container, '_parent_canvas'):
                w = self.log_container._parent_canvas.winfo_width()
            elif hasattr(self.log_container, '_canvas'):
                w = self.log_container._canvas.winfo_width()
            else:
                w = self.log_container.winfo_width()
            
            # Subtract padding and icon width (approx 60px)
            wrap = max(int(w - 60), 100)
            
            for card in self.log_container.winfo_children():
                for child in card.winfo_children():
                    if isinstance(child, ctk.CTkLabel) and getattr(child, 'is_log_message', False):
                        child.configure(wraplength=wrap)

            # Wrapping changes height -> refresh scroll range
            self._refresh_log_scrollregion()
        except Exception:
            pass

    def draw_graph(self):
        """Clears and redraws the entire graph."""
        if not hasattr(self, 'canvas'): return
        
        self.canvas.delete("all")
        
        # Draw Edges first (so they appear behind nodes)
        directed_pairs = set()
        if self.is_directed:
            for e in self.edges:
                directed_pairs.add((int(e.start_node.id), int(e.end_node.id)))

        for edge in self.edges:
            curve_offset = self._get_edge_curve_offset(edge, directed_pairs)
            edge.draw(self.canvas, self.is_directed, show_weight=self.show_weights, curve_offset=curve_offset)
            
        # Draw Nodes
        for node in self.nodes:
            node.draw(self.canvas)
            
        # Highlight selected node if any
        if self.selected_node:
            x, y, r = self.selected_node.x, self.selected_node.y, self.selected_node.radius + 5
            self.canvas.create_oval(x-r, y-r, x+r, y+r, outline="yellow", width=3)

    # --- Interactive Mouse Logic ---

    def _get_edge_curve_offset(self, edge, directed_pairs=None):
        if directed_pairs is None:
            directed_pairs = set()
            if self.is_directed:
                for e in self.edges:
                    directed_pairs.add((int(e.start_node.id), int(e.end_node.id)))

        base = 0
        if self.is_directed:
            u = int(edge.start_node.id)
            v = int(edge.end_node.id)
            if u != v and (v, u) in directed_pairs:
                base = 28 if u < v else -28

        user = 0
        try:
            user = float(getattr(edge, 'user_curve_offset', 0) or 0)
        except Exception:
            user = 0

        total = base + user
        if abs(total) < 0.5:
            return 0
        return total

    def on_left_press(self, event):
        self._press_x = event.x
        self._press_y = event.y
        self._did_drag = False
        self._dragging_mode = None

        self._press_node = self.get_node_at(event.x, event.y)
        self._press_edge = None
        if self._press_node is None:
            self._press_edge = self.get_edge_at(event.x, event.y)

        # Do not change selection here; decide on release unless it becomes a drag.

    def on_left_drag(self, event):
        if self._press_x is None or self._press_y is None:
            return

        dx = event.x - self._press_x
        dy = event.y - self._press_y
        if not self._did_drag and (dx * dx + dy * dy) < 9:
            return

        self._did_drag = True

        # Drag node
        if self._press_node is not None:
            self._dragging_mode = 'node'
            self._press_node.x = float(event.x)
            self._press_node.y = float(event.y)
            self.draw_graph()
            return

        # Drag edge -> adjust curve offset
        if self._press_edge is not None:
            self._dragging_mode = 'edge'
            e = self._press_edge
            directed_pairs = set()
            if self.is_directed:
                for ed in self.edges:
                    directed_pairs.add((int(ed.start_node.id), int(ed.end_node.id)))
            base = 0
            if self.is_directed:
                u = int(e.start_node.id)
                v = int(e.end_node.id)
                if u != v and (v, u) in directed_pairs:
                    base = 28 if u < v else -28

            sx, sy = float(e.start_node.x), float(e.start_node.y)
            ex, ey = float(e.end_node.x), float(e.end_node.y)
            vx, vy = ex - sx, ey - sy
            dist = math.sqrt(vx * vx + vy * vy) or 1.0
            nx, ny = -vy / dist, vx / dist
            mx, my = (sx + ex) / 2.0, (sy + ey) / 2.0
            px, py = float(event.x), float(event.y)

            # projection onto normal gives desired total curve offset
            desired_total = (px - mx) * nx + (py - my) * ny
            # store only user adjustment so base still applies
            e.user_curve_offset = float(desired_total - base)
            self.draw_graph()
            return

    def on_left_release(self, event):
        # If user dragged, do not treat as click-to-connect.
        if self._did_drag:
            self._press_x = None
            self._press_y = None
            self._press_node = None
            self._press_edge = None
            self._dragging_mode = None
            return

        x, y = event.x, event.y
        clicked_node = self.get_node_at(x, y)

        if clicked_node:
            if self.selected_node is None:
                self.selected_node = clicked_node
                self.log(f"Đã chọn Đỉnh {clicked_node.id}. Nhấn vào đỉnh khác để nối.", level='THÔNG BÁO')
            else:
                if self.selected_node == clicked_node:
                    self.selected_node = None
                    self.log("Đã bỏ chọn đỉnh.", level='THÔNG BÁO')
                else:
                    self.add_edge(self.selected_node, clicked_node)
                    self.selected_node = None
        else:
            # Click empty: create node
            self.add_node(x, y)
            self.selected_node = None

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
        self.clicked_edge = self.get_edge_at(x, y)
        if self.clicked_edge:
            menu = Menu(self, tearoff=0)
            menu.add_command(label="Sửa trọng số", command=self.edit_edge_weight_action)
            menu.add_command(label="Xóa cạnh", command=self.delete_edge_action)
            menu.tk_popup(event.x_root, event.y_root)
            return

    def edit_edge_weight_action(self):
        if not getattr(self, 'clicked_edge', None):
            return
        clicked_edge = self.clicked_edge
        new_weight = simpledialog.askinteger("Sửa Trọng số", "Nhập trọng số mới:", initialvalue=clicked_edge.weight)
        if new_weight is not None:
            clicked_edge.weight = new_weight
            self.log(f"Đã cập nhật trọng số cạnh thành {new_weight}", level='THÀNH CÔNG')
            self.draw_graph()
        self.clicked_edge = None

    def delete_edge_action(self):
        if not getattr(self, 'clicked_edge', None):
            return
        e = self.clicked_edge
        try:
            self.edges.remove(e)
        except ValueError:
            pass
        self.log(f"Đã xóa cạnh {e.start_node.label} → {e.end_node.label}", level='THÔNG BÁO')
        self.clicked_edge = None
        self.draw_graph()

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
        directed_pairs = set()
        if self.is_directed:
            for e in self.edges:
                directed_pairs.add((int(e.start_node.id), int(e.end_node.id)))

        for edge in self.edges:
            # Check distance to midpoint (straight) or midpoint of curve (approx)
            mid_x = (edge.start_node.x + edge.end_node.x) / 2
            mid_y = (edge.start_node.y + edge.end_node.y) / 2

            curve_offset = self._get_edge_curve_offset(edge, directed_pairs)
            if curve_offset:
                dx = edge.end_node.x - edge.start_node.x
                dy = edge.end_node.y - edge.start_node.y
                dist0 = math.sqrt(dx**2 + dy**2) or 1.0
                nx = -dy / dist0
                ny = dx / dist0
                cx = mid_x + nx * curve_offset
                cy = mid_y + ny * curve_offset
                mid_x = (edge.start_node.x + 2 * cx + edge.end_node.x) / 4
                mid_y = (edge.start_node.y + 2 * cy + edge.end_node.y) / 4

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
        # Store current direction mode on the edge so algorithms that only
        # receive nodes/edges (no app context) can infer directed vs. undirected.
        new_edge.is_directed = self.is_directed
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
        # Keep edges consistent with current mode (used by traversal algorithms)
        for e in self.edges:
            try:
                e.is_directed = self.is_directed
            except Exception:
                pass
        mode = "Có hướng" if self.is_directed else "Vô hướng"
        self.log(f"Đã chuyển sang chế độ đồ thị: {mode}", level='THÔNG BÁO')
        self.draw_graph()

    def toggle_weights(self):
        self.show_weights = not bool(getattr(self, 'show_weights', True))
        state = "hiện" if self.show_weights else "ẩn"
        self.log(f"Đã {state} trọng số trên cạnh.", level='THÔNG BÁO')
        self.draw_graph()

    # --- Placeholder Methods (For Team Members) ---

    def run_bfs(self):
        self.algo_runner.run_bfs()

    def run_dfs(self):
        self.algo_runner.run_dfs()

    def run_dijkstra(self):
        self.algo_runner.run_dijkstra()

    def run_bellman_ford(self):
        self.algo_runner.run_bellman_ford()

    def run_prim(self):
        self.algo_runner.run_prim()

    def run_check_bipartite(self):
        self.algo_runner.run_check_bipartite()

    def run_kruskal(self):
        self.algo_runner.run_kruskal()

    def run_ford_fulkerson(self):
        self.algo_runner.run_ford_fulkerson()

    def run_fleury(self):
        self.algo_runner.run_fleury()

    def run_hierholzer(self):
        self.algo_runner.run_hierholzer()

    # --- Animation Controls ---

    def toggle_animation_pause(self):
        """Toggle pause/resume for the current algorithm animation."""
        if not hasattr(self, 'algo_runner') or self.algo_runner is None:
            return True
        return bool(self.algo_runner.toggle_pause())

    def animation_next(self):
        """Step forward one animation frame."""
        if not hasattr(self, 'algo_runner') or self.algo_runner is None:
            return
        self.algo_runner.step_next()

    def animation_prev(self):
        """Step backward one animation frame."""
        if not hasattr(self, 'algo_runner') or self.algo_runner is None:
            return
        self.algo_runner.step_prev()

    def show_representations(self):
        if not self.nodes:
            self.log("Không có dữ liệu đồ thị để hiển thị.", level='CẢNH BÁO')
            return

        # Create a new window
        top = ctk.CTkToplevel(self)
        top.title("Biểu diễn Đồ thị")
        top.geometry("600x400")
        
        # Create tabs for Matrix and List
        tabview = ctk.CTkTabview(top)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        tab_matrix = tabview.add("Ma trận kề")
        tab_list = tabview.add("Danh sách kề")
        tab_edges = tabview.add("Danh sách cạnh")
        
        # Matrix Content
        matrix_str = convert_to_adjacency_matrix(self.nodes, self.edges, self.is_directed)
        txt_matrix = ctk.CTkTextbox(tab_matrix, font=ctk.CTkFont(family="Consolas", size=12))
        txt_matrix.pack(fill="both", expand=True)
        txt_matrix.insert("1.0", matrix_str)
        txt_matrix.configure(state="disabled")
        
        # List Content
        list_str = convert_to_adjacency_list(self.nodes, self.edges, self.is_directed)
        txt_list = ctk.CTkTextbox(tab_list, font=ctk.CTkFont(family="Consolas", size=12))
        txt_list.pack(fill="both", expand=True)
        txt_list.insert("1.0", list_str)
        txt_list.configure(state="disabled")

        # Edge List Content
        edge_str = convert_to_edge_list(self.nodes, self.edges, self.is_directed)
        txt_edges = ctk.CTkTextbox(tab_edges, font=ctk.CTkFont(family="Consolas", size=12))
        txt_edges.pack(fill="both", expand=True)
        txt_edges.insert("1.0", edge_str)
        txt_edges.configure(state="disabled")

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
                e = Edge(node_map[u_id], node_map[v_id], w)
                e.is_directed = self.is_directed
                self.edges.append(e)

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
            return
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

        # Recreate edges
        node_map = {int(n.id): n for n in self.nodes}
        for ed in edges_data or []:
            try:
                u = int(ed.get('start'))
                v = int(ed.get('end'))
                w = int(ed.get('weight', 1))
                if u in node_map and v in node_map:
                    e = Edge(node_map[u], node_map[v], w)
                    e.is_directed = self.is_directed
                    self.edges.append(e)
            except Exception:
                continue

        # Update counter
        max_id = max([int(n.id) for n in self.nodes], default=0)
        self.node_counter = max_id + 1

        self.draw_graph()
        self.log(
            f"Đã đọc file: {os.path.basename(path)} ({len(self.nodes)} đỉnh, {len(self.edges)} cạnh)",
            level='THÀNH CÔNG',
        )


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

if __name__ == "__main__":
    app = GraphApp()
    app.mainloop()
