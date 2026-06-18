# HƯỚNG DẪN THỰC HÀNH LAB 16: CLOUD AI ENVIRONMENT SETUP
### Sinh viên thực hiện: Trần Quốc Khánh (MSSV: 2A202600679)

---

## 📌 Giới thiệu dự án
Bài thực hành thực hiện thiết lập hạ tầng mạng bảo mật **Private VPC** trên điện toán đám mây **AWS** bằng công cụ Infrastructure as Code (**Terraform**). 

Do tài khoản học viên bị giới hạn chính sách Free Tier không thể sử dụng máy ảo GPU (`g4dn.xlarge`), dự án đã chuyển đổi thành công sang phương án chạy máy ảo CPU cao cấp (`m7i-flex.large`) và huấn luyện mô hình **LightGBM** trên tập dữ liệu phát hiện giao dịch gian lận (**Credit Card Fraud Detection**) với 284,807 dòng.

---

## 📁 Cấu trúc các tài liệu & Báo cáo
*   **[REPORT.md](REPORT.md)**: Báo cáo kết quả chi tiết, thống kê thời gian huấn luyện, độ chính xác mô hình, và bảng phân tích ước tính chi phí tự động trên AWS.
*   **[benchmark.py](benchmark.py)**: Mã nguồn Python thực hiện tiền xử lý dữ liệu, huấn luyện LightGBM và đo đạc độ trễ inference.
*   **[benchmark_result.json](benchmark_result.json)**: Tệp kết quả lưu trữ các tham số đo đạc hiệu năng sau khi chạy benchmark.
*   **[README_aws.md](README_aws.md)**: Tài liệu hướng dẫn chi tiết thực hành hạ tầng trên AWS.
*   **[README_gcp.md](README_gcp.md)**: Tài liệu hướng dẫn chi tiết thực hành hạ tầng trên GCP.

---

## 🖼️ Thư mục Minh chứng Bài làm (`minh_chung_bai_lam/`)
Toàn bộ hình ảnh kết quả kiểm thử và quản trị tài nguyên AWS được lưu trữ tại thư mục **[minh_chung_bai_lam](minh_chung_bai_lam/)**:

1.  **Ảnh chụp chạy Benchmark**: [benchmark.png](minh_chung_bai_lam/benchmark.png)
    *   *Mô tả*: Kết quả chạy script `python3 benchmark.py` huấn luyện mô hình LightGBM trên CPU Node.
2.  **Ảnh chụp kết quả JSON**: [benchmark_json.png](minh_chung_bai_lam/benchmark_json.png)
    *   *Mô tả*: Nội dung file `benchmark_result.json` chứa các chỉ số đo đạc.
3.  **Ảnh chụp quản lý EC2 Instances**: [intance.png](minh_chung_bai_lam/intance.png)
    *   *Mô tả*: Trạng thái hoạt động của CPU Node và Bastion Host trên AWS Web Console.
4.  **Ảnh chụp hóa đơn chi phí AWS (AWS Billing)**: [cost.png](minh_chung_bai_lam/cost.png)
    *   *Mô tả*: Thống kê chi phí của các tài nguyên phát sinh trong lab.
5.  **Log chi tiết các lệnh thực thi**: [AAIK20_aithucchienTrack2Day16.txt](minh_chung_bai_lam/AAIK20_aithucchienTrack2Day16.txt)
