# Trí Tuệ Nhân Tạo - Thuật Giải A* (AKT) và A* cho Đồ Thị

**Họ và tên:** Trần Thị Kiều Diễm 
**MSSV:** 2033230036

---

## Chương 1. Đọc Hiểu

### 1.1. Thuật Giải AKT (A*) cho 15 Puzzle

#### 1.1.1. Mô Tả Bài Toán

##### 1.1.1.1. Phát Biểu Bài Toán

Xây dựng thuật toán AKT (A* với heuristic tối ưu) để giải bài toán 15 Puzzle như sau: Thuật toán này sử dụng cây tìm kiếm để:

- Duyệt tất cả các trạng thái có thể từ trạng thái ban đầu
- Đánh giá giá trị của mỗi trạng thái dựa trên hàm heuristic (Manhattan distance)
- Chọn nước đi mang lại đường đi tối ưu từ trạng thái ban đầu đến trạng thái đích
- Tìm số bước di chuyển tối thiểu để giải puzzle

15 Puzzle là một bài toán trò chơi xếp hình dạng lưới 4x4 (n=4) với 15 mảnh đánh số từ 1 đến 15 và một ô trống. Mục tiêu là sắp xếp các mảnh từ trạng thái ban đầu về trạng thái đích bằng cách di chuyển các mảnh vào ô trống.

##### 1.1.1.2. Input

**initial_state:** Ma trận 4×4 biểu diễn trạng thái ban đầu của puzzle

- Ô chứa: Số từ 1 đến 15, hoặc 0 (ô trống)
- Ví dụ:
```python
[[1, 2, 3, 4],
 [5, 6, 7, 8],
 [9, 10, 11, 12],
 [13, 14, 0, 15]]
```

**final_state (trạng thái đích):** Ma trận 4×4 mục tiêu
```python
[[1, 2, 3, 4],
 [5, 6, 7, 8],
 [9, 10, 11, 12],
 [13, 14, 15, 0]]
```

##### 1.1.1.3. Output

**Output từ Hàm solve():**

- In ra đường đi từ trạng thái ban đầu đến trạng thái đích (từng bước di chuyển)
- Số bước di chuyển tối thiểu
- Số lượng trạng thái đã được duyệt

**Output Trạng Thái Kết Thúc:**

- Khi tìm thấy lời giải: In ra các trạng thái trung gian và trạng thái đích
- Khi không giải được: Thông báo "Không giải được" nếu trạng thái ban đầu không có lời giải

**Ví dụ Output (Thành Công):**
```
1  2  3  4  
5  6  7  8  
9 10 11 12  
13 14  . 15  

1  2  3  4  
5  6  7  8  
9 10 11 12  
13 14 15  .  

So buoc: 1
So trang thai da duyet: 2
```

#### 1.1.2. Phương Pháp Giải Quyết Bài Toán

**Bước 1: Khởi Tạo**

- Khởi tạo priority queue (open_lst) với node ban đầu
- Tính G = 0 (chi phí từ trạng thái ban đầu)
- Tính H = heuristic(state) (Manhattan distance đến trạng thái đích)
- Tính F = G + H (hàm đánh giá tổng)
- Khởi tạo visited set (closed_lst) rỗng
- Khởi tạo parent map để truy vết

**Bước 2: Kiểm Tra Tính Giải Được**

   - Đếm số inversion (cặp mảnh đảo ngược thứ tự)
   - Tính vị trí hàng của ô trống từ dưới lên
   - 15 Puzzle giải được nếu: (số inversion + vị trí hàng ô trống) là số chẵn
- Nếu không giải được → Dừng, thông báo "Không giải được"
- Nếu giải được → Tiếp tục Bước 3

**Bước 3: Vòng Lặp Chính (A*)**

Thực hiện vòng lặp với các bước sau:

**Bước 3.1: Lấy Node Từ Priority Queue**

- Lấy node có F nhỏ nhất từ priority queue (open_lst)
- Nếu open_lst rỗng → Không tìm thấy lời giải, dừng
- Nếu có node → Tiếp tục Bước 3.2

