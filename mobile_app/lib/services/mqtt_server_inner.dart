import 'package:mqtt_client/mqtt_server_client.dart';
import 'package:mqtt_client/mqtt_client.dart';

MqttClient getClient(String host, String clientId, {int? port}) {
  final client = MqttServerClient(host, clientId);
  if (port != null) client.port = port;
  return client;
}
