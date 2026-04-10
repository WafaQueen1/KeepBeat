import 'package:mqtt_client/mqtt_browser_client.dart';
import 'package:mqtt_client/mqtt_client.dart';

MqttClient getClient(String host, String clientId, {int? port}) {
  // For web, use WebSocket port (default 9001 for this project)
  final String websocketHost = host.startsWith('ws://') || host.startsWith('wss://') ? host : 'ws://$host';
  final client = MqttBrowserClient(websocketHost, clientId);
  client.port = port ?? 9001;
  return client;
}
