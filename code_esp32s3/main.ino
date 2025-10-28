#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"
#include <Adafruit_NeoPixel.h>

// ======= CẤU HÌNH WI-FI & MQTT =======
const char* WIFI_SSID = "Le Thanh Vu";
const char* WIFI_PASS = "Nam180504@@";

const char* MQTT_SERVER = "192.168.1.9";  // IP broker (Mosquitto / EMQX)
const int   MQTT_PORT   = 1883;
const char* MQTT_CLIENT_ID = "esp32s3_fire_dht";
const char* TOPIC_DATA  = "esp32s3/data";

WiFiClient espClient;
PubSubClient client(espClient);

// ======= PINS & SENSORS =======
#define LED_OUT_PIN 21
#define DHTPIN 4
#define DHTTYPE DHT22
#define MQ2_AO_PIN 1
#define RGB_PIN 48

Adafruit_NeoPixel rgb(1, RGB_PIN, NEO_GRB + NEO_KHZ800);
DHT dht(DHTPIN, DHTTYPE);

// ======= THỜI GIAN / TẦN SUẤT =======
const unsigned long SENSOR_INTERVAL_MS = 1000;
unsigned long lastSensorMillis = 0;

// ======= NGƯỠNG & TRỌNG SỐ =======
const float TEMP_WARN_THRESHOLD = 37.0;
const float TEMP_DANGER_THRESHOLD = 50.0;

const float HUMI_WARN_THRESHOLD = 55.0;
const float HUMI_DANGER_THRESHOLD = 35.0;

const int MQ2_AO_WARN = 2500;
const int MQ2_AO_DANGER = 3200;

const float TEMP_RISE_WARN_PER_SEC = 2.0;
const float TEMP_RISE_DANGER_PER_SEC = 5.0;

const int LEVEL_WARNING_MIN = 3;
const int LEVEL_DANGER_MIN = 6;

// ======= TRẠNG THÁI =======
float lastTemp = NAN;
unsigned long lastTempMillis = 0;
unsigned long lastMqttReconnectAttempt = 0;
unsigned long mqttReconnectInterval = 2000;

// ==================== HÀM HỖ TRỢ ====================
void setRGB(uint8_t r, uint8_t g, uint8_t b) {
  rgb.setPixelColor(0, rgb.Color(r, g, b));
  rgb.show();
}

void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;
  Serial.printf("🔌 Kết nối WiFi: %s\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 10000) {
    delay(250);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi đã kết nối!");
    Serial.print("🌐 IP: "); Serial.println(WiFi.localIP());
    setRGB(0, 0, 150);
  } else {
    Serial.println("\n⚠️ WiFi thất bại, thử lại sau.");
    setRGB(150, 0, 150);
  }
}

void connectMQTT() {
  if (!WiFi.isConnected()) return;
  if (client.connected()) return;
  if (millis() - lastMqttReconnectAttempt < mqttReconnectInterval) return;

  lastMqttReconnectAttempt = millis();
  Serial.print("🔗 Kết nối MQTT... ");
  if (client.connect(MQTT_CLIENT_ID)) {
    Serial.println("✅ Thành công!");
    mqttReconnectInterval = 2000;
    client.publish(TOPIC_DATA, "{\"status\":\"online\"}");
    setRGB(0, 150, 0);
  } else {
    Serial.printf("❌ MQTT lỗi (%d), thử lại sau %lu ms\n", client.state(), mqttReconnectInterval);
    setRGB(255, 0, 255);
    mqttReconnectInterval = min(mqttReconnectInterval * 2, 60000UL);
  }
}

// ==================== SETUP ====================
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n🚀 ESP32-S3 Fire Detection System (No-DIG)");

  pinMode(LED_OUT_PIN, OUTPUT);
  digitalWrite(LED_OUT_PIN, LOW);

  rgb.begin();
  setRGB(0, 0, 0);

  Serial.println("⏳ Khởi tạo cảm biến DHT22...");
  dht.begin();
  delay(1500);
  Serial.println("✅ DHT22 sẵn sàng!");

  connectWiFi();
  client.setServer(MQTT_SERVER, MQTT_PORT);
  lastTempMillis = millis();
}

// ==================== LOOP ====================
void loop() {
  connectWiFi();
  connectMQTT();
  client.loop();

  unsigned long now = millis();
  if (now - lastSensorMillis < SENSOR_INTERVAL_MS) return;
  lastSensorMillis = now;

  // ==== đọc cảm biến ====
  int smokeLevel = analogRead(MQ2_AO_PIN);
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(t) || isnan(h)) {
    Serial.println("⚠️ Lỗi đọc DHT22, bỏ qua lần này.");
    setRGB(150, 0, 150);
    return;
  }

  // ==== tính điểm nguy cơ ====
  int riskScore = 0;

  if (t >= TEMP_WARN_THRESHOLD && t < TEMP_DANGER_THRESHOLD) riskScore += 1;
  else if (t >= TEMP_DANGER_THRESHOLD) riskScore += 2;

  if (h <= HUMI_WARN_THRESHOLD && h > HUMI_DANGER_THRESHOLD) riskScore += 1;
  else if (h <= HUMI_DANGER_THRESHOLD) riskScore += 2;

  if (smokeLevel >= MQ2_AO_WARN && smokeLevel < MQ2_AO_DANGER) riskScore += 1;
  else if (smokeLevel >= MQ2_AO_DANGER) riskScore += 2;

  if (!isnan(lastTemp)) {
    float deltaT = t - lastTemp;
    float deltaS = (now - lastTempMillis) / 1000.0f;
    if (deltaS > 1 && fabs(deltaT) > 0.2) {
      float risePerSec = deltaT / deltaS;
      if (risePerSec > TEMP_RISE_DANGER_PER_SEC) riskScore += 4;
      else if (risePerSec > TEMP_RISE_WARN_PER_SEC) riskScore += 2;
    }
  }

  lastTemp = t;
  lastTempMillis = now;

  // ==== xác định mức ====
  String level = "safe";
  if (riskScore >= LEVEL_DANGER_MIN) level = "danger";
  else if (riskScore >= LEVEL_WARNING_MIN) level = "warning";

  // ==== LED hiệu ứng ====
  static unsigned long lastBlink = 0;
  static bool blinkState = false;

  if (level == "safe") {
    setRGB(0, 150, 0);
    digitalWrite(LED_OUT_PIN, LOW);
  } else if (level == "warning") {
    setRGB(255, 128, 0);
    if (now - lastBlink >= 800) {
      lastBlink = now;
      blinkState = !blinkState;
      digitalWrite(LED_OUT_PIN, blinkState);
    }
  } else if (level == "danger") {
    if (now - lastBlink >= 200) {
      lastBlink = now;
      blinkState = !blinkState;
      digitalWrite(LED_OUT_PIN, blinkState);
      setRGB(blinkState ? 255 : 0, 0, 0);
    }
  }

  // ==== gửi MQTT ====
  if (client.connected()) {
    char payload[256];
    snprintf(payload, sizeof(payload),
             "{\"temp\":%.2f,\"humi\":%.2f,\"smoke\":%d,"
             "\"risk\":%d,\"level\":\"%s\",\"time_ms\":%lu}",
             t, h, smokeLevel, riskScore, level.c_str(), now);
    client.publish(TOPIC_DATA, payload);
  }

  // ==== log Serial ====
  Serial.printf("🌡️ %.2f°C | 💧 %.2f%% | 🔥 MQ2:%d | 🧮 Điểm:%d | ⚠️ %s\n",
                t, h, smokeLevel, riskScore, level.c_str());
}
