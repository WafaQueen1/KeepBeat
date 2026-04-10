import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'services/hybrid_sensor_service.dart';
import 'theme/app_theme.dart';
import 'ui/navigation_root.dart';
import 'ui/sign_in_ui.dart';
import 'ui/sign_up_ui.dart';
import 'ui/emergency_alert_ui.dart';
import 'ui/reactive_plan_ui.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ProviderScope(child: KeepBeatApp()));
}

class KeepBeatApp extends ConsumerStatefulWidget {
  const KeepBeatApp({super.key});

  @override
  ConsumerState<KeepBeatApp> createState() => _KeepBeatAppState();
}

class _KeepBeatAppState extends ConsumerState<KeepBeatApp> {
  final HybridSensorService _sensorService = HybridSensorService();

  @override
  void initState() {
    super.initState();
    _sensorService.initializeMqtt();
  }

  @override
  void dispose() {
    _sensorService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'KeepBeat — Vital Pulse',
      theme: AppTheme.lightTheme,
      debugShowCheckedModeBanner: false,
      initialRoute: '/signup',
      routes: {
        '/signup': (context) => const SignUpUI(),
        '/login': (context) => const SignInUI(),
        '/dashboard': (context) =>
            NavigationRoot(sensorService: _sensorService),
        '/emergency': (context) => const EmergencyAlertUI(),
        '/reactive_plan': (context) => const ReactivePlanUI(),
      },
    );
  }
}
