import customtkinter as ctk
import tkinter as tk

class GraphGUI:
    def __init__(self, app):
        """
        Initializes the GUI components for the GraphApp.
        
        Args:
            app: The main GraphApp instance (controller).
        """
        self.app = app
        self.setup_sidebar()
        self.setup_canvas()
        self.setup_right_panel()

    def setup_sidebar(self):
        """Creates the left control panel."""
        self.sidebar = ctk.CTkFrame(self.app, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        # self.sidebar.grid_rowconfigure(20, weight=1) # No longer needed as log is moved

        # Header
        self.lbl_title = ctk.CTkLabel(self.sidebar, text="QUẢN LÝ ĐỒ THỊ", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Group 1: Algorithms
        self.lbl_algo = ctk.CTkLabel(self.sidebar, text="Thuật toán", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_algo.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")

        self.btn_bfs = ctk.CTkButton(self.sidebar, text="BFS", command=self.app.run_bfs)
        self.btn_bfs.grid(row=2, column=0, padx=20, pady=5)
        
        self.btn_dfs = ctk.CTkButton(self.sidebar, text="DFS", command=self.app.run_dfs)
        self.btn_dfs.grid(row=3, column=0, padx=20, pady=5)
        
        self.btn_dijkstra = ctk.CTkButton(self.sidebar, text="Dijkstra", command=self.app.run_dijkstra)
        self.btn_dijkstra.grid(row=4, column=0, padx=20, pady=5)
        
        self.btn_prim = ctk.CTkButton(self.sidebar, text="Prim", command=self.app.run_prim)
        self.btn_prim.grid(row=5, column=0, padx=20, pady=5)

        self.btn_bipartite = ctk.CTkButton(self.sidebar, text="Kiểm tra 2 phía", command=self.app.run_check_bipartite)
        self.btn_bipartite.grid(row=6, column=0, padx=20, pady=5)

        # Advanced Algorithms
        self.lbl_adv = ctk.CTkLabel(self.sidebar, text="Thuật toán nâng cao", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_adv.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="ew")

        self.btn_kruskal = ctk.CTkButton(self.sidebar, text="Kruskal", command=self.app.run_kruskal)
        self.btn_kruskal.grid(row=8, column=0, padx=20, pady=5)

        self.btn_ford = ctk.CTkButton(self.sidebar, text="Ford-Fulkerson", command=self.app.run_ford_fulkerson)
        self.btn_ford.grid(row=9, column=0, padx=20, pady=5)

        self.btn_fleury = ctk.CTkButton(self.sidebar, text="Fleury", command=self.app.run_fleury)
        self.btn_fleury.grid(row=10, column=0, padx=20, pady=5)

        self.btn_hierholzer = ctk.CTkButton(self.sidebar, text="Hierholzer", command=self.app.run_hierholzer)
        self.btn_hierholzer.grid(row=11, column=0, padx=20, pady=5)

        # Group 2: Features
        self.lbl_features = ctk.CTkLabel(self.sidebar, text="Chức năng", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_features.grid(row=12, column=0, padx=20, pady=(20, 0), sticky="ew")

        self.btn_random = ctk.CTkButton(self.sidebar, text="Tạo đồ thị ngẫu nhiên", fg_color="#E67E22", hover_color="#D35400", command=self.app.generate_random)
        self.btn_random.grid(row=13, column=0, padx=20, pady=5)

        self.btn_save = ctk.CTkButton(self.sidebar, text="Lưu file", command=self.app.save_graph)
        self.btn_save.grid(row=14, column=0, padx=20, pady=5)

        self.btn_load = ctk.CTkButton(self.sidebar, text="Đọc file", command=self.app.load_graph)
        self.btn_load.grid(row=15, column=0, padx=20, pady=5)

        self.btn_matrix = ctk.CTkButton(self.sidebar, text="Hiện Ma trận/DS kề", command=self.app.show_representations)
        self.btn_matrix.grid(row=16, column=0, padx=20, pady=5)

        self.btn_toggle = ctk.CTkButton(self.sidebar, text="Đổi: Có hướng/Vô hướng", fg_color="#5D6D7E", hover_color="#34495E", command=self.app.toggle_directed)
        self.btn_toggle.grid(row=17, column=0, padx=20, pady=5)

        # Group 3: Utilities
        self.btn_clear = ctk.CTkButton(self.sidebar, text="Xóa bảng vẽ", fg_color="#C0392B", hover_color="#E74C3C", command=self.app.clear_canvas)
        self.btn_clear.grid(row=18, column=0, padx=20, pady=(20, 10))

    def setup_right_panel(self):
        """Creates the right panel for logs."""
        self.right_panel = ctk.CTkFrame(self.app, width=300, corner_radius=0, fg_color="#212121")
        self.right_panel.grid(row=0, column=2, sticky="nsew")
        self.right_panel.grid_rowconfigure(1, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        # Header Frame
        self.log_header = ctk.CTkFrame(self.right_panel, fg_color="transparent", height=30)
        self.log_header.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.log_header.grid_columnconfigure(0, weight=1)

        # Log Title
        self.lbl_log = ctk.CTkLabel(self.log_header, text="LOGS & SỰ KIỆN", 
                                    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
                                    text_color="gray80", anchor="w")
        self.lbl_log.grid(row=0, column=0, sticky="w")

        # Clear Button
        self.btn_clear_log = ctk.CTkButton(self.log_header, text="Xóa", width=50, height=24, 
                                           font=ctk.CTkFont(size=11),
                                           fg_color="transparent", border_width=1, 
                                           text_color="gray70", border_color="gray50",
                                           hover_color="#333333",
                                           command=self.app.clear_log)
        self.btn_clear_log.grid(row=0, column=1, sticky="e")

        # Log Console
        self.log_box = ctk.CTkTextbox(self.right_panel, font=ctk.CTkFont(family="Consolas", size=12), 
                                      fg_color="#111111", text_color="#e0e0e0", 
                                      activate_scrollbars=True)
        self.log_box.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.log_box.configure(state="disabled")
        
        # Expose log_box to app
        self.app.log_box = self.log_box

    def setup_canvas(self):
        """Creates the drawing surface."""
        self.canvas = tk.Canvas(self.app, bg="#2b2b2b", highlightthickness=0)
        self.canvas.grid(row=0, column=1, sticky="nsew")

        # Event Bindings
        self.canvas.bind("<Button-1>", self.app.on_left_click)
        self.canvas.bind("<Button-3>", self.app.on_right_click) # Windows/Linux Right Click
        self.canvas.bind("<Button-2>", self.app.on_right_click) # MacOS Right Click
        
        # Expose canvas to app
        self.app.canvas = self.canvas
