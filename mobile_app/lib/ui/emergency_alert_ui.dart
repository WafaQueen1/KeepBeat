import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';
import 'reactive_plan_ui.dart';

class EmergencyAlertUI extends StatelessWidget {
  final AlertType alertType;

  const EmergencyAlertUI({
    super.key,
    this.alertType = AlertType.hypoglycemia,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.emergencyGradient),
        child: Stack(
          children: [
            // Urgent Pulse Orbs
            Positioned(
              top: 100,
              left: -40,
              child: _PulseOrb(size: 320, color: Colors.white.withOpacity(0.08)),
            ),
            Positioned(
              bottom: 100,
              right: -80,
              child: _PulseOrb(size: 400, color: Colors.white.withOpacity(0.05)),
            ),
            SafeArea(
              child: Column(
                children: [
                  _buildHeader(context),
                  Expanded(
                    child: SingleChildScrollView(
                      physics: const BouncingScrollPhysics(),
                      padding: const EdgeInsets.symmetric(horizontal: 20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          _EmergencyHero(alertType: alertType),
                          const SizedBox(height: 32),
                          _MachineCheckList(alertType: alertType),
                          const SizedBox(height: 24),
                          _ActionCard(alertType: alertType),
                          const SizedBox(height: 40),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      child: Row(
        children: [
          GestureDetector(
            onTap: () => Navigator.pop(context),
            child: Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.12),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.close_rounded, color: Colors.white),
            ),
          ),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.12),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              children: [
                const Icon(Icons.security_rounded, color: Colors.white, size: 16),
                const SizedBox(width: 6),
                Text(
                  'SECURE LINK',
                  style: AppTheme.textTheme.labelSmall?.copyWith(
                    color: Colors.white,
                    fontSize: 10,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _EmergencyHero extends StatelessWidget {
  final AlertType alertType;
  const _EmergencyHero({required this.alertType});

  String _getTitle() {
    switch (alertType) {
      case AlertType.hypoglycemia:
        return 'HYPOGLYCEMIA ALERT';
      case AlertType.bradycardia:
        return 'LOW HEART RATE';
      case AlertType.highHeartRate:
        return 'HIGH HEART RATE';
      case AlertType.lowBattery:
        return 'PACEMAKER ALERT';
      case AlertType.disconnected:
        return 'PACEMAKER DISCONNECTED';
      default:
        return 'SYSTEM ALERT';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(28),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.12),
            shape: BoxShape.circle,
            border: Border.all(color: Colors.white.withOpacity(0.2)),
          ),
          child: const Icon(Icons.warning_rounded, size: 80, color: Colors.white),
        ),
        const SizedBox(height: 24),
        Text(
          _getTitle(),
          style: AppTheme.textTheme.displaySmall?.copyWith(
            color: Colors.white,
            letterSpacing: 2,
            fontWeight: FontWeight.w900,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 8),
        Text(
          'CRITICAL SITUATION DETECTED',
          style: AppTheme.textTheme.labelSmall?.copyWith(
            color: Colors.white.withOpacity(0.8),
            fontWeight: FontWeight.w600,
            letterSpacing: 1.2,
          ),
        ),
      ],
    );
  }
}

class _MachineCheckList extends StatelessWidget {
  final AlertType alertType;
  const _MachineCheckList({required this.alertType});

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.analytics_outlined, color: AppTheme.primary, size: 24),
              const SizedBox(width: 12),
              Text(
                'MACHINE VERIFICATION',
                style: AppTheme.textTheme.labelLarge?.copyWith(
                  fontSize: 14,
                  letterSpacing: 1,
                  color: AppTheme.onSurface,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          _buildStep(
            'Step 1',
            alertType == AlertType.lowBattery
                ? 'Checking Pacemaker Battery... ERI (12%)'
                : 'Checking Pacemaker Status... OK',
            alertType == AlertType.lowBattery ? false : true,
          ),
          const SizedBox(height: 16),
          _buildStep(
            'Step 2',
            _getStep2Text(),
            alertType == AlertType.hypoglycemia ? false : true,
          ),
        ],
      ),
    );
  }

  String _getStep2Text() {
    switch (alertType) {
      case AlertType.hypoglycemia:
        return 'Verifying Glucose Sensor... Low (65 mg/dL)';
      case AlertType.bradycardia:
        return 'Analyzing Heart Rate... Low (45 BPM)';
      case AlertType.highHeartRate:
        return 'Analyzing Heart Rate... High (115 BPM)';
      case AlertType.lowBattery:
        return 'Syncing Clinical Data... SUCCESS';
      case AlertType.disconnected:
        return 'Verifying Pacemaker Data... SIGNAL LOST';
      default:
        return 'Analyzing Sensors... OK';
    }
  }

  Widget _buildStep(String step, String label, bool isOk) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: AppTheme.primary.withOpacity(0.1),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            step,
            style: AppTheme.textTheme.labelSmall?.copyWith(
              color: AppTheme.primary,
              fontWeight: FontWeight.bold,
              fontSize: 10,
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            label,
            style: AppTheme.textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w600,
              color: AppTheme.onSurface,
            ),
          ),
        ),
        Icon(
          isOk ? Icons.check_circle_rounded : Icons.error_rounded,
          color: isOk ? Colors.green : AppTheme.primary,
          size: 20,
        ),
      ],
    );
  }
}

