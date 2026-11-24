# Bàn giao cho AI / Codex PC

**Trạng thái khi bàn giao:** Đã hoàn thành nghiên cứu mã nguồn và PoC. Chưa có log Mi Band 5 thật của dự án. Chưa xác minh auth, đặc tính WinRT, tốc độ mẫu, gyro hay phân loại chân trên thiết bị đích. Báo cáo tham chiếu chứa một kết quả dương tính về thu gia tốc và một probe khác âm tính.

## Tiếp tục trên máy có phần cứng

1. Đọc [AGENTS.md](AGENTS.md), [timeline](TIMELINE.md) và [hướng dẫn Windows](KIEM-TRA-WINDOWS.md). Kiểm tra PC có BLE và vòng là Mi Band 5 đã liên kết. Nếu thiếu phần cứng hoặc khóa hiện tại, ghi điều kiện còn thiếu.
2. Trên Windows, cài đúng dependencies, kiểm kê GATT, chạy profile `raw` trước. Người giữ vòng nhập khóa qua prompt ẩn tại PC. Công cụ chỉ gắn nhãn payload hợp cấu trúc là XYZ ứng viên. Dùng thử sáu mặt để đối chiếu.
3. Nếu `raw` thiếu gói trong khi auth/start thành công, đọc điều kiện của profile `flutter`. Profile này mở phiên đo HR trực tiếp và bỏ payload HR. Hành vi lưu HR nội bộ của firmware chưa được xác minh.
4. Đối chiếu cổng thu dữ liệu trong báo cáo. Chỉ thu bài thử bàn đạp sau khi qua cổng này. Lưu kết quả tổng hợp theo mẫu dưới đây và cập nhật trạng thái trong README/timeline khi có bằng chứng.

## Nội dung để giao cho phiên AI tiếp theo

> Tiếp tục Phase 0 theo AGENTS.md và HANDOFF.md. Dùng Windows PC có BLE và Mi Band 5 thật. Thực hiện scan, inspect và ba lần capture raw độc lập theo KIEM-TRA-WINDOWS.md. Chủ thiết bị tự nhập khóa trong prompt ẩn. Dựa trên dữ liệu đo, ghi rõ trạng thái BLE/auth, số gói h0001/h0002, cadence, khoảng trống và kết quả sáu mặt. So sánh với ngưỡng trong BAO-CAO.md rồi tiếp tục bài thử cố định hoặc ghi blocker và phương án dự phòng. Chỉ cập nhật repo với kết quả tổng hợp đã loại dữ liệu định danh.

## Mẫu báo cáo kết quả

- Ngày thử, commit PoC, model, firmware/hardware, Windows build và adapter/driver.
- Profile đã dùng, số phiên hoàn tất, thời lượng mỗi phiên, kết quả GATT/auth/start/cleanup.
- Từng phiên ghi số gói `h0001`, `h0002`, số XYZ ứng viên, phân bố byte đầu/độ dài/mẫu mỗi gói, rate từng cửa sổ 10 giây, p95 và khoảng trống lớn nhất.
- Thử sáu mặt ghi trục chi phối, dấu và đáp ứng khi vòng chuyển động. Ghi rõ đơn vị raw và giới hạn suy luận timestamp.
- Nếu đã thử bàn đạp, ghi cấu hình, số người/phiên, cách đồng bộ nhãn, phiên giữ lại, confusion matrix, nhầm phanh ↔ ga, precision/recall mỗi chiều chuyển, báo động giả/phút và độ trễ.
- Kết luận riêng cho cổng thu và cổng phân loại. Ghi trạng thái đạt, chưa đạt hoặc bị chặn, dẫn bằng chứng và xác định bước tiếp theo.

Giữ khóa, địa chỉ BLE, log/CSV thô và video ở máy thu. Khi cần gửi bằng chứng ra ngoài PC, dùng bảng tổng hợp đã rà soát thông tin định danh.
