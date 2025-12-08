# Trí Tuệ Nhân Tạo - Minimax và Alpha–Beta cho TicTacToe n×n

Họ và tên: Trần Thị Kiều Diễm   MSSV: 2033230036

---

## Chương 1. Đọc Hiểu

### 1.1. Thuật toán Minimax cho TicTacToe n×n
#### 1.1.1. Mô tả bài toán
- Phát biểu: Tìm nước đi tối ưu trên bàn cờ n×n, giả định đối thủ chơi tối ưu.
- Input: Ma trận n×n chứa {X, O, EMPTY}, người chơi hiện tại; tùy chọn giới hạn độ sâu.
- Output: Nước đi tối ưu (hàng, cột) và điểm đánh giá: +1 (AI thắng), -1 (AI thua), 0 (hòa/không phân định nếu cắt sớm).

#### 1.1.2. Phát biểu hình thức
- Trạng thái S: ma trận n×n với X/O/EMPTY.
- Actions(s): tập ô trống; Result(s, a): đặt quân hiện tại vào ô a.
- Terminal(s): thắng (hàng, cột, chéo) hoặc hết ô trống.
- Utility(s): 1 nếu X thắng, -1 nếu O thắng, 0 nếu hòa.

#### 1.1.3. Phương pháp giải
- Duyệt cây trò chơi đến lá; MAX lấy max, MIN lấy min.
- Độ phức tạp: O(b^d) với b là branching factor, d là độ sâu.
- Thực tế: thêm `depth_limit` và heuristic trung gian cho bàn lớn để giảm thời gian.

#### 1.1.4. Đối tượng/hàm sử dụng
- Trạng thái bàn, hàm sinh nước đi, hàm kiểm tra thắng/thua/hòa, hàm đánh giá.
- Thuật toán: `minimax` (gọi đệ quy max_value, min_value).

### 1.2. Thuật toán Alpha–Beta cho TicTacToe n×n
#### 1.2.1. Mô tả bài toán
- Phát biểu: Như minimax, thêm cắt tỉa alpha–beta để giảm số nút duyệt.
- Input/Output: Giống minimax.

#### 1.2.2. Phương pháp giải
- Biến alpha: điểm tốt nhất của MAX; beta: điểm tốt nhất của MIN.
- Cắt nhánh khi `alpha >= beta`.
- Kết quả tối ưu như minimax; tốt nhất xấp xỉ O(b^(d/2)), tệ nhất O(b^d).
- Thứ tự duyệt nước “tốt” trước giúp cắt nhiều hơn.

#### 1.2.3. Đối tượng/hàm sử dụng
- Cùng bộ hàm của minimax; thêm tham số alpha, beta và điều kiện cắt.

---

## Chương 2. Lập Trình

### 2.1. Minimax (file `minimax.py`)
- Ngôn ngữ: Python, chơi tương tác trên PowerShell.
- Hỗ trợ bàn n×n; X luôn đi trước; cho phép nhập n và chọn quân X/O.
- Hàm chính: `minimax`, `max_value`, `min_value`; hàm tiện ích về trạng thái, nước đi, kiểm tra thắng.
- Chạy: `python minimax.py`, nhập n và quân cờ.

### 2.2. Alpha–Beta (file `alphabeta.py`)
- Ngôn ngữ: Python, chơi tương tác trên PowerShell.
- Bàn n×n, cắt tỉa alpha–beta, ưu tiên thắng nhanh/thua chậm qua tham số depth trong đánh giá.
- Hàm chính: `minimax_alpha_beta`, `find_best_move`; kèm hàm kiểm tra thắng, sinh nước đi.
- Chạy: `python alphabeta.py`, nhập n và quân cờ.

---

## Chương 3. Báo Cáo So Sánh Minimax vs Alpha–Beta

### 3.1. Điểm chung
- Trả về chiến lược tối ưu nếu duyệt đầy đủ.
- Cùng cần hàm sinh nước đi, hàm kết thúc, hàm đánh giá.
- Phụ thuộc thứ tự nước đi để hiệu quả hơn (đặc biệt với alpha–beta).

### 3.2. Khác biệt chính
- Độ phức tạp: Minimax O(b^d); Alpha–Beta tốt nhất ~O(b^(d/2)), tệ nhất O(b^d).
- Hiệu năng: Alpha–Beta mở rộng ít nút hơn nhờ cắt tỉa; lợi khi sắp xếp nước tốt.
- Cài đặt: Alpha–Beta thêm alpha, beta, điều kiện cắt; logic còn lại giữ khung minimax.

### 3.3. Bảng tóm tắt
- Tiêu chí | Minimax | Alpha–Beta
- Độ tối ưu | Tối ưu | Tối ưu
- Số nút duyệt | Nhiều | Ít hơn (cắt tỉa)
- Độ phức tạp | Đơn giản | Nhỉnh hơn
- Thực tế | Chậm khi d lớn | Nhanh hơn đáng kể
- Phù hợp | Bài nhỏ, demo | Bàn lớn hơn, cần tốc độ