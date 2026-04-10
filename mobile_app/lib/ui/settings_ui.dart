import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';

class SettingsUI extends StatefulWidget {
  const SettingsUI({super.key});

  @override
  State<SettingsUI> createState() => _SettingsUIState();
}

class _SettingsUIState extends State<SettingsUI> {
  // Alert Toggles
  bool _lowGlucose = true;
  bool _highPulse = true;
  bool _batteryCritical = true;
  bool _aiPatternAlerts = true;
  bool _syncAlerts = false;

  // Device & Sync
  bool _autoSync = true;
  bool _backgroundMonitoring = true;

  // Privacy
  bool _dataSharingDoctor = true;
  bool _anonymousAnalytics = false;

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
                      Text('CONFIGURATION',
                          style: AppTheme.textTheme.labelSmall),
                      const SizedBox(height: 4),
                      Text('Settings',
                          style: AppTheme.textTheme.headlineMedium),
                    ],
                  ),
                  GestureDetector(
                    onTap: () => Navigator.of(context)
                        .pushReplacementNamed('/login'),
                    child: Container(
                      width: 44,
                      height: 44,
                      decoration: AppTheme.bentoDecoration,
                      child: const Icon(Icons.logout_rounded,
                          color: AppTheme.primary, size: 20),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // ── Profile Card ──
              Container(
                padding: const EdgeInsets.all(22),
                decoration: AppTheme.primaryCardDecoration,
                child: Row(
                  children: [
                    Container(
                      width: 60,
                      height: 60,
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.25),
                        shape: BoxShape.circle,
                      ),
                      child: const Center(
                        child: Text(
                          'SJ',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w900,
                            fontSize: 20,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Sarah Jenkins',
                            style: AppTheme.textTheme.titleLarge?.copyWith(
                              color: Colors.white,
                              fontSize: 18,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'Clinical ID: #KB-8821',
                            style: AppTheme.textTheme.bodyMedium?.copyWith(
                              color: Colors.white60,
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                    StatusBadge(label: 'Active', color: Colors.white, inverted: true),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // ── Cloud Sync ──
              Container(
                padding: const EdgeInsets.all(20),
                decoration: AppTheme.bentoDecoration,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text('CLOUD SERVICES',
                        style: AppTheme.textTheme.labelSmall),
                    const SizedBox(height: 16),
                    StitchButton(
                      onTap: () {},
                      text: 'Sync with Cloud Now',
                      icon: Icons.sync_rounded,
                    ),
                    const SizedBox(height: 12),
                    Center(
                      child: Text(
                        'Last synced: 2 minutes ago  •  Node: Active',
                        style: AppTheme.textTheme.bodyMedium
                            ?.copyWith(fontSize: 12),
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Divider(height: 1),
                    const SizedBox(height: 16),
                    _toggleRow(
                      'Auto Sync',
                      'Automatically sync data every 30 minutes',
                      _autoSync,
                      (v) => setState(() => _autoSync = v),
                    ),
                    const SizedBox(height: 12),
                    _toggleRow(
                      'Background Monitoring',
                      'Keep sensor active in background mode',
                      _backgroundMonitoring,
                      (v) => setState(() => _backgroundMonitoring = v),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // ── Health Alerts ──
              Container(
                padding: const EdgeInsets.all(20),
                decoration: AppTheme.bentoDecoration,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text('HEALTH ALERTS',
                        style: AppTheme.textTheme.labelSmall),
                    const SizedBox(height: 16),
                    _toggleRow(
                      'Low Glucose Alerts',
                      'Alert when glucose drops below 4.0 mmol/L',
                      _lowGlucose,
                      (v) => setState(() => _lowGlucose = v),
                    ),
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 12),
                      child: Divider(height: 1),
                    ),
                    _toggleRow(
                      'High Pulse Alert',
                      'Alert when heart rate exceeds 120 BPM',
                      _highPulse,
                      (v) => setState(() => _highPulse = v),
                    ),
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 12),
                      child: Divider(height: 1),
                    ),
                    _toggleRow(
                      'Battery Critical (<7%)',
                      'Alert when pacemaker battery is critically low',
                      _batteryCritical,
                      (v) => setState(() => _batteryCritical = v),
                    ),
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 12),
                      child: Divider(height: 1),
                    ),
                    _toggleRow(
                      'AI Pattern Alerts',
                      'Alert on AI-detected metabolic or cardiac anomalies',
                      _aiPatternAlerts,
                      (v) => setState(() => _aiPatternAlerts = v),
                    ),
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 12),
                      child: Divider(height: 1),
                    ),
                    _toggleRow(
                      'Sync Notifications',
                      'Notify on every successful cloud sync',
                      _syncAlerts,
                      (v) => setState(() => _syncAlerts = v),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // ── Privacy & Security ──
              Container(
                padding: const EdgeInsets.all(20),
                decoration: AppTheme.bentoDecoration,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text('PRIVACY & SECURITY',
                        style: AppTheme.textTheme.labelSmall),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Container(
                          width: 40,
                          height: 40,
                          decoration: BoxDecoration(
                            color: AppTheme.accentPurple.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Icon(Icons.shield_rounded,
                              color: AppTheme.accentPurple, size: 20),
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Text(
                            'Your health data is end-to-end encrypted and protected by AI-Sight security systems.',
                            style: AppTheme.textTheme.bodyMedium
                                ?.copyWith(fontSize: 13),
                          ),
                        ),
                      ],
                    ),
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 16),
                      child: Divider(height: 1),
                    ),
                    _toggleRow(
                      'Share Data with Doctor',
                      'Allow your assigned clinician to view your records',
                      _dataSharingDoctor,
                      (v) => setState(() => _dataSharingDoctor = v),
                    ),
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 12),
                      child: Divider(height: 1),
                    ),
                    _toggleRow(
                      'Anonymous Analytics',
                      'Help improve KeepBeat with anonymised usage data',
                      _anonymousAnalytics,
                      (v) => setState(() => _anonymousAnalytics = v),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // ── About ──
              Container(
                padding: const EdgeInsets.all(20),
                decoration: AppTheme.bentoDecoration,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text('ABOUT', style: AppTheme.textTheme.labelSmall),
                    const SizedBox(height: 16),
                    _infoRow('App Version', 'KeepBeat v1.0.0'),
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 10),
                      child: Divider(height: 1),
                    ),
                    _infoRow('Device ID', 'PT_001 — TwinPacemaker'),
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 10),
                      child: Divider(height: 1),
                    ),
                    _infoRow('AI Engine', 'AI-Sight v2.4'),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // ── Logout ──
              StitchButton(
                onTap: () =>
                    Navigator.of(context).pushReplacementNamed('/login'),
                text: 'Sign Out',
                backgroundColor: AppTheme.surface,
                textColor: AppTheme.primary,
                icon: Icons.logout_rounded,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _toggleRow(
      String title, String desc, bool value, ValueChanged<bool> onChanged) {
    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title,
                  style:
                      AppTheme.textTheme.labelLarge?.copyWith(fontSize: 15)),
              const SizedBox(height: 2),
              Text(desc,
                  style:
                      AppTheme.textTheme.bodyMedium?.copyWith(fontSize: 12)),
            ],
          ),
        ),
        const SizedBox(width: 12),
        Switch(
          value: value,
          onChanged: onChanged,
          activeColor: Colors.white,
          activeTrackColor: AppTheme.primary,
          inactiveThumbColor: Colors.white,
          inactiveTrackColor: const Color(0xFFDDE1E7),
        ),
      ],
    );
  }

  Widget _infoRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label,
            style: AppTheme.textTheme.bodyMedium?.copyWith(fontSize: 14)),
        Text(value,
            style: AppTheme.textTheme.labelLarge?.copyWith(fontSize: 13)),
      ],
    );
  }
}
