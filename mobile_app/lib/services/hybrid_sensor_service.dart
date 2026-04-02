import 'dart:convert';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';

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

  void _evaluateSingleBrainSafetyRule(String topic, String payload) {
    // Single-Brain Rule: All real-time safety thresholds are evaluated ONLY on the Fog
    try {
      final data = jsonDecode(payload);
      if (topic.contains('cgm')) {
        double glucose = data['glucose_level'];
        // Hypo < 0.7 g/L, Hyper > 2.5 g/L
        if (glucose < 0.7) {
          print('🚨 CRITICAL ALERT: Hypoglycemia detected ($glucose g/L)');
          // Trigger local device vibration/alarm & save to offline SQLite!
        } else if (glucose > 2.5) {
          print('🚨 CRITICAL ALERT: Hyperglycemia detected ($glucose g/L)');
          // Trigger local device vibration/alarm & save to offline SQLite!
        }
      }
    } catch (e) {
      print('Error parsing sensor data: $e');
    }
  }
}
