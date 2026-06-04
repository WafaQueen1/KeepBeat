import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../theme/app_theme.dart';
import '../providers/patient_provider.dart';
import 'widgets/bento_widgets.dart';

class AlertHistoryUI extends ConsumerWidget {
  const AlertHistoryUI({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final patient = ref.watch(patientContextProvider);
    final initials = patient.fullName.trim().split(' ').take(2).map((e) => e.isNotEmpty ? e[0] : '').join().toUpperCase();

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.pageGradient),
        child: SafeArea(
          child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.fromLTRB(20, 10, 20, 120),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'ALERTS HISTORY',
                      style: AppTheme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.5,
                      ),
                    ),
                    CircleAvatar(
                      radius: 18,
                      backgroundColor: AppTheme.primary.withOpacity(0.1),
                      child: Text(
                        initials,
                        style: AppTheme.textTheme.titleMedium?.copyWith(
                          color: AppTheme.primary,
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 28),
                Text(
                  'Past Alerts',
                  style: AppTheme.textTheme.displaySmall?.copyWith(fontSize: 32),
                ),
                const SizedBox(height: 8),
                Text(
                  'Historical log of your heart & glucose alerts.',
                  style: AppTheme.textTheme.bodyMedium?.copyWith(
                    color: AppTheme.onSurface.withOpacity(0.6),
                  ),
                ),
                const SizedBox(height: 32),
                _AlertCard(
                  icon: Icons.emergency_rounded,
                  iconBackground: AppTheme.primary.withOpacity(0.1),
                  iconColor: AppTheme.primary,
                  chipLabel: 'CRITICAL',
                  chipColor: AppTheme.primary,
                  title: 'Hypoglycemia Alert',
                  body: 'Blood glucose dropped below 70 mg/dL. Immediate sugar intake was recommended.',
                  time: '2 hours ago',
                  actionLabel: 'View Details',
                  tinted: true,
                ),
                const SizedBox(height: 20),
                _AlertCard(
                  icon: Icons.sync_rounded,
                  iconBackground: AppTheme.blue.withOpacity(0.1),
                  iconColor: AppTheme.blue,
                  chipLabel: 'SYSTEM',
                  chipColor: AppTheme.blue,
                  title: 'Daily Sync Complete',
                  body: 'All health data from your wearable devices has been successfully updated.',
                  time: 'Today, 8:45 AM',
                ),
                const SizedBox(height: 20),
                _AlertCard(
                  icon: Icons.psychology_rounded,
                  iconBackground: AppTheme.lavender.withOpacity(0.1),
                  iconColor: AppTheme.lavender,
                  chipLabel: 'AI INSIGHT',
                  chipColor: AppTheme.lavender,
                  title: 'Pattern Detected',
                  body: 'Low activity levels detected in the last 48 hours. AI recommends a light walk.',
                  time: 'Yesterday',
                  actionLabel: 'OPTIMIZE',
                  purple: true,
                  buttonAction: true,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _AlertCard extends StatelessWidget {
  final IconData icon;
  final Color iconBackground;
  final Color iconColor;
  final String chipLabel;
  final Color chipColor;
  final String title;
  final String body;
  final String time;
  final String? actionLabel;
  final bool tinted;
  final bool purple;
  final bool buttonAction;

  const _AlertCard({
    required this.icon,
    required this.iconBackground,
    required this.iconColor,
    required this.chipLabel,
    required this.chipColor,
    required this.title,
    required this.body,
    required this.time,
    this.actionLabel,
    this.tinted = false,
    this.purple = false,
    this.buttonAction = false,
  });

  @override
  Widget build(BuildContext context) {
    final backgroundColor = purple
        ? AppTheme.lavenderSoft.withOpacity(0.72)
        : tinted
            ? const Color(0xFFFFF5F5)
            : Colors.white;
    return Container(
      padding: const EdgeInsets.all(26),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(34),
        boxShadow: const [
          BoxShadow(
            color: AppTheme.shadow,
            blurRadius: 28,
            offset: Offset(0, 12),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 58,
                height: 58,
                decoration: BoxDecoration(
                  color: iconBackground,
                  borderRadius: BorderRadius.circular(18),
                ),
                child: Icon(icon, color: iconColor, size: 30),
              ),
              const Spacer(),
              StatusBadge(
                label: chipLabel,
                color: chipColor,
                inverted: tinted,
              ),
            ],
          ),
          const SizedBox(height: 24),
          Text(
            title,
            style: AppTheme.textTheme.headlineMedium?.copyWith(fontSize: 22),
          ),
          const SizedBox(height: 10),
          Text(
            body,
            style: AppTheme.textTheme.bodyLarge?.copyWith(
              color: AppTheme.onSurface.withOpacity(0.70),
            ),
          ),
          const SizedBox(height: 20),
          Container(height: 1, color: AppTheme.lineSoft),
          const SizedBox(height: 16),
          Row(
            children: [
              Text(
                time,
                style: AppTheme.textTheme.bodyMedium?.copyWith(
                  color: tinted ? AppTheme.primary : AppTheme.onSurfaceMuted,
                ),
              ),
              const Spacer(),
              if (actionLabel != null && !buttonAction)
                Row(
                  children: [
                    Text(
                      actionLabel!,
                      style: AppTheme.textTheme.labelLarge?.copyWith(
                        color: chipColor,
                      ),
                    ),
                    const SizedBox(width: 4),
                    Icon(
                      Icons.chevron_right_rounded,
                      color: chipColor,
                      size: 18,
                    ),
                  ],
                ),
              if (actionLabel != null && buttonAction)
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 18,
                    vertical: 10,
                  ),
                  decoration: BoxDecoration(
                    color: AppTheme.lavender,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    actionLabel!,
                    style: AppTheme.textTheme.labelLarge?.copyWith(
                      color: Colors.white,
                    ),
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}
