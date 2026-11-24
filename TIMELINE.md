# Timeline Phase 0

Mốc cập nhật 2026-11-24. Các khoảng dưới đây là **ước tính công sức** kể từ khi có đủ điều kiện cho từng mốc. Thời gian chờ Windows, vòng thật, khóa hiện tại và người hỗ trợ gắn nhãn được tính riêng.

| Mốc | Trạng thái | Phụ thuộc và việc thực hiện | Đầu ra và thời lượng |
|---|---|---|---|
| A. Nghiên cứu và chuẩn bị PoC | Hoàn thành | Đọc bốn repo, xác định auth và hai trình tự thu, kiểm tra cú pháp và CLI | Báo cáo kỹ thuật, PoC, hướng dẫn Windows |
| B. Kiểm kê BLE trên Windows | Kế tiếp | PC có BLE, vòng đã liên kết, chạy `scan` và `inspect`. Ghi phiên bản vòng và adapter. | Địa chỉ giữ tại PC, danh sách GATT, phiên bản. 20–45 phút. |
| C. Xác minh luồng XYZ | Chờ B và khóa hiện tại | Chạy `raw` qua ba kết nối riêng, ít nhất 90 giây/lần, có thử sáu mặt. Khi auth/start thành công nhưng thiếu dữ liệu, xem điều kiện chạy `flutter` trong hướng dẫn Windows. | Bảng số gói, rate/gap, phản ứng XYZ và kết luận cổng thu dữ liệu. 45–90 phút. |
| D. Thu bài thử bàn đạp | Chờ C đạt ngưỡng | Bàn đạp cố định, vòng ở mu chân phải, ghi nhãn tham chiếu. Thu ít nhất ba phiên độc lập, giữ nguyên phiên cuối để đánh giá. | Bộ dữ liệu giữ cục bộ, biên bản bố trí và phiên giữ lại. 1,5–3 giờ. |
| E. Chấm và kết luận | Chờ D | Dùng baseline nhân quả theo báo cáo, đối chiếu nhãn video/công tắc. Đo nhầm phanh ↔ ga, precision/recall từng chiều và độ trễ. | Bảng chấm, Go/No-Go cho bước nghiên cứu tiếp theo. 2–4 giờ. |

Nếu B/C vướng kết nối hay khóa, ghi **bị chặn** cùng bước và lỗi. Nếu hai profile đã chạy đầy đủ nhưng thu âm tính qua các lần thử, kết luận No-Go cho Mi Band 5 trên cấu hình đó và chuyển sang IMU dự phòng. Nếu chỉ hoàn tất được `raw`, giới hạn kết luận ở profile đã thử. Nếu E chỉ đạt nhận diện chuyển chân, dùng tiếp xúc hoặc video để kiểm tra trạng thái giữ. Xem các ngưỡng đã đề xuất trước khi mở tập đánh giá. [Báo cáo kỹ thuật](BAO-CAO.md#5-cổng-quyết-định-và-phương-án-dự-phòng)
