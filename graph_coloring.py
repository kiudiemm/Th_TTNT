"""Tô màu đồ thị tối ưu bằng quay lui có cắt tỉa.

Usage:
    # đọc từ file ma trận kề
    python graph_coloring.py --input path/to/matrix.txt

    # dùng đồ thị mẫu 6 đỉnh A-F như đề bài
    python graph_coloring.py --sample

    # nhập ma trận kề, số màu trực tiếp từ console
    python graph_coloring.py --console
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


def prompt_positive_int(message: str) -> int:
    """Nhập số nguyên dương từ console."""
    while True:
        raw = input(message).strip()
        try:
            value = int(raw)
        except ValueError:
            print("Vui lòng nhập số nguyên.")
            continue
        if value <= 0:
            print("Giá trị phải lớn hơn 0.")
            continue
        return value


def prompt_matrix_from_console() -> List[List[int]]:
    """Nhập ma trận kề vuông (0/1) từ console."""
    size = prompt_positive_int("Nhập số đỉnh (n): ")
    matrix: List[List[int]] = []
    for idx in range(size):
        while True:
            row_str = input(
                f"Hàng {idx + 1} ({size} số 0/1, cách nhau bởi khoảng trắng): "
            ).strip()
            try:
                row = [int(x) for x in row_str.split()]
            except ValueError:
                print("Chỉ nhập số 0 hoặc 1.")
                continue
            if len(row) != size:
                print(f"Cần đúng {size} giá trị.")
                continue
            if any(v not in (0, 1) for v in row):
                print("Chỉ nhập 0 hoặc 1.")
                continue
            matrix.append(row)
            break
    return matrix


def prompt_max_colors() -> int | None:
    """Tùy chọn nhập số màu mong muốn."""
    raw = input(
        "Nhập số màu mong muốn (k) - bỏ trống để tìm tối ưu: "
    ).strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        print("Giá trị không hợp lệ, bỏ qua k.")
        return None
    if value <= 0:
        print("Số màu phải lớn hơn 0, bỏ qua k.")
        return None
    return value

"""Chuyển từ ma trận kề qua danh sách kề"""
def build_adjacency_list(matrix: List[List[int]]) -> List[List[int]]: 
    size = len(matrix)
    adjacency: List[List[int]] = [[] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            if matrix[i][j] and i != j:
                adjacency[i].append(j)
    return adjacency
"""TẠo danh sách kề từ ma trận 0/1 bỏ qua đường chéo chính"""

"""Thuật toán tô màu tối ưu hóa"""
"""Sắp xếp đỉnh theo bậc giảm dần để giảm nhánh"""

def backtracking_coloring(adjacency: List[List[int]]) -> Tuple[int, Dict[int, int]]:
    """Trả về số sắc tối ưu và phương án tô màu."""
    n = len(adjacency)
    order = sorted(range(n), key=lambda v: len(adjacency[v]), reverse=True)
    best_coloring: Dict[int, int] = {} #chặn trên bằng n+1
    best_colors = n + 1  
    current: Dict[int, int] = {}# tô màu tạm
#kiểm tra màu sắc có hợp lệ kh, có trùng màu với định bên cạnh kh
    def is_valid(vertex: int, color: int) -> bool:
        return all(current.get(nei) != color for nei in adjacency[vertex])
#đếm số màu đang dùng
    def used_colors() -> int:
        return len(set(current.values()))
#hàm đệ quy tìm kiếm tối ưu
    def search(idx: int) -> None:
        nonlocal best_colors, best_coloring
        if idx == n:#tô hết đỉnh
            colors_used = used_colors()
            if colors_used < best_colors:
                best_colors = colors_used
                best_coloring = current.copy()
            return

        vertex = order[idx]#đỉnh hiện tại
        colors_in_use = list(set(current.values()))#liệt kê nhưgx màu đã dùng
        for color in colors_in_use:#thử tất cả màu có thể dùng
            if is_valid(vertex, color):
                current[vertex] = color
                if used_colors() < best_colors:#cắt tỉa nếu số màu đang dùng không thể tốt hơn best color
                    search(idx + 1)
                del current[vertex]

        next_color = len(colors_in_use) #thử màu mới
        if next_color + 1 < best_colors:  #cắt tỉa nếu số màu cần thêm không thể tốt hơn best color
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
        "--console",
        action="store_true",
        help="Nhập ma trận kề, số màu qua console.",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Dùng đồ thị mẫu 6 đỉnh A-F.",
    )
    args = parser.parse_args()

    max_colors: int | None = None
    if args.sample:
        matrix = SAMPLE_MATRIX_6
        labels = SAMPLE_LABELS_6
    elif args.console:
        matrix = prompt_matrix_from_console()
        max_colors = prompt_max_colors()
        labels = None
    elif args.input:
        matrix = read_adjacency_matrix(args.input)
        labels = None
    else:
        raise SystemExit("Cần --console, --sample hoặc --input path/to/matrix.txt")

    adjacency = build_adjacency_list(matrix)
    chromatic_number, coloring = backtracking_coloring(adjacency)

    print(f"Số màu tối thiểu: {chromatic_number}")
    if max_colors is not None:
        if chromatic_number <= max_colors:
            print(f"Đồ thị tô được với {max_colors} màu.")
        else:
            print(
                f"Không thể tô với {max_colors} màu (cần ít nhất {chromatic_number})."
            )
    print("Phân bố màu:", format_coloring(coloring, labels))


if __name__ == "__main__":
    main()

