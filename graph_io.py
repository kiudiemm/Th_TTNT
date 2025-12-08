"""Tiện ích đọc đồ thị từ file văn bản.

File đầu vào chứa ma trận kề vuông; mỗi dòng là các số phân tách bởi
khoảng trắng. Giá trị khác 0 nghĩa là có cạnh.
"""

from __future__ import annotations

from pathlib import Path
from typing import List


def read_adjacency_matrix(file_path: str | Path) -> List[List[int]]:
    """Đọc ma trận kề vuông từ file văn bản.

    Bỏ qua dòng trống hoặc dòng bắt đầu bằng '#'. Giá trị được tách bởi
    dấu cách hoặc tab.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    rows: List[List[int]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        rows.append([int(x) for x in stripped.split()])

    if not rows:
        raise ValueError("Input file is empty or only contains comments.")

    size = len(rows)
    for idx, row in enumerate(rows):
        if len(row) != size:
            raise ValueError(
                f"Row {idx} has length {len(row)} but expected {size} for a square matrix."
            )

    return rows

