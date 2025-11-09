#!/usr/bin/env python3
"""
ESP32-S3 Fire Detection Simulator (Easy Mode)
---------------------------------------------
✔ MQTT 3.1.1 compatible (Mosquitto / EMQX)
✔ Không lỗi Malformed Packet
✔ Hai chế độ:
   - auto:   tự xoay vòng safe → warning → danger
   - manual: bấm phím 1/2/3 để gửi theo ý
"""

import time
import json
import argparse
from paho.mqtt import client as mqtt_client

# ======= CẤU HÌNH MẶC ĐỊNH =======
BROKER = "localhost"      # Mặc định broker nội bộ
PORT = 1883               # Cổng MQTT chuẩn
TOPIC = "esp32s3/data"    # Topic publish
CLIENT_ID = "esp32s3_sim_easy"

# ======= DỮ LIỆU CÁC MỨC =======
LEVELS = {
    "safe":    {"temp": 28.0, "humi": 65.0, "smoke": 1500, "risk": 0},
    "warning": {"temp": 38.5, "humi": 50.0, "smoke": 2600, "risk": 3},
    "danger":  {"temp": 52.0, "humi": 30.0, "smoke": 3400, "risk": 7},
}

# ======= MQTT =======
def make_client():
    client = mqtt_client.Client(
        mqtt_client.CallbackAPIVersion.VERSION1,
        client_id=CLIENT_ID,
        protocol=mqtt_client.MQTTv311
    )
    try:
        client.connect(BROKER, PORT, 60)
        print(f"✅ Đã kết nối MQTT broker tại {BROKER}:{PORT}")
    except Exception as e:
        print("❌ Không thể kết nối broker:", e)
        exit(1)
    return client


# ======= GỬI DỮ LIỆU =======
def publish(client, level_name):
    data = LEVELS[level_name]
    payload = {
        "temp": data["temp"],
        "humi": data["humi"],
        "smoke": data["smoke"],
        "risk": data["risk"],
        "level": level_name,
        "time_ms": int(time.time() * 1000)
    }
    msg = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    client.publish(TOPIC, msg, qos=0, retain=False)
    print(f"[{level_name.upper()}] → {payload}")


# ======= AUTO MODE =======
def run_auto(client, interval=5):
    print("🔁 AUTO MODE: luân phiên safe → warning → danger")
    levels = ["safe", "warning", "danger"]
    i = 0
    while True:
        publish(client, levels[i % 3])
        i += 1
        time.sleep(interval)


# ======= MANUAL MODE =======
def run_manual(client):
    print("🎮 MANUAL MODE: Bấm phím số để gửi")
    print("  [1] Safe   [2] Warning   [3] Danger   [q] Thoát")
    while True:
        key = input("> ").strip()
        if key == "1":
            publish(client, "safe")
        elif key == "2":
            publish(client, "warning")
        elif key == "3":
            publish(client, "danger")
        elif key.lower() == "q":
            print("🛑 Thoát manual mode.")
            break
        else:
            print("⚠️ Nhấn 1 / 2 / 3 / q thôi nha.")


# ======= MAIN =======
def main():
    parser = argparse.ArgumentParser(description="ESP32-S3 MQTT Simulator (Easy)")
    parser.add_argument("--mode", choices=["auto", "manual"], default="manual",
                        help="Chế độ chạy: auto hoặc manual")
    args = parser.parse_args()

    client = make_client()

    if args.mode == "auto":
        run_auto(client, interval=5)
    else:
        run_manual(client)


if __name__ == "__main__":
    main()
