from __future__ import annotations

import copy
import math
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List, Optional, Set, Tuple

# Thuật toán tách riêng
import minimax as mm  # Sườn minimax (2D)
import alphabeta as ab  # Sườn alpha-beta (1D)

# Ký hiệu người chơi
X = "X"
O = "O"
EMPTY = None

# Biến toàn cục
user: Optional[str] = None
ai: Optional[str] = None


def initial_state(n: int = 3) -> List[List[Optional[str]]]:
    """Khởi tạo bàn cờ n×n rỗng."""
    return [[EMPTY for _ in range(n)] for _ in range(n)]


def player(board: List[List[Optional[str]]]) -> str:
    """Xác định người chơi kế tiếp dựa trên số ô đã đánh."""
    count = sum(1 for row in board for cell in row if cell)
    return ai if count % 2 else user


def actions(board: List[List[Optional[str]]]) -> Set[Tuple[int, int]]:
    """Trả về tập các nước đi hợp lệ (i, j)."""
    res: Set[Tuple[int, int]] = set()
    n = len(board)
    for i in range(n):
        for j in range(n):
            if board[i][j] is EMPTY:
                res.add((i, j))
    return res


def result(board: List[List[Optional[str]]], action: Tuple[int, int]) -> List[List[Optional[str]]]:
    """Trả về trạng thái mới sau khi đánh nước action."""
    curr_player = player(board)
    new_board = copy.deepcopy(board)
    i, j = action
    new_board[i][j] = curr_player
    return new_board


# ---------------- Chuyển đổi giữa dạng 2D (GUI) và 1D (alphabeta.py) ----------------
def board_2d_to_ab_list(board: List[List[Optional[str]]]) -> List:
    """
    Chuyển bàn cờ 2D sang list 1D theo kiểu alphabeta.py:
    - Ô trống được giữ số thứ tự (1-based) để alphabeta nhận biết còn trống
    - Ô đã đánh là 'X' hoặc 'O'
    """
    n = len(board)
    flat = []
    idx = 1
    for i in range(n):
        for j in range(n):
            cell = board[i][j]
            if cell in (X, O):
                flat.append(cell)
            else:
                flat.append(idx)
            idx += 1
    return flat


def ab_move_to_2d(move_idx: int, n: int) -> Tuple[int, int]:
    """Chuyển chỉ số 1D (1-based) từ alphabeta.py thành tọa độ (row, col)."""
    pos = move_idx - 1
    return pos // n, pos % n


def _get_horizontal_winner(board, win_condition: int):
    """Kiểm tra thắng theo hàng với win_condition ô liên tiếp."""
    n = len(board)
    for i in range(n):
        for j in range(n - win_condition + 1):
            candidate = board[i][j]
            if candidate is None:
                continue
            # Kiểm tra win_condition ô liên tiếp
            if all(board[i][j + k] == candidate for k in range(win_condition)):
                return candidate
    return None


def _get_vertical_winner(board, win_condition: int):
    """Kiểm tra thắng theo cột với win_condition ô liên tiếp."""
    n = len(board)
    for j in range(n):
        for i in range(n - win_condition + 1):
            candidate = board[i][j]
            if candidate is None:
                continue
            # Kiểm tra win_condition ô liên tiếp
            if all(board[i + k][j] == candidate for k in range(win_condition)):
                return candidate
    return None


def _get_diagonal_winner(board, win_condition: int):
    """Kiểm tra thắng theo đường chéo với win_condition ô liên tiếp."""
    n = len(board)
    
    # Đường chéo chính (từ trái trên xuống phải dưới)
    for i in range(n - win_condition + 1):
        for j in range(n - win_condition + 1):
            candidate = board[i][j]
            if candidate is None:
                continue
            # Kiểm tra win_condition ô liên tiếp trên đường chéo chính
            if all(board[i + k][j + k] == candidate for k in range(win_condition)):
                return candidate
    
    # Đường chéo phụ (từ phải trên xuống trái dưới)
    for i in range(n - win_condition + 1):
        for j in range(win_condition - 1, n):
            candidate = board[i][j]
            if candidate is None:
                continue
            # Kiểm tra win_condition ô liên tiếp trên đường chéo phụ
            if all(board[i + k][j - k] == candidate for k in range(win_condition)):
                return candidate
    
    return None


