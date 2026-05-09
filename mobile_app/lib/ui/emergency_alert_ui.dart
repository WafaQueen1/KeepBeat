import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class EmergencyAlertUI extends StatelessWidget {
  const EmergencyAlertUI({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFFFFF5F5), Color(0xFFFFE1E1)],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(18, 14, 18, 28),
            child: Column(
              children: [
                Row(
                  children: [
                    const Icon(Icons.arrow_back, color: AppTheme.primary),
                    const SizedBox(width: 12),
                    Text('Emergency Action Plan', style: AppTheme.textTheme.titleMedium?.copyWith(color: AppTheme.primary)),
                    const Spacer(),
                    Text('KeepBeat', style: AppTheme.textTheme.labelLarge?.copyWith(color: AppTheme.primary)),
                  ],
                ),
                const SizedBox(height: 24),
                _alertHero(),
                const SizedBox(height: 24),
                _stepPanel(),
                const SizedBox(height: 24),
                _fogCard(),
                const SizedBox(height: 24),
                _itemsCard(),
                const SizedBox(height: 24),
                Container(
                  width: double.infinity,
                  height: 66,
                  decoration: BoxDecoration(
                    gradient: AppTheme.primaryGradient,
                    borderRadius: BorderRadius.circular(18),
                    boxShadow: [
                      BoxShadow(
                        color: AppTheme.primary.withOpacity(0.25),
                        blurRadius: 20,
                        offset: const Offset(0, 10),
                      ),
                    ],
                  ),
                  child: Center(
                    child: Text(
                      "I've Completed These\nSteps",
                      textAlign: TextAlign.center,
                      style: AppTheme.textTheme.titleMedium?.copyWith(color: Colors.white),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Text('◉ Next update in 13 minutes', style: AppTheme.textTheme.bodyMedium?.copyWith(color: const Color(0xFF74839A))),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _alertHero() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: AppTheme.primaryCardDecoration,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('CRITICAL ALERT', style: AppTheme.textTheme.labelSmall?.copyWith(color: Colors.white)),
          const SizedBox(height: 8),
          Text('Hypoglycemia:\n42 mg/dL', style: AppTheme.textTheme.displayMedium?.copyWith(color: Colors.white, fontSize: 28, height: 1.0)),
          const SizedBox(height: 10),
          Text('Detected 2 minutes ago via\nContinuous Glucose Monitor.', style: AppTheme.textTheme.bodyLarge?.copyWith(color: Colors.white)),
          const SizedBox(height: 18),
          Row(
            children: const [
              _ValueBox(label: 'CURRENT', value: '42'),
              SizedBox(width: 12),
              _ValueBox(label: 'TARGET', value: '90+'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _stepPanel() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: AppTheme.bentoDecoration,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: const [
          _PanelTitle(title: 'Immediate Steps'),
          SizedBox(height: 18),
          _ActionRow(icon: Icons.local_florist, title: 'Glucose Intake', body: 'Consume 15g of fast-acting carbs immediately.'),
          SizedBox(height: 14),
          _ActionRow(icon: Icons.accessible, title: 'Rest & Position', body: 'Sit down immediately. Do not attempt to walk or drive until your levels stabilize above 70 mg/dL.'),
          SizedBox(height: 14),
          _ActionRow(icon: Icons.air, title: 'Secondary Measure: Breathing', body: 'If high heart rate occurs: Sit down and perform the Valsalva maneuver or deep breathing.', muted: true),
        ],
      ),
    );
  }

  Widget _fogCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppTheme.lavenderSoft,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFFE7D8FA)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('FOG AGENT GUIDANCE', style: AppTheme.textTheme.labelSmall?.copyWith(color: const Color(0xFF7B29BE))),
          const SizedBox(height: 14),
          Row(
            children: [
              Container(
                width: 58,
                height: 58,
                decoration: BoxDecoration(color: AppTheme.lavender, borderRadius: BorderRadius.circular(16)),
                child: const Icon(Icons.battery_alert, color: Colors.white),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text('Battery Critical (5%)\nSystem entering ultra-low power.', style: AppTheme.textTheme.bodyLarge?.copyWith(color: Colors.white)),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Text(
            'Syncing frequency reduced to preserve vital re-support monitoring. Your local Fog Agent is prioritizing emergency telemetry only.',
            style: AppTheme.textTheme.bodyMedium?.copyWith(color: Colors.white),
          ),
          const SizedBox(height: 14),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(color: const Color(0xFFDEAFFF), borderRadius: BorderRadius.circular(16)),
            child: Text('RECOVERY ACTION:\nConnect to charger within 10 minutes or use the emergency battery pack.', style: AppTheme.textTheme.bodyLarge?.copyWith(color: const Color(0xFF66219D))),
          ),
        ],
      ),
    );
  }

  Widget _itemsCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFEAE7E7),
        borderRadius: BorderRadius.circular(22),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('REQUIRED ITEMS', style: AppTheme.textTheme.labelSmall?.copyWith(color: const Color(0xFF41302D))),
          const SizedBox(height: 16),
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _ItemTile(icon: Icons.local_drink, label: 'SUGAR'),
              _ItemTile(icon: Icons.water_drop, label: 'WATER'),
              _ItemTile(icon: Icons.flash_on, label: 'POWER'),
            ],
          ),
        ],
      ),
    );
  }
}

class _ValueBox extends StatelessWidget {
  final String label;
  final String value;
  const _ValueBox({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.16),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: AppTheme.textTheme.labelSmall?.copyWith(color: Colors.white)),
          const SizedBox(height: 4),
          Text(value, style: AppTheme.textTheme.displayMedium?.copyWith(color: Colors.white, fontSize: 28)),
        ],
      ),
    );
  }
}

class _PanelTitle extends StatelessWidget {
  final String title;
  const _PanelTitle({required this.title});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        const Icon(Icons.medical_services, color: AppTheme.primary),
        const SizedBox(width: 10),
        Text(title, style: AppTheme.textTheme.titleLarge),
      ],
    );
  }
}

class _ActionRow extends StatelessWidget {
  final IconData icon;
  final String title;
  final String body;
  final bool muted;
  const _ActionRow({required this.icon, required this.title, required this.body, this.muted = false});

  @override
  Widget build(BuildContext context) {
    final color = muted ? const Color(0xFFC7C9D1) : AppTheme.primary;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: muted ? const Color(0xFFF3F3F5) : const Color(0xFFF8F5F5),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(14)),
            child: Icon(icon, color: color),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: AppTheme.textTheme.titleMedium?.copyWith(color: muted ? color : AppTheme.onSurface)),
                const SizedBox(height: 4),
                Text(body, style: AppTheme.textTheme.bodyLarge?.copyWith(color: muted ? color : const Color(0xFF5D4540))),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ItemTile extends StatelessWidget {
  final IconData icon;
  final String label;
  const _ItemTile({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 62,
      padding: const EdgeInsets.symmetric(vertical: 14),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(14)),
      child: Column(
        children: [
          Icon(icon, color: AppTheme.primary),
          const SizedBox(height: 10),
          Text(label, style: AppTheme.textTheme.labelSmall?.copyWith(color: const Color(0xFF403332))),
        ],
      ),
    );
  }
}
