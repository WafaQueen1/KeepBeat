import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';

class AlertHistoryUI extends StatefulWidget {
  const AlertHistoryUI({super.key});

  @override
  State<AlertHistoryUI> createState() => _AlertHistoryUIState();
}

class _AlertHistoryUIState extends State<AlertHistoryUI> {
  int _filterIndex = 0;
  final List<String> _filters = ['All', 'Critical', 'Warnings', 'Info'];

  final List<_AlertData> _alerts = [
    _AlertData(
      title: 'Hypoglycemia Alert',
      desc: 'Blood glucose dropped to 42 mg/dL — immediate action required.',
      icon: Icons.warning_rounded,
      color: Color(0xFFEF4444),
      severity: 'CRITICAL',
      time: '2m ago',
      tag: 'Critical',
      route: '/emergency',
    ),
    _AlertData(
      title: 'Tachycardia Detected',
      desc: 'Heart rate elevated to 128 BPM for sustained 8 minutes.',
      icon: Icons.favorite_rounded,
      color: Color(0xFFB6171E),
      severity: 'HIGH RISK',
      time: '47m ago',
      tag: 'Critical',
      route: null,
    ),
    _AlertData(
      title: 'Metabolic Drift',
      desc: 'Moderate drift detected in Heavy IR Stability index.',
      icon: Icons.auto_awesome_rounded,
      color: Color(0xFF7C3AED),
      severity: 'AI PATTERN',
      time: '3h ago',
      tag: 'Warnings',
      route: null,
    ),
    _AlertData(
      title: 'Glucose Spike',
      desc: 'Post-meal glucose rose to 9.8 mmol/L — monitor closely.',
      icon: Icons.opacity_rounded,
      color: Color(0xFFD97706),
      severity: 'WARNING',
      time: '5h ago',
      tag: 'Warnings',
      route: null,
    ),
    _AlertData(
      title: 'Daily Sync Complete',
      desc: 'Heart rate and glucose successfully synced to Cloud.',
      icon: Icons.sync_rounded,
      color: Color(0xFF059669),
      severity: 'SUCCESS',
      time: '10h ago',
      tag: 'Info',
      route: null,
    ),
    _AlertData(
      title: 'Monthly Summary Ready',
      desc: 'Your clinical summary for March is now available.',
      icon: Icons.description_rounded,
      color: Color(0xFF0284C7),
      severity: 'REPORT',
      time: '1d ago',
      tag: 'Info',
      route: null,
    ),
    _AlertData(
      title: 'Device Battery Low',
      desc: 'Pacemaker battery at 12% — schedule replacement soon.',
      icon: Icons.battery_alert_rounded,
      color: Color(0xFFD97706),
      severity: 'WARNING',
      time: '2d ago',
      tag: 'Warnings',
      route: null,
    ),
  ];

  List<_AlertData> get _filtered {
    if (_filterIndex == 0) return _alerts;
    final tag = _filters[_filterIndex];
    return _alerts.where((a) => a.tag == tag).toList();
  }

