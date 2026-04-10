import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';
import '../services/hybrid_sensor_service.dart';

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
  late AnimationController _ecgController;

  @override
  void initState() {
    super.initState();
    _ecgController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    )..repeat();
  }

  @override
  void dispose() {
    _ecgController.dispose();
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
              _buildHeader(),
              const SizedBox(height: 36),

              // ── Animated Heart Hero ──
              StreamBuilder<int>(
                stream: widget.sensorService.heartRateStream,
                builder: (context, snapshot) {
                  final bpm = snapshot.data ?? 72;
                  return Center(child: StitchHeart(bpm: bpm));
                },
              ),
              const SizedBox(height: 12),

              // ── ECG Strip ──
              _buildEcgStrip(),
              const SizedBox(height: 32),

              // ── Stats Row ──
              Row(
                children: [
                  Expanded(
                    child: _statCard(
                      label: 'SPO2',
                      value: '98%',
                      sub: 'Oxygen',
                      icon: Icons.water_drop_rounded,
                      color: AppTheme.accentBlue,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: _statCard(
                      label: 'GLUCOSE',
                      value: '5.4',
                      sub: 'mmol/L',
                      icon: Icons.opacity_rounded,
                      color: AppTheme.accentOrange,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: _statCard(
                      label: 'TEMP',
                      value: '36.8°',
                      sub: 'Celsius',
                      icon: Icons.thermostat_rounded,
                      color: AppTheme.accentGreen,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // ── AI Diagnostic Insight ──
              GestureDetector(
                onTap: widget.onNavigateToAI,
                child: Container(
                  padding: const EdgeInsets.all(20),
                  decoration: AppTheme.bentoDecoration,
                  child: Row(
                    children: [
                      Container(
                        width: 48,
                        height: 48,
                        decoration: BoxDecoration(
                          color: AppTheme.accentPurple.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(14),
                        ),
                        child: const Icon(Icons.auto_awesome_rounded,
                            color: AppTheme.accentPurple, size: 24),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'AI DIAGNOSTIC INSIGHT',
                              style: AppTheme.textTheme.labelSmall,
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Metabolic Drift Detected',
                              style: AppTheme.textTheme.titleMedium?.copyWith(
                                color: AppTheme.accentPurple,
                                fontSize: 16,
                              ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              'View 12h Recovery Forecast →',
                              style: AppTheme.textTheme.bodyMedium
                                  ?.copyWith(fontSize: 13),
                            ),
                          ],
                        ),
                      ),
                      const Icon(Icons.chevron_right_rounded,
                          color: AppTheme.onSurfaceMuted),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // ── Active Alerts ──
              Container(
                padding: const EdgeInsets.all(20),
                decoration: AppTheme.bentoDecoration,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('ACTIVE ALERTS',
                            style: AppTheme.textTheme.labelSmall),
                        StatusBadge(label: '2 Active', color: AppTheme.primary),
                      ],
                    ),
                    const SizedBox(height: 16),
                    _alertItem(
                      title: 'Low Glucose',
                      desc: 'Below 4.0 mmol/L threshold',
                      time: '2m ago',
                      color: AppTheme.primary,
                    ),
                    const Divider(height: 24),
                    _alertItem(
                      title: 'Metabolic Sync',
                      desc: 'Digital twin resync complete',
                      time: '10h ago',
                      color: AppTheme.accentGreen,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // ── Digital Twin Status ──
              Container(
                padding: const EdgeInsets.all(20),
                decoration: AppTheme.primaryCardDecoration,
                child: Row(
                  children: [
                    const Icon(Icons.device_hub_rounded,
                        color: Colors.white, size: 28),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'DIGITAL TWIN',
                            style: AppTheme.textTheme.labelSmall?.copyWith(
                              color: Colors.white54,
                              letterSpacing: 1.6,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Node Active — Synced 1m ago',
                            style: AppTheme.textTheme.titleMedium?.copyWith(
                              color: Colors.white,
                              fontSize: 15,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      width: 10,
                      height: 10,
                      decoration: const BoxDecoration(
                        color: Color(0xFF4ADE80),
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: Color(0x884ADE80),
                            blurRadius: 8,
                            spreadRadius: 2,
                          )
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'DIGITAL TWIN NODE',
              style: AppTheme.textTheme.labelSmall,
            ),
            const SizedBox(height: 4),
            Text(
              'Sarah Jenkins',
              style: AppTheme.textTheme.headlineMedium,
            ),
          ],
        ),
        Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            gradient: AppTheme.primaryGradient,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: AppTheme.primary.withOpacity(0.3),
                blurRadius: 12,
                offset: const Offset(0, 4),
              )
            ],
          ),
          child: const Center(
            child: Text(
              'SJ',
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w800,
                fontSize: 16,
                letterSpacing: 0.5,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildEcgStrip() {
    return Container(
      height: 48,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: AppTheme.bentoDecoration,
      child: AnimatedBuilder(
        animation: _ecgController,
        builder: (context, _) => CustomPaint(
          painter: EcgPainter(
            progress: _ecgController.value,
            color: AppTheme.primary,
          ),
        ),
      ),
    );
  }

  Widget _statCard({
    required String label,
    required String value,
    required String sub,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: AppTheme.bentoDecoration,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: color, size: 18),
          ),
          const SizedBox(height: 12),
          Text(
            value,
            style: AppTheme.textTheme.headlineMedium?.copyWith(
              fontSize: 22,
              fontWeight: FontWeight.w800,
            ),
          ),
          Text(
            sub,
            style: AppTheme.textTheme.bodyMedium?.copyWith(fontSize: 11),
          ),
          const SizedBox(height: 2),
          Text(label, style: AppTheme.textTheme.labelSmall?.copyWith(fontSize: 10)),
        ],
      ),
    );
  }

  Widget _alertItem({
    required String title,
    required String desc,
    required String time,
    required Color color,
  }) {
    return Row(
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
            boxShadow: [BoxShadow(color: color.withOpacity(0.5), blurRadius: 6)],
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title,
                  style: AppTheme.textTheme.labelLarge?.copyWith(fontSize: 14)),
              Text(desc, style: AppTheme.textTheme.bodyMedium?.copyWith(fontSize: 12)),
            ],
          ),
        ),
        Text(time, style: AppTheme.textTheme.labelSmall?.copyWith(fontSize: 10)),
      ],
    );
  }
}
