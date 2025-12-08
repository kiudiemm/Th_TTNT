"""Tô màu đồ thị tối ưu bằng quay lui có cắt tỉa.

Usage:
    # đọc từ file ma trận kề
    python graph_coloring.py --input path/to/matrix.txt

    # dùng đồ thị mẫu 6 đỉnh A-F như đề bài
    python graph_coloring.py --sample
"""

from __future__ import annotations

import argparse
from typing import Dict, List, Sequence, Tuple

from graph_io import read_adjacency_matrix

# Ma trận kề của đồ thị mẫu 6 đỉnh (A,B,C,D,E,F) 
SAMPLE_MATRIX_6: List[List[int]] = [
    [0, 1, 1, 0, 1, 0],
    [1, 0, 1, 1, 0, 1],
    [1, 1, 0, 1, 1, 0],
    [0, 1, 1, 0, 0, 1],
    [1, 0, 1, 0, 0, 1],
    [0, 1, 0, 1, 1, 0],
]
SAMPLE_LABELS_6: List[str] = ["A", "B", "C", "D", "E", "F"]


def build_adjacency_list(matrix: List[List[int]]) -> List[List[int]]:
    size = len(matrix)
    adjacency: List[List[int]] = [[] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            if matrix[i][j] and i != j:
                adjacency[i].append(j)
    return adjacency


def backtracking_coloring(adjacency: List[List[int]]) -> Tuple[int, Dict[int, int]]:
    """Trả về số sắc tối ưu và phương án tô màu."""
    n = len(adjacency)
    order = sorted(range(n), key=lambda v: len(adjacency[v]), reverse=True)
    best_coloring: Dict[int, int] = {}
    best_colors = n + 1  # upper bound
    current: Dict[int, int] = {}

    def is_valid(vertex: int, color: int) -> bool:
        return all(current.get(nei) != color for nei in adjacency[vertex])

    def used_colors() -> int:
        return len(set(current.values()))

    def search(idx: int) -> None:
        nonlocal best_colors, best_coloring
        if idx == n:
            colors_used = used_colors()
            if colors_used < best_colors:
                best_colors = colors_used
                best_coloring = current.copy()
            return

        vertex = order[idx]
        colors_in_use = list(set(current.values()))
        for color in colors_in_use:
            if is_valid(vertex, color):
                current[vertex] = color
                if used_colors() < best_colors:
                    search(idx + 1)
                del current[vertex]

        next_color = len(colors_in_use)
        if next_color + 1 < best_colors:  # +1 because colors are zero-indexed
            current[vertex] = next_color
            search(idx + 1)
            del current[vertex]

    search(0)
    return best_colors, best_coloring


def format_coloring(coloring: Dict[int, int], labels: Sequence[str] | None = None) -> str:
    def name(idx: int) -> str:
        if labels and 0 <= idx < len(labels):
            return labels[idx]
        return f"v{idx}"

    return " ".join(f"{name(v)}:{c}" for v, c in sorted(coloring.items()))


def main() -> None:
    parser = argparse.ArgumentParser(description="Tô màu tối ưu trên đồ thị.")
    parser.add_argument("--input", help="Đường dẫn file ma trận kề.")
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Dùng đồ thị mẫu 6 đỉnh A-F.",
    )
    args = parser.parse_args()

    if args.sample:
        matrix = SAMPLE_MATRIX_6
        labels = SAMPLE_LABELS_6
    elif args.input:
        matrix = read_adjacency_matrix(args.input)
        labels = None
    else:
        raise SystemExit("Cần --sample hoặc --input path/to/matrix.txt")

    adjacency = build_adjacency_list(matrix)
    chromatic_number, coloring = backtracking_coloring(adjacency)

    print(f"Số màu tối thiểu: {chromatic_number}")
    print("Phân bố màu:", format_coloring(coloring, labels))


if __name__ == "__main__":
    main()