def winner(board, win_condition: int = None):
    """Trả về người thắng nếu có, ngược lại None.
        win_condition: Số ô liên tiếp cần để thắng (mặc định = n)
    """
    n = len(board)
    if win_condition is None:
        win_condition = n  # Mặc định: toàn bộ hàng/cột/chéo
    
    if win_condition > n:
        win_condition = n  # Không thể lớn hơn kích thước bàn
    
    return (
        _get_horizontal_winner(board, win_condition)
        or _get_vertical_winner(board, win_condition)
        or _get_diagonal_winner(board, win_condition)
        or None
    )


def terminal(board, win_condition: int = None) -> bool:
    """Trả về True nếu game kết thúc (thắng hoặc hòa)."""
    if winner(board, win_condition) is not None:
        return True
    return all(cell is not EMPTY for row in board for cell in row)


def utility(board, win_condition: int = None) -> int:
    """Giá trị tiện ích: 1 nếu X thắng, -1 nếu O thắng, 0 nếu chưa rõ/hòa."""
    w = winner(board, win_condition)
    if w == X:
        return 1
    if w == O:
        return -1
    return 0


def heuristic(board) -> float:
    """Heuristic đánh giá trạng thái trung gian (cho n > 3)."""
    w = winner(board)
    if w == X:
        return 1000
    if w == O:
        return -1000
    
    n = len(board)
    score = 0
    
    # Đánh giá các hàng
    for i in range(n):
        x_count = sum(1 for j in range(n) if board[i][j] == X)
        o_count = sum(1 for j in range(n) if board[i][j] == O)
        if x_count > 0 and o_count == 0:
            score += x_count * 10
        elif o_count > 0 and x_count == 0:
            score -= o_count * 10
    
    # Đánh giá các cột
    for j in range(n):
        x_count = sum(1 for i in range(n) if board[i][j] == X)
        o_count = sum(1 for i in range(n) if board[i][j] == O)
        if x_count > 0 and o_count == 0:
            score += x_count * 10
        elif o_count > 0 and x_count == 0:
            score -= o_count * 10
    
    # Đánh giá đường chéo chính
    x_count = sum(1 for i in range(n) if board[i][i] == X)
    o_count = sum(1 for i in range(n) if board[i][i] == O)
    if x_count > 0 and o_count == 0:
        score += x_count * 10
    elif o_count > 0 and x_count == 0:
        score -= o_count * 10
    
    # Đánh giá đường chéo phụ
    x_count = sum(1 for i in range(n) if board[i][n-1-i] == X)
    o_count = sum(1 for i in range(n) if board[i][n-1-i] == O)
    if x_count > 0 and o_count == 0:
        score += x_count * 10
    elif o_count > 0 and x_count == 0:
        score -= o_count * 10
    
    return score / 100.0  # Chuẩn hóa về khoảng [-1, 1]


# ========== THUẬT TOÁN MINIMAX==========

def max_value(state, depth: int = 0, max_depth: int = float('inf'), win_condition: int = None):
    """Hàm MAX cho Minimax (theo sườn minimax.py)."""
    if terminal(state, win_condition):
        return utility(state, win_condition)
    
    # Nếu có giới hạn độ sâu và đạt đến giới hạn, dùng heuristic
    if depth >= max_depth:
        return heuristic(state)
    
    v = -math.inf
    for act in actions(state):
        v = max(v, min_value(result(state, act), depth + 1, max_depth, win_condition))
    return v


