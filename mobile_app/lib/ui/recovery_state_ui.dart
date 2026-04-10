import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class RecoveryStateUI extends StatefulWidget {
  const RecoveryStateUI({super.key});

  @override
  State<RecoveryStateUI> createState() => _RecoveryStateUIState();
}

class _RecoveryStateUIState extends State<RecoveryStateUI>
    with SingleTickerProviderStateMixin {
  late AnimationController _progressController;

  @override
  void initState() {
    super.initState();
    _progressController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
      value: 0.72,
    );
    _progressController.animateTo(0.72, duration: const Duration(milliseconds: 1400), curve: Curves.easeOut);
  }

  @override
  void dispose() {
    _progressController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surface,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(24, 20, 24, 110),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // ── Header ──
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('AI RECOVERY STATE',
                          style: AppTheme.textTheme.labelSmall),
                      const SizedBox(height: 4),
                      Text('Recovery Mode',
                          style: AppTheme.textTheme.headlineMedium),
                    ],
                  ),
                  Container(
                    width: 44,
                    height: 44,
                    decoration: AppTheme.bentoDecoration,
                    child: const Icon(Icons.info_outline_rounded,
                        color: AppTheme.primary, size: 20),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // ── Hero Recovery Card ──
              Container(
                padding: const EdgeInsets.all(28),
                decoration: AppTheme.primaryCardDecoration,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 12, vertical: 5),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(100),
                          ),
                          child: Text(
                            'PHASE 2 OF 3',
                            style: AppTheme.textTheme.labelSmall?.copyWith(
                              color: Colors.white,
                              letterSpacing: 1.4,
                              fontSize: 10,
                            ),
                          ),
                        ),
                        const Spacer(),
                        Text(
                          '72%',
                          style: AppTheme.textTheme.headlineMedium?.copyWith(
                            color: Colors.white,
                            fontWeight: FontWeight.w900,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Monitoring Stability',
                      style: AppTheme.textTheme.headlineMedium?.copyWith(
                        color: Colors.white,
                        fontSize: 22,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Your heart is stabilizing precisely. Stay active but monitor all fluctuations closely.',
                      style: AppTheme.textTheme.bodyMedium?.copyWith(
                        color: Colors.white70,
                        fontSize: 14,
                        height: 1.5,
                      ),
                    ),
                    const SizedBox(height: 20),

                    // Progress bar
                    ClipRRect(
                      borderRadius: BorderRadius.circular(100),
                      child: AnimatedBuilder(
                        animation: _progressController,
                        builder: (_, __) => LinearProgressIndicator(
                          value: _progressController.value,
                          minHeight: 8,
                          backgroundColor: Colors.white.withOpacity(0.2),
                          valueColor: const AlwaysStoppedAnimation<Color>(
                              Colors.white),
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Session: 14h 52m',
                            style: AppTheme.textTheme.labelSmall
                                ?.copyWith(color: Colors.white60, fontSize: 10)),
                        Text('Est. complete: 4h 10m',
                            style: AppTheme.textTheme.labelSmall
                                ?.copyWith(color: Colors.white60, fontSize: 10)),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // ── Live Metrics Row ──
              Row(
                children: [
                  Expanded(
                    child: _metricCard(
                      label: 'HEART RATE',
                      value: '86',
                      unit: 'BPM',
                      icon: Icons.favorite_rounded,
                      color: AppTheme.primary,
                      trend: '+2',
                      trendUp: true,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: _metricCard(
                      label: 'GLUCOSE',
                      value: '5.6',
                      unit: 'mmol/L',
                      icon: Icons.opacity_rounded,
                      color: AppTheme.accentOrange,
                      trend: '-0.4',
                      trendUp: false,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // ── AI Predictions ──
              Container(
                padding: const EdgeInsets.all(20),
                decoration: AppTheme.bentoDecoration,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text('AI PREDICTIONS',
                        style: AppTheme.textTheme.labelSmall),
                    const SizedBox(height: 16),
                    _predictionItem(
                      title: 'Metabolic Drift',
                      desc: 'Moderate sync recovery expected in 4h.',
                      icon: Icons.auto_awesome_rounded,
                      color: AppTheme.accentPurple,
                      confidence: 0.84,
                    ),
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 14),
                      child: Divider(height: 1),
                    ),
                    _predictionItem(
                      title: 'Heart Stability',
                      desc: '98% normal heartbeat predicted for next 12h.',
                      icon: Icons.favorite_outline_rounded,
                      color: AppTheme.primary,
                      confidence: 0.98,
                    ),
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 14),
                      child: Divider(height: 1),
                    ),
                    _predictionItem(
                      title: 'Glucose Regulation',
                      desc: 'Levels projected to stabilize within 2h.',
                      icon: Icons.show_chart_rounded,
                      color: AppTheme.accentGreen,
                      confidence: 0.76,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // ── 12H Forecast Chart ──
              Container(
                padding: const EdgeInsets.all(20),
                decoration: AppTheme.bentoDecoration,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text('12H RECOVERY FORECAST',
                        style: AppTheme.textTheme.labelSmall),
                    const SizedBox(height: 16),
                    SizedBox(
                      height: 120,
                      child: CustomPaint(
                        painter: _ForecastChartPainter(),
                        size: const Size(double.infinity, 120),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: ['Now', '3h', '6h', '9h', '12h']
                          .map((t) => Text(t,
                              style: AppTheme.textTheme.labelSmall
                                  ?.copyWith(fontSize: 10)))
                          .toList(),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // ── Recovery Timeline ──
              Container(
                padding: const EdgeInsets.all(20),
                decoration: AppTheme.bentoDecoration,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text('RECOVERY TIMELINE',
                        style: AppTheme.textTheme.labelSmall),
                    const SizedBox(height: 16),
                    _timelineItem('Glucose Re-entry', 'Completed 14h ago',
                        true, AppTheme.accentGreen),
                    _timelineItem('Stability Monitoring', 'In progress — 72%',
                        true, AppTheme.primary),
                    _timelineItem('Full Recovery Clearance',
                        'Estimated in ~4h', false, AppTheme.onSurfaceMuted),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _metricCard({
    required String label,
    required String value,
    required String unit,
    required IconData icon,
    required Color color,
    required String trend,
    required bool trendUp,
  }) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: AppTheme.bentoDecoration,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 18),
              const Spacer(),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: (trendUp ? AppTheme.primary : AppTheme.accentGreen)
                      .withOpacity(0.1),
                  borderRadius: BorderRadius.circular(100),
                ),
                child: Text(
                  trend,
                  style: AppTheme.textTheme.labelSmall?.copyWith(
                    color: trendUp ? AppTheme.primary : AppTheme.accentGreen,
                    fontSize: 10,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(value,
              style: AppTheme.textTheme.headlineMedium
                  ?.copyWith(fontSize: 28, fontWeight: FontWeight.w900)),
          Text(unit, style: AppTheme.textTheme.bodyMedium?.copyWith(fontSize: 12)),
          const SizedBox(height: 4),
          Text(label,
              style: AppTheme.textTheme.labelSmall?.copyWith(fontSize: 10)),
        ],
      ),
    );
  }

  Widget _predictionItem({
    required String title,
    required String desc,
    required IconData icon,
    required Color color,
    required double confidence,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: color, size: 20),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(title,
                        style: AppTheme.textTheme.labelLarge
                            ?.copyWith(fontSize: 14, color: color)),
                  ),
                  Text(
                    '${(confidence * 100).toInt()}%',
                    style: AppTheme.textTheme.labelSmall
                        ?.copyWith(color: color, fontSize: 10),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text(desc,
                  style:
                      AppTheme.textTheme.bodyMedium?.copyWith(fontSize: 12)),
              const SizedBox(height: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(100),
                child: LinearProgressIndicator(
                  value: confidence,
                  minHeight: 4,
                  backgroundColor: color.withOpacity(0.12),
                  valueColor: AlwaysStoppedAnimation<Color>(color),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _timelineItem(
      String title, String sub, bool done, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Column(
            children: [
              Container(
                width: 28,
                height: 28,
                decoration: BoxDecoration(
                  color: done ? color : color.withOpacity(0.15),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  done ? Icons.check_rounded : Icons.circle_outlined,
                  color: done ? Colors.white : color,
                  size: 16,
                ),
              ),
            ],
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: AppTheme.textTheme.labelLarge?.copyWith(
                        fontSize: 14,
                        color: done ? AppTheme.onSurface : AppTheme.onSurfaceMuted)),
                const SizedBox(height: 2),
                Text(sub,
                    style: AppTheme.textTheme.bodyMedium?.copyWith(fontSize: 12)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// Simple smooth forecast chart
class _ForecastChartPainter extends CustomPainter {
  const _ForecastChartPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    // Data points (normalized 0-1, representing recovery progress)
    final points = [0.35, 0.45, 0.55, 0.62, 0.72, 0.78, 0.83, 0.87, 0.89, 0.91];
    final coords = List.generate(points.length, (i) {
      return Offset(w * i / (points.length - 1), h * (1 - points[i]));
    });

    // Gradient fill
    final fillPath = Path()..moveTo(coords.first.dx, h);
    for (int i = 0; i < coords.length - 1; i++) {
      final cp1 = Offset((coords[i].dx + coords[i + 1].dx) / 2, coords[i].dy);
      final cp2 = Offset((coords[i].dx + coords[i + 1].dx) / 2, coords[i + 1].dy);
      fillPath.cubicTo(cp1.dx, cp1.dy, cp2.dx, cp2.dy, coords[i + 1].dx, coords[i + 1].dy);
    }
    fillPath.lineTo(w, h);
    fillPath.close();

    final fillPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [AppTheme.primary.withOpacity(0.18), AppTheme.primary.withOpacity(0.0)],
      ).createShader(Rect.fromLTWH(0, 0, w, h));
    canvas.drawPath(fillPath, fillPaint);

    // Line
    final linePath = Path()..moveTo(coords.first.dx, coords.first.dy);
    for (int i = 0; i < coords.length - 1; i++) {
      final cp1 = Offset((coords[i].dx + coords[i + 1].dx) / 2, coords[i].dy);
      final cp2 = Offset((coords[i].dx + coords[i + 1].dx) / 2, coords[i + 1].dy);
      linePath.cubicTo(cp1.dx, cp1.dy, cp2.dx, cp2.dy, coords[i + 1].dx, coords[i + 1].dy);
    }

    final linePaint = Paint()
      ..color = AppTheme.primary
      ..strokeWidth = 2.5
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    canvas.drawPath(linePath, linePaint);

    // End dot
    final dotPaint = Paint()..color = AppTheme.primary;
    canvas.drawCircle(coords.last, 5, dotPaint);
    canvas.drawCircle(
        coords.last, 5, Paint()..color = Colors.white..style = PaintingStyle.stroke..strokeWidth = 2);
  }

  @override
  bool shouldRepaint(_ForecastChartPainter old) => false;
}