class _ActionCard extends StatelessWidget {
  final AlertType alertType;
  const _ActionCard({required this.alertType});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(38),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.2),
            blurRadius: 40,
            offset: const Offset(0, 20),
          ),
        ],
      ),
      child: Column(
        children: [
          Text(
            'IMMEDIATE ACTIONS',
            style: AppTheme.textTheme.titleLarge?.copyWith(
              color: AppTheme.onSurface,
              letterSpacing: 1,
            ),
          ),
          const SizedBox(height: 24),
          ..._getTasks(),
          const SizedBox(height: 32),
          StitchButton(
            onTap: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => ReactivePlanUI(alertType: alertType),
                ),
              );
            },
            text: 'VIEW ACTION PLAN',
            backgroundColor: AppTheme.primary,
          ),
          const SizedBox(height: 16),
          StitchButton(
            onTap: () => Navigator.of(context).pop(),
            text: 'I AM STABLE',
            backgroundColor: Colors.white,
            textColor: AppTheme.onSurface.withOpacity(0.6),
            border: Border.all(color: AppTheme.line),
          ),
        ],
      ),
    );
  }

  List<Widget> _getTasks() {
    switch (alertType) {
      case AlertType.hypoglycemia:
        return [
          const _PatientTask(icon: Icons.fastfood_rounded, task: 'Eat 15g Fast-Acting Sugar'),
          const SizedBox(height: 12),
          const _PatientTask(icon: Icons.chair_rounded, task: 'Sit Down and Stay Calm'),
        ];
      case AlertType.bradycardia:
        return [
          const _PatientTask(icon: Icons.air_rounded, task: 'Take Deep Breaths'),
          const SizedBox(height: 12),
          const _PatientTask(icon: Icons.chair_rounded, task: 'Stay Seated Immediately'),
        ];
      case AlertType.highHeartRate:
        return [
          const _PatientTask(icon: Icons.stop_circle_outlined, task: 'Stop All Physical Activity'),
          const SizedBox(height: 12),
          const _PatientTask(icon: Icons.water_drop_rounded, task: 'Drink Cool Water'),
        ];
      case AlertType.lowBattery:
        return [
          const _PatientTask(icon: Icons.phone_callback_rounded, task: 'Contact Your Doctor'),
          const SizedBox(height: 12),
          const _PatientTask(icon: Icons.medical_services_rounded, task: 'Schedule Clinic Visit'),
        ];
      case AlertType.disconnected:
        return [
          const _PatientTask(icon: Icons.bluetooth_disabled_rounded, task: 'Check Pacemaker Connection'),
          const SizedBox(height: 12),
          const _PatientTask(icon: Icons.refresh_rounded, task: 'Restart Device Pairing'),
          const SizedBox(height: 12),
          const _PatientTask(icon: Icons.emergency_rounded, task: 'Sit Down Immediately'),
        ];
      default:
        return [
          const _PatientTask(icon: Icons.info_outline_rounded, task: 'Remain Calm'),
          const SizedBox(height: 12),
          const _PatientTask(icon: Icons.timer_rounded, task: 'Wait for Clinical Update'),
        ];
    }
  }
}

class _PatientTask extends StatelessWidget {
  final IconData icon;
  final String task;

  const _PatientTask({required this.icon, required this.task});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: AppTheme.primary.withOpacity(0.08),
            borderRadius: BorderRadius.circular(14),
          ),
          child: Icon(icon, color: AppTheme.primary, size: 22),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Text(
            task,
            style: AppTheme.textTheme.bodyLarge?.copyWith(
              fontWeight: FontWeight.w700,
              fontSize: 15,
            ),
          ),
        ),
      ],
    );
  }
}

class _PulseOrb extends StatelessWidget {
  final double size;
  final Color color;

  const _PulseOrb({required this.size, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: color,
      ),
    );
  }
}
