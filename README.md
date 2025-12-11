# Graph Master

**Graph Master** là một ứng dụng giao diện đồ họa (GUI) hiện đại, chuyên nghiệp để trực quan hóa các thuật toán đồ thị. Ứng dụng được xây dựng bằng Python và thư viện `customtkinter`, mang lại trải nghiệm người dùng mượt mà với giao diện Dark Mode.

## ✨ Tính Năng Chính

*   **Giao Diện Hiện Đại**: Thiết kế Dashboard chuyên nghiệp với tông màu tối (Dark Mode) và điểm nhấn màu xanh (Blue Theme).
*   **Vẽ Đồ Thị Tương Tác**:
    *   **Thêm Nút (Node)**: Nhấn chuột trái vào vùng trống.
    *   **Thêm Cạnh (Edge)**: Nhấn chuột trái vào một nút để chọn (highlight vàng), sau đó nhấn vào nút khác để nối. Cạnh có mũi tên chỉ hướng.
    *   **Chỉnh Sửa**: Nhấn chuột phải vào Nút để đổi tên, hoặc nhấn chuột phải vào Cạnh (số trọng số) để thay đổi trọng số.
*   **Tạo Đồ Thị Ngẫu Nhiên**: Tính năng tự động sinh ra một đồ thị ngẫu nhiên với các nút và liên kết để kiểm thử nhanh.
*   **Log Console**: Bảng nhật ký hiển thị chi tiết các thao tác và bước chạy của thuật toán theo thời gian thực.
*   **Hỗ Trợ Thuật Toán**: Các nút chức năng sẵn sàng cho việc tích hợp BFS, DFS, Dijkstra, và Prim.

## 🛠️ Cài Đặt

1.  **Yêu cầu**: Máy tính đã cài đặt Python 3.x.
2.  **Cài đặt thư viện**:
    Mở terminal và chạy lệnh sau để cài đặt `customtkinter`:
    ```bash
    pip install customtkinter
    ```

## 🚀 Hướng Dẫn Sử Dụng

1.  **Chạy ứng dụng**:
    Từ thư mục gốc của dự án, chạy lệnh:
    ```bash
    python main/main.py
    ```

2.  **Thao tác chuột**:
    *   **Chuột Trái (Left Click)**:
        *   Click vào vùng trống: Tạo nút mới.
        *   Click vào nút: Chọn nút (để chuẩn bị nối cạnh).
    *   **Chuột Phải (Right Click)**:
        *   Click vào Nút: Đổi tên nút.
        *   Click vào Cạnh (số trọng số): Đổi trọng số.

3.  **Chức năng trên thanh công cụ**:
    *   **Algorithms**: Chạy các thuật toán (BFS, DFS, v.v.).
    *   **Random Graph**: Tạo mới một đồ thị ngẫu nhiên.
    *   **Clear Canvas**: Xóa toàn bộ màn hình vẽ.
    *   **Clear Log**: Xóa lịch sử nhật ký.

## 📂 Cấu Trúc Dự Án

```
BTL_CTRR/
├── main/
│   └── main.py       # Mã nguồn chính của ứng dụng (GUI, Logic)
├── algorithms/       # (Dự kiến) Chứa các file cài đặt thuật toán
└── README.md         # Hướng dẫn sử dụng
```

---
*Dự án BTL_CTRR - Graph Master*