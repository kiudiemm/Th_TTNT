# Thuật toán tô màu tối ưu và bài toán người bán hàng

**Họ và tên:** Trần Thị Kiều Diễm
**MSSV:** 2033230036

## Chương 1. Thuật toán tô màu tối ưu trên đồ thị

### 1.1. Mô tả bài toán
#### 1.1.1. Phát biểu bài toán
Tìm số màu nhỏ nhất (số sắc) để tô các đỉnh sao cho hai đỉnh kề nhau không trùng màu.

#### 1.1.2. Input
- Ma trận kề vuông n×n (0/1) biểu diễn đồ thị vô hướng.
- Cho phép dòng chú thích bắt đầu bằng `#`.

#### 1.1.3. Output (expected)
- Số màu tối thiểu.
- Phân bố màu cho từng đỉnh (đỉnh:màu). Với mẫu 6 đỉnh, đỉnh mang nhãn A-F.

### 1.2. Các đối tượng/hàm được sử dụng
- Ma trận kề đọc từ file (`graph_io.read_adjacency_matrix`).
- Chuyển sang danh sách kề (`build_adjacency_list`).
- Hàm kiểm tra hợp lệ màu với láng giềng, trạng thái tô màu hiện tại, nghiệm tốt nhất.

### 1.3. Phương pháp giải (Backtracking + Branch-and-Bound)
1) Sắp xếp đỉnh theo bậc giảm dần để ưu tiên đỉnh nhiều cạnh.  
2) Duyệt DFS, thử lần lượt các màu đã dùng; chỉ mở màu mới khi cần.  
3) Cắt tỉa nếu số màu đang dùng không thể tốt hơn nghiệm tốt nhất.  
4) Khi tô hết đỉnh, cập nhật nghiệm tối ưu (số sắc và phân bố màu).

### 1.4. Ví dụ file ma trận kề (đồ thị mẫu 6 đỉnh A-F)
```
0 1 1 0 1 0
1 0 1 1 0 1
1 1 0 1 1 0
0 1 1 0 0 1
1 0 1 0 0 1
0 1 0 1 1 0
```
File mẫu: `sample_matrix_6.txt`

### 1.5. Kết quả mong đợi khi chạy
```
python graph_coloring.py --sample
# hoặc
python graph_coloring.py --input path/to/matrix.txt
```
In ra: số màu tối thiểu và phân bố màu (theo nhãn A-F nếu dùng mẫu).

---

## Chương 2. Bài toán người bán hàng (Traveling Salesman Problem - TSP)

### 2.1. Mô tả bài toán
#### 2.1.1. Phát biểu bài toán
Tìm chu trình đi qua mỗi thành phố đúng một lần, xuất phát và quay về thành phố gốc với tổng chi phí nhỏ nhất.

#### 2.1.2. Input
- Ma trận chi phí n×n; giá trị 0 được hiểu là không có cạnh (được chuyển thành ∞ khi tính).
- Tham số `start` chọn thành phố xuất phát.

#### 2.1.3. Output (expected)
- Chi phí tối thiểu.
- Chu trình tối ưu (thứ tự các thành phố).

### 2.2. Các đối tượng/hàm được sử dụng
- Ma trận chi phí đọc từ file (`graph_io.read_adjacency_matrix`).
- Hàm quy hoạch động `held_karp` với memo hóa trạng thái `(đỉnh hiện tại, tập đỉnh chưa thăm)`.

### 2.3. Phương pháp giải (Held-Karp – Dynamic Programming trên tập con)
1) Khởi tạo trạng thái cho từng tập con đỉnh chưa thăm, chi phí quay về gốc.  
2) Chuyển trạng thái qua từng đỉnh kế tiếp, chọn chi phí tối thiểu.  
3) Truy vết để dựng lại chu trình tối ưu.

### 2.4. Ví dụ file ma trận chi phí
```
0 10 15 20 0
10 0 35 25 17
15 35 0 30 28
20 25 30 0 23
0 17 28 23 0
```
File mẫu: `sample_tsp_matrix.txt`

### 2.5. Kết quả mong đợi khi chạy
```
python baitoanbanhang.py --input sample_tsp_matrix.txt --start 0
```
In ra: chi phí tối thiểu và chu trình tương ứng.

---

## Chương 3. Hướng dẫn chung
- Yêu cầu: Python 3.10+, không cần thư viện ngoài.  
- File ma trận cho phép chú thích bắt đầu bằng `#`.  
- Lệnh chạy nhanh:
  - Tô màu: `python graph_coloring.py --sample` hoặc `--input file.txt`
  - TSP: `python baitoanbanhang.py --input file.txt --start 0`

