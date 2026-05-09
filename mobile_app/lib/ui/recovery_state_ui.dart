import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';

class RecoveryStateUI extends StatelessWidget {
  const RecoveryStateUI({super.key});

  @override
  Widget build(BuildContext context) {
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
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                    Text(
                      'RECOVERY PLAN',
                      style: AppTheme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.2,
                      ),
                    ),
                    const Spacer(),
                    const CircleAvatar(
                      radius: 18,
                      backgroundImage: AssetImage('assets/images/avatar.png'),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                // Phase Card
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [Color(0xFF6E56CF), Color(0xFF533F9F)],
                    ),
                    borderRadius: BorderRadius.circular(32),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF6E56CF).withOpacity(0.3),
                        blurRadius: 30,
                        offset: const Offset(0, 15),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.history_toggle_off_rounded, color: Colors.white),
                          const SizedBox(width: 12),
                          Text(
                            'RECOVERY PHASE 1',
                            style: AppTheme.textTheme.labelSmall?.copyWith(
                              color: Colors.white.withOpacity(0.8),
                              letterSpacing: 2,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'GLUCOSE STABILIZATION',
                        style: AppTheme.textTheme.headlineMedium?.copyWith(
                          color: Colors.white,
                          fontSize: 22,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Vital signs normalization in progress. AI is monitoring stability patterns.',
                        style: AppTheme.textTheme.bodyMedium?.copyWith(
                          color: Colors.white.withOpacity(0.9),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                // Digital Twin Section
                BentoTile(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('DIGITAL TWIN STATUS', style: AppTheme.textTheme.labelSmall),
                          const StatusBadge(label: 'SYNCED', color: AppTheme.blue),
                        ],
                      ),
                      const SizedBox(height: 24),
                      Center(
                        child: Container(
                          width: 200,
                          height: 200,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            gradient: RadialGradient(
                              colors: [
                                Colors.white.withOpacity(0.05),
                                Colors.black.withOpacity(0.05),
                              ],
                            ),
                          ),
                          child: Image.asset(
                            'assets/images/heart.png',
                            fit: BoxFit.contain,
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                      Row(
                        children: [
                          Expanded(
                            child: _RecoveryMetric(
                              label: 'HEART RATE',
                              value: '82',
                              unit: 'BPM',
                              color: AppTheme.primary,
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: _RecoveryMetric(
                              label: 'GLUCOSE',
                              value: '78',
                              unit: 'MG/DL',
                              color: AppTheme.blue,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                // Instruction List
                Text(
                  'IMMEDIATE STEPS',
                  style: AppTheme.textTheme.labelSmall?.copyWith(letterSpacing: 2),
                ),
                const SizedBox(height: 16),
                _InstructionItem(
                  icon: Icons.check_circle_outline_rounded,
                  title: 'Check Glucose Level',
                  description: 'Verify current sugar levels before consuming any fast-acting carbs.',
                  color: AppTheme.blue,
                ),
                const SizedBox(height: 12),
                _InstructionItem(
                  icon: Icons.medical_services_outlined,
                  title: 'Sit & Rest',
                  description: 'Avoid physical activity for at least 15 minutes until HR stabilizes.',
                  color: AppTheme.primary,
                ),
                const SizedBox(height: 12),
                _InstructionItem(
                  icon: Icons.contact_support_outlined,
                  title: 'Notify Doctor',
                  description: 'If disconnect occurs, check if pacemaker is correctly positioned.',
                  color: AppTheme.lavender,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

class _RecoveryMetric extends StatelessWidget {
  final String label;
  final String value;
  final String unit;
  final Color color;

  const _RecoveryMetric({
    required this.label,
    required this.value,
    required this.unit,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: AppTheme.textTheme.labelSmall?.copyWith(fontSize: 9)),
        const SizedBox(height: 8),
        RichText(
          text: TextSpan(
            children: [
              TextSpan(
                text: value,
                style: AppTheme.textTheme.displaySmall?.copyWith(color: color, fontSize: 32),
              ),
              TextSpan(
                text: ' $unit',
                style: AppTheme.textTheme.labelLarge?.copyWith(color: AppTheme.onSurfaceMuted),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _InstructionItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final Color color;

  const _InstructionItem({
    required this.icon,
    required this.title,
    required this.description,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 15,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
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
                  style: AppTheme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: AppTheme.textTheme.bodyMedium?.copyWith(color: AppTheme.onSurfaceMuted),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
