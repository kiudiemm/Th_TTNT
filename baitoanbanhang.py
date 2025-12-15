from __future__ import annotations

import argparse
from functools import lru_cache
from typing import List, Sequence, Tuple

from graph_io import read_adjacency_matrix

#thuật toán help_karp cho bài toán bán hàng
def held_karp(matrix: Sequence[Sequence[float]], start: int = 0) -> Tuple[float, List[int]]:
    n = len(matrix) #số thành phố
    all_vertices = tuple(v for v in range(n) if v != start) #tập những đỉnh chưa thăm

    @lru_cache(maxsize=None)
    def visit(current: int, remaining: Tuple[int, ...]) -> Tuple[float, Tuple[int, ...]]:#hàm đệ quy tìm kiếm tối ưu
        if not remaining:#nếu không còn đỉnh chưa thăm
            return matrix[current][start], (start,) #quay về điểm xuất phát

        best_cost = float("inf") #chi phí tối thiểu
        best_path: Tuple[int, ...] = () #chu trình tối ưu
        for i, nxt in enumerate(remaining):#duyệt tất cả các đỉnh kế tiếp
            cost_to_next = matrix[current][nxt] #chi phí đến đỉnh kế tiếp
            if cost_to_next == float("inf"): #nếu không có đường
                continue #bỏ qua
            cost_rest, path_rest = visit(nxt, remaining[:i] + remaining[i + 1 :]) #đệ quy tìm kiếm tối ưu
            total_cost = cost_to_next + cost_rest #tính tổng chi phí
            if total_cost < best_cost:#nếu chi phí tôi thiểu nhỏ hơn chi phí tối thiểu hiện tại
                best_cost = total_cost
                best_path = (nxt,) + path_rest 
        return best_cost, best_path

    total_cost, path = visit(start, all_vertices) 
    return total_cost, [start, *path]


def main() -> None:
    parser = argparse.ArgumentParser(description="Giải TSP bằng Held-Karp.")
    parser.add_argument("--input", required=True, help="Đường dẫn file ma trận kề/chi phí.")
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Chỉ số thành phố xuất phát (mặc định: 0).",
    )
    args = parser.parse_args()

    matrix = [[float(x) if int(x) != 0 else float("inf") for x in row] for row in read_adjacency_matrix(args.input)]
    n = len(matrix)
    if not (0 <= args.start < n):
        raise ValueError(f"Start city must be between 0 and {n-1}")

    cost, tour = held_karp(matrix, start=args.start)
    print(f"Chi phí tối thiểu: {cost}")
    print("Chu trình:", " -> ".join(map(str, tour)))


if __name__ == "__main__":
    main()

