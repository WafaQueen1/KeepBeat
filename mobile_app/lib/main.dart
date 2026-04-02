import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'services/hybrid_sensor_service.dart';
import 'theme/app_theme.dart';
import 'ui/patient_mobile_ui.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ProviderScope(child: TwinPacemakerApp()));
}

class TwinPacemakerApp extends ConsumerStatefulWidget {
  const TwinPacemakerApp({super.key});

  @override
  ConsumerState<TwinPacemakerApp> createState() => _TwinPacemakerAppState();
}

class _TwinPacemakerAppState extends ConsumerState<TwinPacemakerApp> {
  final HybridSensorService _sensorService = HybridSensorService();

  @override
  void initState() {
    super.initState();
    // Initialize MQTT ingestion upon startup (Offline + Local Network first)
    _sensorService.initializeMqtt();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TwinPacemaker - VitalGlass Prism',
      theme: AppTheme.lightTheme,
      home: PatientMobileUI(sensorService: _sensorService),
      debugShowCheckedModeBanner: false,
    );
  }
}
