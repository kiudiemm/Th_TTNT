"""Thuật toán Held-Karp (quy hoạch động) cho bài toán người bán hàng.

Usage:
    python tsp_held_karp.py --input path/to/matrix.txt --start 0
"""

from __future__ import annotations

import argparse
from functools import lru_cache
from typing import List, Sequence, Tuple

from graph_io import read_adjacency_matrix


def held_karp(matrix: Sequence[Sequence[float]], start: int = 0) -> Tuple[float, List[int]]:
    n = len(matrix)
    all_vertices = tuple(v for v in range(n) if v != start)

    @lru_cache(maxsize=None)
    def visit(current: int, remaining: Tuple[int, ...]) -> Tuple[float, Tuple[int, ...]]:
        if not remaining:
            return matrix[current][start], (start,)

        best_cost = float("inf")
        best_path: Tuple[int, ...] = ()
        for i, nxt in enumerate(remaining):
            cost_to_next = matrix[current][nxt]
            if cost_to_next == float("inf"):
                continue
            cost_rest, path_rest = visit(nxt, remaining[:i] + remaining[i + 1 :])
            total_cost = cost_to_next + cost_rest
            if total_cost < best_cost:
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

