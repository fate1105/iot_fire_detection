# 💾 IoT Fire Detection Database System

Hệ thống lưu trữ dữ liệu cảnh báo cháy từ **ESP32-S3** sử dụng **SQLite database**.  
Chương trình Python (`mqtt_fire_logger.py`) lắng nghe dữ liệu từ **MQTT Broker (Mosquitto/EMQX)**  
và lưu lại thông tin nhiệt độ, độ ẩm, mức khói, điểm nguy cơ và cấp độ cảnh báo theo thời gian **(múi giờ Việt Nam)**.

---

## 🗄️ Database Schema

### Bảng `fire_logs` – Nhật ký báo cháy

| Cột | Kiểu dữ liệu | Mô tả |
|------|---------------|------|
| `id` | INTEGER (PK) | Khóa chính, tự tăng |
| `timestamp` | TEXT | Thời gian lưu (UTC+7) |
| `device_timestamp` | INTEGER | Thời gian millis từ ESP32 |
| `temperature` | REAL | Nhiệt độ (°C) |
| `humidity` | REAL | Độ ẩm (%) |
| `smoke` | INTEGER | Mức khói (MQ-2) |
| `risk` | INTEGER | Điểm nguy cơ |
| `level` | TEXT | safe / warning / danger |

> 🧠 Bảng được tự động tạo khi chạy chương trình lần đầu (nếu chưa tồn tại).

---

## 🚀 Cách sử dụng
### Sửa lại phần cấu hình
```python
MQTT_BROKER = "192.168.1.9" #Sửa ip ở đây
MQTT_PORT = 1883
TOPIC_FIRE = "esp32s3/data"   # topic ESP32 gửi dữ liệu báo cháy 
```
### Chạy MQTT Logger (Terminal)

```bash
cd database
python mqtt_fire_logger.py
```
### Xem dữ liệu và thống kê

```bash
cd database
python view_fire_data.py
```