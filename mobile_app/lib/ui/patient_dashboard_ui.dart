import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/vitals_provider.dart';
import '../services/hybrid_sensor_service.dart';
import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';

class PatientDashboardUI extends ConsumerStatefulWidget {
  final HybridSensorService sensorService;
  final VoidCallback onNavigateToAI;

  const PatientDashboardUI({
    super.key,
    required this.sensorService,
    required this.onNavigateToAI,
  });

  @override
  ConsumerState<PatientDashboardUI> createState() => _PatientDashboardUIState();
}

class _PatientDashboardUIState extends ConsumerState<PatientDashboardUI>
    with SingleTickerProviderStateMixin {
  late final AnimationController _orbController;

  @override
  void initState() {
    super.initState();
    _orbController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2400),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _orbController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final heartRate = ref.watch(heartRateProvider).value ?? 72;
    final glucose = ref.watch(glucoseProvider).value ?? 5.4;
    final batteryPct = ref.watch(batteryProvider).value ?? 82.0;
    final latestAlert = ref.watch(latestAlertProvider).value;

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.pageGradient),
        child: SafeArea(
          child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.fromLTRB(20, 14, 20, 120),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  children: [
                    const CircleAvatar(
                      radius: 22,
                      backgroundImage: AssetImage('assets/images/avatar.png'),
                    ),
                    const SizedBox(width: 12),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'WELCOME BACK,',
                          style: AppTheme.textTheme.labelSmall?.copyWith(
                            fontSize: 9,
                            letterSpacing: 2,
                            color: AppTheme.onSurface.withOpacity(0.5),
                          ),
                        ),
                        Text(
                          'Wafa Queen',
                          style: AppTheme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w800,
                            fontSize: 18,
                          ),
                        ),
                      ],
                    ),
                    const Spacer(),
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.04),
                            blurRadius: 10,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: const Icon(Icons.notifications_none_rounded, color: AppTheme.onSurface),
                    ),
                  ],
                ),
                const SizedBox(height: 32),
                _HeroOrb(animation: _orbController),
                const SizedBox(height: 32),
                _HeartRateCard(heartRate: heartRate),
                const SizedBox(height: 18),
                Row(
                  children: [
                    Expanded(
                      child: VitalBentoCard(
                        label: 'Glucose',
                        value: glucose.toStringAsFixed(1),
                        unit: 'mg/dL',
                        icon: Icons.water_drop_rounded,
                        accent: AppTheme.blue,
                        status: (glucose < 70 || glucose > 180)
                            ? 'ALERT'
                            : 'OPTIMAL',
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: VitalBentoCard(
                        label: 'Battery',
                        value: batteryPct.toInt().toString(),
                        unit: '%',
                        icon: Icons.bolt_rounded,
                        accent: AppTheme.lavender,
                        trailing: CircularStatusIndicator(
                          value: (batteryPct.clamp(0, 100)) / 100,
                          color: AppTheme.lavender,
                          size: 38,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 18),
                AiInsightBanner(
                  title: 'AI INSIGHT',
                  description:
                      "Your cardiac rhythm is perfectly synchronized. Recovery rate is 94%.",
                  icon: Icons.auto_awesome_rounded,
                  onTap: widget.onNavigateToAI,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _HeroOrb extends StatelessWidget {
  final AnimationController animation;

  const _HeroOrb({required this.animation});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Stack(
        alignment: Alignment.center,
        clipBehavior: Clip.none,
        children: [
          // Background Glow
          Container(
            width: 280,
            height: 280,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: const Color(0xFF1A1D21),
              boxShadow: [
                BoxShadow(
                  color: AppTheme.primary.withOpacity(0.15),
                  blurRadius: 80,
                  offset: const Offset(0, 40),
                ),
              ],
            ),
          ),
          // Inner Glass Gradient
          Container(
            width: 240,
            height: 240,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFF32383E),
                  Color(0xFF17191C),
                ],
              ),
              border: Border.all(color: Colors.white.withOpacity(0.05), width: 1.5),
            ),
          ),
          // Heart Image
          AnimatedBuilder(
            animation: animation,
            builder: (context, child) {
              final scale = 1.0 + (0.05 * animation.value);
              return Transform.scale(
                scale: scale,
                child: child,
              );
            },
            child: Image.asset(
              'assets/images/heart.png',
              width: 160,
              height: 160,
              fit: BoxFit.contain,
            ),
          ),
          // Status Badge
          Positioned(
            bottom: -10,
            child: GlassCard(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      color: Color(0xFF00C853),
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Text(
                    'OPTIMAL STATUS',
                    style: AppTheme.textTheme.labelSmall?.copyWith(
                      color: AppTheme.onSurface,
                      letterSpacing: 1.5,
                      fontSize: 10,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _HeartRateCard extends StatelessWidget {
  final int heartRate;

  const _HeartRateCard({required this.heartRate});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFFDA3433),
            Color(0xFFB6171E),
          ],
        ),
        borderRadius: BorderRadius.circular(32),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primary.withOpacity(0.24),
            blurRadius: 36,
            offset: const Offset(0, 18),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'HEART RATE',
                    style: AppTheme.textTheme.labelSmall?.copyWith(
                      color: Colors.white.withOpacity(0.8),
                      letterSpacing: 1.5,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        '$heartRate',
                        style: AppTheme.textTheme.displayLarge?.copyWith(
                          color: Colors.white,
                          fontSize: 64,
                          height: 1,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: Text(
                          'BPM',
                          style: AppTheme.textTheme.labelLarge?.copyWith(
                            color: Colors.white.withOpacity(0.6),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Icon(Icons.favorite_rounded, color: Colors.white, size: 32),
              ),
            ],
          ),
          const SizedBox(height: 24),
          // Mini Waveform Placeholder
          SizedBox(
            height: 40,
            width: double.infinity,
            child: CustomPaint(
              painter: WaveformPainter(),
            ),
          ),
        ],
      ),
    );
  }
}

class WaveformPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;

    final path = Path();
    path.moveTo(0, size.height / 2);
    for (double i = 0; i < size.width; i += 10) {
      path.lineTo(i, size.height / 2 + (i % 20 == 0 ? -15 : 15));
    }
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => false;
}
