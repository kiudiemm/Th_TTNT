"""GUI Demo cho bài toán người bán hàng (Traveling Salesman Problem).

Ứng dụng cho phép:
- Nhập số thành phố
- Nhập điểm xuất phát
- Nhập ma trận chi phí
- Chạy thuật toán Held-Karp
- Hiển thị đồ thị với chu trình tối ưu
"""

from __future__ import annotations

import math
import random
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, List, Tuple

from baitoanbanhang import held_karp


class TSPGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Bài toán người bán hàng")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        # Biến lưu trữ
        self.num_cities = tk.IntVar(value=5)
        self.start_city = tk.IntVar(value=0)
        self.matrix: List[List[float]] = []
        self.matrix_widgets: List[List[tk.StringVar]] = []
        self.current_tour: List[int] = []
        self.current_cost: float = 0.0

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

        # Phần nhập số thành phố và điểm xuất phát
        input_frame = ttk.LabelFrame(left_frame, text="Thông tin", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)

        # Số thành phố
        ttk.Label(input_frame, text="Số thành phố (n):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        cities_spin = ttk.Spinbox(
            input_frame,
            from_=2,
            to=15,
            textvariable=self.num_cities,
            width=10,
            command=self._on_cities_changed,
        )
        cities_spin.grid(row=0, column=1, padx=5, pady=5)
        cities_spin.bind("<KeyRelease>", lambda e: self._on_cities_changed())

        # Điểm xuất phát
        ttk.Label(input_frame, text="Điểm xuất phát:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        start_spin = ttk.Spinbox(
            input_frame,
            from_=0,
            to=14,
            textvariable=self.start_city,
            width=10,
        )
        start_spin.grid(row=0, column=3, padx=5, pady=5)
        start_spin.bind("<KeyRelease>", lambda e: self._update_start_label())
        start_spin.configure(command=self._update_start_label)

        # Nhãn hiển thị tên đỉnh xuất phát (A, B, C,...)
        self.start_label = ttk.Label(
            input_frame,
            text=f"Đỉnh: {self._city_label(self.start_city.get())}",
        )
        self.start_label.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)

        # Nút tạo ma trận
        ttk.Button(
            input_frame,
            text="Tạo ma trận chi phí",
            command=self._create_matrix_grid,
        ).grid(row=0, column=5, padx=5, pady=5)

        # Nút tạo đồ thị ngẫu nhiên
        ttk.Button(
            input_frame,
            text="Tạo ngẫu nhiên",
            command=self._generate_random_matrix,
        ).grid(row=0, column=6, padx=5, pady=5)

        # Frame cho ma trận chi phí
        matrix_frame = ttk.LabelFrame(
            left_frame,
            text="Ma trận chi phí (0 = không có đường, số > 0 = chi phí)",
            padding="10",
        )
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
            text="Chạy thuật toán TSP",
            command=self._run_algorithm,
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Xóa kết quả",
            command=self._clear_results,
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Tải mẫu 5 thành phố",
            command=self._load_sample,
        ).pack(side=tk.LEFT, padx=5)

        # Frame bên phải: Hiển thị đồ thị
        graph_frame = ttk.LabelFrame(main_frame, text="Đồ thị và chu trình", padding="10")
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

        # Frame chú thích
        legend_frame = ttk.Frame(graph_frame)
        legend_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        self.legend_label = ttk.Label(legend_frame, text="", font=("Arial", 9))
        self.legend_label.pack()

        # Tạo ma trận mặc định
        self._create_matrix_grid()

    def _on_cities_changed(self) -> None:
        """Cập nhật ma trận khi số thành phố thay đổi."""
        try:
            n = self.num_cities.get()
            if n < 2:
                return
            # Cập nhật max của start_city
            self.start_city.set(min(self.start_city.get(), n - 1))
            self._update_start_label()
            self._create_matrix_grid()
        except tk.TclError:
            pass

    def _create_matrix_grid(self) -> None:
        """Tạo lưới Entry cho ma trận chi phí."""
        # Xóa widgets cũ
        for widget in self.matrix_container.winfo_children():
            widget.destroy()
        self.matrix_widgets.clear()

        n = self.num_cities.get()
        if n < 2:
            messagebox.showwarning("Cảnh báo", "Số thành phố phải >= 2")
            return

        # Header row
        ttk.Label(self.matrix_container, text="", width=6).grid(row=0, column=0)
        for j in range(n):
            ttk.Label(
                self.matrix_container,
                text=f"C{j}",
                width=6,
                anchor=tk.CENTER,
            ).grid(row=0, column=j + 1, padx=2, pady=2)

        # Matrix rows với Entry
        for i in range(n):
            ttk.Label(
                self.matrix_container,
                text=f"C{i}",
                width=6,
            ).grid(row=i + 1, column=0, padx=2, pady=2)

            row_widgets: List[tk.StringVar] = []
            for j in range(n):
                var = tk.StringVar(value="0" if i == j else "")
                row_widgets.append(var)

                entry = ttk.Entry(
                    self.matrix_container,
                    textvariable=var,
                    width=6,
                )
                entry.grid(row=i + 1, column=j + 1, padx=2, pady=2)

                if i == j:
                    entry.config(state=tk.DISABLED)  # Đường chéo = 0

            self.matrix_widgets.append(row_widgets)

        # Cập nhật scroll region
        self.matrix_container.update_idletasks()
        self.matrix_canvas.configure(scrollregion=self.matrix_canvas.bbox("all"))

        # Vẽ đồ thị cấu trúc ngay sau khi tạo ma trận
        self.root.after(100, self._draw_graph_structure)

    def _get_matrix_from_widgets(self) -> List[List[float]]:
        """Lấy ma trận từ các Entry."""
        n = self.num_cities.get()
        matrix: List[List[float]] = []
        for i in range(n):
            row: List[float] = []
            for j in range(n):
                if i == j:
                    row.append(0.0)  # Đường chéo chính luôn 0
                else:
                    value_str = self.matrix_widgets[i][j].get().strip()
                    if not value_str:
                        row.append(float("inf"))  # Không có đường
                    else:
                        try:
                            val = float(value_str)
                            row.append(val if val > 0 else float("inf"))
                        except ValueError:
                            row.append(float("inf"))
            matrix.append(row)
        return matrix

    def _generate_random_matrix(self) -> None:
        """Tạo ma trận chi phí ngẫu nhiên."""
        n = self.num_cities.get()
        if n < 2:
            messagebox.showwarning("Cảnh báo", "Số thành phố phải >= 2")
            return

        # Đảm bảo ma trận đã được tạo
        if not self.matrix_widgets or len(self.matrix_widgets) != n:
            self._create_matrix_grid()
            self.root.update_idletasks()

        # Đồng bộ nhãn điểm xuất phát
        self._update_start_label()

        # Tạo ma trận chi phí ngẫu nhiên (không đối xứng hoàn toàn)
        for i in range(n):
            for j in range(n):
                if i == j:
                    self.matrix_widgets[i][j].set("0")
                else:
                    # Chi phí từ 5 đến 50, 80% có đường
                    if random.random() < 0.8:
                        cost = random.randint(5, 50)
                        self.matrix_widgets[i][j].set(str(cost))
                    else:
                        self.matrix_widgets[i][j].set("")  # Không có đường

        # Vẽ lại đồ thị
        self.root.after(100, self._draw_graph_structure)
        self._append_result(f"Đã tạo ma trận chi phí ngẫu nhiên với {n} thành phố.\n")

    def _load_sample(self) -> None:
        """Tải ma trận mẫu 5 thành phố."""
        sample_matrix: List[List[int]] = [
            [0, 10, 15, 20, 0],
            [10, 0, 35, 25, 17],
            [15, 35, 0, 30, 28],
            [20, 25, 30, 0, 23],
            [0, 17, 28, 23, 0],
        ]

        self.num_cities.set(5)
        self.start_city.set(0)
        self._create_matrix_grid()
        self._update_start_label()

        # Đặt giá trị cho các Entry
        for i in range(5):
            for j in range(5):
                if i != j:
                    val = sample_matrix[i][j]
                    self.matrix_widgets[i][j].set(str(val) if val > 0 else "")

        self._append_result("Đã tải ma trận mẫu 5 thành phố.\n")
        # Vẽ lại đồ thị
        self.root.after(100, self._draw_graph_structure)

    def _run_algorithm(self) -> None:
        """Chạy thuật toán TSP và hiển thị kết quả."""
        try:
            n = self.num_cities.get()
            start = self.start_city.get()

            if n < 2:
                messagebox.showerror("Lỗi", "Số thành phố phải >= 2")
                return

            if not (0 <= start < n):
                messagebox.showerror("Lỗi", f"Điểm xuất phát phải từ 0 đến {n-1}")
                return

            # Lấy ma trận từ widgets
            matrix = self._get_matrix_from_widgets()

            # Chạy thuật toán Held-Karp
            cost, tour = held_karp(matrix, start=start)

            # Lưu lại để vẽ đồ thị
            self.current_tour = tour
            self.current_cost = cost

            # Hiển thị kết quả
            self._append_result("=" * 50 + "\n")
            self._append_result(f"Số thành phố: {n}\n")
            self._append_result(f"Điểm xuất phát: {self._city_label(start)}\n")
            self._append_result(f"Chi phí tối thiểu: {cost}\n\n")

            # Hiển thị chu trình
            tour_str = " -> ".join(self._city_label(c) for c in tour)
            self._append_result(f"Chu trình tối ưu:\n{tour_str} -> {self._city_label(tour[0])}\n\n")

            # Hiển thị chi tiết từng cạnh
            self._append_result("Chi tiết từng cạnh:\n")
            total = 0.0
            for idx in range(len(tour)):
                from_city = tour[idx]
                to_city = tour[(idx + 1) % len(tour)]
                edge_cost = matrix[from_city][to_city]
                total += edge_cost
                self._append_result(
                    f"  {self._city_label(from_city)} -> {self._city_label(to_city)}: {edge_cost}\n",
                )
            self._append_result(f"\nTổng chi phí: {total}\n")
            self._append_result("\n" + "=" * 50 + "\n\n")

            # Vẽ đồ thị
            self._draw_graph(matrix, tour)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")

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
        # Vẽ lại đồ thị cấu trúc (không có chu trình)
        self._draw_graph_structure()

    # ----------------- Helpers -----------------
    def _city_label(self, idx: int) -> str:
        """Đổi nhãn thành phố sang A, B, C,... nếu < 26; ngược lại giữ C<idx>."""
        if 0 <= idx < 26:
            return chr(ord("A") + idx)
        return f"C{idx}"

    def _update_start_label(self) -> None:
        """Cập nhật nhãn hiển thị tên đỉnh xuất phát theo giá trị hiện tại."""
        try:
            start = self.start_city.get()
            self.start_label.config(text=f"Đỉnh: {self._city_label(start)}")
        except Exception:
            pass

    def _draw_graph_structure(self) -> None:
        """Vẽ đồ thị cấu trúc (chưa có chu trình) dựa trên ma trận hiện tại."""
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
            radius = min(canvas_width, canvas_height) / 2 - 80

            # Tính toán vị trí đỉnh trên vòng tròn
            positions: Dict[int, Tuple[int, int]] = {}
            for i in range(n):
                angle = 2 * math.pi * i / n - math.pi / 2
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions[i] = (int(x), int(y))

            # Vẽ các cạnh (tất cả các đường có thể)
            for i in range(n):
                for j in range(n):
                    if i != j and matrix[i][j] != float("inf"):
                        x1, y1 = positions[i]
                        x2, y2 = positions[j]
                        # Vẽ cạnh mỏng, màu xám nhạt
                        self.canvas_graph.create_line(
                            x1, y1, x2, y2,
                            fill="#CCCCCC",
                            width=1,
                            tags="edge",
                        )
                        # Vẽ nhãn chi phí ở giữa cạnh (kèm nhãn thành phố)
                        mid_x = (x1 + x2) / 2
                        mid_y = (y1 + y2) / 2
                        cost = matrix[i][j]
                        label_text = (
                            f"{self._city_label(i)}→{self._city_label(j)}\n{int(cost)}"
                        )
                        self.canvas_graph.create_text(
                            mid_x,
                            mid_y,
                            text=label_text,
                            fill="#666666",
                            font=("Arial", 7),
                            tags="cost_label",
                        )

            # Vẽ các đỉnh
            vertex_radius = 25
            start = self.start_city.get()
            for vertex in range(n):
                x, y = positions[vertex]

                # Màu đỉnh: xanh lá nếu là điểm xuất phát, xám nếu không
                fill_color = "#90EE90" if vertex == start else "#E0E0E0"
                outline_color = "#006400" if vertex == start else "black"
                outline_width = 3 if vertex == start else 2

                # Vẽ đỉnh (hình tròn)
                self.canvas_graph.create_oval(
                    x - vertex_radius,
                    y - vertex_radius,
                    x + vertex_radius,
                    y + vertex_radius,
                    fill=fill_color,
                    outline=outline_color,
                    width=outline_width,
                    tags="vertex",
                )

                # Nhãn đỉnh
                label = self._city_label(vertex)
                self.canvas_graph.create_text(
                    x,
                    y,
                    text=label,
                    fill="black",
                    font=("Arial", 11, "bold"),
                    tags="label",
                )

            # Tiêu đề
            self.canvas_graph.create_text(
                center_x,
                20,
                text=f"Đồ thị ({n} thành phố) - Chưa có chu trình",
                fill="black",
                font=("Arial", 12, "bold"),
                tags="title",
            )

        except Exception:
            # Nếu có lỗi (ví dụ ma trận chưa sẵn sàng), bỏ qua
            pass

    def _draw_graph(self, matrix: List[List[float]], tour: List[int]) -> None:
        """Vẽ đồ thị với chu trình tối ưu được highlight."""
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
        radius = min(canvas_width, canvas_height) / 2 - 80

        # Tính toán vị trí đỉnh trên vòng tròn
        positions: Dict[int, Tuple[int, int]] = {}
        for i in range(n):
            angle = 2 * math.pi * i / n - math.pi / 2
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            positions[i] = (int(x), int(y))

        # Màu sắc cho chu trình (màu pastel)
        tour_colors = [
            "#FFB3BA",  # Hồng pastel
            "#BAFFC9",  # Xanh lá pastel
            "#BAE1FF",  # Xanh dương pastel
            "#FFFFBA",  # Vàng pastel
            "#FFDFBA",  # Cam pastel
            "#E0BBE4",  # Tím pastel
            "#B4E4FF",  # Xanh nhạt pastel
            "#FFCCCB",  # Đỏ pastel
        ]

        # Vẽ các cạnh không trong chu trình (mỏng, xám)
        for i in range(n):
            for j in range(n):
                if i != j and matrix[i][j] != float("inf"):
                    # Kiểm tra xem cạnh có trong chu trình không
                    in_tour = False
                    for idx in range(len(tour)):
                        if (tour[idx] == i and tour[(idx + 1) % len(tour)] == j) or (
                            tour[idx] == j and tour[(idx + 1) % len(tour)] == i
                        ):
                            in_tour = True
                            break

                    if not in_tour:
                        x1, y1 = positions[i]
                        x2, y2 = positions[j]
                        self.canvas_graph.create_line(
                            x1, y1, x2, y2,
                            fill="#E0E0E0",
                            width=1,
                            tags="edge",
                        )

        # Vẽ các cạnh trong chu trình (đậm, màu pastel)
        for idx in range(len(tour)):
            from_city = tour[idx]
            to_city = tour[(idx + 1) % len(tour)]
            x1, y1 = positions[from_city]
            x2, y2 = positions[to_city]

            # Màu cạnh thay đổi theo thứ tự trong chu trình
            color = tour_colors[idx % len(tour_colors)]

            # Vẽ cạnh đậm với màu
            self.canvas_graph.create_line(
                x1, y1, x2, y2,
                fill=color,
                width=4,
                tags="tour_edge",
            )

            # Vẽ mũi tên ở giữa cạnh
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            angle = math.atan2(y2 - y1, x2 - x1)
            arrow_size = 8
            arrow_x = mid_x - arrow_size * math.cos(angle)
            arrow_y = mid_y - arrow_size * math.sin(angle)
            self.canvas_graph.create_polygon(
                arrow_x,
                arrow_y,
                arrow_x - arrow_size * math.cos(angle - math.pi / 6),
                arrow_y - arrow_size * math.sin(angle - math.pi / 6),
                arrow_x - arrow_size * math.cos(angle + math.pi / 6),
                arrow_y - arrow_size * math.sin(angle + math.pi / 6),
                fill=color,
                outline=color,
                tags="arrow",
            )

            # Nhãn chi phí
            cost = matrix[from_city][to_city]
            label_x = mid_x + 15 * math.cos(angle + math.pi / 2)
            label_y = mid_y + 15 * math.sin(angle + math.pi / 2)
            self.canvas_graph.create_text(
                label_x,
                label_y,
                text=str(int(cost)),
                fill=color,
                font=("Arial", 9, "bold"),
                tags="cost_label",
            )

        # Vẽ các đỉnh
        vertex_radius = 25
        start = self.start_city.get()
        for vertex in range(n):
            x, y = positions[vertex]

            # Màu đỉnh: xanh lá đậm nếu là điểm xuất phát, xanh nhạt nếu trong chu trình
            if vertex == start:
                fill_color = "#90EE90"  # Xanh lá
                outline_color = "#006400"  # Xanh lá đậm
            elif vertex in tour:
                fill_color = "#E0F7FA"  # Xanh nhạt
                outline_color = "#00838F"  # Xanh đậm
            else:
                fill_color = "#E0E0E0"  # Xám
                outline_color = "black"

            outline_width = 3 if vertex == start else 2

            # Vẽ đỉnh (hình tròn)
            self.canvas_graph.create_oval(
                x - vertex_radius,
                y - vertex_radius,
                x + vertex_radius,
                y + vertex_radius,
                fill=fill_color,
                outline=outline_color,
                width=outline_width,
                tags="vertex",
            )

            # Nhãn đỉnh
            label = self._city_label(vertex)
            self.canvas_graph.create_text(
                x,
                y,
                text=label,
                fill="black",
                font=("Arial", 11, "bold"),
                tags="label",
            )

        # Tiêu đề
        self.canvas_graph.create_text(
            center_x,
            20,
            text=f"Chu trình tối ưu - Chi phí: {int(self.current_cost)}",
            fill="black",
            font=("Arial", 12, "bold"),
            tags="title",
        )

        # Chú thích
        tour_str = " -> ".join(self._city_label(c) for c in tour)
        self.legend_label.config(text=f"Chu trình: {tour_str} -> {self._city_label(tour[0])}")


def main() -> None:
    root = tk.Tk()
    app = TSPGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