def min_value(state, depth: int = 0, max_depth: int = float('inf'), win_condition: int = None):
    """Hàm MIN cho Minimax (theo sườn minimax.py)."""
    if terminal(state, win_condition):
        return utility(state, win_condition)
    
    # Nếu có giới hạn độ sâu và đạt đến giới hạn, dùng heuristic
    if depth >= max_depth:
        return heuristic(state)
    
    v = math.inf
    for act in actions(state):
        v = min(v, max_value(result(state, act), depth + 1, max_depth, win_condition))
    return v


def minimax(board, max_depth: int = float('inf'), win_condition: int = None):
    """Trả về nước đi tối ưu cho người chơi hiện tại (theo sườn minimax.py)."""
    current = player(board)
    best_move = None

    if current == X:
        best_score = -math.inf
        for act in actions(board):
            score = min_value(result(board, act), 1, max_depth, win_condition)
            if score > best_score:
                best_score = score
                best_move = act
    else:
        best_score = math.inf
        for act in actions(board):
            score = max_value(result(board, act), 1, max_depth, win_condition)
            if score < best_score:
                best_score = score
                best_move = act
    return best_move


# ========== THUẬT TOÁN ALPHA-BETA==========

def minimax_alpha_beta_internal(board, n: int, depth: int, alpha: float, beta: float, 
                                 maximizing: bool, max_depth: int, win_condition: int) -> float:
    """Alpha-Beta với cắt tỉa (theo sườn alphabeta.py, nhưng dùng ma trận 2D)."""
    w = winner(board, win_condition)
    if w is not None:
        # Ưu tiên thắng nhanh/thua chậm (giống alphabeta.py)
        return (10 - depth) if w == X else (-10 + depth)
    
    if terminal(board, win_condition):
        return 0
    
    # Nếu đạt đến độ sâu tối đa, dùng heuristic
    if depth >= max_depth:
        return heuristic(board)
    
    if maximizing:
        max_eval = -math.inf
        for act in actions(board):
            new_board = result(board, act)
            eval_val = minimax_alpha_beta_internal(new_board, n, depth + 1, alpha, beta, 
                                                    False, max_depth, win_condition)
            max_eval = max(max_eval, eval_val)
            alpha = max(alpha, eval_val)
            if beta <= alpha:
                break  # prune
        return max_eval
    else:
        min_eval = math.inf
        for act in actions(board):
            new_board = result(board, act)
            eval_val = minimax_alpha_beta_internal(new_board, n, depth + 1, alpha, beta, 
                                                    True, max_depth, win_condition)
            min_eval = min(min_eval, eval_val)
            beta = min(beta, eval_val)
            if beta <= alpha:
                break  # prune
        return min_eval


def minimax_alpha_beta(board, max_depth: int = float('inf'), win_condition: int = None):
    """Trả về nước đi tối ưu cho người chơi hiện tại (theo sườn alphabeta.py)."""
    current = player(board)
    n = len(board)
    best_move = None
    best_val = -math.inf if current == X else math.inf
    
    for act in actions(board):
        new_board = result(board, act)
        move_val = minimax_alpha_beta_internal(
            new_board,
            n,
            0,
            -math.inf,
            math.inf,
            maximizing=False if current == X else True,
            max_depth=max_depth,
            win_condition=win_condition
        )
        
        if current == X and move_val > best_val:
            best_val = move_val
            best_move = act
        elif current == O and move_val < best_val:
            best_val = move_val
            best_move = act
    
    return best_move


# ========== GUI ==========