  @override
  Widget build(BuildContext context) {
    final filtered = _filtered;
    return Scaffold(
      backgroundColor: AppTheme.surface,
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            // ── Header ──
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(24, 20, 24, 0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('NOTIFICATIONS',
                                style: AppTheme.textTheme.labelSmall),
                            const SizedBox(height: 4),
                            Text('Alert History',
                                style: AppTheme.textTheme.headlineMedium),
                          ],
                        ),
                        Container(
                          width: 44,
                          height: 44,
                          decoration: AppTheme.bentoDecoration,
                          child: const Icon(Icons.tune_rounded,
                              color: AppTheme.primary, size: 20),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),

                    // ── Summary strip ──
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: AppTheme.primaryCardDecoration,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _summaryItem('2', 'Critical', Colors.white),
                          _vDivider(),
                          _summaryItem('3', 'Warnings', Colors.white70),
                          _vDivider(),
                          _summaryItem('2', 'Info', Colors.white60),
                        ],
                      ),
                    ),
                    const SizedBox(height: 20),

                    // ── Filter chips ──
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: List.generate(_filters.length, (i) {
                          final selected = i == _filterIndex;
                          return GestureDetector(
                            onTap: () => setState(() => _filterIndex = i),
                            child: AnimatedContainer(
                              duration: const Duration(milliseconds: 200),
                              margin: const EdgeInsets.only(right: 10),
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 18, vertical: 9),
                              decoration: BoxDecoration(
                                color: selected
                                    ? AppTheme.primary
                                    : Colors.white,
                                borderRadius: BorderRadius.circular(100),
                                border: Border.all(
                                  color: selected
                                      ? AppTheme.primary
                                      : AppTheme.cardBorder,
                                  width: 1.5,
                                ),
                                boxShadow: selected
                                    ? [
                                        BoxShadow(
                                          color: AppTheme.primary
                                              .withOpacity(0.25),
                                          blurRadius: 12,
                                          offset: const Offset(0, 4),
                                        )
                                      ]
                                    : [],
                              ),
                              child: Text(
                                _filters[i],
                                style: AppTheme.textTheme.labelLarge?.copyWith(
                                  fontSize: 13,
                                  color: selected
                                      ? Colors.white
                                      : AppTheme.onSurfaceMuted,
                                ),
                              ),
                            ),
                          );
                        }),
                      ),
                    ),
                    const SizedBox(height: 20),
                  ],
                ),
              ),
            ),

            // ── Alert List ──
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(24, 0, 24, 110),
              sliver: SliverList(
                delegate: SliverChildBuilderDelegate(
                  (context, i) {
                    final alert = filtered[i];
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: _buildAlertTile(context, alert),
                    );
                  },
                  childCount: filtered.length,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAlertTile(BuildContext context, _AlertData alert) {
    return GestureDetector(
      onTap: alert.route != null
          ? () => Navigator.of(context).pushNamed(alert.route!)
          : null,
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: AppTheme.bentoDecoration,
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Icon
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: alert.color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(alert.icon, color: alert.color, size: 24),
            ),
            const SizedBox(width: 14),

            // Content
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          alert.title,
                          style: AppTheme.textTheme.labelLarge
                              ?.copyWith(fontSize: 15),
                        ),
                      ),
                      StatusBadge(label: alert.severity, color: alert.color),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    alert.desc,
                    style: AppTheme.textTheme.bodyMedium?.copyWith(fontSize: 13),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    alert.time,
                    style: AppTheme.textTheme.labelSmall?.copyWith(fontSize: 10),
                  ),
                ],
              ),
            ),

            if (alert.route != null) ...[
              const SizedBox(width: 8),
              const Icon(Icons.chevron_right_rounded,
                  color: AppTheme.onSurfaceMuted, size: 20),
            ],
          ],
        ),
      ),
    );
  }

  Widget _summaryItem(String count, String label, Color textColor) {
    return Column(
      children: [
        Text(
          count,
          style: AppTheme.textTheme.headlineMedium?.copyWith(
            color: textColor,
            fontSize: 26,
          ),
        ),
        Text(
          label,
          style: AppTheme.textTheme.labelSmall?.copyWith(
            color: textColor.withOpacity(0.8),
            fontSize: 10,
          ),
        ),
      ],
    );
  }

  Widget _vDivider() {
    return Container(
        width: 1, height: 36, color: Colors.white.withOpacity(0.25));
  }
}

class _AlertData {
  final String title;
  final String desc;
  final IconData icon;
  final Color color;
  final String severity;
  final String time;
  final String tag;
  final String? route;

  const _AlertData({
    required this.title,
    required this.desc,
    required this.icon,
    required this.color,
    required this.severity,
    required this.time,
    required this.tag,
    required this.route,
  });
}
