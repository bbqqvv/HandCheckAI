
# 📐 Ứng Dụng Đo Góc Bàn Tay - README

## 📌 Tổng Quan

Ứng dụng này cung cấp khả năng đo góc bàn tay nâng cao bằng cách sử dụng thị giác máy tính và thư viện MediaPipe. Nó có thể phát hiện bàn tay trong ảnh, tính toán các góc khác nhau (độ nghiêng lòng bàn tay, góc ngón tay), và cung cấp phân tích chi tiết về tư thế tay.

## ✨ Tính Năng Chính

* **Phát hiện nhiều bàn tay**: Có thể phát hiện và phân tích tối đa 2 bàn tay cùng lúc
* **Đo góc toàn diện**:

  * Góc nghiêng của lòng bàn tay (theo phương dọc)
  * Góc xoay của lòng bàn tay (theo phương ngang)
  * Góc riêng biệt của từng ngón tay (ngón cái, trỏ, giữa, áp út, út)
* **Xử lý ảnh nâng cao**: Sử dụng CLAHE, lọc song phương và làm sắc nét để cải thiện khả năng phát hiện
* **Hiển thị trực quan**: Hiển thị các điểm mốc và thông tin góc trên ảnh
* **Xuất dữ liệu**: Lưu các phép đo vào tệp Excel với định dạng có điều kiện
* **Giao diện thân thiện**: Giao diện dạng tab với các bảng kết quả và lịch sử

## 🛠️ Chi Tiết Kỹ Thuật

* **Thị giác máy tính**: Sử dụng MediaPipe Hands để phát hiện điểm mốc
* **Xử lý ảnh**: Dùng OpenCV để tiền xử lý và tăng cường ảnh
* **Giao diện người dùng**: Tkinter với các widget ttk cho giao diện hiện đại
* **Xuất dữ liệu**: Sử dụng OpenPyXL để tạo báo cáo Excel
* **Xử lý lỗi**: Bắt lỗi toàn diện và hiển thị thông báo rõ ràng cho người dùng

## 🚀 Cách Sử Dụng

1. **Tải ảnh**: Nhấn "Open Images" để chọn một hoặc nhiều ảnh tay
2. **Xử lý ảnh**: Nhấn "Process All" để phân tích tất cả các ảnh đã tải
3. **Xem kết quả**:

   * Xem bàn tay được phát hiện với điểm mốc và góc
   * Kiểm tra các phép đo chi tiết trong tab Kết quả
   * Xem lại lịch sử xử lý trong tab Lịch sử
4. **Lưu dữ liệu**: Xuất tất cả kết quả đo ra file Excel bằng "Save Results"
5. **Điều hướng**: Dùng phím mũi tên hoặc nút điều hướng để xem ảnh

## ⚙️ Yêu Cầu Hệ Thống

* Python 3.7 trở lên
* Các gói cần thiết:

  ```
  opencv-python
  mediapipe
  pillow
  openpyxl
  numpy
  ```

## 🏗️ Cấu Trúc Mã Nguồn

* `EnhancedHandTracker`: Logic chính cho phát hiện tay và tính toán góc
* `HandAngleApp`: Lớp chính của ứng dụng, chứa giao diện và quy trình
* Các phương thức quan trọng:

  * `process_frame()`: Quy trình xử lý ảnh chính
  * `calculate_palm_orientation()`: Tính góc lòng bàn tay
  * `calculate_finger_angles()`: Đo góc từng ngón tay
  * `advanced_preprocess()`: Tăng cường chất lượng ảnh để nhận diện tốt hơn

## 💡 Mẹo Để Có Kết Quả Tốt Nhất

* Sử dụng ảnh đủ sáng và bàn tay rõ nét
* Đảm bảo tay không bị xoay quá mức hoặc bị che khuất
* Với nhiều bàn tay, nên để chúng tách biệt trong khung hình
* Ảnh lớn (1000+ pixels) cho kết quả tốt hơn nhưng sẽ được tự động thu nhỏ

## 🐛 Các Vấn Đề Đã Biết

* Khó xử lý khi các bàn tay bị chồng lên nhau quá nhiều
* Góc xoay tay quá lớn có thể làm giảm độ chính xác
* Hiệu suất phụ thuộc vào chất lượng ảnh và điều kiện ánh sáng

## 📜 Giấy Phép

Dự án này là mã nguồn mở và được phép sử dụng miễn phí theo giấy phép MIT.
