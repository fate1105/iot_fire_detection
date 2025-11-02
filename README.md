# 🔥 IoT Fire Detection System – ESP32-S3 + MQTT + Flutter + Web + SQLite

Hệ thống **Cảnh báo cháy thông minh (IoT Fire Detection)** được xây dựng dựa trên **ESP32-S3**, sử dụng các cảm biến **DHT22 (nhiệt độ, độ ẩm)** và **MQ-2 (khói)**.  
Dữ liệu được truyền qua **MQTT (Mosquitto/EMQX)**, lưu trữ bằng **Python SQLite Logger**, và hiển thị realtime qua **Web Dashboard** hoặc **Flutter App**.

---

## 🧠 Tổng quan hệ thống

Hệ thống được chia làm 3 tầng chính:
[ESP32-S3]
│ (Gửi JSON qua MQTT)
▼
[MQTT Broker (Mosquitto/EMQX)]
│
├── [Python Logger] → Lưu vào SQLite Database
├── [Web Dashboard] → Hiển thị realtime qua MQTT WebSocket
└── [Flutter App] → Hiển thị dữ liệu trên điện thoại

---

## ⚙️ Phần cứng sử dụng

| Thiết bị | GPIO | Ghi chú |
|-----------|-------|--------|
| **DHT22** | 4 | Cảm biến nhiệt độ & độ ẩm |
| **MQ-2 (AO)** | 1 | Đo mức khói (analog) |
| **LED cảnh báo** | 21 | Nhấp nháy khi có nguy cơ cháy |
| **LED RGB WS2812** | 48 | Hiển thị trạng thái Wi-Fi/MQTT |
| **Nguồn cấp** | 5V | Cho toàn hệ thống |

---

## 🔌 Firmware – ESP32-S3 Fire Detection

**Chức năng chính:**
- Đọc dữ liệu DHT22 & MQ-2
- Tính **điểm nguy cơ cháy (riskScore)**
- Phát cảnh báo bằng LED thường và LED RGB WS2812
- Gửi dữ liệu JSON lên MQTT Broker

### ⚙️ Cấu hình mạng & MQTT

```cpp
const char* WIFI_SSID = "Le Thanh Vu";
const char* WIFI_PASS = "Nam180504@@";
const char* MQTT_SERVER = "192.168.1.9";
const int   MQTT_PORT   = 1883;
const char* TOPIC_DATA  = "esp32s3/data";
```
### 🧾 Cấu trúc dữ liệu gửi qua MQTT
{
  "temp": 32.4,
  "humi": 81.5,
  "smoke": 2280,
  "risk": 4,
  "level": "warning"
}
🔔 Mức cảnh báo
| Mức | LED RGB | LED thường |
|------|----------|-------------|
| 🟢 **Safe** | Xanh lá | Tắt |
| 🟠 **Warning** | Cam | Nhấp chậm |
| 🔴 **Danger** | Đỏ | Nhấp nhanh |

### 💾 Python MQTT Logger – SQLite Database

#### Chức năng:
Lắng nghe dữ liệu từ MQTT Broker → lưu vào SQLite database theo múi giờ Việt Nam.

### 🌐 Web Dashboard – Real-time Monitoring

#### Chức năng:

Kết nối MQTT WebSocket (port 8083)

Hiển thị realtime nhiệt độ, độ ẩm, khói và mức cảnh báo

Đổi màu giao diện theo cấp độ rủi ro

Hiển thị trạng thái kết nối MQTT

### 📱 Flutter App – Fire Detection Dashboard

Ứng dụng Flutter hiển thị realtime dữ liệu từ MQTT

# 🌟 Tóm tắt

## Hệ thống IoT Fire Detection cung cấp giải pháp:

Phát hiện cháy sớm qua nhiệt độ, độ ẩm, khói
Cảnh báo bằng LED và Dashboard realtime
Lưu trữ dữ liệu phục vụ phân tích thống kê
