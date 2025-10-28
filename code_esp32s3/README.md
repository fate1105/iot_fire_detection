# 🔥 ESP32-S3 Fire Detection Firmware

Firmware cho **ESP32-S3** trong đồ án *Hệ thống cảnh báo cháy thông minh*.  
Thiết bị đọc dữ liệu **DHT22** (nhiệt độ, độ ẩm) và **MQ-2** (khói),  
phát cảnh báo bằng **LED thường + RGB**, và gửi dữ liệu qua **MQTT** (Mosquitto/EMQX).

---

## ⚙️ Cấu hình phần cứng

| Thiết bị | GPIO | Ghi chú |
|-----------|-------|--------|
| DHT22 | 4 | Nhiệt độ, độ ẩm |
| MQ-2 (AO) | 1 | Mức khói (analog) |
| LED cảnh báo | 21 | Chớp theo mức cảnh báo |
| LED RGB WS2812 | 48 | Trạng thái Wi-Fi/MQTT |
| Nguồn | 5V | Cho toàn hệ thống |

---

## 📡 Wi-Fi & MQTT
Sửa lại cấu hình
```cpp
const char* WIFI_SSID = "Le Thanh Vu";
const char* WIFI_PASS = "Nam180504@@";
const char* MQTT_SERVER = "192.168.1.9"; 
const int   MQTT_PORT   = 1883;
const char* TOPIC_DATA  = "esp32s3/data";
```
## 📡 Gửi dữ liệu JSON

Thiết bị gửi dữ liệu qua MQTT topic `esp32s3/data` dưới dạng JSON:

```json
{
  "temp": 32.4,
  "humi": 81.5,
  "smoke": 2280,
  "risk": 4,
  "level": "warning"
}
```

## 🔔 Mức cảnh báo

| Mức | LED RGB | LED thường |
|------|----------|-------------|
| 🟢 **Safe** | Xanh lá | Tắt |
| 🟠 **Warning** | Cam | Nhấp chậm |
| 🔴 **Danger** | Đỏ | Nhấp nhanh |
