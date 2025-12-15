"""
Demo ứng dụng A* cho đồ thị và N-Puzzle với GUI (tkinter)
Cho phép thay đổi số đỉnh n và tương tác trực quan

Code được xây dựng dựa trên:
- astar_graph.py: Class Graph và thuật toán A* cho đồ thị
- puzzle15_akt.py: Class priorityQueue, nodes và logic giải puzzle bằng A*
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import math
import copy
from heapq import heappush, heappop
from astar_graph import Graph
# Import từ puzzle15_akt.py
from puzzle15_akt import priorityQueue, nodes as PuzzleNodes

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def generate_vertex_name(index):
    """Tạo tên đỉnh từ index (A, B, C, ..., Z, AA, AB, ...)"""
    if index < 26:
        return chr(65 + index)  # A-Z
    else:
        first = chr(65 + (index - 26) // 26)
        second = chr(65 + (index - 26) % 26)
        return first + second


def create_grid_graph(n, directed=True):
    """Tạo đồ thị dạng lưới với n đỉnh (có hướng hoặc vô hướng)"""
    cols = int(math.ceil(math.sqrt(n)))
    rows = int(math.ceil(n / cols))
    
    adjac_lis = {}
    positions = {}
    vertices = [generate_vertex_name(i) for i in range(n)]
    
    grid = {}
    idx = 0
    for i in range(rows):
        for j in range(cols):
            if idx < n:
                vertex = vertices[idx]
                grid[(i, j)] = vertex
                positions[vertex] = (j * 50, i * 50)
                idx += 1
    
    # Lưu các cạnh để tạo vô hướng nếu cần
    edges = {}
    
    for (i, j), vertex in grid.items():
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)
        num_directions = random.randint(2, 3)
        for di, dj in directions[:num_directions]:
            ni, nj = i + di, j + dj
            if (ni, nj) in grid:
                neighbor = grid[(ni, nj)]
                weight = random.uniform(1.0, 10.0)
                neighbors.append((neighbor, round(weight, 2)))
                # Lưu cạnh để tạo vô hướng
                if (vertex, neighbor) not in edges:
                    edges[(vertex, neighbor)] = round(weight, 2)
        adjac_lis[vertex] = neighbors
    
    # Nếu vô hướng, thêm cạnh ngược lại
    if not directed:
        for (v1, v2), weight in edges.items():
            # Kiểm tra xem cạnh ngược đã tồn tại chưa
            if not any(n == v1 for n, _ in adjac_lis.get(v2, [])):
                if v2 not in adjac_lis:
                    adjac_lis[v2] = []
                adjac_lis[v2].append((v1, weight))
    
    return adjac_lis, positions, vertices


def create_random_graph(n, edge_probability=0.25, directed=True):
    """Tạo đồ thị ngẫu nhiên với n đỉnh (có hướng hoặc vô hướng)"""
    adjac_lis = {}
    positions = {}
    vertices = [generate_vertex_name(i) for i in range(n)]
    
    for i, vertex in enumerate(vertices):
        angle = 2 * math.pi * i / n
        radius = 150
        x = radius * math.cos(angle) + 200
        y = radius * math.sin(angle) + 200
        positions[vertex] = (x, y)
    
    # Lưu các cạnh để tạo vô hướng nếu cần
    edges = {}
    
    for vertex in vertices:
        neighbors = []
        for other in vertices:
            if vertex != other and random.random() < edge_probability:
                weight = random.uniform(1.0, 10.0)
                neighbors.append((other, round(weight, 2)))
                # Lưu cạnh để tạo vô hướng
                if (vertex, other) not in edges:
                    edges[(vertex, other)] = round(weight, 2)
        adjac_lis[vertex] = neighbors
    
    # Đảm bảo đồ thị có đường đi cơ bản
    for i in range(len(vertices) - 1):
        if not any(v == vertices[i+1] for v, _ in adjac_lis[vertices[i]]):
            weight = random.uniform(1.0, 10.0)
            adjac_lis[vertices[i]].append((vertices[i+1], round(weight, 2)))
            edges[(vertices[i], vertices[i+1])] = round(weight, 2)
    
    # Nếu vô hướng, thêm cạnh ngược lại
    if not directed:
        for (v1, v2), weight in edges.items():
            # Kiểm tra xem cạnh ngược đã tồn tại chưa
            if not any(n == v1 for n, _ in adjac_lis.get(v2, [])):
                if v2 not in adjac_lis:
                    adjac_lis[v2] = []
                adjac_lis[v2].append((v1, weight))
    
    return adjac_lis, positions, vertices


def a_star_with_details(graph, start, stop):
    """
    Chạy A* và trả về path, cost và thông tin chi tiết từng bước
    Dựa trên logic từ Graph.a_star_algorithm trong astar_graph.py
    """
    # Sử dụng logic từ Graph.a_star_algorithm nhưng mở rộng để trả về details
    open_lst = set([start])
    closed_lst = set([])
    poo = {}
    poo[start] = 0
    par = {}
    par[start] = start

    while len(open_lst) > 0:
        n = None
        # Tìm node có f = g + h nhỏ nhất (giống Graph.a_star_algorithm)
        for v in open_lst:
            if n == None or poo[v] + graph.h(v, stop) < poo[n] + graph.h(n, stop):#nếu đỉnh n chưa được duyệt hoặc khoảng cách từ điềm đầu tới đỉnh v nhỏ hơn khoảng cách từ điềm đầu tới đỉnh n
                n = v

        if n == None:#nếu không tìm thấy đỉnh nào thì không có đường đi
            return None, None, None

        if n == stop:
            # Tái tạo đường đi (giống Graph.a_star_algorithm)
            reconst_path = []
            temp = n
            while par[temp] != temp:
                reconst_path.append(temp)
                temp = par[temp]
            reconst_path.append(start)
            reconst_path.reverse()
            
            # Tính toán chi tiết từng bước (mở rộng)
            step_details = []
            total_cost_calculated = 0
            
            for i, vertex in enumerate(reconst_path):
                g = poo.get(vertex, 0)
                h = graph.h(vertex, stop)
                f = g + h
                step_cost = 0
                
                if i > 0:
                    prev_vertex = reconst_path[i-1]
                    neighbors = graph.get_neighbors(prev_vertex)
                    
                    found = False
                    for neighbor, weight in neighbors:
                        if neighbor == vertex:
                            step_cost = weight
                            total_cost_calculated += weight
                            found = True
                            break
                    
                    if not found:
                        step_cost = g - poo.get(prev_vertex, 0)
                        total_cost_calculated += step_cost
                
                step_details.append({
                    'vertex': vertex,
                    'g': round(g, 2),
                    'h': round(h, 2),
                    'f': round(f, 2),
                    'step_cost': round(step_cost, 2) if i > 0 else 0
                })
            
            final_total_cost = poo.get(stop, total_cost_calculated)
            if final_total_cost == 0 and total_cost_calculated > 0:
                final_total_cost = total_cost_calculated
            
            return reconst_path, final_total_cost, step_details

        # Xử lý neighbors (giống Graph.a_star_algorithm)
        for (m, weight) in graph.get_neighbors(n):
            if m not in open_lst and m not in closed_lst:
                open_lst.add(m)
                par[m] = n
                poo[m] = poo[n] + weight
            else:
                if poo[m] > poo[n] + weight:
                    poo[m] = poo[n] + weight
                    par[m] = n
                    if m in closed_lst:
                        closed_lst.remove(m)
                        open_lst.add(m)

        open_lst.remove(n)
        closed_lst.add(n)

    return None, None, None


# ========== N-PUZZLE CLASSES ==========
# Sử dụng class nodes từ puzzle15_akt.py (đã import với tên PuzzleNodes)
# PuzzleNode giờ là alias cho PuzzleNodes từ puzzle15_akt.py
# Class này đã có sẵn __lt__ method để so sánh dựa trên f = g + h (A* algorithm)
PuzzleNode = PuzzleNodes


class AStarDemoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Demo Thuật Toán A* - AKT(Puzzle)")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Biến lưu trữ cho đồ thị
        self.current_graph = None
        self.current_positions = None
        self.current_vertices = None
        self.current_path = None
        self.current_step_details = None
        self.vertex_heuristics = {}
        self.is_directed = True
        
        # Biến lưu trữ cho N-Puzzle
        self.puzzle_mode = "graph"  # "graph" hoặc "puzzle"
        self.puzzle_size = 4
        self.puzzle_initial = None
        self.puzzle_final = None
        self.puzzle_solution = None
        self.puzzle_steps = None
        self.current_puzzle_step = 0  # Bước hiện tại đang xem
        
        # Biến cho drag and drop
        self.dragged_vertex = None
        self.canvas_positions = {}  # Lưu vị trí trên canvas (sau khi scale)
        self.scale = 1
        self.offset_x = 0
        self.offset_y = 0
        
        # Màu sắc cho các đỉnh
        self.vertex_colors = [
            '#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a',
            '#fee140', '#30cfd0', '#a8edea', '#fed6e3', '#ff9a9e',
            '#a18cd1', '#fbc2eb', '#ffecd2', '#fcb69f', '#ff8a80',
            '#84fab0', '#8fd3f4', '#d299c2', '#fef9d7', '#89f7fe',
            '#66a6ff', '#f6d365', '#fda085', '#96fbc4', '#f9d423',
            '#ff4e50', '#fc913a', '#fce043', '#00f2fe', '#4facfe'
        ]
        
        self.setup_ui()
    
    def setup_ui(self):
        # Frame điều khiển bên trái
        control_frame = tk.Frame(self.root, bg='#e8e8e8', width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        control_frame.pack_propagate(False)
        
        # Tiêu đề
        title_label = tk.Label(control_frame, text="A* và AKT", 
                               font=('Arial', 16, 'bold'), bg='#e8e8e8', fg='#667eea')
        title_label.pack(pady=10)
        
        # Chọn mode: Đồ thị hoặc N-Puzzle
        tk.Label(control_frame, text="Chọn bài toán:", font=('Arial', 10, 'bold'), 
                bg='#e8e8e8').pack(anchor='w', padx=10, pady=(10, 5))
        self.mode_var = tk.StringVar(value="graph")
        graph_mode_radio = tk.Radiobutton(control_frame, text="A* cho Đồ Thị", 
                                         variable=self.mode_var, value="graph", 
                                         bg='#e8e8e8', font=('Arial', 9),
                                         command=self.switch_mode)
        graph_mode_radio.pack(anchor='w', padx=20)
        puzzle_mode_radio = tk.Radiobutton(control_frame, text="AKT cho N-Puzzle", 
                                          variable=self.mode_var, value="puzzle", 
                                          bg='#e8e8e8', font=('Arial', 9),
                                          command=self.switch_mode)
        puzzle_mode_radio.pack(anchor='w', padx=20)
        
        # Frame cho điều khiển đồ thị
        self.graph_control_frame = tk.Frame(control_frame, bg='#e8e8e8')
        self.graph_control_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame cho điều khiển N-Puzzle
        self.puzzle_control_frame = tk.Frame(control_frame, bg='#e8e8e8')
        
        # Nhập số đỉnh
        tk.Label(self.graph_control_frame, text="Số đỉnh (n):", font=('Arial', 10, 'bold'), 
                bg='#e8e8e8').pack(anchor='w', padx=10, pady=(10, 5))
        self.n_var = tk.StringVar(value="9")
        n_entry = tk.Entry(self.graph_control_frame, textvariable=self.n_var, font=('Arial', 11), width=15)
        n_entry.pack(padx=10, pady=5)
        
        # Chọn loại đồ thị
        tk.Label(self.graph_control_frame, text="Loại đồ thị:", font=('Arial', 10, 'bold'), 
                bg='#e8e8e8').pack(anchor='w', padx=10, pady=(10, 5))
        self.graph_type_var = tk.StringVar(value="grid")
        grid_radio = tk.Radiobutton(self.graph_control_frame, text="Lưới (Grid)", 
                                    variable=self.graph_type_var, value="grid", 
                                    bg='#e8e8e8', font=('Arial', 9))
        grid_radio.pack(anchor='w', padx=20)
        random_radio = tk.Radiobutton(self.graph_control_frame, text="Ngẫu nhiên (Random)", 
                                     variable=self.graph_type_var, value="random", 
                                     bg='#e8e8e8', font=('Arial', 9))
        random_radio.pack(anchor='w', padx=20)
        
        # Chọn hướng đồ thị
        tk.Label(self.graph_control_frame, text="Hướng đồ thị:", font=('Arial', 10, 'bold'), 
                bg='#e8e8e8').pack(anchor='w', padx=10, pady=(10, 5))
        self.directed_var = tk.BooleanVar(value=True)
        directed_radio = tk.Radiobutton(self.graph_control_frame, text="Có hướng (Directed)", 
                                       variable=self.directed_var, value=True, 
                                       bg='#e8e8e8', font=('Arial', 9))
        directed_radio.pack(anchor='w', padx=20)
        undirected_radio = tk.Radiobutton(self.graph_control_frame, text="Vô hướng (Undirected)", 
                                         variable=self.directed_var, value=False, 
                                         bg='#e8e8e8', font=('Arial', 9))
        undirected_radio.pack(anchor='w', padx=20)
        
        # Nút tạo đồ thị
        create_graph_btn = tk.Button(self.graph_control_frame, text="Tạo Đồ Thị", 
                               command=self.create_graph, bg='#667eea', fg='white',
                               font=('Arial', 11, 'bold'), width=20, height=2)
        create_graph_btn.pack(pady=15)
        
        # Chọn đỉnh bắt đầu
        tk.Label(self.graph_control_frame, text="Đỉnh bắt đầu:", font=('Arial', 10, 'bold'), 
                bg='#e8e8e8').pack(anchor='w', padx=10, pady=(20, 5))
        self.start_var = tk.StringVar()
        self.start_combo = ttk.Combobox(self.graph_control_frame, textvariable=self.start_var, 
                                       state='readonly', width=15, font=('Arial', 10))
        self.start_combo.pack(padx=10, pady=5)
        
        # Chọn đỉnh kết thúc
        tk.Label(self.graph_control_frame, text="Đỉnh kết thúc:", font=('Arial', 10, 'bold'), 
                bg='#e8e8e8').pack(anchor='w', padx=10, pady=(10, 5))
        self.stop_var = tk.StringVar()
        self.stop_combo = ttk.Combobox(self.graph_control_frame, textvariable=self.stop_var, 
                                      state='readonly', width=15, font=('Arial', 10))
        self.stop_combo.pack(padx=10, pady=5)
        # Bind event để tính lại heuristic khi chọn đỉnh đích
        self.stop_combo.bind('<<ComboboxSelected>>', self.on_stop_vertex_changed)
        
        # Nút tìm đường đi
        find_path_btn = tk.Button(self.graph_control_frame, text="Tìm Đường Đi", 
                            command=self.find_path, bg='#f5576c', fg='white',
                            font=('Arial', 11, 'bold'), width=20, height=2)
        find_path_btn.pack(pady=15)
        
        # Frame cho N-Puzzle
        self.puzzle_control_frame = tk.Frame(control_frame, bg='#e8e8e8')
        
        tk.Label(self.puzzle_control_frame, text="N-Puzzle (AKT)", font=('Arial', 11, 'bold'), 
                bg='#e8e8e8', fg='#4caf50').pack(pady=10)
        
        # Nhập kích thước puzzle
        tk.Label(self.puzzle_control_frame, text="Kích thước (n x n):", font=('Arial', 10, 'bold'), 
                bg='#e8e8e8').pack(anchor='w', padx=10, pady=(10, 5))
        self.puzzle_n_var = tk.StringVar(value="4")
        puzzle_n_entry = tk.Entry(self.puzzle_control_frame, textvariable=self.puzzle_n_var, 
                                  font=('Arial', 11), width=15)
        puzzle_n_entry.pack(padx=10, pady=5)
        tk.Label(self.puzzle_control_frame, text="(Ví dụ: 3 = 8-puzzle, 4 = 15-puzzle)", 
                font=('Arial', 8, 'italic'), bg='#e8e8e8', fg='#666').pack(anchor='w', padx=10)
        
        # Nút tạo puzzle mặc định
        create_puzzle_btn = tk.Button(self.puzzle_control_frame, text="Tạo Puzzle Mặc Định", 
                                     command=self.create_default_puzzle, bg='#4caf50', fg='white',
                                     font=('Arial', 10, 'bold'), width=20)
        create_puzzle_btn.pack(pady=10)
        
        # Nút tạo puzzle ngẫu nhiên
        create_random_puzzle_btn = tk.Button(self.puzzle_control_frame, text="Tạo Puzzle Ngẫu Nhiên", 
                                            command=self.create_random_puzzle, bg='#ff9800', fg='white',
                                            font=('Arial', 10, 'bold'), width=20)
        create_random_puzzle_btn.pack(pady=5)
        
        # Nút giải puzzle
        solve_puzzle_btn = tk.Button(self.puzzle_control_frame, text="Giải Puzzle", 
                                    command=self.solve_puzzle, bg='#f5576c', fg='white',
                                    font=('Arial', 11, 'bold'), width=20, height=2)
        solve_puzzle_btn.pack(pady=15)
        
        # Frame điều hướng các bước
        nav_frame = tk.Frame(self.puzzle_control_frame, bg='#e8e8e8')
        nav_frame.pack(pady=10)
        
        self.prev_btn = tk.Button(nav_frame, text="◀ Bước trước", 
                                  command=self.prev_puzzle_step, bg='#2196f3', fg='white',
                                  font=('Arial', 9, 'bold'), width=10, state='disabled')
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.step_label = tk.Label(nav_frame, text="Bước: 0/0", 
                                   font=('Arial', 9), bg='#e8e8e8')
        self.step_label.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = tk.Button(nav_frame, text="Bước sau ▶", 
                                  command=self.next_puzzle_step, bg='#2196f3', fg='white',
                                  font=('Arial', 9, 'bold'), width=10, state='disabled')
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame hiển thị kết quả bên phải
        result_frame = tk.Frame(self.root, bg='white')
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Notebook để hiển thị nhiều tab
        notebook = ttk.Notebook(result_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Vẽ đồ thị / N-Puzzle
        self.main_vis_frame = tk.Frame(notebook, bg='white')
        notebook.add(self.main_vis_frame, text="Hiển Thị")
        # Canvas để vẽ đồ thị
        self.canvas = tk.Canvas(self.main_vis_frame, bg='#fafafa', width=800, height=600)
        
        # Canvas cho N-Puzzle (kích thước lớn hơn để hỗ trợ puzzle lớn)
        self.puzzle_canvas = tk.Canvas(self.main_vis_frame, bg='#fafafa', width=600, height=600)
        # Bind event để vẽ lại khi canvas resize
        self.puzzle_canvas.bind('<Configure>', self.on_puzzle_canvas_resize)
        
        # Bind events cho drag and drop
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Tab 2: Kết quả
        result_tab_frame = tk.Frame(notebook, bg='white')
        notebook.add(result_tab_frame, text="Kết Quả")
        
        # Frame cho kết quả đồ thị
        self.graph_result_frame = tk.Frame(result_tab_frame, bg='white')
        
        # Frame cho đường đi và tổng chi phí
        path_frame = tk.Frame(self.graph_result_frame, bg='white')
        path_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(path_frame, text="Đường đi tìm được:", font=('Arial', 11, 'bold'), 
                bg='white').pack(anchor='w')
        self.path_label = tk.Label(path_frame, text="Chưa tìm đường đi", 
                                  font=('Arial', 12), bg='white', fg='#667eea')
        self.path_label.pack(anchor='w', pady=5)
        
        tk.Label(path_frame, text="Tổng chi phí:", font=('Arial', 11, 'bold'), 
                bg='white').pack(anchor='w', pady=(10, 0))
        self.cost_label = tk.Label(path_frame, text="0", font=('Arial', 12), 
                                   bg='white', fg='#f5576c')
        self.cost_label.pack(anchor='w', pady=5)
        
        # Bảng chi tiết từng bước
        detail_frame = tk.Frame(self.graph_result_frame, bg='white')
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(detail_frame, text="Chi tiết từng bước:", font=('Arial', 11, 'bold'), 
                bg='white').pack(anchor='w', pady=(0, 5))
        
        # Tạo Treeview để hiển thị bảng
        columns = ('Bước', 'Đỉnh', 'g (chi phí từ đầu)', 'h (heuristic)', 'f (g + h)', 'Chi phí bước')
        self.detail_tree = ttk.Treeview(detail_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.detail_tree.heading(col, text=col)
            self.detail_tree.column(col, width=120, anchor='center')
        
        scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.detail_tree.yview)
        self.detail_tree.configure(yscrollcommand=scrollbar.set)
        
        self.detail_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame cho kết quả N-Puzzle
        self.puzzle_result_frame = tk.Frame(result_tab_frame, bg='white')
        
        tk.Label(self.puzzle_result_frame, text="Kết quả giải N-Puzzle:", 
                font=('Arial', 11, 'bold'), bg='white').pack(anchor='w', padx=10, pady=10)
        
        self.result_text = scrolledtext.ScrolledText(self.puzzle_result_frame, 
                                                     font=('Courier', 10), 
                                                     wrap=tk.WORD, width=80, height=30)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Khởi tạo hiển thị mặc định (đồ thị)
        self.graph_control_frame.pack(fill=tk.X, padx=5, pady=5)
        self.puzzle_control_frame.pack_forget()
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.puzzle_canvas.pack_forget()
        self.graph_result_frame.pack(fill=tk.BOTH, expand=True)
        self.puzzle_result_frame.pack_forget()
        
        # Panel chỉnh sửa giá trị h
        h_edit_frame = tk.Frame(control_frame, bg='#e8e8e8')
        h_edit_frame.pack(fill=tk.X, padx=10, pady=(20, 10))
        
        tk.Label(h_edit_frame, text="Chỉnh sửa giá trị h:", font=('Arial', 10, 'bold'), 
                bg='#e8e8e8').pack(anchor='w', pady=(0, 5))
        
        tk.Label(h_edit_frame, text="Đỉnh:", font=('Arial', 9), bg='#e8e8e8').pack(anchor='w')
        self.h_vertex_var = tk.StringVar()
        self.h_vertex_combo = ttk.Combobox(h_edit_frame, textvariable=self.h_vertex_var, 
                                          state='readonly', width=12, font=('Arial', 9))
        self.h_vertex_combo.pack(pady=2)
        
        tk.Label(h_edit_frame, text="Giá trị h:", font=('Arial', 9), bg='#e8e8e8').pack(anchor='w', pady=(5, 0))
        self.h_value_var = tk.StringVar()
        h_entry = tk.Entry(h_edit_frame, textvariable=self.h_value_var, font=('Arial', 10), width=12)
        h_entry.pack(pady=2)
        
        update_h_btn = tk.Button(h_edit_frame, text="Cập nhật h", 
                                command=self.update_heuristic_value, bg='#4caf50', fg='white',
                                font=('Arial', 9, 'bold'), width=12)
        update_h_btn.pack(pady=5)
        
        reset_h_btn = tk.Button(h_edit_frame, text="Reset (tính lại)", 
                               command=self.reset_heuristic, bg='#ff9800', fg='white',
                               font=('Arial', 9, 'bold'), width=12)
        reset_h_btn.pack(pady=2)
    
    def create_graph(self):
        try:
            n = int(self.n_var.get())
            if n < 2 or n > 50:
                messagebox.showerror("Lỗi", "Số đỉnh phải từ 2 đến 50!")
                return
            
            graph_type = self.graph_type_var.get()
            directed = self.directed_var.get()
            
            if graph_type == "grid":
                adjac_lis, positions, vertices = create_grid_graph(n, directed=directed)
            else:
                adjac_lis, positions, vertices = create_random_graph(n, directed=directed)
            
            self.current_graph = adjac_lis
            self.current_positions = positions
            self.current_vertices = vertices
            self.current_path = None
            self.current_step_details = None
            self.is_directed = directed
            
            # Cập nhật combobox
            self.start_combo['values'] = vertices
            self.stop_combo['values'] = vertices
            if vertices:
                self.start_combo.set(vertices[0])
                self.stop_combo.set(vertices[-1])
            
            # Cập nhật combobox cho chỉnh sửa h
            self.h_vertex_combo['values'] = vertices
            
            # Tính heuristic nếu đã chọn đỉnh đích (theo đường chim bay)
            if self.stop_var.get():
                self.on_stop_vertex_changed()
            
            # Vẽ đồ thị
            self.draw_graph_visualization()
            
            graph_type_str = "có hướng" if directed else "vô hướng"
            messagebox.showinfo("Thành công", f"Đã tạo đồ thị {graph_type_str} với {n} đỉnh!\nHeuristic h được tính theo đường chim bay (Euclidean distance).")
            
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def display_graph_info(self):
        if not self.current_graph:
            return
        
        info_text = "=" * 70 + "\n"
        info_text += "THÔNG TIN ĐỒ THỊ\n"
        info_text += "=" * 70 + "\n\n"
        info_text += f"Số đỉnh: {len(self.current_vertices)}\n"
        info_text += f"Danh sách đỉnh: {', '.join(self.current_vertices)}\n"
        
        graph_type_str = "có hướng" if hasattr(self, 'is_directed') and self.is_directed else "vô hướng"
        info_text += f"Loại đồ thị: {graph_type_str.upper()}\n\n"
        info_text += f"Danh sách kề (đồ thị {graph_type_str}):\n"
        info_text += "-" * 70 + "\n"
        
        for vertex in self.current_vertices:
            neighbors = self.current_graph.get(vertex, [])
            if neighbors:
                neighbor_str = ', '.join([f"{n}({w})" for n, w in neighbors])
                info_text += f"{vertex} -> [{neighbor_str}]\n"
            else:
                info_text += f"{vertex} -> []\n"
        
        # Không cần hiển thị graph_info_text nữa vì đã có detail_tree
    
    def find_path(self):
        if not self.current_graph:
            messagebox.showwarning("Cảnh báo", "Vui lòng tạo đồ thị trước!")
            return
        
        start = self.start_var.get()
        stop = self.stop_var.get()
        
        if not start or not stop:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn đỉnh bắt đầu và đỉnh kết thúc!")
            return
        
        if start == stop:
            messagebox.showwarning("Cảnh báo", "Đỉnh bắt đầu và đỉnh kết thúc phải khác nhau!")
            return
        
        try:
            # Tạo đồ thị sử dụng class Graph từ astar_graph.py
            graph = Graph(self.current_graph)
            for vertex, (x, y) in self.current_positions.items():
                graph.set_position(vertex, x, y)  # Thiết lập tọa độ để tính heuristic Euclidean
            
            # Tính giá trị h cho tất cả đỉnh (sử dụng graph.h từ astar_graph.py)
            self.vertex_heuristics = {}
            for vertex in self.current_vertices:
                self.vertex_heuristics[vertex] = round(graph.h(vertex, stop), 2)
            
            # Chạy A* với details (dựa trên logic từ Graph.a_star_algorithm)
            path, total_cost, step_details = a_star_with_details(graph, start, stop)
            
            if path:
                self.current_path = path
                self.current_step_details = step_details
                
                # Hiển thị đường đi
                path_str = ' → '.join(path)
                self.path_label.config(text=path_str, fg='#667eea')
                
                # Hiển thị tổng chi phí
                self.cost_label.config(text=str(round(total_cost, 2)), fg='#f5576c')
                
                # Hiển thị bảng chi tiết
                self.display_step_details(step_details)
                
                # Vẽ lại đồ thị với đường đi
                self.draw_graph_visualization()
                
                messagebox.showinfo("Thành công", f"Tìm thấy đường đi với tổng chi phí: {round(total_cost, 2)}")
            else:
                messagebox.showwarning("Không tìm thấy", "Không tìm thấy đường đi từ {} đến {}!".format(start, stop))
                self.path_label.config(text="Không tìm thấy đường đi", fg='red')
                self.cost_label.config(text="N/A", fg='red')
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def display_step_details(self, step_details):
        # Xóa dữ liệu cũ
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)
        
        # Thêm dữ liệu mới
        for i, step in enumerate(step_details):
            step_num = str(i + 1)
            vertex = step['vertex']
            g = str(step['g'])
            h = str(step['h'])
            f = str(step['f'])
            step_cost = str(step['step_cost']) if step['step_cost'] > 0 else '-'
            
            self.detail_tree.insert('', 'end', values=(step_num, vertex, g, h, f, step_cost))
    
    def display_heuristics(self, start, stop):
        if not self.vertex_heuristics:
            return
        
        heuristic_text = "=" * 70 + "\n"
        heuristic_text += "GIÁ TRỊ HEURISTIC (h) CỦA CÁC ĐỈNH\n"
        heuristic_text += "=" * 70 + "\n\n"
        heuristic_text += f"Đỉnh đích: {stop}\n"
        heuristic_text += f"Phương pháp tính: Đường chim bay (Euclidean distance)\n"
        heuristic_text += f"Công thức: h = √[(x₁-x₂)² + (y₁-y₂)²]\n\n"
        
        for vertex in sorted(self.vertex_heuristics.keys()):
            h_value = self.vertex_heuristics[vertex]
            marker = ""
            if vertex == start:
                marker = " [BẮT ĐẦU]"
            elif vertex == stop:
                marker = " [KẾT THÚC]"
            elif self.current_path and vertex in self.current_path:
                marker = " [TRONG ĐƯỜNG ĐI]"
            
            heuristic_text += f"  {vertex}: h = {h_value}{marker}\n"
        
        self.heuristic_text.delete('1.0', tk.END)
        self.heuristic_text.insert('1.0', heuristic_text)
    
    def draw_graph_visualization(self):
        """Vẽ đồ thị trực quan trên canvas"""
        if not self.current_graph or not self.current_positions:
            return
        
        # Xóa canvas
        self.canvas.delete("all")
        
        # Lấy kích thước canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas chưa được render, đợi một chút
            self.root.after(100, self.draw_graph_visualization)
            return
        
        # Tính toán scale và offset để căn giữa đồ thị
        if self.current_positions:
            all_x = [pos[0] for pos in self.current_positions.values()]
            all_y = [pos[1] for pos in self.current_positions.values()]
            min_x, max_x = min(all_x), max(all_x)
            min_y, max_y = min(all_y), max(all_y)
            
            graph_width = max_x - min_x if max_x > min_x else 400
            graph_height = max_y - min_y if max_y > min_y else 400
            
            scale_x = (canvas_width - 100) / graph_width if graph_width > 0 else 1
            scale_y = (canvas_height - 100) / graph_height if graph_height > 0 else 1
            scale = min(scale_x, scale_y, 1.5)  # Giới hạn scale
            
            offset_x = (canvas_width - graph_width * scale) / 2 - min_x * scale
            offset_y = (canvas_height - graph_height * scale) / 2 - min_y * scale
        else:
            scale = 1
            offset_x = canvas_width / 2
            offset_y = canvas_height / 2
        
        # Vẽ các cạnh
        for vertex, neighbors in self.current_graph.items():
            if vertex not in self.current_positions:
                continue
            x1, y1 = self.current_positions[vertex]
            x1 = x1 * scale + offset_x
            y1 = y1 * scale + offset_y
            
            for neighbor, weight in neighbors:
                if neighbor not in self.current_positions:
                    continue
                x2, y2 = self.current_positions[neighbor]
                x2 = x2 * scale + offset_x
                y2 = y2 * scale + offset_y
                
                # Kiểm tra xem cạnh này có trong đường đi không
                is_in_path = False
                if self.current_path:
                    for i in range(len(self.current_path) - 1):
                        if self.current_path[i] == vertex and self.current_path[i + 1] == neighbor:
                            is_in_path = True
                            break
                
                # Vẽ cạnh
                edge_color = '#f5576c' if is_in_path else '#ccc'
                edge_width = 3 if is_in_path else 1
                
                if self.is_directed:
                    # Vẽ mũi tên cho đồ thị có hướng
                    self.draw_arrow(self.canvas, x1, y1, x2, y2, edge_color, edge_width)
                else:
                    # Vẽ đường thẳng cho đồ thị vô hướng
                    self.canvas.create_line(x1, y1, x2, y2, fill=edge_color, width=edge_width)
                
                # Vẽ trọng số ở giữa cạnh
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                
                text_color = '#f5576c' if is_in_path else '#333'
                bg_color = '#ffe0e0' if is_in_path else 'white'
                outline_color = '#f5576c' if is_in_path else '#666'
                
                # Vẽ nền tròn cho trọng số
                self.canvas.create_oval(mid_x - 18, mid_y - 12, mid_x + 18, mid_y + 12,
                                      fill=bg_color, outline=outline_color, width=2)
                self.canvas.create_text(mid_x, mid_y, text=f"{weight:.1f}", 
                                       fill=text_color, font=('Arial', 9, 'bold' if is_in_path else 'bold'))
        
        # Lưu scale và offset để dùng cho drag and drop
        self.scale = scale
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.canvas_positions = {}
        
        # Vẽ các đỉnh
        for vertex, (orig_x, orig_y) in self.current_positions.items():
            x = orig_x * scale + offset_x
            y = orig_y * scale + offset_y
            
            # Lưu vị trí canvas
            self.canvas_positions[vertex] = (x, y)
            
            # Xác định màu đỉnh - mỗi đỉnh có màu riêng
            if self.current_path:
                if vertex == self.current_path[0]:
                    color = '#4caf50'  # Xanh lá - đỉnh bắt đầu
                elif vertex == self.current_path[-1]:
                    color = '#f5576c'  # Đỏ - đỉnh kết thúc
                elif vertex in self.current_path:
                    color = '#ff9800'  # Cam - đỉnh trong đường đi
                else:
                    # Đỉnh không trong đường đi - dùng màu riêng
                    color = self.get_vertex_color(vertex)
            else:
                # Chưa có đường đi - dùng màu riêng cho mỗi đỉnh
                color = self.get_vertex_color(vertex)
            
            # Vẽ vòng tròn đỉnh với tag để có thể drag
            radius = 20
            oval_id = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, 
                                             fill=color, outline='white', width=3, tags=(f"vertex_{vertex}", "vertex"))
            text_id = self.canvas.create_text(x, y, text=vertex, fill='white', 
                                             font=('Arial', 12, 'bold'), tags=(f"vertex_{vertex}", "vertex"))
            
            # Vẽ giá trị h dưới đỉnh (nhỏ gọn)
            if self.vertex_heuristics and vertex in self.vertex_heuristics:
                h_value = self.vertex_heuristics[vertex]
                # Vẽ text h nhỏ dưới đỉnh
                h_text_id = self.canvas.create_text(x, y + 28, text=f"h={h_value:.1f}", 
                                                   fill='#333', font=('Arial', 8), tags=(f"h_{vertex}", "h_value", f"vertex_{vertex}", "vertex"))
    
    def get_vertex_color(self, vertex):
        """Lấy màu cho đỉnh dựa trên tên đỉnh"""
        if not self.current_vertices:
            return '#667eea'
        
        try:
            index = self.current_vertices.index(vertex)
            return self.vertex_colors[index % len(self.vertex_colors)]
        except:
            return '#667eea'
    
    def on_stop_vertex_changed(self, event=None):
        """Tính lại heuristic khi chọn đỉnh đích"""
        if not self.current_graph or not self.current_positions:
            return
        
        stop = self.stop_var.get()
        if not stop:
            return
        
        try:
            # Tạo đồ thị
            graph = Graph(self.current_graph)
            for vertex, (x, y) in self.current_positions.items():
                graph.set_position(vertex, x, y)
            
            # Tính lại giá trị h cho tất cả đỉnh (theo đường chim bay - Euclidean)
            self.vertex_heuristics = {}
            for vertex in self.current_vertices:
                # Tính Euclidean distance từ đỉnh đến đích
                h_value = graph.h(vertex, stop)
                self.vertex_heuristics[vertex] = round(h_value, 2)
            
            # Vẽ lại đồ thị để hiển thị giá trị h mới
            self.draw_graph_visualization()
        except Exception as e:
            print(f"Lỗi khi tính lại heuristic: {e}")
    
    def draw_arrow(self, canvas, x1, y1, x2, y2, color, width):
        """Vẽ mũi tên từ (x1, y1) đến (x2, y2)"""
        # Tính toán vị trí mũi tên (tránh vẽ vào trong đỉnh)
        radius = 20
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return
        
        unit_x = dx / distance
        unit_y = dy / distance
        
        # Điểm bắt đầu và kết thúc (cách tâm đỉnh một khoảng bằng bán kính)
        start_x = x1 + unit_x * radius
        start_y = y1 + unit_y * radius
        end_x = x2 - unit_x * radius
        end_y = y2 - unit_y * radius
        
        # Vẽ đường thẳng
        canvas.create_line(start_x, start_y, end_x, end_y, fill=color, width=width)
        
        # Vẽ mũi tên
        arrow_length = 12
        angle = math.atan2(dy, dx)
        
        # Tính toán 3 điểm của mũi tên
        arrow_x1 = end_x - arrow_length * math.cos(angle - math.pi / 6)
        arrow_y1 = end_y - arrow_length * math.sin(angle - math.pi / 6)
        arrow_x2 = end_x - arrow_length * math.cos(angle + math.pi / 6)
        arrow_y2 = end_y - arrow_length * math.sin(angle + math.pi / 6)
        
        # Vẽ tam giác mũi tên
        canvas.create_polygon(end_x, end_y, arrow_x1, arrow_y1, arrow_x2, arrow_y2, 
                            fill=color, outline=color)
    
    def on_canvas_click(self, event):
        """Xử lý khi click vào canvas"""
        x, y = event.x, event.y
        
        # Tìm đỉnh gần nhất
        min_dist = float('inf')
        clicked_vertex = None
        
        for vertex, (vx, vy) in self.canvas_positions.items():
            dist = math.sqrt((x - vx)**2 + (y - vy)**2)
            if dist < 30 and dist < min_dist:  # 30 là bán kính + một chút
                min_dist = dist
                clicked_vertex = vertex
        
        if clicked_vertex:
            self.dragged_vertex = clicked_vertex
    
    def on_canvas_drag(self, event):
        """Xử lý khi drag đỉnh"""
        if not self.dragged_vertex:
            return
        
        x, y = event.x, event.y
        
        # Cập nhật vị trí canvas
        self.canvas_positions[self.dragged_vertex] = (x, y)
        
        # Chuyển đổi về tọa độ gốc
        orig_x = (x - self.offset_x) / self.scale if self.scale > 0 else x
        orig_y = (y - self.offset_y) / self.scale if self.scale > 0 else y
        
        # Cập nhật vị trí gốc
        if self.current_positions:
            self.current_positions[self.dragged_vertex] = (orig_x, orig_y)
        
        # Vẽ lại đồ thị
        self.draw_graph_visualization()
    
    def on_canvas_release(self, event):
        """Xử lý khi thả chuột"""
        if self.dragged_vertex:
            # Nếu đã có đường đi, tính lại heuristic và vẽ lại
            if self.current_path and self.stop_var.get():
                try:
                    stop = self.stop_var.get()
                    graph = Graph(self.current_graph)
                    for vertex, (vx, vy) in self.current_positions.items():
                        graph.set_position(vertex, vx, vy)
                    
                    # Tính lại heuristic
                    self.vertex_heuristics = {}
                    for vertex in self.current_vertices:
                        self.vertex_heuristics[vertex] = round(graph.h(vertex, stop), 2)
                    
                    # Vẽ lại
                    self.draw_graph_visualization()
                except:
                    pass
        
        self.dragged_vertex = None
    
    def update_heuristic_value(self):
        """Cập nhật giá trị h cho đỉnh được chọn"""
        vertex = self.h_vertex_var.get()
        try:
            h_value = float(self.h_value_var.get())
            
            if not vertex:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn đỉnh!")
                return
            
            if vertex not in self.current_vertices:
                messagebox.showerror("Lỗi", f"Đỉnh {vertex} không tồn tại!")
                return
            
            # Cập nhật giá trị h
            self.vertex_heuristics[vertex] = round(h_value, 2)
            
            # Vẽ lại đồ thị
            self.draw_graph_visualization()
            
            # Nếu đã có đường đi, tính lại với giá trị h mới
            if self.current_path and self.start_var.get() and self.stop_var.get():
                try:
                    start = self.start_var.get()
                    stop = self.stop_var.get()
                    graph = Graph(self.current_graph)
                    for v, (vx, vy) in self.current_positions.items():
                        graph.set_position(v, vx, vy)
                    
                    # Override hàm h để sử dụng giá trị tùy chỉnh
                    original_h = graph.h
                    custom_heuristics = self.vertex_heuristics.copy()
                    
                    def custom_h(n, goal=None):
                        if goal == stop and n in custom_heuristics:
                            return custom_heuristics[n]
                        return original_h(n, goal)
                    
                    graph.h = custom_h
                    
                    # Chạy lại A*
                    path, total_cost, step_details = a_star_with_details(graph, start, stop)
                    
                    if path:
                        self.current_path = path
                        self.current_step_details = step_details
                        path_str = ' → '.join(path)
                        self.path_label.config(text=path_str, fg='#667eea')
                        self.cost_label.config(text=str(round(total_cost, 2)), fg='#f5576c')
                        self.display_step_details(step_details)
                        self.draw_graph_visualization()
                except Exception as e:
                    print(f"Lỗi khi tính lại đường đi: {e}")
            
            messagebox.showinfo("Thành công", f"Đã cập nhật giá trị h của đỉnh {vertex} thành {round(h_value, 2)}")
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ!")
    
    def reset_heuristic(self):
        """Reset giá trị h về tính toán theo đường chim bay"""
        if not self.stop_var.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn đỉnh đích trước!")
            return
        
        self.on_stop_vertex_changed()
        messagebox.showinfo("Thành công", "Đã reset giá trị h về tính toán theo đường chim bay!")
    
    def switch_mode(self):
        """Chuyển đổi giữa N-Puzzle và Đồ Thị"""
        problem_type = self.mode_var.get()
        self.puzzle_mode = problem_type
        
        if problem_type == "puzzle":
            # Ẩn frame đồ thị, hiện frame puzzle
            self.graph_control_frame.pack_forget()
            self.puzzle_control_frame.pack(fill=tk.X, padx=5, pady=5)
            # Ẩn canvas đồ thị, hiện canvas puzzle
            self.canvas.pack_forget()
            self.puzzle_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            # Ẩn kết quả đồ thị, hiện kết quả puzzle
            self.graph_result_frame.pack_forget()
            self.puzzle_result_frame.pack(fill=tk.BOTH, expand=True)
        else:
            # Ẩn frame puzzle, hiện frame đồ thị
            self.puzzle_control_frame.pack_forget()
            self.graph_control_frame.pack(fill=tk.X, padx=5, pady=5)
            # Ẩn canvas puzzle, hiện canvas đồ thị
            self.puzzle_canvas.pack_forget()
            self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            # Ẩn kết quả puzzle, hiện kết quả đồ thị
            self.puzzle_result_frame.pack_forget()
            self.graph_result_frame.pack(fill=tk.BOTH, expand=True)
    
    # ========== N-PUZZLE FUNCTIONS ==========
    
    def calculate_puzzle_cost(self, mats, final):
        """
        Tính Manhattan distance heuristic cho N-Puzzle
        Dựa trên hàm calculateCosts từ puzzle15_akt.py nhưng hỗ trợ n-puzzle
        """
        n = len(mats)
        distance = 0
        for i in range(n):
            for j in range(n):
                if mats[i][j] != 0:
                    value = mats[i][j]
                    target_row = (value - 1) // n
                    target_col = (value - 1) % n
                    distance += abs(i - target_row) + abs(j - target_col)
        return distance
    
    def create_puzzle_node(self, mats, empty_tile_posi, new_empty_tile_posi, levels, parent, final):
        """
        Tạo node mới cho N-Puzzle
        Dựa trên hàm newNodes từ puzzle15_akt.py nhưng hỗ trợ n-puzzle
        """
        new_mats = copy.deepcopy(mats)
        x1, y1 = empty_tile_posi[0], empty_tile_posi[1]
        x2, y2 = new_empty_tile_posi[0], new_empty_tile_posi[1]
        new_mats[x1][y1], new_mats[x2][y2] = new_mats[x2][y2], new_mats[x1][y1]
        costs = self.calculate_puzzle_cost(new_mats, final)
        return PuzzleNode(parent, new_mats, new_empty_tile_posi, costs, levels)
    
    def is_safe_puzzle(self, row, col):
        """
        Kiểm tra vị trí có hợp lệ trong puzzle
        Dựa trên hàm isSafe từ puzzle15_akt.py nhưng hỗ trợ n-puzzle
        """
        return 0 <= row < self.puzzle_size and 0 <= col < self.puzzle_size
    
    def solve_puzzle_algorithm(self, initial, empty_tile_posi, final):
        """
        Giải N-Puzzle bằng A*
        Dựa trên logic từ hàm solve trong puzzle15_akt.py nhưng hỗ trợ n-puzzle
        Sử dụng priorityQueue và nodes từ puzzle15_akt.py
        """
        rows = [1, 0, -1, 0]  # bottom, left, top, right (giống puzzle15_akt.py)
        cols = [0, -1, 0, 1]
        
        # Sử dụng priorityQueue từ puzzle15_akt.py
        pq = priorityQueue()
        
        # Tạo root node (giống puzzle15_akt.py)
        costs = self.calculate_puzzle_cost(initial, final)
        root = PuzzleNode(None, initial, empty_tile_posi, costs, 0)
        pq.push(root)
        
        visited = set()
        solution_path = []
        
        while not pq.empty():
            # Lấy node có f nhỏ nhất (giống puzzle15_akt.py)
            minimum = pq.pop()
            
            # Convert matrix to tuple for set comparison (giống puzzle15_akt.py)
            mats_tuple = tuple(tuple(row) for row in minimum.mats)
            if mats_tuple in visited:
                continue
            visited.add(mats_tuple)
            
            # Nếu tìm thấy giải pháp (giống puzzle15_akt.py)
            if minimum.costs == 0:
                node = minimum
                while node:
                    solution_path.insert(0, copy.deepcopy(node.mats))
                    node = node.parent
                return solution_path, minimum.levels, len(visited)
            
            # Tạo các node con (giống puzzle15_akt.py)
            for i in range(4):
                new_tile_posi = [
                    minimum.empty_tile_posi[0] + rows[i],
                    minimum.empty_tile_posi[1] + cols[i]
                ]
                
                if self.is_safe_puzzle(new_tile_posi[0], new_tile_posi[1]):
                    child = self.create_puzzle_node(
                        minimum.mats, minimum.empty_tile_posi, new_tile_posi,
                        minimum.levels + 1, minimum, final
                    )
                    child_tuple = tuple(tuple(row) for row in child.mats)
                    if child_tuple not in visited:
                        pq.push(child)
        
        return None, None, len(visited)
    
    def create_default_puzzle(self):
        """Tạo puzzle mặc định với kích thước n x n"""
        try:
            n = int(self.puzzle_n_var.get())
            if n < 2 or n > 6:
                messagebox.showerror("Lỗi", "Kích thước puzzle phải từ 2 đến 6!")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ!")
            return
        
        self.puzzle_size = n
        total = n * n
        
        # Tạo puzzle ban đầu: gần giải được (chỉ đổi 2 số cuối)
        self.puzzle_initial = [[0] * n for _ in range(n)]
        num = 1
        for i in range(n):
            for j in range(n):
                if num < total:
                    self.puzzle_initial[i][j] = num
                    num += 1
        
        # Đổi 2 số cuối để tạo puzzle có thể giải được
        if total > 1:
            self.puzzle_initial[n-1][n-2], self.puzzle_initial[n-1][n-1] = \
                self.puzzle_initial[n-1][n-1], self.puzzle_initial[n-1][n-2]
        
        # Tạo puzzle đích (goal state)
        self.puzzle_final = [[0] * n for _ in range(n)]
        num = 1
        for i in range(n):
            for j in range(n):
                if num < total:
                    self.puzzle_final[i][j] = num
                    num += 1
        
        self.puzzle_solution = None
        self.puzzle_steps = None
        self.current_puzzle_step = 0
        self.draw_puzzle(self.puzzle_initial)
        self.update_puzzle_navigation(0)
        messagebox.showinfo("Thành công", f"Đã tạo {total-1}-puzzle ({n}x{n}) mặc định!")
    
    def count_inversions(self, puzzle_flat):
        """Đếm số inversion để kiểm tra puzzle có thể giải được"""
        inversions = 0
        n = len(puzzle_flat)
        for i in range(n):
            if puzzle_flat[i] == 0:
                continue
            for j in range(i + 1, n):
                if puzzle_flat[j] != 0 and puzzle_flat[i] > puzzle_flat[j]:
                    inversions += 1
        return inversions
    
    def is_solvable(self, puzzle, empty_row):
        """Kiểm tra puzzle có thể giải được không"""
        n = len(puzzle)
        puzzle_flat = [puzzle[i][j] for i in range(n) for j in range(n)]
        inversions = self.count_inversions(puzzle_flat)
        
        # Với puzzle n x n:
        # - Nếu n lẻ: puzzle giải được nếu số inversion chẵn
        # - Nếu n chẵn: puzzle giải được nếu (inversion + empty_row) chẵn
        if n % 2 == 1:
            return inversions % 2 == 0
        else:
            return (inversions + empty_row) % 2 == 0
    
    def create_random_puzzle(self):
        """Tạo puzzle ngẫu nhiên có thể giải được"""
        try:
            n = int(self.puzzle_n_var.get())
            if n < 2 or n > 6:
                messagebox.showerror("Lỗi", "Kích thước puzzle phải từ 2 đến 6!")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ!")
            return
        
        self.puzzle_size = n
        total = n * n
        
        # Tạo puzzle đích trước
        self.puzzle_final = [[0] * n for _ in range(n)]
        num = 1
        for i in range(n):
            for j in range(n):
                if num < total:
                    self.puzzle_final[i][j] = num
                    num += 1
        
        # Tạo puzzle ngẫu nhiên bằng cách di chuyển từ goal state
        # Điều này đảm bảo puzzle luôn có thể giải được
        import random
        rows = [1, 0, -1, 0]
        cols = [0, -1, 0, 1]
        
        current = copy.deepcopy(self.puzzle_final)
        empty_pos = [n-1, n-1]
        
        # Thực hiện nhiều bước di chuyển ngẫu nhiên
        num_moves = random.randint(50, 200)
        prev_move = -1
        
        for _ in range(num_moves):
            possible_moves = []
            for i in range(4):
                new_row = empty_pos[0] + rows[i]
                new_col = empty_pos[1] + cols[i]
                if self.is_safe_puzzle(new_row, new_col):
                    # Tránh di chuyển ngược lại bước trước
                    if i != (prev_move + 2) % 4:
                        possible_moves.append(i)
            
            if possible_moves:
                move = random.choice(possible_moves)
                new_row = empty_pos[0] + rows[move]
                new_col = empty_pos[1] + cols[move]
                
                # Hoán đổi
                current[empty_pos[0]][empty_pos[1]], current[new_row][new_col] = \
                    current[new_row][new_col], current[empty_pos[0]][empty_pos[1]]
                empty_pos = [new_row, new_col]
                prev_move = move
        
        self.puzzle_initial = current
        self.puzzle_solution = None
        self.puzzle_steps = None
        self.current_puzzle_step = 0
        self.draw_puzzle(self.puzzle_initial)
        self.update_puzzle_navigation(0)
        messagebox.showinfo("Thành công", f"Đã tạo {total-1}-puzzle ({n}x{n}) ngẫu nhiên!")
    
    def on_puzzle_canvas_resize(self, event):
        """Vẽ lại puzzle khi canvas resize"""
        if self.puzzle_initial:
            if self.puzzle_solution and self.current_puzzle_step < len(self.puzzle_solution):
                self.draw_puzzle(self.puzzle_solution[self.current_puzzle_step])
            else:
                self.draw_puzzle(self.puzzle_initial)
    
    def solve_puzzle(self):
        """Giải N-Puzzle"""
        if not self.puzzle_initial or not self.puzzle_final:
            messagebox.showwarning("Cảnh báo", "Vui lòng tạo puzzle trước!")
            return
        
        # Tìm vị trí ô trống
        empty_pos = None
        for i in range(self.puzzle_size):
            for j in range(self.puzzle_size):
                if self.puzzle_initial[i][j] == 0:
                    empty_pos = [i, j]
                    break
            if empty_pos:
                break
        
        if not empty_pos:
            messagebox.showerror("Lỗi", "Không tìm thấy ô trống trong puzzle!")
            return
        
        try:
            solution_path, num_steps, num_visited = self.solve_puzzle_algorithm(
                self.puzzle_initial, empty_pos, self.puzzle_final
            )
            
            if solution_path:
                self.puzzle_solution = solution_path
                self.puzzle_steps = num_steps
                self.display_puzzle_result(solution_path, num_steps, num_visited)
                messagebox.showinfo("Thành công", 
                                  f"Đã tìm thấy lời giải!\nSố bước: {num_steps}\nSố trạng thái đã duyệt: {num_visited}")
            else:
                messagebox.showerror("Lỗi", "Không tìm thấy lời giải!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def draw_puzzle(self, state):
        """Vẽ puzzle trên canvas với kích thước tự động điều chỉnh"""
        self.puzzle_canvas.delete("all")
        n = len(state)
        
        # Tính toán kích thước cell dựa trên n
        canvas_width = self.puzzle_canvas.winfo_width() if self.puzzle_canvas.winfo_width() > 1 else 600
        canvas_height = self.puzzle_canvas.winfo_height() if self.puzzle_canvas.winfo_height() > 1 else 600
        
        # Để lại margin
        margin = 50
        available_width = canvas_width - 2 * margin
        available_height = canvas_height - 2 * margin
        
        # Tính cell_size để vừa với canvas
        cell_size = min(available_width // n, available_height // n, 100)
        if n > 4:
            cell_size = min(cell_size, 70)  # Giới hạn cho puzzle lớn
        
        # Tính toán font size dựa trên cell_size
        font_size = max(12, min(20, cell_size // 4))
        
        # Tính toán vị trí bắt đầu để căn giữa
        total_width = n * cell_size
        total_height = n * cell_size
        start_x = margin + (available_width - total_width) // 2
        start_y = margin + (available_height - total_height) // 2
        
        for i in range(n):
            for j in range(n):
                x1 = start_x + j * cell_size
                y1 = start_y + i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                value = state[i][j]
                if value == 0:
                    # Ô trống
                    self.puzzle_canvas.create_rectangle(x1, y1, x2, y2, 
                                                       fill='#e0e0e0', outline='#999', width=2)
                else:
                    # Ô có số
                    self.puzzle_canvas.create_rectangle(x1, y1, x2, y2, 
                                                       fill="#da9ed9", outline='#333', width=2)
                    self.puzzle_canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, 
                                                   text=str(value), 
                                                   font=('Arial', font_size, 'bold'), fill='white')
    
    def display_puzzle_result(self, solution_path, num_steps, num_visited):
        """Hiển thị kết quả giải N-Puzzle"""
        if not solution_path:
            return
        
        n = len(solution_path[0])
        puzzle_name = f"{n*n - 1}-puzzle ({n}x{n})"
        
        # Hiển thị từng bước
        self.result_text.delete('1.0', tk.END)
        text = "=" * 80 + "\n"
        text += f"KẾT QUẢ GIẢI {puzzle_name.upper()} BẰNG A* (AKT)\n"
        text += "=" * 80 + "\n\n"
        text += f"Số bước: {num_steps}\n"
        text += f"Số trạng thái đã duyệt: {num_visited}\n\n"
        text += "Các bước giải:\n"
        text += "-" * 80 + "\n\n"
        
        # Chỉ hiển thị một số bước đầu và cuối nếu quá nhiều
        max_display = 10
        if len(solution_path) <= max_display:
            # Hiển thị tất cả
            for step, state in enumerate(solution_path):
                text += f"Bước {step}:\n"
                for row in state:
                    text += " ".join(f"{val:3d}" if val != 0 else "   " for val in row) + "\n"
                text += "\n"
        else:
            # Hiển thị 5 bước đầu
            for step in range(5):
                text += f"Bước {step}:\n"
                for row in solution_path[step]:
                    text += " ".join(f"{val:3d}" if val != 0 else "   " for val in row) + "\n"
                text += "\n"
            text += "...\n...\n...\n\n"
            # Hiển thị 5 bước cuối
            for step in range(len(solution_path) - 5, len(solution_path)):
                text += f"Bước {step}:\n"
                for row in solution_path[step]:
                    text += " ".join(f"{val:3d}" if val != 0 else "   " for val in row) + "\n"
                text += "\n"
            text += f"\n(Lưu ý: Đã ẩn {len(solution_path) - 10} bước ở giữa. Sử dụng nút điều hướng để xem tất cả)\n"
        
        self.result_text.insert('1.0', text)
        
        # Vẽ bước đầu tiên và cập nhật điều hướng
        if solution_path:
            self.current_puzzle_step = 0
            self.draw_puzzle(solution_path[0])
            self.update_puzzle_navigation(len(solution_path))
    
    def display_step_by_step(self, step_details, path):
        """Hiển thị từng bước chi tiết với chi phí"""
        if not step_details or not path:
            self.step_text.delete('1.0', tk.END)
            self.step_text.insert('1.0', "Chưa có dữ liệu từng bước.")
            return
        
        text = "=" * 80 + "\n"
        text += "CHI TIẾT TỪNG BƯỚC CỦA THUẬT TOÁN A*\n"
        text += "=" * 80 + "\n\n"
        
        total_cost = 0
        
        for i, step in enumerate(step_details):
            step_num = step['vertex']
            g = step['g']
            h = step['h']
            f = step['f']
            step_cost = step['step_cost']
            
            text += f"BƯỚC {i + 1}: Đến đỉnh {step_num}\n"
            text += "-" * 80 + "\n"
            
            if i == 0:
                text += f"  • Đây là đỉnh bắt đầu\n"
            else:
                prev_vertex = path[i - 1] if i > 0 else None
                text += f"  • Di chuyển từ đỉnh {prev_vertex} đến đỉnh {step_num}\n"
                text += f"  • Chi phí bước này: {step_cost}\n"
                total_cost += step_cost
            
            text += f"  • g (chi phí từ đầu): {g}\n"
            text += f"  • h (heuristic - khoảng cách ước tính đến đích): {h}\n"
            text += f"  • f = g + h = {f}\n"
            
            if i < len(step_details) - 1:
                text += "\n"
        
        text += "\n" + "=" * 80 + "\n"
        text += f"TỔNG CHI PHÍ: {total_cost if total_cost > 0 else step_details[-1]['g']}\n"
        text += "=" * 80 + "\n"
        
        self.step_text.delete('1.0', tk.END)
        self.step_text.insert('1.0', text)
    
    def update_puzzle_navigation(self, total_steps):
        """Cập nhật trạng thái nút điều hướng puzzle"""
        if not self.puzzle_solution:
            self.prev_btn.config(state='disabled')
            self.next_btn.config(state='disabled')
            self.step_label.config(text="Bước: 0/0")
            return
        
        total = len(self.puzzle_solution)
        self.step_label.config(text=f"Bước: {self.current_puzzle_step + 1}/{total}")
        
        if self.current_puzzle_step <= 0:
            self.prev_btn.config(state='disabled')
        else:
            self.prev_btn.config(state='normal')
        
        if self.current_puzzle_step >= total - 1:
            self.next_btn.config(state='disabled')
        else:
            self.next_btn.config(state='normal')
    
    def prev_puzzle_step(self):
        """Xem bước trước của puzzle"""
        if self.puzzle_solution and self.current_puzzle_step > 0:
            self.current_puzzle_step -= 1
            self.draw_puzzle(self.puzzle_solution[self.current_puzzle_step])
            self.update_puzzle_navigation(len(self.puzzle_solution))
    
    def next_puzzle_step(self):
        """Xem bước sau của puzzle"""
        if self.puzzle_solution and self.current_puzzle_step < len(self.puzzle_solution) - 1:
            self.current_puzzle_step += 1
            self.draw_puzzle(self.puzzle_solution[self.current_puzzle_step])
            self.update_puzzle_navigation(len(self.puzzle_solution))


def main():
    root = tk.Tk()
    app = AStarDemoGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

