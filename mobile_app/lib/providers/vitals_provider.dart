import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'sensor_service_provider.dart';

final heartRateProvider = StreamProvider<int>((ref) {
  final service = ref.watch(sensorServiceProvider);
  return service.heartRateStream;
});

final glucoseProvider = StreamProvider<double>((ref) {
  final service = ref.watch(sensorServiceProvider);
  return service.glucoseStream;
});

final batteryProvider = StreamProvider<double>((ref) {
  final service = ref.watch(sensorServiceProvider);
  return service.batteryStream;
});

final latestAlertProvider = StreamProvider<String>((ref) {
  final service = ref.watch(sensorServiceProvider);
  return service.alertStream;
});

