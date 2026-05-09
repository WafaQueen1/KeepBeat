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
      backgroundColor: AppTheme.surface,
      body: StitchBackdrop(
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(18, 10, 18, 120),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.arrow_back, color: AppTheme.primary),
                    const SizedBox(width: 18),
                    Text('Settings', style: AppTheme.textTheme.titleLarge?.copyWith(color: AppTheme.primary)),
                  ],
                ),
                const SizedBox(height: 28),
                Container(
                  padding: const EdgeInsets.all(18),
                  decoration: AppTheme.primaryCardDecoration,
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 28,
                        backgroundColor: Colors.white.withOpacity(0.22),
                        backgroundImage: const AssetImage('assets/images/avatar.png'),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Marcus\nHolloway', style: AppTheme.textTheme.headlineMedium?.copyWith(color: Colors.white, fontSize: 20)),
                            const SizedBox(height: 2),
                            Text('PREMIUM\nHEALTH\nMEMBER', style: AppTheme.textTheme.labelLarge?.copyWith(color: Colors.white, letterSpacing: 1.1)),
                          ],
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.22),
                          borderRadius: BorderRadius.circular(18),
                        ),
                        child: Text('View\nProfile', textAlign: TextAlign.center, style: AppTheme.textTheme.titleMedium?.copyWith(color: Colors.white)),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                BentoTile(
                  child: Column(
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.sensors, color: AppTheme.primary),
                          const Spacer(),
                          StatusBadge(label: 'CONNECTED', color: AppTheme.blue),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Align(
                        alignment: Alignment.centerLeft,
                        child: Text('KeepBeat Fog Sensor', style: AppTheme.textTheme.headlineMedium?.copyWith(fontSize: 18)),
                      ),
                      Align(
                        alignment: Alignment.centerLeft,
                        child: Text('S/N: KB-9920-FOG', style: AppTheme.textTheme.bodyLarge),
                      ),
                      const SizedBox(height: 16),
                      const Divider(color: AppTheme.line),
                      const SizedBox(height: 14),
                      Row(
                        children: [
                          const Icon(Icons.sync, size: 16, color: AppTheme.onSurfaceMuted),
                          const SizedBox(width: 8),
                          Text('Last Sync: 2m ago', style: AppTheme.textTheme.bodyMedium),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                BentoTile(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.monitor_heart, color: AppTheme.primary),
                          const SizedBox(width: 10),
                          Text('Health Alerts', style: AppTheme.textTheme.headlineMedium?.copyWith(fontSize: 18)),
                        ],
                      ),
                      const SizedBox(height: 18),
                      _toggle('Low Glucose Alerts', _lowGlucose, (v) => setState(() => _lowGlucose = v)),
                      const SizedBox(height: 16),
                      _toggle('High Heart Rate', _highPulse, (v) => setState(() => _highPulse = v)),
                      const SizedBox(height: 16),
                      _toggle('Battery Critical', _batteryCritical, (v) => setState(() => _batteryCritical = v)),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                BentoTile(
                  child: Column(
                    children: [
                      Container(
                        width: 92,
                        height: 92,
                        decoration: BoxDecoration(
                          color: const Color(0xFFF2D5FF),
                          borderRadius: BorderRadius.circular(28),
                        ),
                        child: const Icon(Icons.psychology, color: AppTheme.lavender, size: 36),
                      ),
                      const SizedBox(height: 20),
                      Text('AI & Security Shield', style: AppTheme.textTheme.displayMedium?.copyWith(fontSize: 22)),
                      const SizedBox(height: 10),
                      Text(
                        'Our Fog Agent analytics ensures your data stays on-device while providing deep health predictions.',
                        textAlign: TextAlign.center,
                        style: AppTheme.textTheme.bodyLarge,
                      ),
                      const SizedBox(height: 22),
                      StitchButton(onTap: () {}, text: 'Biometric Lock', icon: Icons.fingerprint, backgroundColor: AppTheme.lavender),
                      const SizedBox(height: 14),
                      StitchButton(onTap: () {}, text: 'Data Settings', backgroundColor: const Color(0xFFE4E5E8), textColor: const Color(0xFF5B3E39), icon: Icons.shield),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                _menuCard(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _toggle(String label, bool value, ValueChanged<bool> onChanged) {
    return Row(
      children: [
        Expanded(child: Text(label, style: AppTheme.textTheme.titleMedium)),
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

  Widget _menuCard() {
    return Container(
      decoration: AppTheme.bentoDecoration,
      child: Column(
        children: [
          _menuRow(Icons.help_outline, 'Help Center'),
          const Divider(height: 1, color: AppTheme.line),
          _menuRow(Icons.verified_user_outlined, 'Privacy Policy'),
          const Divider(height: 1, color: AppTheme.line),
          Padding(
            padding: const EdgeInsets.all(18),
            child: Row(
              children: [
                Container(
                  width: 42,
                  height: 42,
                  decoration: BoxDecoration(
                    color: AppTheme.redSoft,
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: const Icon(Icons.logout, color: AppTheme.primary),
                ),
                const SizedBox(width: 16),
                Text('Log Out', style: AppTheme.textTheme.titleMedium?.copyWith(color: AppTheme.primary)),
                const Spacer(),
                Text('VERSION 4.2.1', style: AppTheme.textTheme.labelSmall?.copyWith(color: const Color(0xFFFF9D9D))),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _menuRow(IconData icon, String title) {
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
          const Icon(Icons.chevron_right, color: Color(0xFFBAC6D8)),
        ],
      ),
    );
  }
}