**Bước 3.2: Kiểm Tra Trạng Thái Đích**

- So sánh state hiện tại với trạng thái đích
- Nếu là trạng thái đích:
  - Truy vết đường đi từ node hiện tại về root bằng parent map
  - In ra đường đi (các trạng thái trung gian)
  - Trả về số bước và số trạng thái đã duyệt
- Nếu chưa phải đích → Tiếp tục Bước 3.3

**Bước 3.3: Đánh Dấu Đã Xét**

- Thêm node hiện tại vào closed_lst (visited set)
- Tăng biến đếm số trạng thái đã duyệt
- Tiếp tục Bước 3.4

**Bước 3.4: Sinh Các Trạng Thái Con**

Với vị trí ô trống hiện tại (row, col), sinh 4 trạng thái con có thể:

- **Di chuyển lên (UP):** Nếu row > 0
  - Hoán đổi ô trống với ô phía trên
  - Tạo node mới với G_new = G + 1
  
- **Di chuyển xuống (DOWN):** Nếu row < 3
  - Hoán đổi ô trống với ô phía dưới
  - Tạo node mới với G_new = G + 1
  
- **Di chuyển trái (LEFT):** Nếu col > 0
  - Hoán đổi ô trống với ô bên trái
  - Tạo node mới với G_new = G + 1
  
- **Di chuyển phải (RIGHT):** Nếu col < 3
  - Hoán đổi ô trống với ô bên phải
  - Tạo node mới với G_new = G + 1

**Bước 3.5: Xử Lý Các Node Con**

Với mỗi node con được sinh ra:

- **Bước 3.5.1:** Kiểm tra node con đã trong closed_lst chưa
  - Nếu đã xét → Bỏ qua node này
  - Nếu chưa xét → Tiếp tục Bước 3.5.2

- **Bước 3.5.2:** Tính toán giá trị cho node con
  - G_new = G_current + 1
  - H_new = calculateCosts(state_new, final) (Manhattan distance)
  - F_new = G_new + H_new
  - Lưu parent = node hiện tại

- **Bước 3.5.3:** Kiểm tra node con trong open_lst
  - Nếu chưa trong open_lst: Thêm vào open_lst
  - Nếu đã trong open_lst: Kiểm tra đường đi tốt hơn
    - Nếu G_new < G_old: Cập nhật G, H, F và parent
    - Nếu không tốt hơn: Giữ nguyên

**Bước 3.6: Quay Lại Bước 3.1**

- Quay lại Bước 3.1 để tiếp tục vòng lặp
- Lặp lại cho đến khi tìm thấy đích hoặc open_lst rỗng

#### 1.1.3. Xác Định Các Đối Tượng Được Sử Dụng

##### 1.1.3.1. Bước 1: Khởi Tạo

**Class priorityQueue**

- **Input:** Không
- **Output:** Priority queue object
- **Chức năng:** 
  - Tạo hàng đợi ưu tiên để lưu trữ các node
  - Push: Thêm node vào queue
  - Pop: Lấy node có F nhỏ nhất
  - Empty: Kiểm tra queue rỗng

**Class nodes**

- **Input:** 
  - parent: Node cha
  - mats: Ma trận trạng thái hiện tại
  - empty_tile_posi: Vị trí ô trống [row, col]
  - costs: Giá trị heuristic H
  - levels: Số bước đã đi (G)
- **Output:** Node object
- **Chức năng:** 
  - Lưu trữ thông tin trạng thái
  - So sánh nodes dựa trên costs (F = G + H)
  - Hỗ trợ truy vết đường đi qua parent

##### 1.1.3.2. Bước 2: Kiểm Tra Tính Giải Được

**Hàm count_inversions(state)**

- **Input:** state (Ma trận 4×4)
- **Output:** Số inversion (số cặp đảo ngược)
- **Chức năng:** Đếm số cặp mảnh đảo ngược thứ tự trong trạng thái (bỏ qua ô trống)

