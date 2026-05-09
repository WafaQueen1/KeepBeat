import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';

class SettingsUI extends StatefulWidget {
  const SettingsUI({super.key});

  @override
  State<SettingsUI> createState() => _SettingsUIState();
}

class _SettingsUIState extends State<SettingsUI> {
  bool _lowGlucose = true;
  bool _highPulse = true;
  bool _batteryCritical = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.pageGradient),
        child: SafeArea(
          child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.fromLTRB(20, 10, 20, 120),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                    Text(
                      'SETTINGS',
                      style: AppTheme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w800,
                        letterSpacing: 1.5,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 28),
                // Profile Card
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(28),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(32),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.04),
                        blurRadius: 24,
                        offset: const Offset(0, 12),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      const CircleAvatar(
                        radius: 32,
                        backgroundImage: AssetImage('assets/images/avatar.png'),
                      ),
                      const SizedBox(width: 20),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Wafa Queen',
                              style: AppTheme.textTheme.titleLarge?.copyWith(
                                fontWeight: FontWeight.w900,
                                fontSize: 22,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'PREMIUM MEMBER',
                              style: AppTheme.textTheme.labelSmall?.copyWith(
                                color: AppTheme.onSurface.withOpacity(0.4),
                                letterSpacing: 1.5,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: AppTheme.lavender.withOpacity(0.1),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.edit_rounded, color: AppTheme.lavender, size: 20),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                // Device Status
                BentoTile(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('PAIRED DEVICE', style: AppTheme.textTheme.labelSmall),
                          const StatusBadge(label: 'ACTIVE', color: AppTheme.blue),
                        ],
                      ),
                      const SizedBox(height: 20),
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: AppTheme.primary.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: const Icon(Icons.sensor_occupied_rounded, color: AppTheme.primary),
                          ),
                          const SizedBox(width: 16),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'KeepBeat Fog Sensor',
                                style: AppTheme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
                              ),
                              Text(
                                'S/N: KB-9920-FOG',
                                style: AppTheme.textTheme.bodySmall?.copyWith(color: AppTheme.onSurfaceMuted),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                // Alerts Toggle
                BentoTile(
                  title: 'ALERTS & NOTIFICATIONS',
                  child: Column(
                    children: [
                      _toggleRow(
                        label: 'Low Glucose Alerts',
                        value: _lowGlucose,
                        onChanged: (value) => setState(() => _lowGlucose = value),
                      ),
                      const SizedBox(height: 12),
                      _toggleRow(
                        label: 'Heart Rhythm Alert',
                        value: _highPulse,
                        onChanged: (value) => setState(() => _highPulse = value),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                // Danger Zone / Logout
                StitchButton(
                  onTap: () => Navigator.of(context).pushReplacementNamed('/login'),
                  text: 'LOG OUT',
                  icon: Icons.logout_rounded,
                  backgroundColor: AppTheme.primary.withOpacity(0.08),
                  textColor: AppTheme.primary,
                ),
                const SizedBox(height: 32),
                Center(
                  child: Text(
                    'KEEPBEAT VERSION 4.2.1',
                    style: AppTheme.textTheme.labelSmall?.copyWith(
                      color: AppTheme.onSurface.withOpacity(0.3),
                      letterSpacing: 2,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _toggleRow({
    required String label,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Row(
      children: [
        Expanded(
          child: Text(label, style: AppTheme.textTheme.titleMedium),
        ),
        Switch(
          value: value,
          onChanged: onChanged,
          activeColor: Colors.white,
          activeTrackColor: AppTheme.primary,
          inactiveThumbColor: Colors.white,
          inactiveTrackColor: const Color(0xFFDADDE2),
        ),
      ],
    );
  }

  Widget _menuRow({required IconData icon, required String title}) {
    return Padding(
      padding: const EdgeInsets.all(18),
      child: Row(
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              color: const Color(0xFFF2F5FA),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Icon(icon, color: const Color(0xFF7D8799)),
          ),
          const SizedBox(width: 16),
          Text(title, style: AppTheme.textTheme.titleMedium),
          const Spacer(),
          const Icon(
            Icons.chevron_right_rounded,
            color: Color(0xFFBAC6D8),
          ),
        ],
      ),
    );
  }
}
