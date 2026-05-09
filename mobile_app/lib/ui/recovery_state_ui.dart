import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';

class RecoveryStateUI extends StatelessWidget {
  const RecoveryStateUI({super.key});

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
                    AppLogoWordmark(
                      assetPath: 'assets/images/logoKeepBeat.png',
                      logoSize: 28,
                      textSize: 18,
                      redText: true,
                    ),
                    Spacer(),
                    Icon(Icons.notifications, color: Color(0xFF7C7A87)),
                  ],
                ),
                const SizedBox(height: 22),
                Row(
                  children: [
                    Expanded(child: _miniStat('AVG. HEART RATE', '74', 'BPM', '-2% week', AppTheme.primary, AppTheme.blueSoft)),
                    const SizedBox(width: 12),
                    Expanded(child: _miniStat('AVG. GLUCOSE', '5.6', 'g/L', 'Stable', AppTheme.blue, AppTheme.lavenderSoft)),
                  ],
                ),
                const SizedBox(height: 20),
                BentoTile(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('Heart Rate Trends', style: AppTheme.textTheme.displayMedium?.copyWith(fontSize: 24)),
                                Text('Last 7 days activity', style: AppTheme.textTheme.bodyLarge),
                              ],
                            ),
                          ),
                          Container(
                            width: 48,
                            height: 48,
                            decoration: BoxDecoration(color: AppTheme.redSoft, borderRadius: BorderRadius.circular(16)),
                            child: const Icon(Icons.favorite, color: AppTheme.primary),
                          ),
                        ],
                      ),
                      const SizedBox(height: 24),
                      SizedBox(height: 180, child: CustomPaint(painter: _TrendPainter(color: AppTheme.primary))),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
                            .map((d) => Text(d, style: AppTheme.textTheme.labelSmall))
                            .toList(),
                      ),
                      const SizedBox(height: 16),
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF7F4F4),
                          borderRadius: BorderRadius.circular(18),
                        ),
                        child: const Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            _MetricText(title: 'PEAK BPM', value: '142'),
                            _MetricText(title: 'RESTING', value: '62'),
                            _MetricText(title: 'VARIABILITY', value: '45ms'),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
                BentoTile(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('Glucose Stability', style: AppTheme.textTheme.displayMedium?.copyWith(fontSize: 24)),
                                Text('Daily glycemic index', style: AppTheme.textTheme.bodyLarge),
                              ],
                            ),
                          ),
                          Container(
                            width: 48,
                            height: 48,
                            decoration: BoxDecoration(color: AppTheme.blueSoft, borderRadius: BorderRadius.circular(16)),
                            child: const Icon(Icons.bar_chart, color: AppTheme.blue),
                          ),
                        ],
                      ),
                      const SizedBox(height: 22),
                      SizedBox(height: 180, child: CustomPaint(painter: _TrendPainter(color: AppTheme.blue, fill: true))),
                      const SizedBox(height: 16),
                      Container(
                        padding: const EdgeInsets.all(18),
                        decoration: BoxDecoration(
                          color: AppTheme.lavenderSoft,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.auto_awesome, color: AppTheme.lavender),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                'AI Insight: VitalGlass Prism predicts stable levels for the next 4 hours based on your activity data.',
                                style: AppTheme.textTheme.labelLarge?.copyWith(color: const Color(0xFF7025B0)),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 22),
                Text('Detailed Logs', style: AppTheme.textTheme.displayMedium?.copyWith(fontSize: 24)),
                const SizedBox(height: 14),
                _logItem(Icons.restaurant, 'Post-Lunch Peak', 'Today, 1:45 PM', '6.1 g/L', AppTheme.blue),
                const SizedBox(height: 12),
                _logItem(Icons.directions_run, 'Morning Cardio', 'Today, 8:15 AM', '128 BPM', AppTheme.primary),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _miniStat(String label, String value, String unit, String chip, Color color, Color chipBg) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: AppTheme.bentoDecoration,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: AppTheme.textTheme.labelSmall?.copyWith(color: const Color(0xFF45302D))),
          const SizedBox(height: 10),
          RichText(
            text: TextSpan(
              children: [
                TextSpan(text: value, style: AppTheme.textTheme.displayMedium?.copyWith(fontSize: 30, color: color)),
                TextSpan(text: ' $unit', style: AppTheme.textTheme.titleMedium?.copyWith(color: color.withOpacity(0.8))),
              ],
            ),
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(color: chipBg, borderRadius: BorderRadius.circular(999)),
            child: Text(chip, style: AppTheme.textTheme.labelLarge?.copyWith(color: color)),
          ),
        ],
      ),
    );
  }

  Widget _logItem(IconData icon, String title, String time, String value, Color valueColor) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: AppTheme.bentoDecoration,
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: AppTheme.blueSoft,
              borderRadius: BorderRadius.circular(18),
            ),
            child: Icon(icon, color: valueColor),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: AppTheme.textTheme.titleMedium),
                Text(time, style: AppTheme.textTheme.bodyMedium),
              ],
            ),
          ),
          Text(value, style: AppTheme.textTheme.titleLarge?.copyWith(color: valueColor)),
        ],
      ),
    );
  }
}

class _MetricText extends StatelessWidget {
  final String title;
  final String value;
  const _MetricText({required this.title, required this.value});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: AppTheme.textTheme.labelSmall?.copyWith(color: const Color(0xFF67514C))),
        const SizedBox(height: 6),
        Text(value, style: AppTheme.textTheme.titleLarge),
      ],
    );
  }
}

class _TrendPainter extends CustomPainter {
  final Color color;
  final bool fill;
  const _TrendPainter({required this.color, this.fill = false});

  @override
  void paint(Canvas canvas, Size size) {
    final path = Path();
    final points = [
      Offset(0, size.height * 0.72),
      Offset(size.width * 0.16, size.height * 0.60),
      Offset(size.width * 0.32, size.height * 0.45),
      Offset(size.width * 0.46, size.height * 0.62),
      Offset(size.width * 0.68, size.height * 0.26),
      Offset(size.width * 0.86, size.height * 0.72),
      Offset(size.width, size.height * 0.18),
    ];
    path.moveTo(points.first.dx, points.first.dy);
    for (var i = 0; i < points.length - 1; i++) {
      final a = points[i];
      final b = points[i + 1];
      final cp1 = Offset((a.dx + b.dx) / 2, a.dy);
      final cp2 = Offset((a.dx + b.dx) / 2, b.dy);
      path.cubicTo(cp1.dx, cp1.dy, cp2.dx, cp2.dy, b.dx, b.dy);
    }

    if (fill) {
      final fillPath = Path.from(path)
        ..lineTo(size.width, size.height)
        ..lineTo(0, size.height)
        ..close();
      canvas.drawPath(
        fillPath,
        Paint()
          ..shader = LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [color.withOpacity(0.18), Colors.transparent],
          ).createShader(Rect.fromLTWH(0, 0, size.width, size.height)),
      );
    }

    canvas.drawPath(
      path,
      Paint()
        ..color = color
        ..strokeWidth = 3
        ..style = PaintingStyle.stroke,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
