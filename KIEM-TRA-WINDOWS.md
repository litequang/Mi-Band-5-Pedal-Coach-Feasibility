# Hướng dẫn Codex PC · Kiểm tra Mi Band 5 thực tế

Chạy trên **Windows 10 hoặc Windows 11**, với adapter BLE hoạt động, Python 3.12 và PowerShell tương tác. Dùng Mi Band 5 đã bind với tài khoản của bạn. Công cụ được kiểm tra cú pháp và CLI trên Linux; phép thử WinRT và phần cứng thực hiện theo hướng dẫn này. [Tài liệu Bleak WinRT](https://bleak.readthedocs.io/en/stable/backends/windows.html) · [Bleak 1.1.1](https://github.com/hbldh/bleak/tree/v1.1.1)

## Chuẩn bị

1. Đọc model, firmware và hardware nếu màn hình About hoặc app hiện có cung cấp. Giữ phiên bản hiện tại và giữ liên kết với app. Lấy **auth key của phiên bind hiện có** từ bản lưu của chính bạn hoặc tra cứu bằng phương pháp tài khoản phù hợp trong tài liệu Gadgetbridge. Ưu tiên quy trình có thể thực hiện tại máy mà không thay đổi bind. Nếu chưa có khóa phù hợp, vẫn chạy được `scan` và `inspect`; ghi trạng thái bị chặn ở auth. [Gadgetbridge · Huami/Xiaomi server pairing](https://gadgetbridge.org/basics/pairing/huami-xiaomi-server/)
2. Tắt Bluetooth trên điện thoại tạm thời để nhường kết nối, rồi đánh thức màn hình vòng. Không dùng Unpair, Reset, Update firmware hoặc thiết lập vòng lại. Giải nén gói vào thư mục làm việc trên PC. Mở Windows Terminal hoặc PowerShell trực tiếp trên máy.
3. Trong thư mục chứa `miband5_probe.py`, tạo môi trường riêng và quét.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\miband5_probe.py scan
```

Chọn đúng địa chỉ vòng của bạn từ dòng thiết bị, nhất là khi có nhiều Band gần đó. Nếu tên không hiện, đánh thức vòng và quét lại trước khi bỏ qua bước nhận diện. Trong các lệnh sau, thay địa chỉ ví dụ bằng địa chỉ vừa quan sát. Dùng thư mục đầu ra ở máy local.

```powershell
$bandAddress = 'AA:BB:CC:DD:EE:FF'
.\.venv\Scripts\python.exe .\miband5_probe.py inspect --address $bandAddress
.\.venv\Scripts\python.exe .\miband5_probe.py capture --address $bandAddress --profile raw --seconds 90
```

`inspect` tạo `run.log` với danh sách GATT và các phiên bản đọc được, không yêu cầu key. `capture` yêu cầu khóa 32 ký tự hex, có thể có tiền tố `0x`. Nhập ngay trong prompt ẩn của tiến trình Python. Không gửi khóa cho Codex, đưa vào tham số dòng lệnh, lưu cùng thư mục dự án, dán vào log hay đưa lên GitHub. Nếu Codex PC chạy lệnh từ terminal không tương tác, người dùng mở PowerShell trực tiếp để nhập.

## Ba bước xác minh

1. Xem `auth_ok` trong terminal hoặc `run.log`. Trong phép thử `raw`, dùng sáu tư thế quanh ba trục, giữ mỗi tư thế vài giây, rồi đặt yên và làm một chuyển động ngắn. Sau đó, xếp theo `packet_id` và `sample_in_packet` để kiểm tra dấu và mức XYZ thay đổi hợp lý. Lặp lại ba phiên kết nối riêng.
2. Nếu `raw` đã auth và gửi lệnh thành công nhưng thiếu gói hợp lệ, kiểm tra profile dưới đây nếu việc bật HR trực tiếp tạm thời phù hợp với ràng buộc trên vòng của bạn. Profile này chỉ gửi lệnh điều khiển phiên đo và bỏ dữ liệu HR. Lưu tự động nội bộ của firmware khi bật HR chưa được xác minh. Nếu cần bảo đảm không phát sinh bản ghi HR nội bộ, dừng ở kết quả profile `raw` và đánh dấu `flutter` chưa thử.

```powershell
.\.venv\Scripts\python.exe .\miband5_probe.py capture --address $bandAddress --profile flutter --seconds 90
```

3. Chỉ chuyển sang thử bàn đạp khi luồng XYZ ổn định qua phép thử phần cứng. Dùng bàn đạp vật lý cố định hoặc xe đã tắt và cố định. Gắn vòng ở mu chân phải, mở phiên capture dài hơn nếu cần, quay video ground truth cục bộ và nhấn phím mốc theo thiết kế trong báo cáo. Không thử khi xe đang vận hành.

| Phím | Mốc |
|---|---|
| `1`, `2` | `brake`, `gas` |
| `3`, `4` | `brake_to_gas`, `gas_to_brake` |
| `0`, `s` | `other`, `sync` |
| `q` | Kết thúc và đóng phiên |

Để dừng, ưu tiên `q` hoặc chờ hết thời gian. Kiểm tra `cleanup_failed` nếu mất kết nối hoặc quy trình dừng lỗi. Bật lại Bluetooth điện thoại sau khi thử và quan sát app có kết nối lại bình thường.

## Đọc kết quả

| Tệp | Cách dùng |
|---|---|
| `run.log` | Phiên bản, GATT, trạng thái auth, profile, lệnh điều khiển, khoảng thời gian thu, số notification, số mẫu ứng viên, khoảng trống giữa batch và rate theo cửa sổ 10 giây sau 5 giây đầu. Số toàn phiên và thống kê khoảng trống có tính mép cửa sổ. |
| `packets.csv` | Một dòng cho mỗi gói control/data, có hex gốc, chiều dài và kết quả decode. Control ACK chỉ nằm ở cột `channel=control`. |
| `samples.csv` | Một dòng cho mỗi XYZ ứng viên, thứ tự mẫu trong gói đếm từ 0. Các dòng cùng gói dùng chung `rx_ns` là thời gian nhận phía PC. |
| `markers.csv` | Mốc phiên và phím gắn nhãn, cùng đồng hồ đơn điệu với gói. Mốc phím cần đối chiếu video/công tắc trước khi dùng làm ground truth. |

- **Không tìm thấy hoặc không connect.** Kiểm tra Bluetooth Windows, driver, khoảng cách, màn hình vòng và kết nối trên điện thoại. Quét lại địa chỉ. Nếu Windows yêu cầu bind mới hoặc vòng yêu cầu reset/cập nhật, dừng phép thử theo ràng buộc.
- **GATT khác hoặc thiếu đặc tính.** Lưu inventory, model và firmware. Không thay UUID theo tên friendly. So sánh UUID và properties trong báo cáo.
- **Auth bị từ chối hoặc timeout.** Kiểm tra khóa ứng với đúng thiết bị và bind hiện tại. Một số firmware có thể khác. Dừng nếu chỉ còn phương án thay khóa, unpair hoặc reset.
- **Có ACK, không có dữ liệu.** Đếm `channel=data` và xem gói h0001. Nếu auth/start thành công và hai profile đều cho 0 gói h0002 qua các lần thử, ghi âm tính với firmware và cấu hình đã thử.
- **Có dữ liệu chưa giải mã.** Báo độ dài, byte đầu và số gói theo loại, lưu hex để phân tích hậu kiểm. Chỉ gọi là accelerometer sau khi đáp ứng thử tư thế. Mã thoát `0` trong capture chỉ có nghĩa đã thấy ít nhất một gói XYZ ứng viên, `2` là không thấy mẫu XYZ ứng viên, `1` là lỗi và `130` là Ctrl+C.

## Bản ghi bàn giao từ Codex PC

Gửi model, firmware/hardware, bản Windows và adapter/driver, số lần thử mỗi profile, kết quả GATT/auth/cleanup, số gói h0001 và h0002, số mẫu hợp lệ, bảng độ dài/loại gói, rate và gap theo phiên, kết quả thử sáu mặt, và nếu làm bài thử bàn đạp thì thêm confusion matrix cùng độ trễ. Có thể kèm CSV/log đã rà soát thông tin định danh. Giữ khóa auth và video gốc tại máy.
