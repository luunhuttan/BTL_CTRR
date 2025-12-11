import customtkinter as ctk
import tkinter as tk
from tkinter import simpledialog
import math
import random
import datetime

# --- 1. Style & Theme Setup ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class Node:
    def __init__(self, id, x, y, label=None):
        self.id = id
        self.x = x
        self.y = y
        self.label = label if label else str(id)
        self.radius = 20
        self.color = "#3B8ED0"  # Cyan/Blue-ish
        self.text_color = "white"

    def draw(self, canvas):
        x0, y0 = self.x - self.radius, self.y - self.radius
        x1, y1 = self.x + self.radius, self.y + self.radius
        
        # Draw circle with outline for better visibility
        canvas.create_oval(x0, y0, x1, y1, fill=self.color, outline="white", width=2)
        
        # Draw label
        canvas.create_text(self.x, self.y, text=self.label, fill=self.text_color, font=("Roboto", 12, "bold"))

class Edge:
    def __init__(self, start_node, end_node, weight=1):
        self.start_node = start_node
        self.end_node = end_node
        self.weight = weight
        self.color = "gray70"

    def draw(self, canvas):
        # Calculate vector to shorten the line so arrow is visible (not covered by node)
        start_x, start_y = self.start_node.x, self.start_node.y
        end_x, end_y = self.end_node.x, self.end_node.y
        
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Shorten by node radius (20) + small buffer
            shorten_len = self.end_node.radius + 2 
            ratio = shorten_len / distance
            end_x = end_x - dx * ratio
            end_y = end_y - dy * ratio

        # Draw line
        canvas.create_line(start_x, start_y, 
                           end_x, end_y, 
                           fill=self.color, width=2, smooth=True, arrow=tk.LAST)
        
        # Calculate midpoint
        mid_x = (self.start_node.x + self.end_node.x) / 2
        mid_y = (self.start_node.y + self.end_node.y) / 2
        
        # Draw weight with a small background for readability
        text = str(self.weight)
        canvas.create_rectangle(mid_x - 10, mid_y - 10, mid_x + 10, mid_y + 10, fill="#2b2b2b", outline="")
        canvas.create_text(mid_x, mid_y, text=text, fill="gray90", font=("Roboto", 10))

class GraphApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Graph Master - Advanced")
        self.geometry("1200x800")
        self.minsize(900, 700)

        # Data Structures
        self.nodes = []
        self.edges = []
        self.node_counter = 1
        self.selected_node = None

        # Layout Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- GUI Layout ---
        self.create_sidebar()
        self.create_main_area()
        
        # Initial Log
        self.log_message("Application started.")
        self.log_message("Ready to draw or generate graphs.")

    def create_sidebar(self):
        # Left Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1) # Spacer

        # Title
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Graph Master", 
                                       font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # --- Section 1: Algorithms ---
        self.algo_label = ctk.CTkLabel(self.sidebar_frame, text="Algorithms", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.algo_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")

        self.btn_bfs = ctk.CTkButton(self.sidebar_frame, text="Run BFS", command=self.run_bfs)
        self.btn_bfs.grid(row=2, column=0, padx=20, pady=5)

        self.btn_dfs = ctk.CTkButton(self.sidebar_frame, text="Run DFS", command=self.run_dfs)
        self.btn_dfs.grid(row=3, column=0, padx=20, pady=5)

        self.btn_dijkstra = ctk.CTkButton(self.sidebar_frame, text="Run Dijkstra", command=self.run_dijkstra)
        self.btn_dijkstra.grid(row=4, column=0, padx=20, pady=5)

        self.btn_prim = ctk.CTkButton(self.sidebar_frame, text="Run Prim", command=self.run_prim)
        self.btn_prim.grid(row=5, column=0, padx=20, pady=5)

        # --- Section 2: Operations ---
        self.ops_label = ctk.CTkLabel(self.sidebar_frame, text="Operations", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.ops_label.grid(row=6, column=0, padx=20, pady=(20, 0), sticky="ew")

        self.btn_random = ctk.CTkButton(self.sidebar_frame, text="Random Graph", 
                                        fg_color="#E67E22", hover_color="#D35400", # Orange for special action
                                        command=self.generate_random_graph)
        self.btn_random.grid(row=7, column=0, padx=20, pady=5)

        self.btn_clear = ctk.CTkButton(self.sidebar_frame, text="Clear Canvas", 
                                       fg_color="#C0392B", hover_color="#E74C3C", # Red
                                       command=self.clear_canvas)
        self.btn_clear.grid(row=8, column=0, padx=20, pady=5)

        # --- Section 3: Log Console ---
        self.log_label = ctk.CTkLabel(self.sidebar_frame, text="Log Console", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.log_label.grid(row=11, column=0, padx=20, pady=(10, 0), sticky="ew")

        self.log_box = ctk.CTkTextbox(self.sidebar_frame, height=150, width=240)
        self.log_box.grid(row=12, column=0, padx=20, pady=(5, 5))
        self.log_box.configure(state="disabled") # Read-only initially

        self.btn_clear_log = ctk.CTkButton(self.sidebar_frame, text="Clear Log", height=24,
                                           fg_color="gray40", hover_color="gray50",
                                           command=self.clear_log)
        self.btn_clear_log.grid(row=13, column=0, padx=20, pady=(0, 20))

    def create_main_area(self):
        # Right Main Area (Canvas)
        self.canvas = tk.Canvas(self, bg="#242424", highlightthickness=0)
        self.canvas.grid(row=0, column=1, sticky="nsew")

        # Bind Events
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click) # Windows/Linux Right Click
        self.canvas.bind("<Button-2>", self.on_right_click) # Mac Right Click

    # --- Feature C: Logger ---
    def log_message(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {message}\n"
        
        self.log_box.configure(state="normal")
        self.log_box.insert("end", full_msg)
        self.log_box.see("end") # Auto-scroll
        self.log_box.configure(state="disabled")

    def clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    # --- Feature B: Random Graph Generator ---
    def generate_random_graph(self):
        self.clear_canvas(log=False)
        
        # Canvas dimensions (fallback if not yet drawn)
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100: w = 800
        if h < 100: h = 600
        
        padding = 50
        num_nodes = random.randint(10, 15)
        
        self.log_message(f"Generating {num_nodes} random nodes...")

        # Generate Nodes
        for i in range(num_nodes):
            x = random.randint(padding, w - padding)
            y = random.randint(padding, h - padding)
            self.add_node(x, y, log=False)

        # Generate Edges (Randomly connect nodes)
        # Strategy: Ensure every node has at least one edge, plus some random extras
        num_edges_added = 0
        for i in range(len(self.nodes)):
            node_a = self.nodes[i]
            
            # Connect to 1 or 2 random other nodes
            targets = random.sample(self.nodes, min(len(self.nodes), 3))
            for node_b in targets:
                if node_a != node_b:
                    # Random weight
                    weight = random.randint(1, 20)
                    if self.add_edge(node_a, node_b, weight=weight, log=False):
                        num_edges_added += 1

        self.redraw()
        self.log_message(f"Random graph created: {len(self.nodes)} nodes, {num_edges_added} edges.")

    # --- Interactive Logic ---

    def on_left_click(self, event):
        clicked_node = self.get_node_at(event.x, event.y)

        if clicked_node:
            # Node Interaction
            if self.selected_node is None:
                # First click: Select
                self.selected_node = clicked_node
                self.log_message(f"Selected Node {clicked_node.id}")
            else:
                if self.selected_node != clicked_node:
                    # Second click: Create Edge
                    self.add_edge(self.selected_node, clicked_node)
                    self.selected_node = None 
                else:
                    # Deselect
                    self.selected_node = None
                    self.log_message("Deselected node.")
        else:
            # Empty Space: Create Node
            self.add_node(event.x, event.y)
            self.selected_node = None
        
        self.redraw()

    def on_right_click(self, event):
        # Check for Node hit
        clicked_node = self.get_node_at(event.x, event.y)
        if clicked_node:
            new_label = simpledialog.askstring("Rename Node", f"Enter new label for Node {clicked_node.id}:", initialvalue=clicked_node.label)
            if new_label:
                old_label = clicked_node.label
                clicked_node.label = new_label
                self.log_message(f"Renamed Node '{old_label}' to '{new_label}'")
                self.redraw()
            return

        # Check for Edge hit
        clicked_edge = self.get_edge_at(event.x, event.y)
        if clicked_edge:
            new_weight = simpledialog.askinteger("Update Weight", "Enter new weight:", initialvalue=clicked_edge.weight)
            if new_weight is not None:
                clicked_edge.weight = new_weight
                self.log_message(f"Updated edge weight to {new_weight}")
                self.redraw()
            return

        # Background hit
        if self.selected_node:
            self.selected_node = None
            self.redraw()

    # --- Helpers ---

    def get_node_at(self, x, y):
        for node in self.nodes:
            dist = math.sqrt((node.x - x)**2 + (node.y - y)**2)
            if dist <= node.radius:
                return node
        return None

    def get_edge_at(self, x, y, threshold=15):
        for edge in self.edges:
            mid_x = (edge.start_node.x + edge.end_node.x) / 2
            mid_y = (edge.start_node.y + edge.end_node.y) / 2
            dist = math.sqrt((mid_x - x)**2 + (mid_y - y)**2)
            if dist <= threshold:
                return edge
        return None

    def add_node(self, x, y, log=True):
        new_node = Node(self.node_counter, x, y)
        self.nodes.append(new_node)
        self.node_counter += 1
        if log:
            self.log_message(f"Added Node {new_node.id} at ({x}, {y})")
        return new_node

    def add_edge(self, start, end, weight=1, log=True):
        # Prevent duplicate edges
        for edge in self.edges:
            if (edge.start_node == start and edge.end_node == end) or \
               (edge.start_node == end and edge.end_node == start):
                return False
        
        new_edge = Edge(start, end, weight)
        self.edges.append(new_edge)
        if log:
            self.log_message(f"Added Edge: {start.label} <-> {end.label} (W: {weight})")
        return True

    def redraw(self):
        self.canvas.delete("all")
        
        # Draw Edges (Bottom)
        for edge in self.edges:
            edge.draw(self.canvas)
            
        # Draw Nodes (Top)
        for node in self.nodes:
            node.draw(self.canvas)
            
        # Highlight selected
        if self.selected_node:
            x, y, r = self.selected_node.x, self.selected_node.y, self.selected_node.radius + 4
            self.canvas.create_oval(x-r, y-r, x+r, y+r, outline="yellow", width=3)

    def clear_canvas(self, log=True):
        self.nodes = []
        self.edges = []
        self.node_counter = 1
        self.selected_node = None
        self.redraw()
        if log:
            self.log_message("Canvas cleared.")

    # --- Algorithm Placeholders ---
    def run_bfs(self):
        self.log_message("Starting BFS Algorithm...")
        # Logic would go here
        self.log_message("BFS Completed.")
    
    def run_dfs(self):
        self.log_message("Starting DFS Algorithm...")
        self.log_message("DFS Completed.")

    def run_dijkstra(self):
        self.log_message("Starting Dijkstra's Algorithm...")
        self.log_message("Dijkstra Completed.")

    def run_prim(self):
        self.log_message("Starting Prim's Algorithm...")
        self.log_message("Prim Completed.")

if __name__ == "__main__":
    app = GraphApp()
    app.mainloop()
