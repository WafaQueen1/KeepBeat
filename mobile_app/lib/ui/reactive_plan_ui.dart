import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';

class ReactivePlanUI extends StatelessWidget {
  const ReactivePlanUI({super.key});

  @override
  Widget build(BuildContext context) {
    return const EmergencyAlertUIBridge();
  }
}

class EmergencyAlertUIBridge extends StatelessWidget {
  const EmergencyAlertUIBridge({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surface,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(22, 10, 22, 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  GestureDetector(
                    onTap: () => Navigator.of(context).pop(),
                    child: const Icon(Icons.arrow_back, color: AppTheme.primary),
                  ),
                  const SizedBox(width: 14),
                  Text('Emergency Action Plan', style: AppTheme.textTheme.titleMedium?.copyWith(color: AppTheme.primary)),
                ],
              ),
              const SizedBox(height: 26),
              Container(
                padding: const EdgeInsets.all(18),
                decoration: AppTheme.primaryCardDecoration,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('RECOVERY PHASE:\nMONITORING STABILITY', style: AppTheme.textTheme.headlineMedium?.copyWith(color: Colors.white, fontSize: 20)),
                    const SizedBox(height: 10),
                    Text('Post-hypoglycemia alert dismissed. Vital signs normalization in progress.', style: AppTheme.textTheme.bodyLarge?.copyWith(color: Colors.white)),
                    const SizedBox(height: 14),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.18),
                        borderRadius: BorderRadius.circular(999),
                      ),
                      child: Text('14:52 REMAINING', style: AppTheme.textTheme.titleMedium?.copyWith(color: Colors.white)),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 22),
              BentoTile(
                title: 'DIGITAL TWIN STATUS',
                child: Column(
                  children: [
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        StatusBadge(label: 'GLUCOSE STABILIZING', color: AppTheme.blue),
                        const Spacer(),
                        Text('72', style: AppTheme.textTheme.displayLarge?.copyWith(color: AppTheme.primary, fontSize: 58)),
                      ],
                    ),
                    Image.asset('assets/images/heart.png', height: 220, fit: BoxFit.contain),
                    Row(
                      children: const [
                        Expanded(child: _BottomMetric(title: 'HEART RATE', value: '84', unit: 'BPM')),
                        SizedBox(width: 12),
                        Expanded(child: _BottomMetric(title: 'VARIABILITY', value: '56', unit: 'ms')),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              AiInsightBanner(
                title: 'AI Prediction',
                description: 'Based on current insulin-on-board and metabolic rate, stability is expected within 12 minutes. No further action required.',
                icon: Icons.auto_awesome,
                onTap: () {},
              ),
              const SizedBox(height: 20),
              BentoTile(
                title: 'ACTIVE ALERTS',
                child: Column(
                  children: const [
                    _AlertMini(icon: Icons.water_drop, color: AppTheme.primary, title: 'Glucose Low', subtitle: 'Dismissed 3m ago'),
                    SizedBox(height: 18),
                    _AlertMini(icon: Icons.bolt, color: AppTheme.blue, title: 'Metabolic Surge', subtitle: 'Normalizing'),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              BentoTile(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Recovery Timeline', style: AppTheme.textTheme.displayMedium?.copyWith(fontSize: 22)),
                    Text('LAST 60 MINUTES', style: AppTheme.textTheme.labelSmall),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        _chip('HEART RATE', false),
                        const SizedBox(width: 10),
                        _chip('GLUCOSE', true),
                      ],
                    ),
                    const SizedBox(height: 28),
                    SizedBox(height: 170, child: CustomPaint(painter: _TimelinePainter())),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _chip(String text, bool active) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: active ? AppTheme.primary : const Color(0xFFF0F2F6),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        text,
        style: AppTheme.textTheme.labelSmall?.copyWith(color: active ? Colors.white : AppTheme.onSurface),
      ),
    );
  }
}

class _BottomMetric extends StatelessWidget {
  final String title;
  final String value;
  final String unit;
  const _BottomMetric({required this.title, required this.value, required this.unit});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFF7F7FA),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: AppTheme.textTheme.labelSmall),
          const SizedBox(height: 6),
          RichText(
            text: TextSpan(
              children: [
                TextSpan(text: value, style: AppTheme.textTheme.headlineMedium?.copyWith(fontSize: 32)),
                TextSpan(text: ' $unit', style: AppTheme.textTheme.bodyMedium?.copyWith(color: AppTheme.onSurfaceMuted)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _AlertMini extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String title;
  final String subtitle;
  const _AlertMini({required this.icon, required this.color, required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 42,
          height: 42,
          decoration: BoxDecoration(color: color.withOpacity(0.14), borderRadius: BorderRadius.circular(14)),
          child: Icon(icon, color: color),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: AppTheme.textTheme.titleMedium),
              Text(subtitle, style: AppTheme.textTheme.bodyMedium),
            ],
          ),
        ),
        const Icon(Icons.chevron_right, color: Color(0xFFC4CDD9)),
      ],
    );
  }
}

class _TimelinePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final path = Path()
      ..moveTo(0, size.height * 0.72)
      ..cubicTo(size.width * 0.3, size.height * 0.78, size.width * 0.55, size.height * 0.92, size.width * 0.7, size.height * 0.68)
      ..cubicTo(size.width * 0.82, size.height * 0.50, size.width * 0.92, size.height * 0.58, size.width, size.height * 0.66);
    canvas.drawPath(
      path,
      Paint()
        ..color = AppTheme.primary
        ..strokeWidth = 2
        ..style = PaintingStyle.stroke,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
