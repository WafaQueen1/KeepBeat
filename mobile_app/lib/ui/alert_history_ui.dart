import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';

class AlertHistoryUI extends StatelessWidget {
  const AlertHistoryUI({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surface,
      body: StitchBackdrop(
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(18, 10, 18, 120),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: const [
                    CircleAvatar(radius: 18, backgroundImage: AssetImage('assets/images/avatar.png')),
                    SizedBox(width: 12),
                    AppLogoWordmark(assetPath: 'assets/images/logoKeepBeat.png', logoSize: 28, textSize: 18, redText: true),
                    Spacer(),
                    Icon(Icons.notifications, color: Color(0xFF7B7A86)),
                  ],
                ),
                const SizedBox(height: 26),
                Text('Alerts History', style: AppTheme.textTheme.displayMedium?.copyWith(fontSize: 26)),
                const SizedBox(height: 6),
                Text('Real-time health monitoring logs', style: AppTheme.textTheme.bodyLarge),
                const SizedBox(height: 20),
                _alertCard(
                  icon: Icons.ac_unit,
                  iconBg: AppTheme.redSoft,
                  title: 'Hypoglycemia Alert',
                  body: 'Blood glucose dropped below 70 mg/dL. Immediate sugar intake recommended.',
                  time: '2 hours ago',
                  action: 'View Details',
                  chip: 'CRITICAL',
                  accent: AppTheme.primary,
                  tinted: true,
                ),
                const SizedBox(height: 18),
                _alertCard(
                  icon: Icons.sync,
                  iconBg: AppTheme.blueSoft,
                  title: 'Daily Sync Complete',
                  body: 'All health data from your wearable devices has been successfully updated to the cloud twin.',
                  time: 'Today, 8:45 AM',
                  chip: 'SYSTEM',
                  accent: AppTheme.blue,
                ),
                const SizedBox(height: 18),
                _alertCard(
                  icon: Icons.psychology,
                  iconBg: AppTheme.lavenderSoft,
                  title: 'Pattern Detected',
                  body: 'Low activity levels detected in the last 48 hours. Consider a light 15-minute walk to maintain rhythm.',
                  time: 'Yesterday',
                  chip: 'AI INSIGHT',
                  accent: AppTheme.lavender,
                  purple: true,
                  action: 'OPTIMIZE',
                ),
                const SizedBox(height: 18),
                _alertCard(
                  icon: Icons.insert_chart,
                  iconBg: const Color(0xFFEAF2FF),
                  title: 'Monthly Summary Ready',
                  body: 'Your comprehensive heart health report for November is now available for review.',
                  time: 'Nov 1, 10:00 AM',
                  chip: 'ACTIVITY',
                  accent: const Color(0xFF3877F2),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _alertCard({
    required IconData icon,
    required Color iconBg,
    required String title,
    required String body,
    required String time,
    required String chip,
    required Color accent,
    String? action,
    bool tinted = false,
    bool purple = false,
  }) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: purple ? AppTheme.lavenderSoft : (tinted ? const Color(0xFFFFF6F6) : Colors.white),
        borderRadius: BorderRadius.circular(34),
        border: Border.all(color: tinted ? const Color(0xFFF2D4D4) : AppTheme.line),
        boxShadow: const [
          BoxShadow(color: AppTheme.shadow, blurRadius: 24, offset: Offset(0, 10)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(color: iconBg, borderRadius: BorderRadius.circular(18)),
                child: Icon(icon, color: accent),
              ),
              const Spacer(),
              StatusBadge(label: chip, color: accent),
            ],
          ),
          const SizedBox(height: 20),
          Text(title, style: AppTheme.textTheme.headlineMedium?.copyWith(fontSize: 20)),
          const SizedBox(height: 8),
          Text(body, style: AppTheme.textTheme.bodyLarge?.copyWith(color: const Color(0xFF654946))),
          const SizedBox(height: 18),
          const Divider(color: AppTheme.line),
          const SizedBox(height: 12),
          Row(
            children: [
              Text(time, style: AppTheme.textTheme.bodyMedium?.copyWith(color: tinted ? AppTheme.primary : AppTheme.onSurfaceMuted)),
              const Spacer(),
              if (action != null)
                Text(action, style: AppTheme.textTheme.labelLarge?.copyWith(color: accent)),
            ],
          ),
        ],
      ),
    );
  }
}
