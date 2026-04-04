import 'dart:convert';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';
import '../database/local_data_repository.dart';
import 'cloud_sync_service.dart';

class HybridSensorService {
  final MqttServerClient client = MqttServerClient('10.0.2.2', 'fog_reactive_agent_client');
  String currentPatientId = 'PT_001';
  Function(String)? onAlert;
  Function(double)? onHeartRateUpdate;

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
        
        _evaluateSingleBrainSafetyRule(c[0].topic, payload);
      });
    }
  }

  void _onDisconnected() {
    print('MQTT Client completely disconnected');
  }

  Future<void> _evaluateSingleBrainSafetyRule(String topic, String payload) async {
    try {
      final data = jsonDecode(payload);
      final String sensorType = topic.contains('cgm') ? 'cgm' : 'pacemaker';
      final double value = (topic.contains('cgm') ? data['glucose_level'] : data['heart_rate'])?.toDouble() ?? 0.0;
      final int timestamp = data['timestamp'] ?? (DateTime.now().millisecondsSinceEpoch / 1000).round();
      final String deviceId = data['device_id'] ?? 'device_unknown';

      // 1. Buffer data locally (Fog logic)
      final repo = LocalDataRepository();
      await repo.insertLocallyBufferedData({
        'sensor_id': deviceId,
        'type': sensorType,
        'value': value,
        'timestamp': timestamp,
      });

      // 2. Real-time Heart Rate Stream Update
      if (sensorType == 'pacemaker' && onHeartRateUpdate != null) {
        onHeartRateUpdate!(value);
      }

      // 3. Single-Brain Safety Check (Fog-only threshold logic)
      _checkSafetyThresholds(sensorType, value);

      // 4. Cloud Synchronization (Fog-to-Cloud)
      CloudSyncService().syncData(patientId: currentPatientId).catchError((e) => print('Sync failed: $e'));
      
    } catch (e) {
      print('Error parsing sensor data: $e');
    }
  }

  void _checkSafetyThresholds(String type, double value) {
    if (type == 'cgm') {
      if (value < 0.70) {
        onAlert?.call('CRITICAL: Hypoglycemia detected ($value g/L)');
      } else if (value > 2.50) {
        onAlert?.call('WARNING: Hyperglycemia detected ($value g/L)');
      }
    } else if (type == 'pacemaker') {
      if (value < 50.0) {
        onAlert?.call('CRITICAL: Bradycardia detected ($value BPM)');
      } else if (value > 120.0) {
        onAlert?.call('WARNING: Tachycardia detected ($value BPM)');
      }
    }
  }
}
