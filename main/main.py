import customtkinter as ctk
import tkinter as tk
from tkinter import simpledialog
import math
import datetime

# --- Configuration ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- Data Structures (The Contract) ---
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
        
        # Draw circle with a clean outline
        canvas.create_oval(x0, y0, x1, y1, fill=self.color, outline="white", width=2)
        
        # Draw label centered
        canvas.create_text(self.x, self.y, text=self.label, fill=self.text_color, font=("Roboto", 12, "bold"))

class Edge:
    def __init__(self, start_node, end_node, weight=1):
        self.start_node = start_node
        self.end_node = end_node
        self.weight = int(weight)
        self.color = "gray70"

    def draw(self, canvas):
        # Calculate start and end points
        start_x, start_y = self.start_node.x, self.start_node.y
        end_x, end_y = self.end_node.x, self.end_node.y
        
        # Calculate vector to shorten the line so arrow is visible (not covered by node)
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Shorten by node radius (20) + small buffer
            shorten_len = self.end_node.radius + 2 
            ratio = shorten_len / distance
            end_x = end_x - dx * ratio
            end_y = end_y - dy * ratio
        
        # Draw the line
        # Using arrow=tk.LAST to indicate direction, which is standard for BFS/DFS visualization
        canvas.create_line(start_x, start_y, end_x, end_y, 
                           fill=self.color, width=2, smooth=True, arrow=tk.LAST)
        
        # Calculate midpoint for weight text
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        
        # Draw weight with a small background box for readability
        text = str(self.weight)
        # Create a small background rectangle behind text
        canvas.create_rectangle(mid_x - 10, mid_y - 10, mid_x + 10, mid_y + 10, fill="#2b2b2b", outline="")
        canvas.create_text(mid_x, mid_y, text=text, fill="gray90", font=("Roboto", 10))

