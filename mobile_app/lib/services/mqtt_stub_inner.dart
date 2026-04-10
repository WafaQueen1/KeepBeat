import 'package:mqtt_client/mqtt_client.dart';

MqttClient getClient(String host, String clientId, {int? port}) =>
    throw UnsupportedError('Neither dart:io nor dart:html was found');
