from __future__ import annotations

import copy
import math
from typing import List, Optional, Set, Tuple

# Ký hiệu người chơi
X = "X"
O = "O"
EMPTY = None

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


def _get_horizontal_winner(board):#kiểm tra thắng theo hàng
    n = len(board)
    for i in range(n):
        candidate = board[i][0]
        if candidate is None:
            continue
        if all(board[i][j] == candidate for j in range(n)):#
            return candidate
    return None


def _get_vertical_winner(board):#kiểm tra thắng theo cột
    n = len(board)
    for j in range(n):
        candidate = board[0][j]
        if candidate is None:
            continue
        if all(board[i][j] == candidate for i in range(n)):
            return candidate
    return None


def _get_diagonal_winner(board):#kiểm tra thắng theo đường chéo
    n = len(board)
    candidate = board[0][0]
    if candidate is not None and all(board[i][i] == candidate for i in range(n)):#kiểm tra đường chéo chính
        return candidate
    candidate = board[0][n - 1]
    if candidate is not None and all(board[i][n - 1 - i] == candidate for i in range(n)):#kiểm tra đường chéo phụ
        return candidate
    return None


def winner(board):#kiểm tra thắng
    """Trả về người thắng nếu có, ngược lại None."""
    return (
        _get_horizontal_winner(board)#kiểm tra thắng theo hàng
        or _get_vertical_winner(board)#kiểm tra thắng theo cột
        or _get_diagonal_winner(board)#kiểm tra thắng theo đường chéo
        or None
    )


def terminal(board) -> bool:
    """Trả về True nếu game kết thúc (thắng hoặc hòa)."""
    if winner(board) is not None:
        return True
    return all(cell is not EMPTY for row in board for cell in row)


def utility(board) -> int:
    """Giá trị tiện ích: 1 nếu X thắng, -1 nếu O thắng, 0 nếu chưa rõ/hòa."""
    w = winner(board)
    if w == X:
        return 1
    if w == O:
        return -1
    return 0


def max_value(state):#giá trị tối đa
    if terminal(state):#kiểm tra trạng thái kết thúc
        return utility(state)
    v = -math.inf
    for act in actions(state):
        v = max(v, min_value(result(state, act)))#gọi hàm min_value để tìm giá trị tối thiểu
    return v


def min_value(state):#giá trị tối thiểu
    if terminal(state):
        return utility(state)
    v = math.inf
    for act in actions(state):
        v = min(v, max_value(result(state, act)))#gọi hàm max_value để tìm giá trị tối đa
    return v


def minimax(board):
    """Trả về nước đi tối ưu cho người chơi hiện tại."""
    current = player(board)
    best_move = None

    if current == X:
        best_score = -math.inf
        for act in actions(board):
            score = min_value(result(board, act))
            if score > best_score:#nếu giá trị tối thiểu lớn hơn giá trị tối đa thì cập nhật giá trị tối đa
                best_score = score
                best_move = act
    else:
        best_score = math.inf
        for act in actions(board):
            score = max_value(result(board, act))
            if score < best_score:#nếu giá trị tối đa nhỏ hơn giá trị tối thiểu thì cập nhật giá trị tối thiểu
                best_score = score
                best_move = act
    return best_move


def _prompt_int(msg: str) -> int:
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("Vui lòng nhập số nguyên.")


def input_board(n: int) -> List[List[Optional[str]]]:
    """Nhập ma trận n×n từ console."""
    print(f"\nNhập ma trận {n}×{n} (X, O, hoặc rỗng để bỏ qua):")
    print("Ví dụ: X O None hoặc X O _")
    board = initial_state(n)
    
    for i in range(n):
        while True:
            row_input = input(f"Hàng {i} (cách nhau bởi dấu cách): ").strip().split()
            if len(row_input) != n:
                print(f"Vui lòng nhập đúng {n} giá trị.")
                continue
            
            valid = True
            for j, val in enumerate(row_input):
                val_upper = val.upper()
                if val_upper == "X":
                    board[i][j] = X
                elif val_upper == "O":
                    board[i][j] = O
                elif val_upper in ["NONE", "_", "", "EMPTY"]:
                    board[i][j] = EMPTY
                else:
                    print(f"Giá trị '{val}' không hợp lệ. Chỉ chấp nhận X, O, None, _, hoặc rỗng.")
                    valid = False
                    break
            
            if valid:
                break
    
    print("\nMa trận đã nhập:")
    for row in board:
        print(row)
    
    return board


def main():
    global user, ai
    n = _prompt_int("Nhập kích thước bàn cờ n (mặc định 3): ") or 3
    if n < 3:
        print("Kích thước tối thiểu là 3. Sử dụng n=3.")
        n = 3
    
    choice = input("\nChọn:\n1. Nhập ma trận ban đầu\n2. Bắt đầu từ bàn cờ trống\nLựa chọn (1/2, mặc định 2): ").strip()
    
    if choice == "1":
        board = input_board(n)
    else:
        board = initial_state(n)

    print("Chọn quân của bạn (X/O), X đi trước:")
    user = input().strip().upper() or X
    user = X if user not in {X, O} else user
    ai = O if user == X else X

    while True:
        print("\nTrạng thái bàn:")
        for row in board:
            print(row)

        if terminal(board):
            w = winner(board)
            if w is None:
                print("Game kết thúc: Hòa.")
            else:
                print(f"Game kết thúc: {w} thắng.")
            break

        turn = player(board)
        if turn == user:
            print("Lượt của bạn. Nhập vị trí (row, col) 0-index.")
            i = _prompt_int("Row: ")
            j = _prompt_int("Col: ")
            if 0 <= i < n and 0 <= j < n and board[i][j] is EMPTY:
                board = result(board, (i, j))
            else:
                print("Ô không hợp lệ, thử lại.")
        else:
            print("Lượt AI, đang tính...")
            move = minimax(board)
            if move is None:
                # Không có nước đi (hòa)
                break
            board = result(board, move)
            print(f"AI đánh: {move}")


if __name__ == "__main__":
    main()

