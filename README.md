# Mi Band 5 Pedal Coach · Phase 0

Nghiên cứu khả năng dùng dữ liệu chuyển động BLE của Xiaomi Mi Band 5 để phân biệt chân phải đang ở phanh, ga hoặc đang chuyển giữa hai bàn đạp.

**Trạng thái ngày 2026-11-24:** Đã đối chiếu bốn repo và hoàn thành PoC thu dữ liệu. Đã kiểm tra cú pháp và CLI trên Linux. Còn chờ phép đo trên Mi Band 5 thật với Windows. **GO cho phép thử có kiểm soát. Chưa đủ dữ liệu để mở Phase 1.**

## Làm gì tiếp

1. Dùng Windows, Mi Band 5 đã liên kết với app và khóa xác thực hiện tại. Làm theo [hướng dẫn Windows](KIEM-TRA-WINDOWS.md) để chạy `scan`, `inspect`, rồi `capture --profile raw`.
2. Thử ba lần kết nối độc lập, mỗi lần tối thiểu 90 giây. Kiểm tra gói dữ liệu trên `h0002`, phản ứng XYZ khi đổi sáu tư thế, số mẫu/giây và khoảng trống giữa các batch.
3. Ghi kết quả theo [mẫu bàn giao](HANDOFF.md). Nếu xác nhận luồng ổn định, làm bài thử bàn đạp cố định trước khi quyết định Phase 1.

| Tài liệu | Dùng khi |
|---|---|
| [Bản đồ dự án](PROJECT-MAP.md) | Tìm luồng dữ liệu, tệp nguồn, mốc quyết định và đầu ra |
| [Timeline](TIMELINE.md) | Xem thứ tự thực hiện, phụ thuộc, thời lượng ước tính và điều kiện hoàn thành |
| [Bàn giao cho AI / Codex PC](HANDOFF.md) | Tiếp tục từ trạng thái hiện tại và ghi bằng chứng mới |
| [Báo cáo kỹ thuật](BAO-CAO.md) | Đối chiếu nguồn, giao thức, phép đo, ngưỡng và phương án dự phòng |
| [Hướng dẫn Windows](KIEM-TRA-WINDOWS.md) | Cài công cụ, xác thực, thu và đọc CSV |

Chỉ thử trên bàn đạp cố định hoặc xe đã tắt và cố định. Giữ khóa BLE, địa chỉ thiết bị, CSV/log thô và video ở máy thu. Repo công khai dùng để lưu mã, tài liệu và kết quả tổng hợp đã rà soát.