**Hàm is_solvable(state)**

- **Input:** state (Ma trận 4×4)
- **Output:** True hoặc False
- **Chức năng:** 
  - Gọi count_inversions() để đếm inversion
  - Tìm vị trí hàng của ô trống từ dưới lên
  - Kiểm tra: (inversions + blank_row) % 2 == 0
  - Trả về True nếu giải được, False nếu không

##### 1.1.3.3. Bước 3: Thuật Toán A*

**Hàm calculateCosts(mats, final)**

- **Input:** 
  - mats: Ma trận trạng thái hiện tại
  - final: Ma trận trạng thái đích
- **Output:** Manhattan distance (số nguyên)
- **Chức năng:** 
  - Với mỗi mảnh (khác 0), tính khoảng cách Manhattan từ vị trí hiện tại đến vị trí đích
  - Tổng tất cả khoảng cách Manhattan
  - Trả về giá trị heuristic H

**Hàm newNodes(mats, empty_tile_posi, new_empty_tile_posi, levels, parent, final)**

- **Input:**
  - mats: Ma trận trạng thái hiện tại
  - empty_tile_posi: Vị trí ô trống hiện tại
  - new_empty_tile_posi: Vị trí ô trống mới
  - levels: Số bước (G)
  - parent: Node cha
  - final: Ma trận trạng thái đích
- **Output:** Node mới
- **Chức năng:**
  - Copy ma trận hiện tại
  - Hoán đổi ô trống với ô tại vị trí mới
  - Tính costs (heuristic) bằng calculateCosts()
  - Tạo và trả về node mới

**Hàm isSafe(x, y)**

- **Input:** x, y (tọa độ)
- **Output:** True hoặc False
- **Chức năng:** Kiểm tra tọa độ (x, y) có hợp lệ trong ma trận 4×4 không (0 ≤ x, y < 4)

**Hàm printMatrix(mats)**

- **Input:** mats (Ma trận 4×4)
- **Output:** Không (chỉ in ra màn hình)
- **Chức năng:** In ma trận dưới dạng 4×4, ô trống (0) hiển thị là "."

**Hàm printPath(root)**

- **Input:** root (Node gốc)
- **Output:** Không (chỉ in ra màn hình)
- **Chức năng:**
  - Đệ quy in đường đi từ root đến node hiện tại
  - In từng trạng thái trong đường đi

**Hàm solve(initial, empty_tile_posi, final)**

- **Input:**
  - initial: Ma trận trạng thái ban đầu
  - empty_tile_posi: Vị trí ô trống ban đầu [row, col]
  - final: Ma trận trạng thái đích
- **Output:** Không (chỉ in kết quả)
- **Chức năng:**
  - Khởi tạo priority queue với node ban đầu
  - Vòng lặp chính:
    - Lấy node có F nhỏ nhất
    - Kiểm tra trạng thái đích
    - Sinh các node con
    - Cập nhật open_lst và closed_lst
  - In kết quả khi tìm thấy đích

---

### 1.2. Thuật Giải A* cho Đồ Thị

#### 1.2.1. Mô Tả Bài Toán

##### 1.2.1.1. Phát Biểu Bài Toán

Xây dựng thuật toán A* để tìm đường đi ngắn nhất giữa 2 đỉnh trong đồ thị có trọng số như sau: Thuật toán này sử dụng cây tìm kiếm để:

- Duyệt tất cả các đỉnh có thể từ đỉnh nguồn
- Đánh giá giá trị của mỗi đỉnh dựa trên hàm heuristic (Euclidean, Manhattan, hoặc tùy chỉnh)
- Chọn đường đi mang lại chi phí nhỏ nhất từ đỉnh nguồn đến đỉnh đích
- Tìm đường đi tối ưu với thời gian nhanh hơn so với các thuật toán tìm kiếm đơn giản

##### 1.2.1.2. Input

**adjac_lis:** Dictionary biểu diễn đồ thị dưới dạng danh sách kề

