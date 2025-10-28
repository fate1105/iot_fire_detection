# 🌐 ESP32-S3 Fire Detection Web Dashboard

Giao diện web realtime hiển thị dữ liệu cảm biến **nhiệt độ – độ ẩm – khói – mức nguy cơ**  
từ **ESP32-S3** qua **MQTT WebSocket (Mosquitto/EMQX)**.

---

## 🧩 Tính năng

- Hiển thị dữ liệu realtime từ topic MQTT `esp32s3/data`
- Cập nhật tự động mỗi khi ESP32-S3 gửi JSON mới
- Hiển thị trạng thái kết nối MQTT (Connected/Disconnected)
- Đổi màu hiển thị theo mức độ cảnh báo:
  - 🟢 **SAFE** → Xanh lá  
  - 🟠 **WARNING** → Cam  
  - 🔴 **DANGER** → Đỏ (chớp nháy)
- Giao diện responsive, phông chữ hiện đại (Inter), nền gradient

---

## 🚀 Cách chạy

### 1️⃣ Mở trực tiếp bằng trình duyệt  
Chỉ cần mở file **`index.html`** trong Chrome/Edge.

> ⚠️ **Yêu cầu:**  
> - MQTT broker (Mosquitto/EMQX) đang chạy và bật **WebSocket port (8083)**.  
> - ESP32-S3 đang publish dữ liệu lên topic `esp32s3/data`.

---

### 2️⃣ Cấu hình địa chỉ MQTT Broker

Trong file `index.html`, sửa lại phần config:
```js
const CONFIG = {
  MQTT_HOST: "ws://192.168.1.9:8083",  // Địa chỉ WebSocket của Mosquitto hoặc EMQX
  TOPIC: "esp32s3/data",
  RECONNECT_MS: 5000,
};