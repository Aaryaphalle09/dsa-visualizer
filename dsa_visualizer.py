import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading
from collections import deque

# ─── THEME ───────────────────────────────────────────────────────────────────
BG         = "#0a0a0f"
SURFACE    = "#12121a"
SURFACE2   = "#1a1a26"
BORDER     = "#2a2a3f"
ACCENT     = "#7c6cfc"
ACCENT2    = "#fc6c8f"
ACCENT3    = "#6cfcbc"
GREEN      = "#4caf80"
TEXT       = "#e8e8f0"
MUTED      = "#6b6b8a"
WHITE      = "#ffffff"


# ─── MAIN APP ────────────────────────────────────────────────────────────────
class DSAVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("DSA Visualizer — Aarya Phalle")
        self.root.geometry("1100x700")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.sorting = False
        self.stop_flag = False
        self.arr = []
        self.speed = 50

        self._build_header()
        self._build_tabs()
        self._build_sorting_tab()
        self._build_graph_tab()

        self.show_tab("sorting")
        self.generate_array()

    # ── HEADER ────────────────────────────────────────────────────────────────
    def _build_header(self):
        header = tk.Frame(self.root, bg=SURFACE, height=50)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(header, text="dsa.visualizer", font=("Courier", 14, "bold"),
                 bg=SURFACE, fg=ACCENT).pack(side="left", padx=20, pady=12)
        tk.Label(header, text="built by Aarya Phalle", font=("Arial", 10),
                 bg=SURFACE, fg=MUTED).pack(side="right", padx=20)

    # ── TABS ──────────────────────────────────────────────────────────────────
    def _build_tabs(self):
        self.tab_bar = tk.Frame(self.root, bg=BG, height=40)
        self.tab_bar.pack(fill="x")

        self.tab_btns = {}
        for name, label in [("sorting", "Sorting Algorithms"), ("graph", "Graph Traversal")]:
            btn = tk.Button(self.tab_bar, text=label, font=("Arial", 10, "bold"),
                            bg=BG, fg=MUTED, bd=0, padx=20, pady=8,
                            cursor="hand2",
                            command=lambda n=name: self.show_tab(n))
            btn.pack(side="left")
            self.tab_btns[name] = btn

        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(fill="both", expand=True)
        self.tabs = {}

    def show_tab(self, name):
        for n, f in self.tabs.items():
            f.pack_forget()
            self.tab_btns[n].config(bg=BG, fg=MUTED)
        self.tabs[name].pack(fill="both", expand=True)
        self.tab_btns[name].config(bg=SURFACE, fg=ACCENT)

    # ── SORTING TAB ───────────────────────────────────────────────────────────
    def _build_sorting_tab(self):
        frame = tk.Frame(self.content, bg=BG)
        self.tabs["sorting"] = frame

        # Controls
        ctrl = tk.Frame(frame, bg=SURFACE, pady=10)
        ctrl.pack(fill="x", padx=20, pady=(15, 0))

        tk.Label(ctrl, text="Algorithm:", font=("Arial", 10), bg=SURFACE, fg=TEXT).pack(side="left", padx=(15,4))
        self.algo_var = tk.StringVar(value="Bubble Sort")
        algo_menu = ttk.Combobox(ctrl, textvariable=self.algo_var, width=16,
                                  values=["Bubble Sort", "Selection Sort", "Insertion Sort"],
                                  state="readonly")
        algo_menu.pack(side="left", padx=(0, 15))
        algo_menu.bind("<<ComboboxSelected>>", self.update_complexity)

        tk.Label(ctrl, text="Size:", font=("Arial", 10), bg=SURFACE, fg=TEXT).pack(side="left", padx=(0,4))
        self.size_var = tk.IntVar(value=30)
        tk.Scale(ctrl, from_=10, to=60, orient="horizontal", variable=self.size_var,
                 bg=SURFACE, fg=TEXT, troughcolor=BORDER, highlightthickness=0,
                 length=100, showvalue=True).pack(side="left", padx=(0,15))

        tk.Label(ctrl, text="Speed (ms):", font=("Arial", 10), bg=SURFACE, fg=TEXT).pack(side="left", padx=(0,4))
        self.speed_var = tk.IntVar(value=50)
        tk.Scale(ctrl, from_=10, to=300, orient="horizontal", variable=self.speed_var,
                 bg=SURFACE, fg=TEXT, troughcolor=BORDER, highlightthickness=0,
                 length=100, showvalue=True).pack(side="left", padx=(0,15))

        self.gen_btn = tk.Button(ctrl, text="Generate Array", font=("Arial", 10, "bold"),
                                  bg=SURFACE2, fg=TEXT, bd=0, padx=12, pady=6,
                                  cursor="hand2", command=self.generate_array)
        self.gen_btn.pack(side="left", padx=5)

        self.sort_btn = tk.Button(ctrl, text="▶  Sort", font=("Arial", 10, "bold"),
                                   bg=ACCENT, fg=WHITE, bd=0, padx=12, pady=6,
                                   cursor="hand2", command=self.start_sort)
        self.sort_btn.pack(side="left", padx=5)

        self.stop_btn = tk.Button(ctrl, text="■  Stop", font=("Arial", 10, "bold"),
                                   bg=SURFACE2, fg=TEXT, bd=0, padx=12, pady=6,
                                   cursor="hand2", command=self.stop_sort, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        # Canvas
        self.sort_canvas = tk.Canvas(frame, bg=SURFACE, highlightthickness=0)
        self.sort_canvas.pack(fill="both", expand=True, padx=20, pady=10)

        # Info bar
        info = tk.Frame(frame, bg=SURFACE, pady=8)
        info.pack(fill="x", padx=20, pady=(0, 5))

        self.cmp_label  = self._info_item(info, "Comparisons", "0")
        self.swap_label = self._info_item(info, "Swaps", "0")
        self.status_label = self._info_item(info, "Status", "Ready")
        self.tc_label   = self._info_item(info, "Time Complexity", "O(n²)")
        self.sc_label   = self._info_item(info, "Space Complexity", "O(1)")

        # Step display
        self.step_var = tk.StringVar(value="Generate an array and press Sort to begin.")
        step_frame = tk.Frame(frame, bg=SURFACE2, pady=6)
        step_frame.pack(fill="x", padx=20, pady=(0, 15))
        tk.Frame(step_frame, bg=ACCENT, width=4).pack(side="left", fill="y")
        tk.Label(step_frame, textvariable=self.step_var, font=("Arial", 10),
                 bg=SURFACE2, fg=TEXT, anchor="w", padx=10).pack(side="left", fill="x", expand=True)

    def _info_item(self, parent, label, value):
        f = tk.Frame(parent, bg=SURFACE, padx=20)
        f.pack(side="left")
        tk.Label(f, text=label.upper(), font=("Arial", 8), bg=SURFACE, fg=MUTED).pack()
        val = tk.Label(f, text=value, font=("Courier", 14, "bold"), bg=SURFACE, fg=ACCENT)
        val.pack()
        return val

    def generate_array(self):
        self.stop_flag = True
        self.sorting = False
        n = self.size_var.get()
        self.arr = [random.randint(10, 99) for _ in range(n)]
        self.comparisons = 0
        self.swaps = 0
        self.update_stats()
        self.status_label.config(text="Ready")
        self.step_var.set("Array generated! Press ▶ Sort to visualize.")
        self.sort_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.draw_bars()

    def draw_bars(self, comparing=[], swapping=[], sorted_indices=[], all_sorted=False):
        self.sort_canvas.delete("all")
        if not self.arr:
            return
        w = self.sort_canvas.winfo_width() or 800
        h = self.sort_canvas.winfo_height() or 320
        n = len(self.arr)
        bar_w = max(2, (w - 20) / n)
        max_val = max(self.arr) if self.arr else 1

        for i, val in enumerate(self.arr):
            x1 = 10 + i * bar_w
            x2 = x1 + bar_w - 2
            bar_h = (val / max_val) * (h - 30)
            y1 = h - bar_h
            y2 = h - 2

            if all_sorted or i in sorted_indices:
                color = GREEN
            elif i in swapping:
                color = ACCENT3
            elif i in comparing:
                color = ACCENT2
            else:
                color = ACCENT

            self.sort_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        self.root.update_idletasks()

    def update_stats(self):
        self.cmp_label.config(text=str(self.comparisons))
        self.swap_label.config(text=str(self.swaps))

    def update_complexity(self, event=None):
        algo = self.algo_var.get()
        comp = {"Bubble Sort": ("O(n²)", "O(1)"),
                "Selection Sort": ("O(n²)", "O(1)"),
                "Insertion Sort": ("O(n²)", "O(1)")}
        tc, sc = comp.get(algo, ("O(n²)", "O(1)"))
        self.tc_label.config(text=tc)
        self.sc_label.config(text=sc)

    def start_sort(self):
        if self.sorting:
            return
        if not self.arr:
            self.generate_array()
            return
        self.stop_flag = False
        self.sorting = True
        self.comparisons = 0
        self.swaps = 0
        self.sort_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.gen_btn.config(state="disabled")
        self.status_label.config(text="Running")

        algo = self.algo_var.get()
        thread = threading.Thread(target=self._run_sort, args=(algo,), daemon=True)
        thread.start()

    def _run_sort(self, algo):
        if algo == "Bubble Sort":
            self._bubble_sort()
        elif algo == "Selection Sort":
            self._selection_sort()
        elif algo == "Insertion Sort":
            self._insertion_sort()

        if not self.stop_flag:
            self.draw_bars(all_sorted=True)
            self.status_label.config(text="Sorted ✓")
            self.step_var.set("Array is fully sorted!")
        self.sorting = False
        self.sort_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.gen_btn.config(state="normal")

    def _sleep(self):
        time.sleep(self.speed_var.get() / 1000)

    def _bubble_sort(self):
        arr = self.arr
        n = len(arr)
        sorted_idx = set()
        for i in range(n - 1):
            for j in range(n - i - 1):
                if self.stop_flag:
                    return
                self.comparisons += 1
                self.update_stats()
                self.draw_bars(comparing=[j, j+1], sorted_indices=list(sorted_idx))
                self.step_var.set(f"Comparing arr[{j}]={arr[j]} and arr[{j+1}]={arr[j+1]}")
                self._sleep()
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
                    self.swaps += 1
                    self.update_stats()
                    self.draw_bars(swapping=[j, j+1], sorted_indices=list(sorted_idx))
                    self.step_var.set(f"Swapping {arr[j+1]} and {arr[j]}")
                    self._sleep()
            sorted_idx.add(n - 1 - i)

    def _selection_sort(self):
        arr = self.arr
        n = len(arr)
        sorted_idx = set()
        for i in range(n - 1):
            min_idx = i
            for j in range(i + 1, n):
                if self.stop_flag:
                    return
                self.comparisons += 1
                self.update_stats()
                self.draw_bars(comparing=[min_idx, j], sorted_indices=list(sorted_idx))
                self.step_var.set(f"Finding min: arr[{min_idx}]={arr[min_idx]}, checking arr[{j}]={arr[j]}")
                self._sleep()
                if arr[j] < arr[min_idx]:
                    min_idx = j
            if min_idx != i:
                arr[i], arr[min_idx] = arr[min_idx], arr[i]
                self.swaps += 1
                self.update_stats()
                self.draw_bars(swapping=[i, min_idx], sorted_indices=list(sorted_idx))
                self.step_var.set(f"Placing minimum {arr[i]} at position {i}")
                self._sleep()
            sorted_idx.add(i)

    def _insertion_sort(self):
        arr = self.arr
        n = len(arr)
        sorted_idx = set([0])
        for i in range(1, n):
            key = arr[i]
            j = i - 1
            self.step_var.set(f"Inserting arr[{i}]={key} into sorted portion")
            while j >= 0 and arr[j] > key:
                if self.stop_flag:
                    return
                self.comparisons += 1
                self.swaps += 1
                self.update_stats()
                arr[j + 1] = arr[j]
                self.draw_bars(comparing=[j, j+1], sorted_indices=list(sorted_idx))
                self.step_var.set(f"Moving {arr[j]} right to make space for {key}")
                self._sleep()
                j -= 1
            arr[j + 1] = key
            sorted_idx.add(i)
            self.draw_bars(sorted_indices=list(sorted_idx))
            self._sleep()

    def stop_sort(self):
        self.stop_flag = True
        self.status_label.config(text="Stopped")
        self.stop_btn.config(state="disabled")
        self.sort_btn.config(state="normal")
        self.gen_btn.config(state="normal")

    # ── GRAPH TAB ─────────────────────────────────────────────────────────────
    def _build_graph_tab(self):
        frame = tk.Frame(self.content, bg=BG)
        self.tabs["graph"] = frame

        self.nodes = []
        self.edges = []
        self.graph_mode = "add"
        self.selected_node = None
        self.graph_animating = False
        self.NODE_R = 22

        # Controls
        ctrl = tk.Frame(frame, bg=SURFACE, pady=8)
        ctrl.pack(fill="x", padx=20, pady=(15, 0))

        self.mode_btns = {}
        modes = [("add", "+ Add Node"), ("edge", "↔ Add Edge")]
        for key, label in modes:
            btn = tk.Button(ctrl, text=label, font=("Arial", 10, "bold"),
                            bg=SURFACE2, fg=MUTED, bd=0, padx=12, pady=6,
                            cursor="hand2", command=lambda k=key: self.set_graph_mode(k))
            btn.pack(side="left", padx=4)
            self.mode_btns[key] = btn

        tk.Button(ctrl, text="▶ BFS", font=("Arial", 10, "bold"),
                  bg=ACCENT, fg=WHITE, bd=0, padx=12, pady=6,
                  cursor="hand2", command=self.run_bfs).pack(side="left", padx=4)

        tk.Button(ctrl, text="▶ DFS", font=("Arial", 10, "bold"),
                  bg=ACCENT2, fg=WHITE, bd=0, padx=12, pady=6,
                  cursor="hand2", command=self.run_dfs).pack(side="left", padx=4)

        tk.Button(ctrl, text="Load Sample", font=("Arial", 10, "bold"),
                  bg=SURFACE2, fg=TEXT, bd=0, padx=12, pady=6,
                  cursor="hand2", command=self.load_sample).pack(side="left", padx=4)

        tk.Button(ctrl, text="✕ Clear", font=("Arial", 10, "bold"),
                  bg=SURFACE2, fg=ACCENT2, bd=0, padx=12, pady=6,
                  cursor="hand2", command=self.clear_graph).pack(side="left", padx=4)

        self.graph_hint = tk.Label(ctrl, text="Click canvas to add nodes",
                                    font=("Arial", 9), bg=SURFACE, fg=MUTED)
        self.graph_hint.pack(side="left", padx=15)

        # Canvas
        self.graph_canvas = tk.Canvas(frame, bg=SURFACE, highlightthickness=0, cursor="crosshair")
        self.graph_canvas.pack(fill="both", expand=True, padx=20, pady=10)
        self.graph_canvas.bind("<Button-1>", self.on_graph_click)

        # Info + Log side by side
        bottom = tk.Frame(frame, bg=BG)
        bottom.pack(fill="x", padx=20, pady=(0, 15))

        info = tk.Frame(bottom, bg=SURFACE, pady=8)
        info.pack(side="left", fill="y", padx=(0, 10))
        self.node_count_label = self._info_item(info, "Nodes", "0")
        self.edge_count_label = self._info_item(info, "Edges", "0")
        self.graph_algo_label = self._info_item(info, "Algorithm", "—")
        self.graph_steps_label = self._info_item(info, "Steps", "0")

        log_frame = tk.Frame(bottom, bg=SURFACE)
        log_frame.pack(side="left", fill="both", expand=True)
        tk.Label(log_frame, text="Traversal Log", font=("Arial", 9, "bold"),
                 bg=SURFACE, fg=MUTED).pack(anchor="w", padx=10, pady=(5,0))
        self.log_text = tk.Text(log_frame, height=5, bg=SURFACE2, fg=TEXT,
                                 font=("Courier", 9), bd=0, state="disabled",
                                 insertbackground=TEXT)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)

        self.set_graph_mode("add")

    def set_graph_mode(self, mode):
        self.graph_mode = mode
        self.selected_node = None
        hints = {"add": "Click on canvas to place a node.",
                 "edge": "Click two nodes one after another to connect them."}
        self.graph_hint.config(text=hints.get(mode, ""))
        for k, btn in self.mode_btns.items():
            btn.config(bg=ACCENT if k == mode else SURFACE2,
                       fg=WHITE if k == mode else MUTED)
        self.draw_graph()

    def on_graph_click(self, event):
        if self.graph_animating:
            return
        x, y = event.x, event.y
        if self.graph_mode == "add":
            too_close = any(((n["x"]-x)**2 + (n["y"]-y)**2) ** 0.5 < self.NODE_R * 2.5
                            for n in self.nodes)
            if not too_close:
                self.nodes.append({"x": x, "y": y, "id": len(self.nodes)})
                self.update_graph_info()
                self.draw_graph()
        elif self.graph_mode == "edge":
            clicked = next((n for n in self.nodes
                            if ((n["x"]-x)**2 + (n["y"]-y)**2) ** 0.5 < self.NODE_R), None)
            if not clicked:
                return
            if not self.selected_node:
                self.selected_node = clicked
                self.draw_graph()
            elif self.selected_node["id"] != clicked["id"]:
                a, b = self.selected_node["id"], clicked["id"]
                exists = any((e["a"] == a and e["b"] == b) or
                             (e["a"] == b and e["b"] == a) for e in self.edges)
                if not exists:
                    self.edges.append({"a": a, "b": b})
                self.selected_node = None
                self.update_graph_info()
                self.draw_graph()

    def draw_graph(self, visited=set(), in_queue=set(), start_id=None):
        c = self.graph_canvas
        c.delete("all")

        for e in self.edges:
            a, b = self.nodes[e["a"]], self.nodes[e["b"]]
            c.create_line(a["x"], a["y"], b["x"], b["y"], fill=BORDER, width=2)

        for n in self.nodes:
            fill = ACCENT
            if n["id"] == start_id:
                fill = GREEN
            elif n["id"] in visited:
                fill = ACCENT3
            elif n["id"] in in_queue:
                fill = ACCENT2
            if self.selected_node and self.selected_node["id"] == n["id"]:
                fill = "#ffc107"

            c.create_oval(n["x"]-self.NODE_R, n["y"]-self.NODE_R,
                          n["x"]+self.NODE_R, n["y"]+self.NODE_R,
                          fill=fill, outline=WHITE, width=2)
            c.create_text(n["x"], n["y"], text=str(n["id"]),
                          font=("Courier", 12, "bold"), fill=WHITE)

    def get_adjacency(self):
        adj = {n["id"]: [] for n in self.nodes}
        for e in self.edges:
            adj[e["a"]].append(e["b"])
            adj[e["b"]].append(e["a"])
        return adj

    def add_log(self, msg, color=None):
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n")
        if color:
            last_line = int(self.log_text.index("end-1c").split(".")[0])
            self.log_text.tag_add(color, f"{last_line}.0", f"{last_line}.end")
            self.log_text.tag_config(color, foreground=color)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def run_bfs(self):
        if not self.nodes or self.graph_animating:
            return
        thread = threading.Thread(target=self._bfs_thread, daemon=True)
        thread.start()

    def _bfs_thread(self):
        self.graph_animating = True
        self.graph_algo_label.config(text="BFS")
        self.clear_log()
        self.add_log("Starting BFS from node 0", ACCENT3)
        adj = self.get_adjacency()
        visited, queue, in_queue = set(), deque([0]), set([0])
        steps = 0
        while queue:
            curr = queue.popleft()
            visited.add(curr)
            in_queue.discard(curr)
            steps += 1
            self.graph_steps_label.config(text=str(steps))
            self.add_log(f"  Visiting node {curr}", ACCENT3)
            self.draw_graph(visited, in_queue, start_id=0)
            time.sleep(0.6)
            for nb in adj[curr]:
                if nb not in visited and nb not in in_queue:
                    queue.append(nb)
                    in_queue.add(nb)
                    self.add_log(f"    → Enqueue node {nb}")
            self.draw_graph(visited, in_queue, start_id=0)
            time.sleep(0.3)
        self.add_log("BFS complete!", ACCENT)
        self.graph_animating = False

    def run_dfs(self):
        if not self.nodes or self.graph_animating:
            return
        thread = threading.Thread(target=self._dfs_thread, daemon=True)
        thread.start()

    def _dfs_thread(self):
        self.graph_animating = True
        self.graph_algo_label.config(text="DFS")
        self.clear_log()
        self.add_log("Starting DFS from node 0", ACCENT2)
        adj = self.get_adjacency()
        visited, stack = set(), [0]
        steps = 0
        while stack:
            curr = stack.pop()
            if curr in visited:
                continue
            visited.add(curr)
            steps += 1
            self.graph_steps_label.config(text=str(steps))
            self.add_log(f"  Visiting node {curr}", ACCENT2)
            self.draw_graph(visited, set(stack), start_id=0)
            time.sleep(0.6)
            for nb in reversed(adj[curr]):
                if nb not in visited:
                    stack.append(nb)
                    self.add_log(f"    → Push node {nb} to stack")
            self.draw_graph(visited, set(stack), start_id=0)
            time.sleep(0.3)
        self.add_log("DFS complete!", ACCENT)
        self.graph_animating = False

    def clear_graph(self):
        self.nodes = []
        self.edges = []
        self.selected_node = None
        self.graph_animating = False
        self.update_graph_info()
        self.clear_log()
        self.add_log("Graph cleared.")
        self.draw_graph()

    def load_sample(self):
        self.clear_graph()
        w = self.graph_canvas.winfo_width() or 700
        h = self.graph_canvas.winfo_height() or 350
        cx, cy = w // 2, h // 2
        positions = [(cx, cy-130), (cx+150, cy-60), (cx+120, cy+90),
                     (cx-120, cy+90), (cx-150, cy-60), (cx, cy+10), (cx+60, cy-60)]
        for i, (x, y) in enumerate(positions):
            self.nodes.append({"x": x, "y": y, "id": i})
        self.edges = [{"a":0,"b":1},{"a":1,"b":2},{"a":2,"b":3},
                      {"a":3,"b":4},{"a":4,"b":0},{"a":0,"b":5},
                      {"a":1,"b":5},{"a":2,"b":6},{"a":5,"b":6}]
        self.update_graph_info()
        self.draw_graph()
        self.add_log("Sample graph loaded! Click ▶ BFS or ▶ DFS to visualize.")

    def update_graph_info(self):
        self.node_count_label.config(text=str(len(self.nodes)))
        self.edge_count_label.config(text=str(len(self.edges)))


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = DSAVisualizer(root)
    root.mainloop()
