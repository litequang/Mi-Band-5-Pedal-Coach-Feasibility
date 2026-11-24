# Hướng dẫn cho agent

- Bắt đầu ở [HANDOFF.md](HANDOFF.md) và [TIMELINE.md](TIMELINE.md). Phạm vi hiện tại là nghiên cứu khả thi Phase 0 và PoC thu dữ liệu.
- Giữ nguyên firmware, phiên bind, cấu hình và dữ liệu đã lưu trên Mi Band 5. Dùng auth key hiện có nhập ẩn tại Windows. Không root, reset, unpair, cập nhật firmware, ghi đè dữ liệu hoặc đăng ký khóa mới.
- Chạy `raw` trước. Dùng `flutter` theo điều kiện trong hướng dẫn Windows vì profile này bật phiên HR trực tiếp tạm thời. Giữ ghi BLE trong phạm vi xác thực và điều khiển phiên thu.
- Trình bày riêng kết quả từ nguồn công khai, kết quả kiểm tra phần mềm và kết quả thiết bị thật. Không dùng dữ liệu mô phỏng để xác nhận phần cứng. Chỉ thử trên bộ bàn đạp cố định hoặc xe đã tắt hoàn toàn và cố định.
- Giữ khóa, địa chỉ thiết bị, bản ghi BLE/CSV/log thô và video ngoài Git. Khi có bằng chứng mới, cập nhật trạng thái và ghi kết quả tổng hợp đã rà soát theo [HANDOFF.md](HANDOFF.md).
