"""GUI Demo cho bài toán tô màu đồ thị.

Ứng dụng cho phép:
- Nhập số đỉnh đồ thị
- Nhập số màu mong muốn
- Nhập ma trận kề (checkbox hoặc text)
- Chạy thuật toán và hiển thị kết quả
- Hiển thị đồ thị dưới dạng đồ họa
"""

from __future__ import annotations

import math
import random
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Callable, Dict, List, Tuple

from graph_coloring import (
    backtracking_coloring,
    build_adjacency_list,
    format_coloring,
)


class GraphColoringGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Tô màu đồ thị - Demo GUI")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        # Biến lưu trữ
        self.num_vertices = tk.IntVar(value=6)
        self.num_colors = tk.IntVar(value=3)
        self.matrix: List[List[int]] = []
        self.matrix_widgets: List[List[tk.IntVar]] = []
        self.current_coloring: Dict[int, int] = {}
        self.current_adjacency: List[List[int]] = []

        self._create_widgets()

    def _create_widgets(self) -> None:
        # Frame chính - chia làm 2 cột: trái (input) và phải (đồ thị)
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Frame bên trái: Input và kết quả
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        main_frame.rowconfigure(0, weight=1)

        # Phần nhập số đỉnh và số màu
        input_frame = ttk.LabelFrame(left_frame, text="Thông tin đồ thị", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)

        # Số đỉnh
        ttk.Label(input_frame, text="Số đỉnh (n):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        vertices_spin = ttk.Spinbox(
            input_frame,
            from_=2,
            to=20,
            textvariable=self.num_vertices,
            width=10,
            command=self._on_vertices_changed,
        )
        vertices_spin.grid(row=0, column=1, padx=5, pady=5)
        vertices_spin.bind("<KeyRelease>", lambda e: self._on_vertices_changed())

        # Số màu
        ttk.Label(input_frame, text="Số màu (k):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        colors_spin = ttk.Spinbox(
            input_frame,
            from_=1,
            to=20,
            textvariable=self.num_colors,
            width=10,
        )
        colors_spin.grid(row=0, column=3, padx=5, pady=5)

        # Nút tạo ma trận
        ttk.Button(
            input_frame,
            text="Tạo ma trận kề",
            command=self._create_matrix_grid,
        ).grid(row=0, column=4, padx=5, pady=5)

        # Nút tạo đồ thị ngẫu nhiên
        ttk.Button(
            input_frame,
            text="Tạo đồ thị ngẫu nhiên",
            command=self._generate_random_graph,
        ).grid(row=0, column=5, padx=5, pady=5)

        # Frame cho ma trận kề
        matrix_frame = ttk.LabelFrame(left_frame, text="Ma trận kề (0 = không có cạnh, 1 = có cạnh)", padding="10")
        matrix_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        left_frame.rowconfigure(1, weight=1)

        # Canvas với scrollbar cho ma trận lớn
        canvas = tk.Canvas(matrix_frame, bg="white")
        scrollbar = ttk.Scrollbar(matrix_frame, orient="vertical", command=canvas.yview)
        self.matrix_container = ttk.Frame(canvas)

        self.matrix_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=self.matrix_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        matrix_frame.columnconfigure(0, weight=1)
        matrix_frame.rowconfigure(0, weight=1)

        self.matrix_canvas = canvas

        # Frame kết quả
        result_frame = ttk.LabelFrame(left_frame, text="Kết quả", padding="10")
        result_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        left_frame.rowconfigure(2, weight=1)

        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            height=8,
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        # Nút chạy thuật toán
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=3, column=0, pady=10)

        ttk.Button(
            button_frame,
            text="Chạy thuật toán tô màu",
            command=self._run_algorithm,
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Xóa kết quả",
            command=self._clear_results,
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Tải mẫu 6 đỉnh",
            command=self._load_sample,
        ).pack(side=tk.LEFT, padx=5)

        # Frame bên phải: Hiển thị đồ thị
        graph_frame = ttk.LabelFrame(main_frame, text="Đồ thị", padding="10")
        graph_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.rowconfigure(0, weight=1)

        # Canvas để vẽ đồ thị
        self.canvas_graph = tk.Canvas(
            graph_frame,
            bg="white",
            width=500,
            height=500,
        )
        self.canvas_graph.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Frame chú thích màu
        legend_frame = ttk.Frame(graph_frame)
        legend_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        self.legend_label = ttk.Label(legend_frame, text="", font=("Arial", 9))
        self.legend_label.pack()

        # Tạo ma trận mặc định
        self._create_matrix_grid()

    def _on_vertices_changed(self) -> None:
        """Cập nhật ma trận khi số đỉnh thay đổi."""
        try:
            n = self.num_vertices.get()
            if n < 2:
                return
            self._create_matrix_grid()
        except tk.TclError:
            pass

    def _create_matrix_grid(self) -> None:
        """Tạo lưới checkbox cho ma trận kề."""
        # Xóa widgets cũ
        for widget in self.matrix_container.winfo_children():
            widget.destroy()
        self.matrix_widgets.clear()

        n = self.num_vertices.get()
        if n < 2:
            messagebox.showwarning("Cảnh báo", "Số đỉnh phải >= 2")
            return

        # Header row
        ttk.Label(self.matrix_container, text="", width=4).grid(row=0, column=0)
        for j in range(n):
            ttk.Label(
                self.matrix_container,
                text=f"v{j}",
                width=4,
                anchor=tk.CENTER,
            ).grid(row=0, column=j + 1, padx=2, pady=2)

        # Matrix rows với checkbox
        for i in range(n):
            ttk.Label(
                self.matrix_container,
                text=f"v{i}",
                width=4,
            ).grid(row=i + 1, column=0, padx=2, pady=2)

            row_widgets: List[tk.IntVar] = []
            for j in range(n):
                var = tk.IntVar(value=0)
                row_widgets.append(var)

                if i == j:
                    # Đường chéo chính: không cho chọn (luôn 0)
                    checkbox = ttk.Checkbutton(
                        self.matrix_container,
                        variable=var,
                        state=tk.DISABLED,
                    )
                else:
                    # Thêm callback để vẽ lại đồ thị khi checkbox thay đổi
                    # Sử dụng default argument để capture đúng giá trị i, j
                    def make_callback(r: int, c: int) -> Callable:
                        return lambda *args: self._on_matrix_changed()
                    var.trace_add("write", make_callback(i, j))
                    checkbox = ttk.Checkbutton(
                        self.matrix_container,
                        variable=var,
                    )

                checkbox.grid(row=i + 1, column=j + 1, padx=2, pady=2)

            self.matrix_widgets.append(row_widgets)

        # Cập nhật scroll region
        self.matrix_container.update_idletasks()
        self.matrix_canvas.configure(scrollregion=self.matrix_canvas.bbox("all"))

        # Vẽ đồ thị cấu trúc ngay sau khi tạo ma trận
        self.root.after(100, self._draw_graph_structure)

    def _get_matrix_from_widgets(self) -> List[List[int]]:
        """Lấy ma trận từ các checkbox."""
        n = self.num_vertices.get()
        matrix: List[List[int]] = []
        for i in range(n):
            row: List[int] = []
            for j in range(n):
                if i == j:
                    row.append(0)  # Đường chéo chính luôn 0
                else:
                    row.append(self.matrix_widgets[i][j].get())
            matrix.append(row)
        return matrix

    def _on_matrix_changed(self) -> None:
        """Callback khi ma trận thay đổi - vẽ lại đồ thị cấu trúc."""
        self.root.after(100, self._draw_graph_structure)

    def _generate_random_graph(self) -> None:
        """Tạo đồ thị ngẫu nhiên với số đỉnh hiện tại."""
        n = self.num_vertices.get()
        if n < 2:
            messagebox.showwarning("Cảnh báo", "Số đỉnh phải >= 2")
            return

        # Đảm bảo ma trận đã được tạo
        if not self.matrix_widgets or len(self.matrix_widgets) != n:
            self._create_matrix_grid()
            self.root.update_idletasks()

        # Tạo ma trận kề ngẫu nhiên (đối xứng)
        # Xác suất có cạnh: 30-50% tùy số đỉnh
        probability = 0.4 if n <= 10 else 0.3

        # Tạo ma trận
        for i in range(n):
            for j in range(i + 1, n):
                if random.random() < probability:
                    # Có cạnh
                    self.matrix_widgets[i][j].set(1)
                    self.matrix_widgets[j][i].set(1)
                else:
                    # Không có cạnh
                    self.matrix_widgets[i][j].set(0)
                    self.matrix_widgets[j][i].set(0)

        # Vẽ lại đồ thị
        self.root.after(100, self._draw_graph_structure)
        self._append_result(f"Đã tạo đồ thị ngẫu nhiên với {n} đỉnh.\n")

    def _load_sample(self) -> None:
        """Tải đồ thị mẫu 6 đỉnh."""
        sample_matrix: List[List[int]] = [
            [0, 1, 1, 0, 1, 0],
            [1, 0, 1, 1, 0, 1],
            [1, 1, 0, 1, 1, 0],
            [0, 1, 1, 0, 0, 1],
            [1, 0, 1, 0, 0, 1],
            [0, 1, 0, 1, 1, 0],
        ]

        self.num_vertices.set(6)
        self._create_matrix_grid()

        # Đặt giá trị cho các checkbox
        for i in range(6):
            for j in range(6):
                if i != j:
                    self.matrix_widgets[i][j].set(sample_matrix[i][j])

        self._append_result("Đã tải đồ thị mẫu 6 đỉnh (A-F).\n")
        # Vẽ lại đồ thị
        self.root.after(100, self._draw_graph_structure)

    def _run_algorithm(self) -> None:
        """Chạy thuật toán tô màu và hiển thị kết quả."""
        try:
            n = self.num_vertices.get()
            k = self.num_colors.get()

            if n < 2:
                messagebox.showerror("Lỗi", "Số đỉnh phải >= 2")
                return

            if k < 1:
                messagebox.showerror("Lỗi", "Số màu phải >= 1")
                return

            # Lấy ma trận từ widgets
            matrix = self._get_matrix_from_widgets()

            # Kiểm tra ma trận có đối xứng không (đồ thị vô hướng)
            for i in range(n):
                for j in range(n):
                    if matrix[i][j] != matrix[j][i]:
                        messagebox.showwarning(
                            "Cảnh báo",
                            f"Ma trận không đối xứng tại ({i},{j}). "
                            "Đồ thị vô hướng cần ma trận đối xứng.",
                        )
                        return

            # Chuyển sang danh sách kề và chạy thuật toán
            adjacency = build_adjacency_list(matrix)
            chromatic_number, coloring = backtracking_coloring(adjacency)

            # Lưu lại để vẽ đồ thị
            self.current_adjacency = adjacency
            self.current_coloring = coloring

            # Kiểm tra tính hợp lệ: các đỉnh kề nhau không được cùng màu
            is_valid_coloring = self._validate_coloring(adjacency, coloring)

            # Hiển thị kết quả
            self._append_result("=" * 50 + "\n")
            self._append_result(f"Số đỉnh: {n}\n")
            self._append_result(f"Số màu nhập vào: {k}\n")
            self._append_result(f"Số màu tối thiểu (số sắc): {chromatic_number}\n\n")

            if chromatic_number <= k:
                self._append_result(f"✓ Đồ thị có thể tô được với {k} màu.\n")
            else:
                self._append_result(
                    f"✗ Không thể tô với {k} màu (cần ít nhất {chromatic_number} màu).\n",
                )

            # Hiển thị kết quả kiểm tra
            if is_valid_coloring:
                self._append_result("\n✓ KIỂM TRA: Tất cả các đỉnh kề nhau đều có màu khác nhau (HỢP LỆ)\n")
            else:
                self._append_result("\n✗ CẢNH BÁO: Có đỉnh kề nhau cùng màu (KHÔNG HỢP LỆ)\n")

            self._append_result(f"\nPhân bố màu:\n")
            # Hiển thị theo nhãn A,B,C,...
            coloring_str = " ".join(
                f"{self._vertex_label(v)}:{c}" for v, c in sorted(coloring.items())
            )
            self._append_result(f"{coloring_str}\n\n")

            # Bảng màu chi tiết: màu idx, tên, các đỉnh dùng màu
            self._append_result("Bảng màu (tên - đỉnh dùng màu):\n")
            color_palette = self._color_palette()
            unique_colors = sorted(set(coloring.values()))
            for color_idx in unique_colors:
                color_hex, color_name = color_palette[color_idx % len(color_palette)]
                vertices = [self._vertex_label(v) for v, c in coloring.items() if c == color_idx]
                self._append_result(
                    f"  Màu {color_idx}: {color_name} -> {vertices}\n"
                )
            self._append_result("\n")

            # Hiển thị chi tiết từng đỉnh (tên màu + danh sách đỉnh kề)
            self._append_result("Chi tiết:\n")
            palette = self._color_palette()
            for vertex, color in sorted(coloring.items()):
                _, color_name = palette[color % len(palette)]
                neighbor_labels = [self._vertex_label(n) for n in adjacency[vertex]]
                neighbor_text = ", ".join(neighbor_labels) if neighbor_labels else "không kề"
                self._append_result(
                    f"  ✓ Đỉnh {self._vertex_label(vertex)}: {color_name} "
                    f"(kề với: {neighbor_text})\n"
                )
            self._draw_graph(matrix, coloring)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")

    def _validate_coloring(self, adjacency: List[List[int]], coloring: Dict[int, int]) -> bool:
        """Kiểm tra tính hợp lệ của cách tô màu: các đỉnh kề nhau không được cùng màu."""
        for vertex in range(len(adjacency)):
            vertex_color = coloring.get(vertex, -1)
            for neighbor in adjacency[vertex]:
                neighbor_color = coloring.get(neighbor, -1)
                if vertex_color == neighbor_color:
                    return False  # Tìm thấy đỉnh kề cùng màu
        return True  # Tất cả đỉnh kề đều khác màu

    def _vertex_label(self, idx: int) -> str:
        """Đổi nhãn đỉnh sang A, B, C,... nếu < 26; ngược lại giữ v<idx>."""
        if 0 <= idx < 26:
            return chr(ord("A") + idx)
        return f"v{idx}"

    def _color_palette(self) -> List[Tuple[str, str]]:
        """Trả về bảng màu pastel (hex, tên)."""
        return [
            ("#FFB3BA", "Hồng pastel"),
            ("#BAFFC9", "Xanh lá pastel"),
            ("#BAE1FF", "Xanh dương pastel"),
            ("#FFFFBA", "Vàng pastel"),
            ("#FFDFBA", "Cam pastel"),
            ("#E0BBE4", "Tím pastel"),
            ("#B4E4FF", "Xanh nhạt pastel"),
            ("#FFCCCB", "Đỏ pastel"),
            ("#C7CEEA", "Xanh tím pastel"),
            ("#F0E6FF", "Tím nhạt pastel"),
            ("#FFE4E1", "Hồng đào pastel"),
            ("#E6F3FF", "Xanh da trời pastel"),
            ("#FFF4E6", "Kem pastel"),
            ("#E0F2F1", "Xanh ngọc pastel"),
            ("#FCE4EC", "Hồng nhạt pastel"),
            ("#E8F5E9", "Xanh lá nhạt pastel"),
            ("#FFF3E0", "Cam nhạt pastel"),
            ("#F3E5F5", "Tím lavender pastel"),
            ("#E0F7FA", "Xanh cyan pastel"),
            ("#FFF9C4", "Vàng chanh pastel"),
            ("#F1F8E9", "Xanh lá chanh pastel"),
            ("#FEE5E5", "Đỏ hồng pastel"),
            ("#E1F5FE", "Xanh băng pastel"),
            ("#FFF8E1", "Vàng nhạt pastel"),
            ("#F8BBD0", "Hồng đậm pastel"),
        ]

    def _append_result(self, text: str) -> None:
        """Thêm text vào kết quả."""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, text)
        self.result_text.see(tk.END)
        self.result_text.config(state=tk.DISABLED)

    def _clear_results(self) -> None:
        """Xóa kết quả."""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        # Vẽ lại đồ thị cấu trúc (không tô màu)
        self._draw_graph_structure()

    def _draw_graph_structure(self) -> None:
        """Vẽ đồ thị cấu trúc (chưa tô màu) dựa trên ma trận hiện tại."""
        try:
            matrix = self._get_matrix_from_widgets()
            n = len(matrix)
            if n == 0:
                return

            # Xóa đồ thị cũ
            self.canvas_graph.delete("all")
            self.legend_label.config(text="")

            # Lấy kích thước canvas
            canvas_width = self.canvas_graph.winfo_width()
            canvas_height = self.canvas_graph.winfo_height()

            # Nếu canvas chưa được render, dùng kích thước mặc định
            if canvas_width <= 1:
                canvas_width = 500
            if canvas_height <= 1:
                canvas_height = 500

            # Tính toán vị trí trung tâm và bán kính
            center_x = canvas_width / 2
            center_y = canvas_height / 2
            radius = min(canvas_width, canvas_height) / 2 - 60

            # Tính toán vị trí đỉnh trên vòng tròn
            positions: Dict[int, Tuple[int, int]] = {}
            for i in range(n):
                angle = 2 * math.pi * i / n - math.pi / 2
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions[i] = (int(x), int(y))

            # Vẽ các cạnh trước
            for i in range(n):
                for j in range(i + 1, n):
                    if matrix[i][j] == 1:
                        x1, y1 = positions[i]
                        x2, y2 = positions[j]
                        self.canvas_graph.create_line(
                            x1, y1, x2, y2,
                            fill="#666666",
                            width=2,
                            tags="edge",
                        )

            # Vẽ các đỉnh (màu xám, chưa tô màu)
            vertex_radius = 20
            for vertex in range(n):
                x, y = positions[vertex]

                # Vẽ đỉnh (màu xám)
                self.canvas_graph.create_oval(
                    x - vertex_radius,
                    y - vertex_radius,
                    x + vertex_radius,
                    y + vertex_radius,
                    fill="#E0E0E0",
                    outline="black",
                    width=2,
                    tags="vertex",
                )

                # Nhãn đỉnh
                label = f"v{vertex}"
                self.canvas_graph.create_text(
                    x,
                    y,
                    text=label,
                    fill="black",
                    font=("Arial", 10, "bold"),
                    tags="label",
                )

            # Tiêu đề
            self.canvas_graph.create_text(
                center_x,
                20,
                text=f"Đồ thị ({n} đỉnh) - Chưa tô màu",
                fill="black",
                font=("Arial", 12, "bold"),
                tags="title",
            )

        except Exception:
            # Nếu có lỗi (ví dụ ma trận chưa sẵn sàng), bỏ qua
            pass

    def _draw_graph(self, matrix: List[List[int]], coloring: Dict[int, int]) -> None:
        """Vẽ đồ thị với các đỉnh được tô màu bằng tkinter Canvas."""
        n = len(matrix)
        if n == 0:
            return

        # Xóa đồ thị cũ
        self.canvas_graph.delete("all")

        # Lấy kích thước canvas
        canvas_width = self.canvas_graph.winfo_width()
        canvas_height = self.canvas_graph.winfo_height()

        # Nếu canvas chưa được render, dùng kích thước mặc định
        if canvas_width <= 1:
            canvas_width = 500
        if canvas_height <= 1:
            canvas_height = 500

        # Tính toán vị trí trung tâm và bán kính
        center_x = canvas_width / 2
        center_y = canvas_height / 2
        radius = min(canvas_width, canvas_height) / 2 - 60  # Để lại khoảng trống cho nhãn

        # Tính toán vị trí đỉnh trên vòng tròn
        positions: Dict[int, Tuple[int, int]] = {}
        for i in range(n):
            angle = 2 * math.pi * i / n - math.pi / 2  # Bắt đầu từ trên
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            positions[i] = (int(x), int(y))

        # Màu sắc cho các đỉnh - bảng màu pastel (hex, tên)
        color_palette = self._color_palette()

        # Vẽ các cạnh trước (để chúng ở phía sau)
        for i in range(n):
            for j in range(i + 1, n):
                if matrix[i][j] == 1:
                    x1, y1 = positions[i]
                    x2, y2 = positions[j]
                    self.canvas_graph.create_line(
                        x1, y1, x2, y2,
                        fill="#666666",
                        width=2,
                        tags="edge",
                    )

        # Vẽ các đỉnh với màu tương ứng
        vertex_radius = 20
        for vertex in range(n):
            x, y = positions[vertex]
            color_idx = coloring.get(vertex, 0)
            color_hex, _ = color_palette[color_idx % len(color_palette)]

            # Vẽ đỉnh (hình tròn)
            self.canvas_graph.create_oval(
                x - vertex_radius,
                y - vertex_radius,
                x + vertex_radius,
                y + vertex_radius,
                fill=color_hex,
                outline="black",
                width=2,
                tags="vertex",
            )

            # Nhãn đỉnh
            label = self._vertex_label(vertex)
            self.canvas_graph.create_text(
                x,
                y,
                text=label,
                fill="black",
                font=("Arial", 10, "bold"),
                tags="label",
            )

        # Tiêu đề
        chromatic_number = len(set(coloring.values()))
        self.canvas_graph.create_text(
            center_x,
            20,
            text=f"Đồ thị với {chromatic_number} màu",
            fill="black",
            font=("Arial", 12, "bold"),
            tags="title",
        )

        # Chú thích màu
        legend_text = "Chú thích màu: "
        unique_colors = sorted(set(coloring.values()))
        legend_parts = []
        for color_idx in unique_colors:
            vertices = [self._vertex_label(v) for v, c in coloring.items() if c == color_idx]
            _, color_name = color_palette[color_idx % len(color_palette)]
            legend_parts.append(f"Màu {color_idx} ({color_name}): {vertices}")

        legend_full = " | ".join(legend_parts)
        self.legend_label.config(text=legend_full)


def main() -> None:
    root = tk.Tk()
    app = GraphColoringGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

