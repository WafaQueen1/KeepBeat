import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/hybrid_sensor_service.dart';

final sensorServiceProvider = Provider<HybridSensorService>((ref) {
  final service = HybridSensorService();
  service.initializeMqtt();
  ref.onDispose(service.dispose);
  return service;
});

