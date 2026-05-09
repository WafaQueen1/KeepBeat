import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'theme/app_theme.dart';
import 'ui/navigation_root.dart';
import 'ui/sign_in_ui.dart';
import 'ui/sign_up_ui.dart';
import 'ui/emergency_alert_ui.dart';
import 'ui/reactive_plan_ui.dart';
import 'providers/sensor_service_provider.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ProviderScope(child: KeepBeatApp()));
}

class KeepBeatApp extends ConsumerWidget {
  const KeepBeatApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sensorService = ref.watch(sensorServiceProvider);
    return MaterialApp(
      title: 'KeepBeat — Vital Pulse',
      theme: AppTheme.lightTheme,
      debugShowCheckedModeBanner: false,
      initialRoute: '/signup',
      routes: {
        '/signup': (context) => const SignUpUI(),
        '/login': (context) => const SignInUI(),
        '/dashboard': (context) =>
            NavigationRoot(sensorService: sensorService),
        '/emergency': (context) => const EmergencyAlertUI(),
        '/reactive_plan': (context) => const ReactivePlanUI(),
      },
    );
  }
}
