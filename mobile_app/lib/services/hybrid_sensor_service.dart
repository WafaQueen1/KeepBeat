import 'dart:async';
import 'dart:convert';
import 'package:mqtt_client/mqtt_client.dart';
import 'mqtt_client_factory.dart';
import '../database/local_data_repository.dart';
import 'cloud_sync_service.dart';

class HybridSensorService {
  late final MqttClient client;
  String currentPatientId = 'PT_001';
  Function(String)? onAlert;
  
  // High-Fidelity Clinical Streams
  final _heartRateController = StreamController<int>.broadcast();
  Stream<int> get heartRateStream => _heartRateController.stream;

  HybridSensorService() {
    client = MqttClientFactory.createClient('localhost', 'fog_reactive_agent_client');
  }

  Future<void> initializeMqtt() async {
    client.keepAlivePeriod = 60;
    client.onDisconnected = _onDisconnected;
    
    final connMessage = MqttConnectMessage()
        .withClientIdentifier('fog_reactive_agent')
        .startClean()
        .withWillQos(MqttQos.atLeastOnce);
    client.connectionMessage = connMessage;

    try {
      await client.connect();
    } catch (e) {
      client.disconnect();
      return;
    }

    if (client.connectionStatus!.state == MqttConnectionState.connected) {
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
    print('MQTT Client disconnected');
  }

  Future<void> _evaluateSingleBrainSafetyRule(String topic, String payload) async {
    try {
      final data = jsonDecode(payload);
      final String sensorType = topic.contains('cgm') ? 'cgm' : 'pacemaker';
      final double value = (topic.contains('cgm') ? data['glucose_level'] : data['heart_rate'])?.toDouble() ?? 0.0;
      final int timestamp = data['timestamp'] ?? (DateTime.now().millisecondsSinceEpoch / 1000).round();

      final repo = LocalDataRepository();
      await repo.insertLocallyBufferedData({
        'sensor_id': data['device_id'] ?? 'device_unknown',
        'type': sensorType,
        'value': value,
        'timestamp': timestamp,
      });

      // 2. Real-time Stream Injection
      if (sensorType == 'pacemaker') {
        _heartRateController.sink.add(value.toInt());
      }

      _checkSafetyThresholds(sensorType, value);
      CloudSyncService().syncData(patientId: currentPatientId).catchError((e) => print('Sync failed: $e'));
      
    } catch (e) {
      print('Error parsing sensor data: $e');
    }
  }

  void _checkSafetyThresholds(String type, double value) {
    if (type == 'cgm') {
      if (value < 0.70) onAlert?.call('CRITICAL: Hypoglycemia ($value g/L)');
    } else if (type == 'pacemaker') {
      if (value < 50.0) onAlert?.call('CRITICAL: Bradycardia ($value BPM)');
      if (value > 120.0) onAlert?.call('WARNING: Tachycardia ($value BPM)');
    }
  }

  void dispose() {
    _heartRateController.close();
  }
}

