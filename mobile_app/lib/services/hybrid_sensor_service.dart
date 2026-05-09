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

  final _glucoseController = StreamController<double>.broadcast();
  Stream<double> get glucoseStream => _glucoseController.stream;

  final _batteryController = StreamController<double>.broadcast();
  Stream<double> get batteryStream => _batteryController.stream;

  final _alertController = StreamController<String>.broadcast();
  Stream<String> get alertStream => _alertController.stream;

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
      // Back-compat topics
      client.subscribe('twinpacemaker/sensors/cgm', MqttQos.atMostOnce);
      client.subscribe('twinpacemaker/sensors/pacemaker', MqttQos.atMostOnce);

      // Explicit topics (requested)
      client.subscribe('pacemaker/heart_rate', MqttQos.atMostOnce);
      client.subscribe('cgm/glucose', MqttQos.atMostOnce);
      client.subscribe('pacemaker/battery', MqttQos.atMostOnce);
      
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
      final bool isBattery = topic.contains('battery') || (data is Map && data.containsKey('battery'));
      final String sensorType = (topic.contains('cgm') || topic.contains('glucose')) ? 'cgm' : 'pacemaker';

      final double value = isBattery
          ? _readDouble(data, ['battery', 'battery_level', 'level', 'pct']) ?? 0.0
          : (sensorType == 'cgm'
              ? (_readDouble(data, ['glucose_level', 'glucose', 'value']) ?? 0.0)
              : (_readDouble(data, ['heart_rate', 'bpm', 'value']) ?? 0.0));
      final int timestamp = data['timestamp'] ?? (DateTime.now().millisecondsSinceEpoch / 1000).round();

      final repo = LocalDataRepository();
      await repo.insertLocallyBufferedData({
        'sensor_id': data['device_id'] ?? 'device_unknown',
        'type': isBattery ? 'battery' : sensorType,
        'value': value,
        'timestamp': timestamp,
      });

      // 2. Real-time Stream Injection
      if (isBattery) {
        _batteryController.sink.add(value);
      } else if (sensorType == 'cgm') {
        _glucoseController.sink.add(value);
      } else if (sensorType == 'pacemaker') {
        _heartRateController.sink.add(value.toInt());
      }

      _checkSafetyThresholds(isBattery ? 'battery' : sensorType, value);
      CloudSyncService().syncData(patientId: currentPatientId).catchError((e) => print('Sync failed: $e'));
      
    } catch (e) {
      print('Error parsing sensor data: $e');
    }
  }

  void _checkSafetyThresholds(String type, double value) {
    if (type == 'cgm') {
      if (value < 0.70) _emitAlert('CRITICAL: Hypoglycemia ($value g/L)');
      if (value > 2.50) _emitAlert('CRITICAL: Hyperglycemia ($value g/L)');
    } else if (type == 'battery') {
      if (value > 0 && value < 10.0) _emitAlert('CRITICAL: Pacemaker battery low ($value%)');
    } else if (type == 'pacemaker') {
      if (value < 50.0) _emitAlert('CRITICAL: Bradycardia ($value BPM)');
      if (value > 120.0) _emitAlert('WARNING: Tachycardia ($value BPM)');
    }
  }

  void _emitAlert(String message) {
    onAlert?.call(message);
    if (!_alertController.isClosed) _alertController.add(message);
  }

  double? _readDouble(dynamic data, List<String> keys) {
    if (data is! Map) return null;
    for (final k in keys) {
      final v = data[k];
      if (v == null) continue;
      if (v is num) return v.toDouble();
      if (v is String) return double.tryParse(v);
    }
    return null;
  }

  void dispose() {
    _heartRateController.close();
    _glucoseController.close();
    _batteryController.close();
    _alertController.close();
    try {
      client.disconnect();
    } catch (_) {}
  }
}

