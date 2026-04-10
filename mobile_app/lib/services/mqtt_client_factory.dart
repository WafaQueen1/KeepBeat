import 'package:mqtt_client/mqtt_client.dart';
import 'mqtt_stub_inner.dart'
    if (dart.library.io) 'mqtt_server_inner.dart'
    if (dart.library.html) 'mqtt_browser_inner.dart';

abstract class MqttClientFactory {
  static MqttClient createClient(String host, String clientId, {int? port}) {
    return getClient(host, clientId, port: port);
  }
}
