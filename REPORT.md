# BÁO CÁO KẾT QUẢ THỰC HÀNH LAB 16
## Triển khai và Đo đạc hiệu năng môi trường Machine Learning CPU trên AWS

---

### I. THÔNG TIN HẠ TẦNG & LÝ DO ĐIỀU CHỈNH
*   **Môi trường mạng**: Mạng Private VPC cách ly hoàn toàn, giao tiếp bên ngoài qua Application Load Balancer (ALB) và Bastion Host.
*   **Dòng máy ảo (CPU Node)**: `m7i-flex.large` (2 vCPUs, 8 GiB RAM).
*   **Hệ điều hành**: Amazon Linux 2023 (`al2023-ami-*-x86_64`).
*   **Lý do chuyển sang phương án CPU**:
    Do tài khoản AWS mới bị áp dụng chính sách giới hạn nghiêm ngặt về nhóm tài nguyên (Service Quota GPU = 0 vCPU) và chỉ cho phép khởi tạo các dòng máy ảo nằm trong danh mục **Free Tier**. Để tránh bị gián đoạn bài học, mô hình Deep Learning/GPU đã được chuyển đổi sang bài toán Machine Learning cổ điển (phân loại giao dịch gian lận bằng thuật toán gradient boosting **LightGBM**) chạy trên instance CPU tối ưu chi phí là `m7i-flex.large`.

---

### II. ƯỚC TÍNH CHI PHÍ TỰ ĐỘNG (REGION: US-EAST-1)

Dưới đây là bảng phân tích chi phí ước tính dựa trên biểu giá chính thức của AWS tại khu vực `us-east-1` cho cả hai trường hợp: **Đang áp dụng Free Tier** và **Giá On-Demand tiêu chuẩn**.

| Tài nguyên / Dịch vụ | Cấu hình kỹ thuật | Đơn giá On-Demand | Chi phí thực tế (Free Tier) | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| **EC2 CPU Node** | `m7i-flex.large` (2 vCPUs, 8 GB RAM) | \$0.0862 / giờ | \$0.00 / giờ | Được áp dụng Free Tier đặc biệt cho một số tài khoản. |
| **EC2 Bastion Host** | `t3.micro` (2 vCPUs, 1 GB RAM) | \$0.0104 / giờ | \$0.00 / giờ | Miễn phí tối đa 750 giờ/tháng. |
| **NAT Gateway** | 1 cổng tại Public Subnet | \$0.0450 / giờ | \$0.0450 / giờ | Không thuộc diện Free Tier. Tính phí cố định từ khi tạo. |
| **Application Load Balancer**| 1 ALB tiếp nhận traffic cổng 80 | \$0.0225 / giờ | \$0.0225 / giờ | Không thuộc diện Free Tier. |
| **EBS Storage (GPU Node)** | 150 GB SSD gp3 | \$0.0167 / giờ | \$0.0133 / giờ | Hỗ trợ 30 GB miễn phí, chỉ tính phí phần vượt hạn mức. |
| **EBS Storage (Bastion)** | 8 GB SSD gp3 | \$0.0009 / giờ | \$0.00 / giờ | Nằm trong hạn mức 30 GB miễn phí. |
| **Tổng chi phí ước tính** | | **~\$0.1817 / giờ** | **~\$0.0808 / giờ** | **Rất rẻ và tối ưu ngân sách thực hành.** |

> **⚠️ Khuyến cáo**: Dù chạy CPU hay GPU, chi phí cố định của NAT Gateway và ALB vẫn phát sinh liên tục theo giờ. Cần chạy `terraform destroy` ngay sau khi nộp bài để tránh phát sinh chi phí ngoài ý muốn.

---

### III. KẾT QUẢ ĐO ĐẠC HIỆU NĂNG (BENCHMARK RESULTS)

Mô hình đã được thử nghiệm với tập dữ liệu thực tế **Credit Card Fraud Detection** từ Kaggle (gồm 284,807 dòng giao dịch, 30 đặc trưng kỹ thuật số).

#### 1. Thời gian xử lý & Huấn luyện (Training Performance)
*   **Thời gian tải dữ liệu (Load Time)**: **1.0780 giây**
*   **Thời gian huấn luyện (Training Time - 100 rounds)**: **3.0353 giây**
*   **Số lượng dòng xử lý**: 284,807 dòng dữ liệu.

#### 2. Độ chính xác của mô hình (Evaluation Metrics)
Do tập dữ liệu mất cân bằng nghiêm trọng (giao dịch gian lận chiếm tỷ lệ rất nhỏ), các chỉ số được đo đạc chặt chẽ như sau:
*   **AUC-ROC**: **0.806111** (Mức độ phân biệt giữa giao dịch sạch và giao dịch gian lận ở mức tốt).
*   **Accuracy (Độ chính xác toàn cục)**: **99.8455%**
*   **Precision (Độ chuẩn xác)**: **54.3860%** (Trong số các giao dịch mô hình cảnh báo gian lận, có 54.38% là thực sự gian lận).
*   **Recall (Độ phủ)**: **63.2653%** (Mô hình phát hiện được 63.26% tổng số vụ gian lận thực tế).
*   **F1-Score**: **0.584906**

#### 3. Tốc độ dự báo (Inference Latency & Throughput)
*   **Độ trễ dự báo đơn lẻ (Inference Latency - 1 dòng)**: **0.1996 ms** (mili-giây).
*   **Băng thông xử lý (Throughput - Lô 1000 dòng)**: **429,674.26 dòng/giây**.

---

### IV. NHẬN XÉT VÀ ĐÁNH GIÁ CHI TIẾT
1.  **Về tốc độ huấn luyện**: Thuật toán LightGBM khi huấn luyện trên CPU `m7i-flex.large` cho tốc độ cực kỳ ấn tượng, chỉ mất hơn **3 giây** để hoàn thành 100 vòng lặp trên gần 285,000 dòng dữ liệu. Điều này chứng minh rằng với các tập dữ liệu dạng bảng (tabular data), việc sử dụng thuật toán tối ưu hóa cây quyết định trên CPU đa nhân mang lại hiệu quả chi phí và thời gian huấn luyện vượt trội so với việc thiết lập và khởi động một hệ thống Deep Learning trên GPU đắt đỏ.
2.  **Về tốc độ dự báo (Inference Speed)**: Độ trễ phản hồi chỉ **~0.2 ms** cho mỗi giao dịch cùng với băng thông xử lý lên đến **~430,000 giao dịch/giây** chứng tỏ hệ thống hoàn toàn đủ khả năng triển khai thực tế vào các hệ thống phát hiện gian lận thời gian thực (real-time transaction scoring), đáp ứng tốt các yêu cầu khắt khe về mặt thời gian phản hồi của ngành tài chính/ngân hàng.
3.  **Về mức độ khả thi**: Việc tận dụng instance CPU Free Tier (`m7i-flex.large`) thay vì GPU vừa giúp sinh viên hoàn thành đầy đủ các tiêu chí thực hành hạ tầng đám mây (Cloud Infrastructure Setup, VPC, Route Table, NAT, Security Group, ALB, Bastion Host) vừa kiểm soát chi phí thực hành ở mức cực kỳ thấp (~0.08 USD/giờ) so với việc sử dụng GPU (~0.60 USD/giờ).
