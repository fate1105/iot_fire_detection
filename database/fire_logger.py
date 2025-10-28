"""
ESP32-S3 Fire Detection → SQLite Logger + Telegram Alert (Vietnam timezone)
Nghe topic MQTT, lưu dữ liệu vào SQLite và gửi cảnh báo Telegram khi phát hiện cháy.
"""

import sqlite3
import json
import time
from datetime import datetime, timezone, timedelta
import paho.mqtt.client as mqtt
import requests  # dùng để gửi tin nhắn Telegram

# ============================== CONFIG ==============================

# ⚙️ MQTT cấu hình
MQTT_BROKER = "192.168.1.9"  # 🛠️ Sửa IP máy chủ tại đây
MQTT_PORT = 1883
TOPIC_FIRE = "esp32s3/data"  # topic ESP32 gửi dữ liệu báo cháy

# 💾 Database
DB_FILE = "fire_data.db"
VN_TZ = timezone(timedelta(hours=7))  # Asia/Ho_Chi_Minh (UTC+7)

# 💬 Telegram Alert
TELEGRAM_TOKEN = "8159024125:AAH7B472lHdLWi1UfDoYYvoW6Ug-ZrhBDwM"  # 🟡 thay token bot thật của bạn
CHAT_ID = "5548903675"                    # 🟡 thay chat ID của bạn


# =========================== DATABASE INIT ===========================

def init_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS fire_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,           -- thời gian theo VN
            device_timestamp INTEGER, -- thời gian thiết bị gửi (millis)
            temperature REAL,
            humidity REAL,
            smoke INTEGER,
            risk INTEGER,
            level TEXT                -- safe / warning / danger
        )
    """)
    conn.commit()
    conn.close()
    print(f"[DB] Ready ({DB_FILE})")


# ============================ TELEGRAM ALERT ============================

def send_telegram_alert(message: str):
    """Gửi cảnh báo qua Telegram"""
    if not TELEGRAM_TOKEN or not CHAT_ID or "YOUR_" in TELEGRAM_TOKEN:
        return  # bỏ qua nếu chưa cấu hình
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        requests.post(url, data=payload, timeout=5)
        print("[TG] Alert sent to Telegram ✅")
    except Exception as e:
        print(f"[TG] Failed to send Telegram alert: {e}")


# ============================ MQTT CALLBACKS ============================

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] Connected to {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(TOPIC_FIRE)
        print(f"[MQTT] Subscribed: {TOPIC_FIRE}")
    else:
        print(f"[MQTT] Connect failed (rc={rc})")


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    try:
        data = json.loads(payload)
        save_fire_data(data)

        # 🔔 Nếu mức cảnh báo không an toàn → gửi tin nhắn Telegram
        level = data.get("level", "safe")
        if level == "danger":
            send_telegram_alert(
                f"🚨 CẢNH BÁO CHÁY! 🔥\n"
                f"Nhiệt độ: {data.get('temp')}°C\n"
                f"Độ ẩm: {data.get('humi')}%\n"
                f"Khói: {data.get('smoke')}\n"
                f"Thời gian: {now_vn()}"
            )
        elif level == "warning":
            send_telegram_alert(
                f"⚠️ Cảnh báo sớm!\n"
                f"Nhiệt độ: {data.get('temp')}°C\n"
                f"Độ ẩm: {data.get('humi')}%\n"
                f"Khói: {data.get('smoke')}\n"
                f"Thời gian: {now_vn()}"
            )

    except json.JSONDecodeError:
        print(f"[WARN] Invalid JSON: {payload}")
    except Exception as e:
        print(f"[ERR] {e}")


# ============================ SAVE FUNCTIONS ============================

def now_vn():
    """Thời gian hiện tại theo múi giờ Việt Nam."""
    return datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S")


def save_fire_data(data):
    """Lưu dữ liệu báo cháy từ ESP32-S3 vào SQLite."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        INSERT INTO fire_logs (timestamp, device_timestamp, temperature, humidity, smoke, risk, level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        now_vn(),
        data.get("time_ms"),
        data.get("temp"),
        data.get("humi"),
        data.get("smoke"),
        data.get("risk"),
        data.get("level")
    ))

    conn.commit()
    conn.close()
    print(f"[DB] Saved: {data.get('level').upper()} @ {now_vn()} | "
          f"T={data.get('temp')}°C H={data.get('humi')}% S={data.get('smoke')} Risk={data.get('risk')}")


# ============================== MAIN LOOP ==============================

def main():
    print("=== MQTT → SQLite Fire Logger + Telegram Alert ===")
    print(f"Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Topic:  {TOPIC_FIRE}")
    print(f"DB:     {DB_FILE}")
    print("Timezone: Asia/Ho_Chi_Minh (UTC+7)\n")

    init_database()

    client = mqtt.Client(client_id="fire_logger_" + str(int(time.time())))
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print("[RUNNING] Listening for MQTT fire detection data...\n")
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[STOPPED] Exiting...")
        client.disconnect()
    except Exception as e:
        print(f"[ERR] {e}")


if __name__ == "__main__":
    main()
