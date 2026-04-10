import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';

class ReactivePlanUI extends StatelessWidget {
  const ReactivePlanUI({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surface,
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // ── Header ──
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 16, 20, 0),
              child: Row(
                children: [
                  GestureDetector(
                    onTap: () => Navigator.of(context).pop(),
                    child: Container(
                      width: 44,
                      height: 44,
                      decoration: AppTheme.bentoDecoration,
                      child: const Icon(Icons.arrow_back_rounded,
                          color: AppTheme.primary, size: 20),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('INTERVENTION PROTOCOL',
                          style: AppTheme.textTheme.labelSmall),
                      Text('Reactive Action Plan',
                          style: AppTheme.textTheme.titleLarge),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 8),

            // ── Content ──
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Event summary card
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: AppTheme.primaryCardDecoration,
                      child: Row(
                        children: [
                          Container(
                            width: 48,
                            height: 48,
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(14),
                            ),
                            child: const Icon(Icons.warning_amber_rounded,
                                color: Colors.white, size: 24),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Hypoglycemia Event',
                                  style:
                                      AppTheme.textTheme.titleMedium?.copyWith(
                                    color: Colors.white,
                                    fontSize: 16,
                                  ),
                                ),
                                Text(
                                  'Glucose: 42 mg/dL  •  Detected 5 min ago',
                                  style: AppTheme.textTheme.bodyMedium
                                      ?.copyWith(
                                    color: Colors.white60,
                                    fontSize: 12,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),

                    Text('YOUR ACTION PLAN',
                        style: AppTheme.textTheme.labelSmall),
                    const SizedBox(height: 16),

                    _stepCard(
                      number: 1,
                      icon: Icons.fastfood_rounded,
                      color: AppTheme.accentOrange,
                      title: 'Glucose Re-entry',
                      desc:
                          'Consume 15g of fast-acting glucose as instructed. Options include: 4oz fruit juice, glucose tablets, or 3-4 glucose gels.',
                      duration: '0 – 5 min',
                      done: true,
                    ),
                    const SizedBox(height: 14),

                    _stepCard(
                      number: 2,
                      icon: Icons.airline_seat_recline_normal_rounded,
                      color: AppTheme.accentBlue,
                      title: 'Absolute Rest',
                      desc:
                          'Sit or lay down for 15 minutes. High-pulse activities are strictly restricted. Keep phone accessible.',
                      duration: '5 – 20 min',
                      done: false,
                    ),
                    const SizedBox(height: 14),

                    _stepCard(
                      number: 3,
                      icon: Icons.monitor_heart_rounded,
                      color: AppTheme.primary,
                      title: 'Pulse Verification',
                      desc:
                          'Await the 15-minute predictive pulse update from AI-Sight. Target: heart rate below 100 BPM.',
                      duration: '20 – 35 min',
                      done: false,
                    ),
                    const SizedBox(height: 14),

                    _stepCard(
                      number: 4,
                      icon: Icons.call_rounded,
                      color: AppTheme.accentGreen,
                      title: 'Clinical Check-in',
                      desc:
                          'If glucose does not recover above 70 mg/dL within 30 minutes, contact your assigned doctor or emergency services.',
                      duration: 'If no improvement',
                      done: false,
                    ),
                    const SizedBox(height: 32),

                    StitchButton(
                      onTap: () =>
                          Navigator.of(context).pushReplacementNamed('/dashboard'),
                      text: 'Steps Completed — Return to Dashboard',
                      icon: Icons.check_circle_rounded,
                    ),
                    const SizedBox(height: 16),
                    Center(
                      child: Text(
                        'AI-Sight will automatically monitor your recovery progress.',
                        textAlign: TextAlign.center,
                        style: AppTheme.textTheme.bodyMedium
                            ?.copyWith(fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _stepCard({
    required int number,
    required IconData icon,
    required Color color,
    required String title,
    required String desc,
    required String duration,
    required bool done,
  }) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: AppTheme.bentoDecoration,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Step number + icon
          Column(
            children: [
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: done ? color : color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: done
                    ? const Icon(Icons.check_rounded,
                        color: Colors.white, size: 26)
                    : Icon(icon, color: color, size: 26),
              ),
              const SizedBox(height: 6),
              Text(
                '0$number',
                style: AppTheme.textTheme.labelSmall?.copyWith(
                  color: color,
                  fontSize: 12,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ],
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        title,
                        style: AppTheme.textTheme.labelLarge
                            ?.copyWith(fontSize: 16),
                      ),
                    ),
                    if (done)
                      StatusBadge(label: 'Done', color: AppTheme.accentGreen),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  desc,
                  style: AppTheme.textTheme.bodyMedium?.copyWith(
                    fontSize: 13,
                    height: 1.5,
                  ),
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Icon(Icons.timer_outlined,
                        size: 14, color: AppTheme.onSurfaceMuted),
                    const SizedBox(width: 4),
                    Text(
                      duration,
                      style: AppTheme.textTheme.labelSmall
                          ?.copyWith(fontSize: 10),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
