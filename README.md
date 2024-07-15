# IDE PyCharm

Để chạy được mã Python này, anh em cần cài đặt các thư viện sau:

1. **OpenCV**: Để xử lý hình ảnh.
2. **Mediapipe**: Để phát hiện và theo dõi bàn tay.
3. **numpy**: Để tính toán các phép toán số học.
4. **tkinter**: Để tạo giao diện người dùng. Thư viện này thường có sẵn trong Python mặc định.
5. **Pillow**: Để xử lý hình ảnh trong tkinter.
6. **openpyxl**: Để làm việc với file Excel.

Anh em có thể cài đặt các thư viện này bằng pip. Dưới đây là câu lệnh để cài đặt từng thư viện:

```sh
pip install opencv-python-headless
pip install mediapipe
pip install numpy
pip install pillow
pip install openpyxl
```

Anh em cũng có thể cài đặt tất cả các thư viện này cùng một lúc bằng cách sử dụng tệp `requirements.txt`. Tạo tệp `requirements.txt` với nội dung sau:

```
opencv-python-headless
mediapipe
numpy
pillow
openpyxl
```

Sau đó chạy lệnh sau trong thư mục chứa tệp `requirements.txt`:

```sh
pip install -r requirements.txt
```

### Lưu ý

- **opencv-python-headless**: Phiên bản OpenCV không có giao diện đồ họa, phù hợp cho các ứng dụng không yêu cầu hiển thị hình ảnh bằng GUI của OpenCV.
- **tkinter**: Thư viện này thường có sẵn trong Python mặc định, nhưng nếu bạn gặp vấn đề khi sử dụng, bạn có thể cần cài đặt riêng. Trên Ubuntu, bạn có thể cài đặt bằng lệnh sau:
  ```sh
  sudo apt-get install python3-tk
  ```

Sau khi cài đặt các thư viện cần thiết, bạn có thể chạy mã Python đã cung cấp để đo góc bàn tay.
