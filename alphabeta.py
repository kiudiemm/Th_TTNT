from __future__ import annotations

import math
from typing import List, Optional

# Ký hiệu người chơi
X = "X"
O = "O"


def make_board(n: int) -> List:
    """Tạo danh sách 1 chiều gồm n*n ô, giá trị khởi tạo là 1..n*n."""
    return [i + 1 for i in range(n * n)]


def print_board(board: List, n: int) -> None:
    """In bàn cờ n×n."""
    for r in range(n):
        row = board[r * n : (r + 1) * n]
        print(" | ".join(str(x) for x in row))
    print()


def get_available_cells(board: List) -> List[int]:
    """Các ô chưa đánh (giá trị còn là số)."""
    return [cell for cell in board if isinstance(cell, int)]


def get_winner(board: List, n: int) -> Optional[str]:
    """Kiểm tra thắng theo hàng/cột/chéo."""
    # hàng
    for r in range(n):#duyệt từng hàng      
        line = board[r * n : (r + 1) * n]
        if all(x == line[0] for x in line) and isinstance(line[0], str):
            return line[0]
    # cột
    for c in range(n):#duyệt từng cột
        col = [board[r * n + c] for r in range(n)]
        if all(x == col[0] for x in col) and isinstance(col[0], str):
            return col[0]
    # chéo chính
    diag = [board[i * n + i] for i in range(n)]#duyệt từng đường chéo chính
    if all(x == diag[0] for x in diag) and isinstance(diag[0], str):
        return diag[0]
    # chéo phụ
    adiag = [board[i * n + (n - 1 - i)] for i in range(n)]#duyệt từng đường chéo phụ
    if all(x == adiag[0] for x in adiag) and isinstance(adiag[0], str):
        return adiag[0]
    return None


def minimax_alpha_beta(position: List, n: int, depth: int, alpha: float, beta: float, maximizing: bool) -> int:#alpha-beta với ưu tiên thắng nhanh/thua chậm bằng điều chỉnh depth
    """Alpha–Beta với ưu tiên thắng nhanh/thua chậm bằng điều chỉnh depth."""
    win = get_winner(position, n)
    if win is not None:
        #ưu tiên thắng nhanh/thua chậm bằng điều chỉnh depth
        return 10 - depth if win == X else -10 + depth
    if not get_available_cells(position):
        return 0

    if maximizing:
        max_eval = -math.inf
        for cell in get_available_cells(position):
            position[cell - 1] = X#đánh X   
            eval_val = minimax_alpha_beta(position, n, depth + 1, alpha, beta, False)#gọi hàm alpha-beta để tìm giá trị tối ưu
            position[cell - 1] = cell
            max_eval = max(max_eval, eval_val)
            alpha = max(alpha, eval_val)
            if beta <= alpha:
                break  # prune
        return max_eval
    else:
        min_eval = math.inf
        for cell in get_available_cells(position):
            position[cell - 1] = O#đánh O
            eval_val = minimax_alpha_beta(position, n, depth + 1, alpha, beta, True)
            position[cell - 1] = cell
            min_eval = min(min_eval, eval_val)
            beta = min(beta, eval_val)
            if beta <= alpha:
                break  # prune
        return min_eval


def find_best_move(position: List, n: int, ai: str) -> int:#tìm nước đi tốt nhất cho AI
    """Trả về chỉ số ô tốt nhất cho AI (X hoặc O)."""
    best_val = -math.inf if ai == X else math.inf
    best_move = -1

    for cell in get_available_cells(position):
        position[cell - 1] = ai
        move_val = minimax_alpha_beta(
            position,
            n,
            0,
            -math.inf,
            math.inf,
            maximizing=False if ai == X else True,
        )
        position[cell - 1] = cell

        if ai == X and move_val > best_val:
            best_val = move_val
            best_move = cell
        elif ai == O and move_val < best_val:
            best_val = move_val
            best_move = cell
    return best_move


def input_board(n: int) -> List:
    """Nhập ma trận n×n từ console và chuyển sang định dạng 1 chiều."""
    print(f"\nNhập ma trận {n}×{n} (X, O, hoặc số để giữ trống):")
    print("Ví dụ: X O 3 hoặc X O _")
    board = make_board(n)
    
    for i in range(n):
        while True:
            row_input = input(f"Hàng {i} (cách nhau bởi dấu cách): ").strip().split()
            if len(row_input) != n:
                print(f"Vui lòng nhập đúng {n} giá trị.")
                continue
            
            valid = True
            for j, val in enumerate(row_input):
                idx = i * n + j
                val_upper = val.upper()
                if val_upper == "X":
                    board[idx] = X
                elif val_upper == "O":
                    board[idx] = O
                elif val.isdigit() and int(val) == idx + 1:
                    board[idx] = idx + 1  # Giữ nguyên số
                elif val_upper in ["_", "", "NONE", "EMPTY"]:
                    board[idx] = idx + 1  # Giữ nguyên số (ô trống)
                else:
                    print(f"Giá trị '{val}' không hợp lệ. Chỉ chấp nhận X, O, số, hoặc _.")
                    valid = False
                    break
            
            if valid:
                break
    
    print("\nMa trận đã nhập:")
    print_board(board, n)
    
    return board


def main():
    n_str = input("Chọn kích thước bàn cờ n (mặc định 3): ").strip()
    n = int(n_str) if n_str.isdigit() and int(n_str) >= 3 else 3

    player = input("Chọn chơi X hay O? ").strip().upper()
    player = player if player in {X, O} else X
    ai = O if player == X else X

    choice = input("\nChọn:\n1. Nhập ma trận ban đầu\n2. Bắt đầu từ bàn cờ trống\nLựa chọn (1/2, mặc định 2): ").strip()
    
    if choice == "1":
        board = input_board(n)
    else:
        board = make_board(n)
    
    # Xác định lượt đi dựa trên số ô đã đánh
    moves_played = sum(1 for cell in board if isinstance(cell, str))
    turn = X if moves_played % 2 == 0 else O

    while True:
        if turn == ai:
            move = find_best_move(board, n, ai)
            board[move - 1] = ai
            turn = player
        else:
            print_board(board, n)
            while True:
                try:
                    human_input = int(input("Nhập ô (theo số hiển thị): ").strip())
                except ValueError:
                    print("Vui lòng nhập số hợp lệ.")
                    continue
                if human_input in get_available_cells(board):
                    board[human_input - 1] = player
                    turn = ai
                    break
                print("Ô không hợp lệ, thử lại.")

        moves_played += 1
        w = get_winner(board, n)
        if w is not None:
            print_board(board, n)
            print(f"{w} thắng!")
            break
        if moves_played == n * n:
            print_board(board, n)
            print("Hòa.")
            break


if __name__ == "__main__":
    main()

