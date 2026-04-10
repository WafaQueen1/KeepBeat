import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';

class EmergencyAlertUI extends StatefulWidget {
  const EmergencyAlertUI({super.key});

  @override
  State<EmergencyAlertUI> createState() => _EmergencyAlertUIState();
}

class _EmergencyAlertUIState extends State<EmergencyAlertUI>
    with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;
  late Animation<double> _pulseAnim;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    )..repeat(reverse: true);
    _pulseAnim = Tween<double>(begin: 0.92, end: 1.08)
        .chain(CurveTween(curve: Curves.easeInOut))
        .animate(_pulseController);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.primary,
      body: SafeArea(
        child: Column(
          children: [
            // ── Top bar ──
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 12, 20, 0),
              child: Row(
                children: [
                  GestureDetector(
                    onTap: () => Navigator.of(context).pop(),
                    child: Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Icon(Icons.arrow_back_rounded,
                          color: Colors.white, size: 20),
                    ),
                  ),
                  const Spacer(),
                  Text(
                    'EMERGENCY PROTOCOL',
                    style: AppTheme.textTheme.labelSmall?.copyWith(
                      color: Colors.white60,
                      letterSpacing: 1.6,
                      fontSize: 10,
                    ),
                  ),
                  const Spacer(),
                  const SizedBox(width: 40),
                ],
              ),
            ),

            // ── Alert Hero ──
            Expanded(
              flex: 2,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Pulsing warning icon
                  AnimatedBuilder(
                    animation: _pulseAnim,
                    builder: (_, __) => Transform.scale(
                      scale: _pulseAnim.value,
                      child: Container(
                        width: 100,
                        height: 100,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.15),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.warning_amber_rounded,
                          color: Colors.white,
                          size: 52,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  Text(
                    'HYPOGLYCEMIA',
                    style: AppTheme.textTheme.labelSmall?.copyWith(
                      color: Colors.white60,
                      fontSize: 12,
                      letterSpacing: 2.4,
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    '42 mg/dL',
                    style: AppTheme.textTheme.displayMedium?.copyWith(
                      color: Colors.white,
                      fontSize: 52,
                      fontWeight: FontWeight.w900,
                      letterSpacing: -2,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(100),
                    ),
                    child: Text(
                      'Critical — Immediate Action Required',
                      style: AppTheme.textTheme.labelLarge?.copyWith(
                        color: Colors.white,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // ── Action Panel ──
            Expanded(
              flex: 3,
              child: Container(
                margin: const EdgeInsets.all(12),
                padding: const EdgeInsets.fromLTRB(24, 28, 24, 24),
                decoration: const BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.all(Radius.circular(32)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text('IMMEDIATE STEPS',
                        style: AppTheme.textTheme.labelSmall),
                    const SizedBox(height: 20),

                    _actionStep(
                      step: '01',
                      icon: Icons.fastfood_rounded,
                      title: 'Glucose Intake',
                      desc:
                          'Consume 15g of fast-acting carbs (juice, glucose tabs).',
                      color: AppTheme.accentOrange,
                    ),
                    const Divider(height: 28),
                    _actionStep(
                      step: '02',
                      icon: Icons.airline_seat_recline_extra_rounded,
                      title: 'Rest & Position',
                      desc:
                          'Sit or lay down immediately. Avoid any physical exertion.',
                      color: AppTheme.accentBlue,
                    ),
                    const Divider(height: 28),
                    _actionStep(
                      step: '03',
                      icon: Icons.timer_rounded,
                      title: 'Wait 15 Minutes',
                      desc:
                          'Recheck glucose level. Contact doctor if no improvement.',
                      color: AppTheme.accentPurple,
                    ),

                    const Spacer(),

                    // ── Action Buttons ──
                    StitchButton(
                      onTap: () {},
                      text: 'Call Emergency Services',
                      icon: Icons.phone_rounded,
                    ),
                    const SizedBox(height: 10),
                    StitchButton(
                      onTap: () =>
                          Navigator.of(context).pushNamed('/reactive_plan'),
                      text: 'View Full Action Plan',
                      backgroundColor: AppTheme.background,
                      textColor: AppTheme.primary,
                      icon: Icons.list_alt_rounded,
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

  Widget _actionStep({
    required String step,
    required IconData icon,
    required String title,
    required String desc,
    required Color color,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(14),
          ),
          child: Icon(icon, color: color, size: 24),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: AppTheme.textTheme.labelLarge?.copyWith(fontSize: 15),
              ),
              const SizedBox(height: 3),
              Text(
                desc,
                style: AppTheme.textTheme.bodyMedium?.copyWith(fontSize: 13),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