- Key: Tên đỉnh (string)
- Value: List các tuple (đỉnh kề, trọng số)
- Ví dụ:
```python
{
    'A': [('B', 1), ('C', 3), ('D', 7)],
    'B': [('D', 5)],
    'C': [('D', 12)],
    'D': []
}
```

**start:** Đỉnh nguồn (string)

- Ví dụ: 'A'

**stop:** Đỉnh đích (string)

- Ví dụ: 'D'

**positions (tùy chọn):** Dictionary lưu tọa độ các đỉnh để tính heuristic

- Key: Tên đỉnh
- Value: Tuple (x, y)
- Ví dụ: `{'A': (0, 0), 'B': (1, 1), 'D': (3, 2)}`

##### 1.2.1.3. Output

**Output từ Hàm a_star_algorithm():**

- In ra đường đi từ start đến stop
- In ra tổng chi phí của đường đi

**Ví dụ Output (Thành Công):**
```
Path found: ['A', 'B', 'D']
Total cost: 6
```

**Output Trạng Thái Kết Thúc:**

- Khi tìm thấy đường đi: In ra danh sách đỉnh và tổng chi phí
- Khi không tìm thấy đường đi: Thông báo "Path does not exist!"

#### 1.2.2. Phương Pháp Giải Quyết Bài Toán

**Bước 1: Khởi Tạo**

- Khởi tạo open_lst (set) chứa đỉnh nguồn (start)
- Khởi tạo closed_lst (set) rỗng
- Khởi tạo poo (dictionary) lưu chi phí từ start: poo[start] = 0
- Khởi tạo par (dictionary) lưu parent: par[start] = start
- Tiếp tục Bước 2

**Bước 2: Vòng Lặp Chính (A*)**

Thực hiện vòng lặp với các bước sau:

**Bước 2.1: Tìm Đỉnh Có F Nhỏ Nhất**

- Duyệt tất cả đỉnh trong open_lst
- Tính F = poo[v] + h(v, stop) cho mỗi đỉnh
- Chọn đỉnh n có F nhỏ nhất
- Nếu không tìm thấy (n == None) → Không có đường đi, dừng
- Nếu tìm thấy → Tiếp tục Bước 2.2

**Bước 2.2: Kiểm Tra Đỉnh Đích**

- So sánh n với stop
- Nếu n == stop:
  - Truy vết đường đi từ stop về start bằng par map
  - Tạo danh sách reconst_path
  - Đảo ngược danh sách để có đường đi từ start đến stop
  - In kết quả và trả về
- Nếu chưa phải đích → Tiếp tục Bước 2.3

**Bước 2.3: Xử Lý Các Đỉnh Kề**

Với mỗi đỉnh kề (m, weight) của n:

- **Bước 2.3.1:** Kiểm tra đỉnh kề
  - Nếu m đã trong closed_lst → Bỏ qua
  - Nếu m chưa trong closed_lst → Tiếp tục Bước 2.3.2

- **Bước 2.3.2:** Tính toán chi phí mới
  - tentative_g = poo[n] + weight
  
- **Bước 2.3.3:** Xử lý đỉnh kề
  - **Nếu m chưa trong open_lst và closed_lst:**
    - Thêm m vào open_lst
    - Lưu parent: par[m] = n
    - Lưu chi phí: poo[m] = tentative_g
  
  - **Nếu m đã trong open_lst hoặc closed_lst:**
    - Kiểm tra: poo[m] > tentative_g?
    - Nếu tốt hơn:
      - Cập nhật: poo[m] = tentative_g
      - Cập nhật: par[m] = n
      - Nếu m trong closed_lst: Di chuyển m từ closed_lst sang open_lst

**Bước 2.4: Đánh Dấu Đã Xét**

- Loại bỏ n khỏi open_lst
- Thêm n vào closed_lst
- Tiếp tục Bước 2.1

**Bước 2.5: Kết Thúc**

