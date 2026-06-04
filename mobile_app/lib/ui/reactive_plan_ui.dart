import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/app_theme.dart';
import '../providers/patient_provider.dart';
import 'widgets/bento_widgets.dart';

enum AlertType {
  hypoglycemia,
  bradycardia,
  highHeartRate,
  lowBattery,
  disconnected,
  normal
}

class ReactivePlanUI extends ConsumerWidget {
  final AlertType alertType;

  const ReactivePlanUI({
    super.key,
    this.alertType = AlertType.hypoglycemia,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final patient = ref.watch(patientContextProvider);
    final initials = patient.fullName.trim().split(' ').take(2).map((e) => e.isNotEmpty ? e[0] : '').join().toUpperCase();

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.pageGradient),
        child: SafeArea(
          child: Column(
            children: [
              _buildHeader(context, initials),
              Expanded(
                child: SingleChildScrollView(
                  physics: const BouncingScrollPhysics(),
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      _RecoveryHero(alertType: alertType),
                      const SizedBox(height: 24),
                      _ActionPlanSection(alertType: alertType),
                      const SizedBox(height: 120), // Bottom padding
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context, String initials) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 10, 20, 20),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
            onPressed: () => Navigator.of(context).pop(),
          ),
          const AppLogoWordmark(
            assetPath: 'assets/images/logoKeepBeat.png',
            logoSize: 28,
            textSize: 16,
            redText: true,
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
    );
  }
}

class _RecoveryHero extends StatelessWidget {
  final AlertType alertType;

  const _RecoveryHero({required this.alertType});

  @override
  Widget build(BuildContext context) {
    String title;
    String subtitle;
    Color accentColor;

    switch (alertType) {
      case AlertType.hypoglycemia:
        title = 'Glucose Recovery';
        subtitle = 'Vitals are stabilizing. Focus on glycemic balance.';
        accentColor = AppTheme.blue;
        break;
      case AlertType.bradycardia:
        title = 'Rhythm Stabilization';
        subtitle = 'Heart rate is recovering. Maintain calm breathing.';
        accentColor = AppTheme.primary;
        break;
      case AlertType.highHeartRate:
        title = 'Cardiac Cooling';
        subtitle = 'Heart rate is lowering. Keep activity minimal.';
        accentColor = AppTheme.primary;
        break;
      case AlertType.lowBattery:
        title = 'System Maintenance';
        subtitle = 'Device battery is low. Follow replacement protocol.';
        accentColor = AppTheme.lavender;
        break;
      default:
        title = 'Monitoring Stability';
        subtitle = 'Vital signs are returning to baseline.';
        accentColor = AppTheme.blue;
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(38),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 30,
            offset: const Offset(0, 15),
          ),
        ],
      ),
      child: Column(
        children: [
          StatusBadge(label: 'RECOVERY PHASE', color: accentColor),
          const SizedBox(height: 28),
          Stack(
            alignment: Alignment.center,
            children: [
              Container(
                width: 160,
                height: 160,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      accentColor.withOpacity(0.12),
                      Colors.transparent,
                    ],
                  ),
                ),
              ),
              Image.asset(
                'assets/images/heart.png',
                width: 130,
                height: 130,
                fit: BoxFit.contain,
              ),
            ],
          ),
          const SizedBox(height: 24),
          Text(
            title,
            style: AppTheme.textTheme.displaySmall?.copyWith(fontSize: 26),
          ),
          const SizedBox(height: 8),
          Text(
            subtitle,
            textAlign: TextAlign.center,
            style: AppTheme.textTheme.bodyMedium?.copyWith(
              color: AppTheme.onSurface.withOpacity(0.5),
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}

class _ActionPlanSection extends StatelessWidget {
  final AlertType alertType;

  const _ActionPlanSection({required this.alertType});

  @override
  Widget build(BuildContext context) {
    List<_InstructionItem> instructions = [];

    switch (alertType) {
      case AlertType.hypoglycemia:
        instructions = [
          const _InstructionItem(
            icon: Icons.water_drop_rounded,
            color: AppTheme.blue,
            title: 'Verify Glucose Level',
            subtitle: 'Confirm level is below 70 mg/dL before action.',
            isDone: true,
          ),
          const _InstructionItem(
            icon: Icons.fastfood_rounded,
            color: AppTheme.primary,
            title: '15g Glucose Intake',
            subtitle: 'Consume fast-acting carbs (juice/honey).',
          ),
          const _InstructionItem(
            icon: Icons.timer_rounded,
            color: AppTheme.lavender,
            title: 'Wait 15 Minutes',
            subtitle: 'Sit still and allow glucose to absorb.',
          ),
          const _InstructionItem(
            icon: Icons.water_drop_rounded,
            color: AppTheme.blue,
            title: 'Re-check Glucose',
            subtitle: 'Verify if levels are above 90 mg/dL.',
          ),
        ];
        break;
      case AlertType.disconnected:
        instructions = [
          const _InstructionItem(
            icon: Icons.bluetooth_disabled_rounded,
            color: AppTheme.primary,
            title: 'Check Device Position',
            subtitle: 'Ensure sensor is properly attached to skin.',
            isDone: true,
          ),
          const _InstructionItem(
            icon: Icons.refresh_rounded,
            color: AppTheme.blue,
            title: 'Restart Bluetooth',
            subtitle: 'Toggle Bluetooth on your phone settings.',
          ),
          const _InstructionItem(
            icon: Icons.medical_services_rounded,
            color: AppTheme.lavender,
            title: 'Contact Support',
            subtitle: 'If data persists, device may be displaced.',
          ),
        ];
        break;
      case AlertType.bradycardia:
        instructions = [
          const _InstructionItem(
            icon: Icons.air_rounded,
            color: AppTheme.blue,
            title: 'Deep Breathing',
            subtitle: 'Slow, controlled breaths to stabilize rhythm.',
            isDone: true,
          ),
          const _InstructionItem(
            icon: Icons.chair_rounded,
            color: AppTheme.primary,
            title: 'Stay Seated',
            subtitle: 'Avoid standing until heart rate is >60 BPM.',
          ),
          const _InstructionItem(
            icon: Icons.medical_services_rounded,
            color: AppTheme.lavender,
            title: 'Notify Physician',
            subtitle: 'Alert doctor of the low heart rate event.',
          ),
        ];
        break;
      case AlertType.highHeartRate:
        instructions = [
          const _InstructionItem(
            icon: Icons.pan_tool_rounded,
            color: AppTheme.primary,
            title: 'Stop Activity',
            subtitle: 'Immediately cease any physical exertion.',
            isDone: true,
          ),
          const _InstructionItem(
            icon: Icons.local_drink_rounded,
            color: AppTheme.blue,
            title: 'Cool Hydration',
            subtitle: 'Drink cool water and rest in a cool area.',
          ),
          const _InstructionItem(
            icon: Icons.favorite_rounded,
            color: AppTheme.lavender,
            title: 'Monitor Rhythm',
            subtitle: 'Check for stability in the next 10 mins.',
          ),
        ];
        break;
      case AlertType.lowBattery:
        instructions = [
          const _InstructionItem(
            icon: Icons.phone_in_talk_rounded,
            color: AppTheme.lavender,
            title: 'Contact Clinic',
            subtitle: 'Call your cardiologist for ERI verification.',
            isDone: true,
          ),
          const _InstructionItem(
            icon: Icons.calendar_month_rounded,
            color: AppTheme.primary,
            title: 'Schedule Within 48h',
            subtitle: 'Replacement must be planned immediately.',
          ),
          const _InstructionItem(
            icon: Icons.info_outline_rounded,
            color: AppTheme.blue,
            title: 'Limit Stress',
            subtitle: 'Keep physical activity low until replaced.',
          ),
        ];
        break;
      default:
        instructions = [
          const _InstructionItem(
            icon: Icons.check_circle_rounded,
            color: Colors.green,
            title: 'System Normal',
            subtitle: 'No immediate actions required.',
            isDone: true,
          ),
        ];
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4, bottom: 16),
          child: Text(
            'RECOVERY ACTION PLAN',
            style: AppTheme.textTheme.titleSmall?.copyWith(
              letterSpacing: 1.5,
              fontWeight: FontWeight.w800,
              color: AppTheme.onSurface.withOpacity(0.4),
            ),
          ),
        ),
        ...instructions.map((item) => Padding(
              padding: const EdgeInsets.only(bottom: 14),
              child: item,
            )),
        const SizedBox(height: 32),
        StitchButton(
          onTap: () => Navigator.of(context).popUntil((route) => route.isFirst),
          text: 'I AM STABLE',
          backgroundColor: Colors.green.shade600,
        ),
        const SizedBox(height: 40),
      ],
    );
  }
}

class _InstructionItem extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String title;
  final String subtitle;
  final bool isDone;

  const _InstructionItem({
    required this.icon,
    required this.color,
    required this.title,
    required this.subtitle,
    this.isDone = false,
  });

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTheme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w800,
                    decoration: isDone ? TextDecoration.lineThrough : null,
                  ),
                ),
                Text(
                  subtitle,
                  style: AppTheme.textTheme.bodySmall?.copyWith(
                    color: AppTheme.onSurface.withOpacity(0.5),
                  ),
                ),
              ],
            ),
          ),
          Icon(
            isDone ? Icons.check_circle_rounded : Icons.circle_outlined,
            color: isDone ? Colors.green : AppTheme.onSurface.withOpacity(0.2),
          ),
        ],
      ),
    );
  }
}
