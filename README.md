# Quản Lý Đồ Thị (Graph Master)

**Quản Lý Đồ Thị** là một ứng dụng giao diện đồ họa (GUI) hiện đại để trực quan hóa và xử lý các thuật toán đồ thị. Ứng dụng được xây dựng bằng Python và thư viện `customtkinter`, hỗ trợ vẽ đồ thị tương tác và chạy các thuật toán phổ biến.

## ✨ Tính Năng Chính

*   **Giao Diện Tiếng Việt**: Thân thiện, dễ sử dụng với chế độ tối (Dark Mode).
*   **Vẽ Đồ Thị Tương Tác**:
    *   **Thêm Đỉnh**: Nhấn chuột trái vào vùng trống.
    *   **Thêm Cạnh**: Nhấn chuột trái vào một đỉnh để chọn (viền vàng), sau đó nhấn vào đỉnh khác để nối.
    *   **Chỉnh Sửa**: Nhấn chuột phải vào Đỉnh để đổi tên, hoặc nhấn chuột phải vào Cạnh để thay đổi trọng số.
*   **Thuật Toán Đa Dạng**: Hỗ trợ khung sườn cho BFS, DFS, Dijkstra, Prim, Kruskal, Ford-Fulkerson, Fleury, Hierholzer.
*   **Tiện Ích**:
    *   Tạo đồ thị ngẫu nhiên.
    *   Lưu/Đọc đồ thị từ file.
    *   Xem biểu diễn dưới dạng Ma trận kề/Danh sách kề.
    *   Nhật ký hoạt động (Log Console) chi tiết.

## 🛠️ Cài Đặt

1.  **Yêu cầu**: Python 3.x.
2.  **Cài đặt thư viện**:
    ```bash
    pip install customtkinter
    ```

## 🚀 Hướng Dẫn Chạy

Từ thư mục gốc của dự án (`d:\BTL_CTRR`), chạy lệnh:

```bash
python main/main.py
```

## 📂 Cấu Trúc Dự Án

Dự án được tổ chức theo mô hình module hóa để dễ dàng quản lý và phát triển nhóm:

```
BTL_CTRR/
├── main/                   # Chứa mã nguồn chính của ứng dụng
│   ├── main.py             # Controller: Điểm bắt đầu, xử lý sự kiện chính
│   ├── app_ui.py           # View: Cấu hình giao diện, nút bấm, bố cục
│   └── graph_objects.py    # Model: Định nghĩa lớp Node (Đỉnh) và Edge (Cạnh)
│
├── algorithms/             # Chứa logic các thuật toán (Skeleton code)
│   ├── algo_traversal.py   # BFS, DFS, Kiểm tra đồ thị 2 phía
│   ├── algo_opt.py         # Dijkstra, Prim, Kruskal, Ford-Fulkerson
│   └── algo_euler.py       # Fleury, Hierholzer
│
├── data/                   # Xử lý dữ liệu và tiện ích
│   ├── data_handler.py     # Lưu/Đọc file JSON, chuyển đổi ma trận/danh sách kề
│   └── generator.py        # Thuật toán sinh đồ thị ngẫu nhiên
│
└── README.md               # Tài liệu hướng dẫn
```

## 👥 Phân Công (Gợi ý)

*   **Thành viên 1**: Phát triển GUI (`main/`) - *Đã hoàn thành cơ bản*.
*   **Thành viên 2**: Cài đặt `algorithms/algo_traversal.py` (BFS, DFS, Bipartite).
*   **Thành viên 3**: Cài đặt `algorithms/algo_opt.py` (Dijkstra, Prim, Kruskal, Max Flow).
*   **Thành viên 4**: Cài đặt `data/data_handler.py` và hiển thị ma trận.
*   **Thành viên 5**: Cài đặt `data/generator.py` (Random Graph) và Lưu/Đọc file.
*   **Thành viên 6**: Cài đặt `algorithms/algo_euler.py` (Fleury, Hierholzer).

---
*Bài Tập Lớn - Cấu Trúc Rời Rạc*
