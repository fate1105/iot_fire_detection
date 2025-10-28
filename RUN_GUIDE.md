🧭 RUN GUIDE — Hướng Dẫn Chạy Hệ Thống Cảnh Báo Cháy Thông Minh
Hệ thống bao gồm các thành phần:

🔥 ESP32-S3 (đọc cảm biến, gửi MQTT)

🐳 Mosquitto Broker (Docker)

💾 Python SQLite Logger

🌐 Web Dashboard

📱 Flutter App (tùy chọn)

## 📦 BƯỚC 2: Cài đặt Python Dependencies

```bash
pip install paho-mqtt requests
```

Kiểm tra đã cài:
```bash
pip list | findstr "paho-mqtt requests"
```

✅ Kết quả mong đợi:
```
paho-mqtt          x.x.x
requests           x.x.x
```

---

## 🐳 BƯỚC 3: Setup Mosquitto MQTT Broker

### Windows PowerShell:

```powershell
# 1. Di chuyển vào thư mục project
cd iot_fire_detection

# 2. Tạo thư mục cấu hình
New-Item -ItemType Directory -Force -Path "mosquitto\config"
New-Item -ItemType Directory -Force -Path "mosquitto\data"

# 3. Tạo file mosquitto.conf với nội dung CHÍNH XÁC
Set-Content -Path "mosquitto\config\mosquitto.conf" -Value @"
listener 1883 0.0.0.0
allow_anonymous true

listener 8083 0.0.0.0
protocol websockets
allow_anonymous true

log_dest stdout
log_type all

persistence true
persistence_location /mosquitto/data/
"@

# 4. Kiểm tra file đã tạo đúng chưa
Get-Content "mosquitto\config\mosquitto.conf"

# 5. Xóa container cũ (nếu có)
docker rm -f mosquitto

# 6. Chạy Mosquitto container
docker run -d `
  --name mosquitto `
  -p 1883:1883 `
  -p 8083:8083 `
  -v "${PWD}\mosquitto\config:/mosquitto/config" `
  -v "${PWD}\mosquitto\data:/mosquitto/data" `
  eclipse-mosquitto

# 7. Kiểm tra logs 
docker logs mosquitto
```

### ✅ Kết quả PHẢI thấy trong logs:

```
mosquitto version 2.0.x starting
Config loaded from /mosquitto/config/mosquitto.conf.
Opening ipv4 listen socket on port 1883.
Opening ipv6 listen socket on port 1883.
Opening websockets listen socket on port 8083.
Opening ipv6 listen socket on port 8083.
mosquitto version 2.0.x running
```

---

## 🔌 BƯỚC 4: Setup ESP32-S3 Hardware
Mở Arduino IDE 2.x

Chọn Board: ESP32S3 Dev Module

Mở file main.ino

Kiểm tra Wi-Fi & MQTT config:
```cpp
const char* WIFI_SSID = "Le Thanh Vu";
const char* WIFI_PASS = "Nam180504@@";
const char* MQTT_SERVER = "192.168.1.9";
```

Kết nối ESP32 qua cổng USB → chọn COM → Upload

Mở Serial Monitor (115200 baud)

✅ Kết quả mong đợi:

✅ WiFi đã kết nối!
🔗 Kết nối MQTT... ✅ Thành công!
🌡️ 32.1°C | 💧 81.2% | 🔥 MQ2:2287 | 🧮 Điểm:4 | ⚠️ warning

## 💾 BƯỚC 5: Chạy Database Logger (Optional)

Mở Terminal mới:

```bash
cd database
python fire_logger.py
```
💡 Chức năng:

Nghe MQTT topic esp32s3/data
Lưu dữ liệu vào SQLite (fire_data.db)
Tự động tạo bảng fire_logs nếu chưa có

Xem dữ liệu đã lưu (terminal khác):
```bash
cd database
python view_fire_data.py
```
Chọn:
[1] View Fire Logs → xem dữ liệu mới nhất
[2] View Statistics → xem thống kê 24h gần nhất

---

## 🌐 BƯỚC 6: Chạy Web Dashboard (Realtime Monitor)
Mở Terminal mới:

```bash
cd web/src
python -m http.server 3000
```
Sau đó truy cập trình duyệt tại:
```bash
http://localhost:3000/web_dashboard.html
```
---

## 📱 BƯỚC 7: Chạy Flutter App (Optional)

```bash
cd app_flutter
flutter pub get
flutter run
```

**Lưu ý:**
- **Android Emulator:** Sửa IP thành `10.0.2.2` trong code
- **Physical Device:** Sửa IP thành IP máy tính thật
```dart
  // ⚙️ Cấu hình MQTT tĩnh
  static const String mqttHost = '192.168.1.9'; // 🧩 Thay IP tại đây
  static const int mqttPort = 1883;             // TCP port (ESP / Python)
  static const int mqttWsPort = 8083;           // WebSocket port (Flutter Web)
  static const String topic = 'esp32s3/data';
  ```
---

## Sơ đồ luồng dữ liệu tổng quan
ESP32-S3 → MQTT Broker → Python Logger → SQLite DB → Web/Flutter Dashboard