# --- Main Application (GUI Controller) ---
class GraphApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Window Setup
        self.title("GRAPH MASTER")
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

        self.create_sidebar()
        self.create_main_canvas()
        
        self.log("Application started. Ready.")

    def create_sidebar(self):
        """Creates the left control panel."""
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1) # Push log to bottom

        # Header
        self.lbl_title = ctk.CTkLabel(self.sidebar, text="GRAPH MASTER", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Group 1: Algorithms
        self.lbl_algo = ctk.CTkLabel(self.sidebar, text="Algorithms", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_algo.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")

        self.btn_bfs = ctk.CTkButton(self.sidebar, text="BFS", command=self.run_bfs)
        self.btn_bfs.grid(row=2, column=0, padx=20, pady=5)
        
        self.btn_dfs = ctk.CTkButton(self.sidebar, text="DFS", command=self.run_dfs)
        self.btn_dfs.grid(row=3, column=0, padx=20, pady=5)
        
        self.btn_dijkstra = ctk.CTkButton(self.sidebar, text="Dijkstra", command=self.run_dijkstra)
        self.btn_dijkstra.grid(row=4, column=0, padx=20, pady=5)
        
        self.btn_prim = ctk.CTkButton(self.sidebar, text="Prim", command=self.run_prim)
        self.btn_prim.grid(row=5, column=0, padx=20, pady=5)

        self.btn_bipartite = ctk.CTkButton(self.sidebar, text="Check Bipartite", command=self.run_check_bipartite)
        self.btn_bipartite.grid(row=6, column=0, padx=20, pady=5)

        # Advanced Algorithms
        self.lbl_adv = ctk.CTkLabel(self.sidebar, text="Advanced Algo", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_adv.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="ew")

        self.btn_kruskal = ctk.CTkButton(self.sidebar, text="Kruskal", command=self.run_kruskal)
        self.btn_kruskal.grid(row=8, column=0, padx=20, pady=5)

        self.btn_ford = ctk.CTkButton(self.sidebar, text="Ford-Fulkerson", command=self.run_ford_fulkerson)
        self.btn_ford.grid(row=9, column=0, padx=20, pady=5)

        self.btn_fleury = ctk.CTkButton(self.sidebar, text="Fleury", command=self.run_fleury)
        self.btn_fleury.grid(row=10, column=0, padx=20, pady=5)

        self.btn_hierholzer = ctk.CTkButton(self.sidebar, text="Hierholzer", command=self.run_hierholzer)
        self.btn_hierholzer.grid(row=11, column=0, padx=20, pady=5)

        # Group 2: Features
        self.lbl_features = ctk.CTkLabel(self.sidebar, text="Features", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_features.grid(row=12, column=0, padx=20, pady=(20, 0), sticky="ew")

        self.btn_random = ctk.CTkButton(self.sidebar, text="Random Graph", fg_color="#E67E22", hover_color="#D35400", command=self.generate_random)
        self.btn_random.grid(row=13, column=0, padx=20, pady=5)

        self.btn_save = ctk.CTkButton(self.sidebar, text="Save File", command=self.save_graph)
        self.btn_save.grid(row=14, column=0, padx=20, pady=5)

        self.btn_load = ctk.CTkButton(self.sidebar, text="Load File", command=self.load_graph)
        self.btn_load.grid(row=15, column=0, padx=20, pady=5)

        self.btn_matrix = ctk.CTkButton(self.sidebar, text="Show Matrix/List", command=self.show_representations)
        self.btn_matrix.grid(row=16, column=0, padx=20, pady=5)

        # Group 3: Utilities
        self.btn_clear = ctk.CTkButton(self.sidebar, text="Clear Canvas", fg_color="#C0392B", hover_color="#E74C3C", command=self.clear_canvas)
        self.btn_clear.grid(row=17, column=0, padx=20, pady=(20, 10))

        # Log Console
        self.lbl_log = ctk.CTkLabel(self.sidebar, text="Log Console", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_log.grid(row=18, column=0, padx=20, pady=(10, 0), sticky="ew")

        self.log_box = ctk.CTkTextbox(self.sidebar, height=150)
        self.log_box.grid(row=19, column=0, padx=20, pady=(5, 20), sticky="ew")
        self.log_box.configure(state="disabled")

    def create_main_canvas(self):
        """Creates the drawing surface."""
        self.canvas = tk.Canvas(self, bg="#2b2b2b", highlightthickness=0)
        self.canvas.grid(row=0, column=1, sticky="nsew")

        # Event Bindings
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click) # Windows/Linux Right Click
        self.canvas.bind("<Button-2>", self.on_right_click) # MacOS Right Click

    # --- Core Logic: Logging & Drawing ---

    def log(self, message):
        """Appends a message to the log console with a timestamp."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {message}\n"
        
        self.log_box.configure(state="normal")
        self.log_box.insert("end", full_msg)
        self.log_box.see("end") # Auto-scroll to bottom
        self.log_box.configure(state="disabled")

    def draw_graph(self):
        """Clears and redraws the entire graph."""
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
                self.log(f"Selected Node {clicked_node.id}. Click another to connect.")
            else:
                if self.selected_node == clicked_node:
                    # Clicked same node -> Deselect
                    self.selected_node = None
                    self.log("Deselected node.")
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
            new_label = simpledialog.askstring("Rename Node", f"Enter new label for Node {clicked_node.id}:", initialvalue=clicked_node.label)
            if new_label:
                clicked_node.label = new_label
                self.log(f"Renamed Node {clicked_node.id} to '{new_label}'")
                self.draw_graph()
            return

        # Check Edge Hit
        clicked_edge = self.get_edge_at(x, y)
        if clicked_edge:
            new_weight = simpledialog.askinteger("Edit Weight", "Enter new weight:", initialvalue=clicked_edge.weight)
            if new_weight is not None:
                clicked_edge.weight = new_weight
                self.log(f"Updated Edge weight to {new_weight}")
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
        self.log(f"Node {new_node.id} created at ({x}, {y})")

    def add_edge(self, start, end):
        # Check for duplicates
        for edge in self.edges:
            if (edge.start_node == start and edge.end_node == end):
                self.log("Edge already exists!")
                return

        new_edge = Edge(start, end)
        self.edges.append(new_edge)
        self.log(f"Connected Node {start.label} to Node {end.label}")

    def clear_canvas(self):
        self.nodes = []
        self.edges = []
        self.node_counter = 1
        self.selected_node = None
        self.draw_graph()
        self.log("Canvas cleared.")

    # --- Placeholder Methods (For Team Members) ---

    def run_bfs(self):
        self.log("BFS: Feature coming soon (Member 2)...")
        # TODO: Connected to Member 2's code

    def run_dfs(self):
        self.log("DFS: Feature coming soon (Member 2)...")
        # TODO: Connected to Member 2's code

    def run_dijkstra(self):
        self.log("Dijkstra: Feature coming soon (Member 3)...")
        # TODO: Connected to Member 3's code

    def run_prim(self):
        self.log("Prim: Feature coming soon (Member 3)...")
        # TODO: Connected to Member 3's code

    def run_check_bipartite(self):
        self.log("Check Bipartite: Feature coming soon (Member 2)...")
        # TODO: Connected to Member 2's code

    def run_kruskal(self):
        self.log("Kruskal: Feature coming soon (Member 3)...")
        # TODO: Connected to Member 3's code

    def run_ford_fulkerson(self):
        self.log("Ford-Fulkerson: Feature coming soon (Member 3)...")
        # TODO: Connected to Member 3's code

    def run_fleury(self):
        self.log("Fleury: Feature coming soon (Member 3/6)...")
        # TODO: Connected to Member 3/6's code

    def run_hierholzer(self):
        self.log("Hierholzer: Feature coming soon (Member 3/6)...")
        # TODO: Connected to Member 3/6's code

    def show_representations(self):
        self.log("Show Matrix/List: Feature coming soon (Member 4)...")
        # TODO: Connected to Member 4's code

    def generate_random(self):
        self.log("Random Graph: Feature coming soon (Member 4)...")
        # TODO: Connected to Member 4's code

    def save_graph(self):
        self.log("Save File: Feature coming soon (Member 5)...")
        # TODO: Connected to Member 5's code

    def load_graph(self):
        self.log("Load File: Feature coming soon (Member 5)...")
        # TODO: Connected to Member 5's code

if __name__ == "__main__":
    app = GraphApp()
    app.mainloop()