- Nếu open_lst rỗng và chưa tìm thấy đích → Không có đường đi
- In "Path does not exist!" và trả về None

#### 1.2.3. Xác Định Các Đối Tượng Được Sử Dụng

##### 1.2.3.1. Bước 1: Khởi Tạo

**Class Graph**

- **Input:** adjac_lis (Dictionary danh sách kề)
- **Output:** Graph object
- **Chức năng:** 
  - Lưu trữ cấu trúc đồ thị
  - Quản lý tọa độ các đỉnh (nếu có) để tính heuristic

**Hàm __init__(self, adjac_lis)**

- **Input:** adjac_lis (Dictionary)
- **Output:** Không
- **Chức năng:** Khởi tạo đồ thị với danh sách kề và dictionary positions rỗng

**Hàm set_position(self, vertex, x, y)**

- **Input:**
  - vertex: Tên đỉnh (string)
  - x, y: Tọa độ (float)
- **Output:** Không
- **Chức năng:** Thiết lập tọa độ của đỉnh để tính heuristic Euclidean hoặc Manhattan

##### 1.2.3.2. Bước 2: Thuật Toán A*

**Hàm get_neighbors(self, v)**

- **Input:** v (Tên đỉnh - string)
- **Output:** List các tuple (đỉnh kề, trọng số)
- **Chức năng:** Trả về danh sách các đỉnh kề và trọng số cạnh của đỉnh v

**Hàm h(self, n, goal=None)**

- **Input:**
  - n: Tên đỉnh (string)
  - goal: Tên đỉnh đích (string, tùy chọn)
- **Output:** Giá trị heuristic (float)
- **Chức năng:**
  - Nếu có goal và cả n, goal đều có tọa độ: Tính Euclidean distance
  - Nếu không: Trả về giá trị heuristic mặc định (0 hoặc giá trị trong dictionary H)
  - Hỗ trợ nhiều loại heuristic tùy chỉnh

**Hàm a_star_algorithm(self, start, stop)**

- **Input:**
  - start: Đỉnh nguồn (string)
  - stop: Đỉnh đích (string)
- **Output:** Danh sách đỉnh từ start đến stop (hoặc None nếu không tìm thấy)
- **Chức năng:**
  - Khởi tạo open_lst, closed_lst, poo, par
  - Vòng lặp chính:
    - Tìm đỉnh có F nhỏ nhất trong open_lst
    - Kiểm tra đỉnh đích
    - Xử lý các đỉnh kề
    - Cập nhật open_lst và closed_lst
  - Truy vết và in kết quả

##### 1.2.3.3. Bước 3: Test Cases

**Hàm main()**

- **Input:** Không (chạy trực tiếp)
- **Output:** Không (chỉ in kết quả)
- **Chức năng:**
  - Tạo các đồ thị test
  - Gọi a_star_algorithm() cho các test cases
  - In kết quả ra màn hình

**Test Case 1: Đồ thị từ ảnh**

- Đồ thị: A → B (1), A → C (3), A → D (7), B → D (5), C → D (12)
- Tìm đường từ A đến D
- Kết quả mong đợi: ['A', 'B', 'D'] với cost = 6

**Test Case 2: Đồ thị dạng lưới**

- Đồ thị lưới 3×3 với các cạnh có trọng số 1.0
- Tìm đường từ A đến I
- Kiểm tra thuật toán với đồ thị có cấu trúc đặc biệt

**Test Case 3: Đồ thị không liên thông**

- Đồ thị có 2 thành phần liên thông riêng biệt
- Tìm đường giữa 2 đỉnh không liên thông
- Kiểm tra xử lý trường hợp không có đường đi

---

**Độ Phức Tạp:**

- **Thời gian:** O(b^d) với b là branching factor (số đỉnh kề trung bình), d là độ sâu tìm kiếm
- **Không gian:** O(b^d) để lưu trữ các node trong open_lst và closed_lst
- **Với heuristic tốt:** Độ phức tạp có thể giảm đáng kể so với tìm kiếm mù
