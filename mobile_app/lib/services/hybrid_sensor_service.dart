import 'dart:convert';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';
import '../database/local_data_repository.dart';
import 'cloud_sync_service.dart';

class HybridSensorService {
  // Use 10.0.2.2 for Android Emulator connecting to local host, or 127.0.0.1 for desktop
  final MqttServerClient client = MqttServerClient('10.0.2.2', 'fog_reactive_agent_client');

  Future<void> initializeMqtt() async {
    client.port = 1883;
    client.keepAlivePeriod = 60;
    client.onDisconnected = _onDisconnected;
    
    final connMessage = MqttConnectMessage()
        .withClientIdentifier('fog_reactive_agent')
        .startClean()
        .withWillQos(MqttQos.atLeastOnce);
    client.connectionMessage = connMessage;

    try {
      print('Connecting to MQTT broker...');
      await client.connect();
    } catch (e) {
      print('MQTT connection failed: $e');
      client.disconnect();
      return;
    }

    if (client.connectionStatus!.state == MqttConnectionState.connected) {
      print('Connected to MQTT Broker successfully');
      client.subscribe('twinpacemaker/sensors/cgm', MqttQos.atMostOnce);
      client.subscribe('twinpacemaker/sensors/pacemaker', MqttQos.atMostOnce);
      
      client.updates!.listen((List<MqttReceivedMessage<MqttMessage>> c) {
        final MqttPublishMessage recMess = c[0].payload as MqttPublishMessage;
        final String payload = MqttPublishPayload.bytesToStringAsString(recMess.payload.message);
        
        print('Received via MQTT on ${c[0].topic}: $payload');
        _evaluateSingleBrainSafetyRule(c[0].topic, payload);
      });
    }
  }

  void _onDisconnected() {
    print('MQTT Client completely disconnected');
  }

  Future<void> _evaluateSingleBrainSafetyRule(String topic, String payload) async {
    // Single-Brain Rule: All real-time safety thresholds are evaluated ONLY on the Fog
    try {
      final data = jsonDecode(payload);
      final String sensorType = topic.contains('cgm') ? 'cgm' : 'pacemaker';
      final double value = (topic.contains('cgm') ? data['glucose_level'] : data['heart_rate'])?.toDouble() ?? 0.0;
      final int timestamp = data['timestamp'] ?? (DateTime.now().millisecondsSinceEpoch / 1000).round();
      final String deviceId = data['device_id'] ?? 'device_unknown';

      // 1. Buffer data locally
      final repo = LocalDataRepository();
      await repo.insertLocallyBufferedData({
        'sensor_id': deviceId,
        'type': sensorType,
        'value': value,
        'timestamp': timestamp,
      });

      // 2. Local Safety Checks (Real-time reactivity on the Fog)
      if (sensorType == 'cgm') {
        if (value < 0.7) {
          print('🚨 CRITICAL ALERT: Hypoglycemia detected ($value g/L)');
        } else if (value > 2.5) {
          print('🚨 CRITICAL ALERT: Hyperglycemia detected ($value g/L)');
        }
      } else if (sensorType == 'pacemaker') {
        if (value < 40.0) {
          print('🚨 CRITICAL ALERT: Bradycardia detected ($value bpm)');
        } else if (value > 120.0) {
          print('🚨 CRITICAL ALERT: Tachycardia detected ($value bpm)');
        }
      }

      // 3. Opportunistic Cloud Synchronization
      CloudSyncService().syncData().catchError((e) => print('Background sync failed: $e'));
      
    } catch (e) {
      print('Error parsing sensor data: $e');
    }
  }
}
