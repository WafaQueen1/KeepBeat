import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';

class EmergencyAlertUI extends StatelessWidget {
  const EmergencyAlertUI({super.key});

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
                  Padding(
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
                                style: AppTheme.textTheme.labelSmall?.copyWith(color: Colors.white, fontSize: 10),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  Expanded(
                    child: SingleChildScrollView(
                      physics: const BouncingScrollPhysics(),
                      padding: const EdgeInsets.fromLTRB(24, 20, 24, 40),
                      child: Column(
                        children: [
                          const SizedBox(height: 20),
                          // Giant Urgent Icon
                          Container(
                            width: 180,
                            height: 180,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: Colors.white.withOpacity(0.1),
                              border: Border.all(color: Colors.white.withOpacity(0.2), width: 2),
                            ),
                            child: Center(
                              child: Container(
                                width: 130,
                                height: 130,
                                decoration: const BoxDecoration(
                                  color: Colors.white,
                                  shape: BoxShape.circle,
                                  boxShadow: [
                                    BoxShadow(color: Colors.black26, blurRadius: 30, offset: Offset(0, 15)),
                                  ],
                                ),
                                child: const Icon(
                                  Icons.warning_amber_rounded,
                                  color: AppTheme.primary,
                                  size: 72,
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(height: 40),
                          Text(
                            'EMERGENCY ALERT',
                            style: AppTheme.textTheme.labelLarge?.copyWith(
                              color: Colors.white.withOpacity(0.9),
                              letterSpacing: 4,
                              fontWeight: FontWeight.w900,
                            ),
                          ),
                          const SizedBox(height: 12),
                          Text(
                            'CRITICAL GLUCOSE',
                            textAlign: TextAlign.center,
                            style: AppTheme.textTheme.displayMedium?.copyWith(
                              color: Colors.white,
                              fontSize: 38,
                              height: 1.1,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            '42 mg/dL',
                            style: AppTheme.textTheme.displayLarge?.copyWith(
                              color: Colors.white,
                              fontSize: 56,
                            ),
                          ),
                          const SizedBox(height: 40),
                          // Action Card
                          GlassCard(
                            padding: const EdgeInsets.all(28),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.all(8),
                                      decoration: BoxDecoration(
                                        color: AppTheme.primary.withOpacity(0.1),
                                        borderRadius: BorderRadius.circular(10),
                                      ),
                                      child: const Icon(Icons.bolt_rounded, color: AppTheme.primary),
                                    ),
                                    const SizedBox(width: 12),
                                    Text(
                                      'IMMEDIATE ACTION',
                                      style: AppTheme.textTheme.labelSmall?.copyWith(color: AppTheme.primary),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 20),
                                Text(
                                  'Consume 15g of fast-acting sugar (e.g., fruit juice, honey, or glucose tabs) immediately.',
                                  style: AppTheme.textTheme.bodyLarge?.copyWith(
                                    height: 1.4,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                const SizedBox(height: 24),
                                StitchButton(
                                  onTap: () {},
                                  text: 'Call Emergency (911)',
                                  icon: Icons.phone_in_talk_rounded,
                                  height: 64,
                                ),
                                const SizedBox(height: 14),
                                StitchButton(
                                  onTap: () => Navigator.pushNamed(context, '/reactive_plan'),
                                  text: 'Full Reactive Plan',
                                  backgroundColor: Colors.transparent,
                                  textColor: AppTheme.primary,
                                  border: Border.all(color: AppTheme.primary.withOpacity(0.2)),
                                  height: 58,
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 32),
                          Text(
                            'AI DIAGNOSIS: SEVERE HYPOGLYCEMIA',
                            style: AppTheme.textTheme.labelSmall?.copyWith(
                              color: Colors.white.withOpacity(0.6),
                              letterSpacing: 1.2,
                            ),
                          ),
                          const SizedBox(height: 20),
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
