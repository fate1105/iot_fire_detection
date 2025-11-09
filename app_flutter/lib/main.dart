import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';
import 'package:provider/provider.dart';

// ==================== MAIN APP ====================
void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => MqttController(),
      child: MaterialApp(
        title: 'Fire Detection Dashboard',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepOrange),
          useMaterial3: true,
          fontFamily: 'Inter',
        ),
        home: const FireDashboard(),
      ),
    );
  }
}

// ==================== DASHBOARD UI ====================
class FireDashboard extends StatelessWidget {
  const FireDashboard({super.key});

  @override
  Widget build(BuildContext context) {
    final mqtt = context.watch<MqttController>();
    final data = mqtt.sensorData;

    Color levelColor(String level) {
      switch (level) {
        case 'warning':
          return Colors.orange;
        case 'danger':
          return Colors.red;
        default:
          return Colors.green;
      }
    }

    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        title: const Text("🔥 ESP32-S3 Fire Detection"),
        backgroundColor: Colors.deepOrange,
        foregroundColor: Colors.white,
      ),
      body: Center(
        child: Card(
          margin: const EdgeInsets.all(20),
          elevation: 8,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          child: Padding(
            padding: const EdgeInsets.all(25),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                _buildStatusBadge(mqtt.connected),
                const SizedBox(height: 20),
                _buildMetric("🌡️ Temperature", "${data['temp']} °C"),
                _buildMetric("💧 Humidity", "${data['humi']} %"),
                _buildMetric("🔥 Smoke", "${data['smoke']}"),
                _buildMetric("🧮 Risk Score", "${data['risk']}"),
                const SizedBox(height: 25),
                AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  padding:
                      const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                  decoration: BoxDecoration(
                    color: levelColor(data['level']),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    data['level'].toUpperCase(),
                    style: const TextStyle(
                        fontSize: 20,
                        color: Colors.white,
                        fontWeight: FontWeight.bold),
                  ),
                ),
                const SizedBox(height: 20),
                Text(
                  "Last update: ${mqtt.lastUpdate}",
                  style: const TextStyle(color: Colors.grey, fontSize: 14),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMetric(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label,
              style:
                  const TextStyle(fontSize: 16, fontWeight: FontWeight.w500)),
          Text(value,
              style:
                  const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildStatusBadge(bool connected) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: connected ? Colors.green : Colors.red,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Text(
        connected ? "🔌 MQTT Connected" : "⚠️ MQTT Disconnected",
        style:
            const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
      ),
    );
  }
}

// ==================== CONTROLLER ====================
class MqttController extends ChangeNotifier {
  late MqttServerClient _client;
  bool connected = false;
  Map<String, dynamic> sensorData = {
    'temp': '--',
    'humi': '--',
    'smoke': '--',
    'risk': '--',
    'level': 'safe',
  };
  String lastUpdate = '--';

  // ⚙️ Cấu hình MQTT tĩnh
  static const String mqttHost = '172.20.10.6'; // 🧩 Thay IP tại đây
  static const int mqttPort = 1883;             // TCP port (ESP / Python)
  static const int mqttWsPort = 8083;           // WebSocket port (Flutter Web)
  static const String topic = 'esp32s3/data';

  MqttController() {
    _connect();
  }

  Future<void> _connect() async {
    if (kIsWeb) {
      // Web dùng WebSocket
      _client = MqttServerClient.withPort('ws://$mqttHost', 'flutter_fire_web', mqttWsPort);
      _client.useWebSocket = true;
      debugPrint('🌐 Using WebSocket mode ($mqttWsPort)');
    } else {
      // Android / Desktop dùng TCP
      _client = MqttServerClient(mqttHost, 'flutter_fire_mobile');
      _client.port = mqttPort;
      debugPrint('📱 Using TCP mode ($mqttPort)');
    }

    _client.keepAlivePeriod = 20;
    _client.onConnected = _onConnected;
    _client.onDisconnected = _onDisconnected;
    _client.logging(on: false);
    _client.setProtocolV311();
    _client.autoReconnect = true;

    final connMess = MqttConnectMessage()
        .withClientIdentifier(
            'flutter_fire_${DateTime.now().millisecondsSinceEpoch}')
        .startClean();
    _client.connectionMessage = connMess;

    try {
      await _client.connect();
    } catch (e) {
      debugPrint('❌ MQTT connect error: $e');
      _client.disconnect();
    }

    _client.updates?.listen((List<MqttReceivedMessage<MqttMessage>> events) {
      final recMess = events[0].payload as MqttPublishMessage;
      final payload =
          MqttPublishPayload.bytesToStringAsString(recMess.payload.message);

      try {
        final jsonData = jsonDecode(payload);
        sensorData = {
          'temp': jsonData['temp'] ?? '--',
          'humi': jsonData['humi'] ?? '--',
          'smoke': jsonData['smoke'] ?? '--',
          'risk': jsonData['risk'] ?? '--',
          'level': jsonData['level'] ?? 'safe',
        };
        final now = DateTime.now();
        lastUpdate = "${now.hour}:${now.minute}:${now.second}";
        notifyListeners();
      } catch (e) {
        debugPrint('⚠️ Invalid JSON: $e');
      }
    });
  }

  void _onConnected() {
    connected = true;
    _client.subscribe(topic, MqttQos.atMostOnce);
    notifyListeners();
  }

  void _onDisconnected() {
    connected = false;
    notifyListeners();
  }
}
