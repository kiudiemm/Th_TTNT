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


def _get_horizontal_winner(board):
    n = len(board)
    for i in range(n):
        candidate = board[i][0]
        if candidate is None:
            continue
        if all(board[i][j] == candidate for j in range(n)):
            return candidate
    return None


def _get_vertical_winner(board):
    n = len(board)
    for j in range(n):
        candidate = board[0][j]
        if candidate is None:
            continue
        if all(board[i][j] == candidate for i in range(n)):
            return candidate
    return None


def _get_diagonal_winner(board):
    n = len(board)
    candidate = board[0][0]
    if candidate is not None and all(board[i][i] == candidate for i in range(n)):
        return candidate
    candidate = board[0][n - 1]
    if candidate is not None and all(board[i][n - 1 - i] == candidate for i in range(n)):
        return candidate
    return None


def winner(board):
    """Trả về người thắng nếu có, ngược lại None."""
    return (
        _get_horizontal_winner(board)
        or _get_vertical_winner(board)
        or _get_diagonal_winner(board)
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


def max_value(state):
    if terminal(state):
        return utility(state)
    v = -math.inf
    for act in actions(state):
        v = max(v, min_value(result(state, act)))
    return v


def min_value(state):
    if terminal(state):
        return utility(state)
    v = math.inf
    for act in actions(state):
        v = min(v, max_value(result(state, act)))
    return v


def minimax(board):
    """Trả về nước đi tối ưu cho người chơi hiện tại."""
    current = player(board)
    best_move = None

    if current == X:
        best_score = -math.inf
        for act in actions(board):
            score = min_value(result(board, act))
            if score > best_score:
                best_score = score
                best_move = act
    else:
        best_score = math.inf
        for act in actions(board):
            score = max_value(result(board, act))
            if score < best_score:
                best_score = score
                best_move = act
    return best_move


def _prompt_int(msg: str) -> int:
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("Vui lòng nhập số nguyên.")


def main():
    global user, ai
    n = _prompt_int("Nhập kích thước bàn cờ n (mặc định 3): ") or 3
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