class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe - Minimax & Alpha-Beta")
        self.root.geometry("1200x700")
        
        # Biến
        self.board = None
        self.n = 3
        self.win_condition = 3
        self.use_alpha_beta = True
        self.game_started = False
        
        self.create_widgets()
    
    def create_widgets(self):
        # Frame chính chia làm 2 phần: trái và phải
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # ========== PHẦN TRÁI: Cấu hình và nhập ma trận ==========
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Frame cấu hình
        config_frame = ttk.LabelFrame(left_frame, text="Cấu Hình", padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Chọn thuật toán
        ttk.Label(config_frame, text="Thuật toán:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.algo_var = tk.StringVar(value="Alpha-Beta")
        ttk.Radiobutton(config_frame, text="Minimax", variable=self.algo_var, value="Minimax").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(config_frame, text="Alpha-Beta", variable=self.algo_var, value="Alpha-Beta").grid(row=0, column=2, padx=5)
        
        # Chọn quân
        ttk.Label(config_frame, text="Chọn quân:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.player_var = tk.StringVar(value="X")
        ttk.Radiobutton(config_frame, text="X", variable=self.player_var, value="X").grid(row=1, column=1, padx=5)
        ttk.Radiobutton(config_frame, text="O", variable=self.player_var, value="O").grid(row=1, column=2, padx=5)
        
        # Kích thước bàn cờ
        ttk.Label(config_frame, text="Kích thước n:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.size_var = tk.StringVar(value="3")
        size_spin = ttk.Spinbox(config_frame, from_=3, to=10, textvariable=self.size_var, width=5)
        size_spin.grid(row=2, column=1, padx=5, sticky=tk.W)
        
        # Số ô cần để thắng
        ttk.Label(config_frame, text="Số ô để thắng:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.win_condition_var = tk.StringVar(value="3")
        win_spin = ttk.Spinbox(config_frame, from_=3, to=10, textvariable=self.win_condition_var, width=5)
        win_spin.grid(row=3, column=1, padx=5, sticky=tk.W)
        ttk.Label(config_frame, text="(Ví dụ: bàn 6x6, thắng khi có 3 ô liên tiếp)").grid(row=3, column=2, padx=5, sticky=tk.W)
        
        # Số bước (độ sâu)
        ttk.Label(config_frame, text="Số bước:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.depth_var = tk.StringVar(value="3")
        depth_spin = ttk.Spinbox(config_frame, from_=1, to=10, textvariable=self.depth_var, width=5)
        depth_spin.grid(row=4, column=1, padx=5, sticky=tk.W)
        ttk.Label(config_frame, text="(Số bước AI tính toán trước)").grid(row=4, column=2, padx=5, sticky=tk.W)
        
        # Nút bắt đầu
        ttk.Button(config_frame, text="Bắt Đầu Game", command=self.start_game).grid(row=5, column=1, padx=10, pady=5)
        
        # Frame nhập ma trận
        matrix_frame = ttk.LabelFrame(left_frame, text="Nhập Ma Trận Ban Đầu (Tùy chọn)", padding=10)
        matrix_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Text area để nhập ma trận
        ttk.Label(matrix_frame, text="Nhập ma trận (mỗi hàng một dòng, cách nhau bởi dấu cách):\nVí dụ: X O None hoặc X O _").pack(anchor=tk.W)
        self.matrix_text = scrolledtext.ScrolledText(matrix_frame, height=10, width=40)
        self.matrix_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Button(matrix_frame, text="Áp Dụng Ma Trận", command=self.apply_matrix).pack(pady=5)
        
        # ========== PHẦN PHẢI: Bàn cờ ==========
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Frame bàn cờ
        self.board_frame = ttk.LabelFrame(right_frame, text="Bàn Cờ", padding=10)
        self.board_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame thông tin (ở dưới cùng)
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = ttk.Label(info_frame, text="Chưa bắt đầu game", font=("Arial", 10, "bold"))
        self.status_label.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(info_frame, mode='indeterminate', length=100)
        self.progress.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(info_frame, text="Reset", command=self.reset_game).pack(side=tk.RIGHT, padx=5)
        ttk.Button(info_frame, text="AI Đi", command=self.ai_move).pack(side=tk.RIGHT, padx=5)
    
    def start_game(self):
        """Bắt đầu game mới."""
        global user, ai
        
        try:
            self.n = int(self.size_var.get())
            if self.n < 3 or self.n > 10:
                messagebox.showerror("Lỗi", "Kích thước phải từ 3 đến 10!")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Kích thước không hợp lệ!")
            return
        
        try:
            self.win_condition = int(self.win_condition_var.get())
            if self.win_condition < 3 or self.win_condition > self.n:
                messagebox.showerror("Lỗi", f"Số ô để thắng phải từ 3 đến {self.n}!")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Số ô để thắng không hợp lệ!")
            return
        
        user = self.player_var.get()
        ai = O if user == X else X
        self.use_alpha_beta = (self.algo_var.get() == "Alpha-Beta")
        self.game_started = True

        # Đồng bộ user/ai cho module minimax.py
        mm.user = user
        mm.ai = ai
        
        # Lấy số bước từ giao diện
        try:
            self.max_depth = int(self.depth_var.get())
            if self.max_depth < 1 or self.max_depth > 10:
                messagebox.showerror("Lỗi", "Số bước phải từ 1 đến 10!")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Số bước không hợp lệ!")
            return
        
        # Khởi tạo bàn cờ
        self.board = initial_state(self.n)
        
        # Vẽ bàn cờ
        self.draw_board()
        
        algo_name = "Alpha-Beta" if self.use_alpha_beta else "Minimax"
        win_info = f" - Thắng khi có {self.win_condition} ô liên tiếp"
        steps_info = f" - Số bước: {self.max_depth}"
        self.status_label.config(text=f"Game đã bắt đầu - Thuật toán: {algo_name}{win_info}{steps_info} - Bạn chơi: {user}")
        
        # Nếu AI đi trước
        if user == O:
            self.root.after(500, self.ai_move)
    
    def apply_matrix(self):
        """Áp dụng ma trận từ text area."""
        if not self.game_started:
            messagebox.showwarning("Cảnh báo", "Vui lòng bắt đầu game trước!")
            return
        
        text = self.matrix_text.get("1.0", tk.END).strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if len(lines) != self.n:
            messagebox.showerror("Lỗi", f"Phải có đúng {self.n} hàng!")
            return
        
        try:
            new_board = initial_state(self.n)
            for i, line in enumerate(lines):
                values = line.split()
                if len(values) != self.n:
                    raise ValueError(f"Hàng {i} không đủ {self.n} giá trị")
                
                for j, val in enumerate(values):
                    val_upper = val.upper()
                    if val_upper == "X":
                        new_board[i][j] = X
                    elif val_upper == "O":
                        new_board[i][j] = O
                    elif val_upper in ["NONE", "_", "", "EMPTY"]:
                        new_board[i][j] = EMPTY
                    else:
                        raise ValueError(f"Giá trị '{val}' không hợp lệ")
            
            self.board = new_board
            self.draw_board()
            messagebox.showinfo("Thành công", "Đã áp dụng ma trận!")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
    
    def draw_board(self):
        """Vẽ bàn cờ."""
        # Xóa các widget cũ
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        
        if self.board is None:
            return
        
        # Tạo grid buttons
        self.buttons = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                btn = tk.Button(
                    self.board_frame,
                    text=self.get_cell_text(i, j),
                    font=("Arial", 16, "bold"),
                    width=4,
                    height=2,
                    command=lambda r=i, c=j: self.on_cell_click(r, c)
                )
                btn.grid(row=i, column=j, padx=2, pady=2)
                row.append(btn)
            self.buttons.append(row)
    
    def get_cell_text(self, i, j):
        """Lấy text hiển thị cho ô."""
        if self.board is None:
            return ""
        cell = self.board[i][j]
        if cell == X:
            return "X"
        elif cell == O:
            return "O"
        else:
            return ""
    
    def on_cell_click(self, row, col):
        """Xử lý khi click vào ô."""
        if not self.game_started:
            messagebox.showwarning("Cảnh báo", "Vui lòng bắt đầu game trước!")
            return
        
        if terminal(self.board, self.win_condition):
            return
        
        if player(self.board) != user:
            messagebox.showinfo("Thông báo", "Chưa đến lượt bạn!")
            return
        
        if self.board[row][col] is not EMPTY:
            messagebox.showwarning("Cảnh báo", "Ô này đã được đánh!")
            return
        
        # Người chơi đánh
        self.board = result(self.board, (row, col))
        self.draw_board()
        
        # Kiểm tra kết thúc
        if terminal(self.board, self.win_condition):
            self.check_game_over()
            return
        
        # AI đánh
        self.root.after(500, self.ai_move)
    
    def ai_move(self):
        """AI thực hiện nước đi (chạy trong thread riêng để không block UI)."""
        if not self.game_started or self.board is None:
            return
        
        if terminal(self.board, self.win_condition):
            self.check_game_over()
            return
        
        if player(self.board) != ai:
            return
        
        # Hiển thị progress
        algo_name = "Alpha-Beta" if self.use_alpha_beta else "Minimax"
        self.status_label.config(text=f"AI ({algo_name}) đang tính toán...")
        self.progress.start()
        self.root.update()
        
        # Chạy trong thread riêng
        def calculate_move():
            try:
                if self.use_alpha_beta:
                    move = self.get_move_alphabeta()
                else:
                    move = self.get_move_minimax()
                
                # Cập nhật UI trong main thread
                self.root.after(0, lambda: self.apply_ai_move(move))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi tính toán: {e}"))
        
        thread = threading.Thread(target=calculate_move, daemon=True)
        thread.start()
    
    def apply_ai_move(self, move):
        """Áp dụng nước đi của AI (gọi từ main thread)."""
        self.progress.stop()
        
        if move is None:
            self.check_game_over()
            return
        
        self.board = result(self.board, move)
        self.draw_board()
        
        algo_name = "Alpha-Beta" if self.use_alpha_beta else "Minimax"
        self.status_label.config(text=f"AI ({algo_name}) đã đánh tại {move} - Lượt của bạn")
        
        # Kiểm tra kết thúc
        if terminal(self.board, self.win_condition):
            self.root.after(500, self.check_game_over)

    # --------- Thuật toán gọi ra từ file minimax.py / alphabeta.py ---------
    def get_move_minimax(self) -> Optional[Tuple[int, int]]:
        """
        Gọi minimax từ file minimax.py (sử dụng bàn 2D).
        - minimax.py dùng biến toàn cục mm.user/mm.ai, đã được set ở start_game.
        """
        return mm.minimax(self.board)

    def get_move_alphabeta(self) -> Optional[Tuple[int, int]]:
        """
        Gọi alpha-beta từ file alphabeta.py (sử dụng bàn 1D).
        - Chuyển đổi bàn 2D -> list 1D với ô trống là số (1-based) như alphabeta.py yêu cầu.
        - Trả về tọa độ (row, col) để áp dụng cho bàn 2D GUI.
        """
        ab_board = board_2d_to_ab_list(self.board)
        move_idx = ab.find_best_move(ab_board, self.n, ai)
        if move_idx == -1:
            return None
        return ab_move_to_2d(move_idx, self.n)
    
    def check_game_over(self):
        """Kiểm tra và hiển thị kết quả game."""
        w = winner(self.board, self.win_condition)
        if w is not None:
            messagebox.showinfo("Kết thúc", f"{w} thắng!")
            self.status_label.config(text=f"Game kết thúc - {w} thắng!")
        elif terminal(self.board, self.win_condition):
            messagebox.showinfo("Kết thúc", "Hòa!")
            self.status_label.config(text="Game kết thúc - Hòa!")
    
    def reset_game(self):
        """Reset game."""
        self.game_started = False
        self.board = None
        self.draw_board()
        self.status_label.config(text="Chưa bắt đầu game")


def main():
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

