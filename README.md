# Google Sheet Data Viewer

A simple Python application to fetch and display data from a public Google Sheet, with filtering capabilities and random row selection.

## Features

- Load data from any public Google Sheet
- Display data in a table format
- Filter data by column values
- Select random rows from filtered data
- Dark mode option (enhanced version)
- Download filtered data as CSV or Excel (enhanced version)
- Data statistics visualization (enhanced version)

## Versions

This repository contains two versions of the application:

1. **Basic Version (app.py)**: A simple implementation with core features
2. **Enhanced Version (app_enhanced.py)**: A more feature-rich version with improved UI, dark mode, statistics, and download options

## Installation

1. Clone this repository
2. Install the required packages:

```
pip install -r requirements.txt
```

3. Run the application:

For the basic version:
```
streamlit run app.py
```

For the enhanced version:
```
streamlit run app_enhanced.py
```

## Usage

1. Enter the URL of your public Google Sheet
2. The data will be displayed in a table
3. Use the filters to narrow down the data
4. Click "Select Random Rows" to randomly select rows from the filtered data
5. In the enhanced version, you can also:
   - Download the filtered data as CSV or Excel
   - View basic statistics about the data
   - Toggle dark mode
   - Adjust the number of random rows to select

## Note

- The Google Sheet must be publicly accessible (shared with "Anyone with the link can view")
- For large sheets, the initial load may take a few seconds

---

# Ứng dụng Xem Dữ liệu từ Google Sheet

Một ứng dụng Python đơn giản để lấy và hiển thị dữ liệu từ Google Sheet công khai, với khả năng lọc và chọn ngẫu nhiên các hàng.

## Tính năng

- Tải dữ liệu từ bất kỳ Google Sheet công khai nào
- Hiển thị dữ liệu ở dạng bảng
- Lọc dữ liệu theo giá trị cột
- Chọn ngẫu nhiên các hàng từ dữ liệu đã lọc
- Tùy chọn chế độ tối (phiên bản nâng cao)
- Tải xuống dữ liệu đã lọc dưới dạng CSV hoặc Excel (phiên bản nâng cao)
- Trực quan hóa thống kê dữ liệu (phiên bản nâng cao)

## Phiên bản

Repository này chứa hai phiên bản của ứng dụng:

1. **Phiên bản Cơ bản (app.py)**: Một triển khai đơn giản với các tính năng cốt lõi
2. **Phiên bản Nâng cao (app_enhanced.py)**: Một phiên bản nhiều tính năng hơn với giao diện người dùng cải tiến, chế độ tối, thống kê và tùy chọn tải xuống

## Cài đặt

1. Clone repository này
2. Cài đặt các gói cần thiết:

```
pip install -r requirements.txt
```

3. Chạy ứng dụng:

Đối với phiên bản cơ bản:
```
streamlit run app.py
```

Đối với phiên bản nâng cao:
```
streamlit run app_enhanced.py
```

## Cách sử dụng

1. Nhập URL của Google Sheet công khai của bạn
2. Dữ liệu sẽ được hiển thị dạng bảng
3. Sử dụng bộ lọc để thu hẹp dữ liệu
4. Nhấp "Select Random Rows" để chọn ngẫu nhiên các hàng từ dữ liệu đã lọc
5. Trong phiên bản nâng cao, bạn cũng có thể:
   - Tải xuống dữ liệu đã lọc dưới dạng CSV hoặc Excel
   - Xem thống kê cơ bản về dữ liệu
   - Bật chế độ tối
   - Điều chỉnh số lượng hàng ngẫu nhiên để chọn

## Lưu ý

- Google Sheet phải được truy cập công khai (chia sẻ với "Bất kỳ ai có liên kết đều có thể xem")
- Đối với các bảng tính lớn, lần tải đầu tiên có thể mất vài giây 