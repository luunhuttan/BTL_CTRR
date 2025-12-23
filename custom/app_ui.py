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
        self.sidebar.grid_rowconfigure(0, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)

        # Make sidebar scrollable to avoid hiding controls on smaller heights.
        try:
            self.sidebar_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
            self.sidebar_scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
            self.sidebar_scroll.grid_columnconfigure(0, weight=1)
            parent = self.sidebar_scroll

            # Mouse wheel scrolling (Windows/Linux/Mac) - active only when cursor is over the sidebar.
            self._install_sidebar_mousewheel(self.sidebar_scroll)
        except Exception:
            parent = self.sidebar

        # Header (previous style)
        self.lbl_title = ctk.CTkLabel(
            parent,
            text="QUẢN LÝ ĐỒ THỊ",
            justify="center",
            anchor="center",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.lbl_title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Group 1: Algorithms
        self.lbl_algo = ctk.CTkLabel(parent, text="Thuật toán", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_algo.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")

        self.btn_bfs = ctk.CTkButton(parent, text="BFS", command=self.app.run_bfs)
        self.btn_bfs.grid(row=2, column=0, padx=20, pady=5)
        
        self.btn_dfs = ctk.CTkButton(parent, text="DFS", command=self.app.run_dfs)
        self.btn_dfs.grid(row=3, column=0, padx=20, pady=5)
        
        self.btn_dijkstra = ctk.CTkButton(parent, text="Dijkstra", command=self.app.run_dijkstra)
        self.btn_dijkstra.grid(row=4, column=0, padx=20, pady=5)

        self.btn_bellman_ford = ctk.CTkButton(parent, text="Bellman-Ford", command=self.app.run_bellman_ford)
        self.btn_bellman_ford.grid(row=5, column=0, padx=20, pady=5)
        
        self.btn_prim = ctk.CTkButton(parent, text="Prim", command=self.app.run_prim)
        self.btn_prim.grid(row=6, column=0, padx=20, pady=5)

        self.btn_bipartite = ctk.CTkButton(parent, text="Kiểm tra 2 phía", command=self.app.run_check_bipartite)
        self.btn_bipartite.grid(row=7, column=0, padx=20, pady=5)

        # Animation Controls
        self.anim_controls = ctk.CTkFrame(parent, fg_color="transparent")
        self.anim_controls.grid(row=8, column=0, padx=20, pady=(5, 10), sticky="ew")
        self.anim_controls.grid_columnconfigure((0, 1, 2), weight=1)

        def _toggle_pause():
            paused = bool(self.app.toggle_animation_pause())
            try:
                self.btn_pause.configure(text="Tiếp tục" if paused else "Tạm dừng")
            except Exception:
                pass

        self.btn_prev = ctk.CTkButton(self.anim_controls, text="Back", width=70, command=self.app.animation_prev)
        self.btn_prev.grid(row=0, column=0, padx=(0, 5), pady=0, sticky="ew")

        self.btn_pause = ctk.CTkButton(self.anim_controls, text="Stop", width=70, command=_toggle_pause)
        self.btn_pause.grid(row=0, column=1, padx=5, pady=0, sticky="ew")

        self.btn_next = ctk.CTkButton(self.anim_controls, text="Next", width=70, command=self.app.animation_next)
        self.btn_next.grid(row=0, column=2, padx=(5, 0), pady=0, sticky="ew")

        # Advanced Algorithms
        self.lbl_adv = ctk.CTkLabel(parent, text="Thuật toán nâng cao", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_adv.grid(row=9, column=0, padx=20, pady=(10, 0), sticky="ew")

        self.btn_kruskal = ctk.CTkButton(parent, text="Kruskal", command=self.app.run_kruskal)
        self.btn_kruskal.grid(row=10, column=0, padx=20, pady=5)

        self.btn_ford = ctk.CTkButton(parent, text="Ford-Fulkerson", command=self.app.run_ford_fulkerson)
        self.btn_ford.grid(row=11, column=0, padx=20, pady=5)

        self.btn_fleury = ctk.CTkButton(parent, text="Fleury", command=self.app.run_fleury)
        self.btn_fleury.grid(row=12, column=0, padx=20, pady=5)

        self.btn_hierholzer = ctk.CTkButton(parent, text="Hierholzer", command=self.app.run_hierholzer)
        self.btn_hierholzer.grid(row=13, column=0, padx=20, pady=5)

        # Group 2: Features
        self.lbl_features = ctk.CTkLabel(parent, text="Chức năng", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_features.grid(row=14, column=0, padx=20, pady=(20, 0), sticky="ew")

        self.btn_random = ctk.CTkButton(parent, text="Tạo đồ thị ngẫu nhiên", fg_color="#E67E22", hover_color="#D35400", command=self.app.generate_random)
        self.btn_random.grid(row=15, column=0, padx=20, pady=5)

        self.btn_save = ctk.CTkButton(parent, text="Lưu file", command=self.app.save_graph)
        self.btn_save.grid(row=16, column=0, padx=20, pady=5)

        self.btn_load = ctk.CTkButton(parent, text="Đọc file", command=self.app.load_graph)
        self.btn_load.grid(row=17, column=0, padx=20, pady=5)

        self.btn_matrix = ctk.CTkButton(parent, text="Hiện Ma trận/DS kề", command=self.app.show_representations)
        self.btn_matrix.grid(row=18, column=0, padx=20, pady=5)

        self.btn_toggle = ctk.CTkButton(parent, text="Đổi: Có hướng/Vô hướng", fg_color="#5D6D7E", hover_color="#34495E", command=self.app.toggle_directed)
        self.btn_toggle.grid(row=19, column=0, padx=20, pady=5)

        self.btn_toggle_weight = ctk.CTkButton(parent, text="Bật/Tắt trọng số", fg_color="#5D6D7E", hover_color="#34495E", command=self.app.toggle_weights)
        self.btn_toggle_weight.grid(row=20, column=0, padx=20, pady=5)

        # Group 3: Utilities
        self.btn_clear = ctk.CTkButton(parent, text="Xóa bảng vẽ", fg_color="#C0392B", hover_color="#E74C3C", command=self.app.clear_canvas)
        self.btn_clear.grid(row=21, column=0, padx=20, pady=(20, 10))

    def _install_sidebar_mousewheel(self, scrollable_frame: "ctk.CTkScrollableFrame"):
        """Allow scrolling the sidebar with the mouse wheel.

        CustomTkinter's CTkScrollableFrame sometimes doesn't scroll with the wheel by default
        depending on OS/backend, so we bind it here.
        """

        # Try to access the internal canvas used by CTkScrollableFrame.
        canvas = getattr(scrollable_frame, "_parent_canvas", None)
        if canvas is None:
            return

        def _on_windows_mousewheel(event):
            # event.delta is typically 120/-120 per notch on Windows.
            step = int(-1 * (event.delta / 120)) if event.delta else 0
            if step:
                canvas.yview_scroll(step, "units")
            return "break"

        def _on_linux_scroll_up(_event):
            canvas.yview_scroll(-1, "units")
            return "break"

        def _on_linux_scroll_down(_event):
            canvas.yview_scroll(1, "units")
            return "break"

        def _bind_all(_event=None):
            # Bind on root so that wheel works when hovering child widgets too.
            self.app.bind_all("<MouseWheel>", _on_windows_mousewheel)
            self.app.bind_all("<Button-4>", _on_linux_scroll_up)
            self.app.bind_all("<Button-5>", _on_linux_scroll_down)

        def _unbind_all(_event=None):
            self.app.unbind_all("<MouseWheel>")
            self.app.unbind_all("<Button-4>")
            self.app.unbind_all("<Button-5>")

        # Activate only when mouse is over the scrollable region.
        for w in (scrollable_frame, canvas):
            try:
                w.bind("<Enter>", _bind_all)
                w.bind("<Leave>", _unbind_all)
            except Exception:
                pass

    def setup_right_panel(self):
        """Creates the right panel for logs."""
        # Grip column (narrow) - placed before the right panel
        self.grip = ctk.CTkFrame(self.app, width=12, fg_color="transparent")
        self.grip.grid(row=0, column=2, sticky="ns")
        # Bind drag events to app handlers
        self.grip.bind("<Button-1>", lambda e: self.app.start_grip_drag(e))
        self.grip.bind("<B1-Motion>", lambda e: self.app.grip_drag(e))
        self.grip.bind("<ButtonRelease-1>", lambda e: self.app.end_grip_drag(e))

        # Collapse/expand button placed inside the grip
        try:
            self.btn_toggle_log = ctk.CTkButton(self.grip, text='◀', width=28, height=28, fg_color='transparent', hover_color='transparent', command=self.app.toggle_log)
            # place near top center
            self.btn_toggle_log.place(relx=0.5, rely=0.02, anchor='n')
            # expose to app for toggling text
            self.app.ui_btn_toggle_log = self.btn_toggle_log
        except Exception:
            pass

        self.right_panel = ctk.CTkFrame(self.app, width=300, corner_radius=0, fg_color="#212121")
        self.right_panel.grid(row=0, column=3, sticky="nsew")
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

        # Log Console: use a scrollable frame to host individual "card" widgets
        try:
            self.log_container = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent")
            self.log_container.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
            self.log_container.grid_columnconfigure(0, weight=1)
            # Expose log container to app for adding/removing cards
            self.app.log_container = self.log_container
        except Exception:
            # Fallback to textbox if CTkScrollableFrame is not available
            self.log_box = ctk.CTkTextbox(self.right_panel, font=ctk.CTkFont(family="Consolas", size=12), 
                                          fg_color="#111111", text_color="#e0e0e0", 
                                          activate_scrollbars=True)
            self.log_box.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
            self.log_box.configure(state="disabled")
            self.app.log_box = self.log_box
        # Expose grip and toggle to app UI for control
        self.app.grip = self.grip
        self.app.btn_toggle_log = getattr(self, 'btn_toggle_log', None)

    def setup_canvas(self):
        """Creates the drawing surface."""
        self.canvas = tk.Canvas(self.app, bg="#2b2b2b", highlightthickness=0)
        self.canvas.grid(row=0, column=1, sticky="nsew")

        # Event Bindings
        self.canvas.bind("<Button-1>", self.app.on_left_press)
        self.canvas.bind("<B1-Motion>", self.app.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.app.on_left_release)
        self.canvas.bind("<Button-3>", self.app.on_right_click) # Windows/Linux Right Click
        self.canvas.bind("<Button-2>", self.app.on_right_click) # MacOS Right Click
        
        # Expose canvas to app
        self.app.canvas = self.canvas
