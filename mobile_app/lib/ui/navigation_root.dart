import 'dart:ui';

import 'package:flutter/material.dart';

import '../services/hybrid_sensor_service.dart';
import '../theme/app_theme.dart';
import 'alert_history_ui.dart';
import 'patient_dashboard_ui.dart';
import 'reactive_plan_ui.dart';
import 'settings_ui.dart';

class NavigationRoot extends StatefulWidget {
  final HybridSensorService sensorService;

  const NavigationRoot({super.key, required this.sensorService});

  @override
  State<NavigationRoot> createState() => _NavigationRootState();
}

class _NavigationRootState extends State<NavigationRoot> {
  int _selectedIndex = 0;

  late final List<Widget> _screens;

  @override
  void initState() {
    super.initState();
    _screens = [
      PatientDashboardUI(
        sensorService: widget.sensorService,
        onNavigateToAI: () => _navigateTo(1),
      ),
      const ReactivePlanUI(),
      const AlertHistoryUI(),
      const SettingsUI(),
    ];
  }

  void _navigateTo(int index) {
    if (mounted) {
      setState(() => _selectedIndex = index);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surface,
      extendBody: true,
      body: IndexedStack(
        index: _selectedIndex,
        children: _screens,
      ),
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.fromLTRB(14, 0, 14, 14),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(32),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 22, sigmaY: 22),
            child: Container(
              height: 86,
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.84),
                borderRadius: BorderRadius.circular(32),
                boxShadow: const [
                  BoxShadow(
                    color: AppTheme.shadow,
                    blurRadius: 26,
                    offset: Offset(0, -2),
                  ),
                ],
              ),
              child: Row(
                children: [
                  _NavItem(
                    icon: Icons.favorite_rounded,
                    label: 'TWIN',
                    index: 0,
                    selectedIndex: _selectedIndex,
                    onTap: _navigateTo,
                  ),
                  _NavItem(
                    icon: Icons.bar_chart_rounded,
                    label: 'STATS',
                    index: 1,
                    selectedIndex: _selectedIndex,
                    onTap: _navigateTo,
                  ),
                  _NavItem(
                    icon: Icons.emergency_rounded,
                    label: 'ALERTS',
                    index: 2,
                    selectedIndex: _selectedIndex,
                    onTap: _navigateTo,
                  ),
                  _NavItem(
                    icon: Icons.settings_rounded,
                    label: 'SETTINGS',
                    index: 3,
                    selectedIndex: _selectedIndex,
                    onTap: _navigateTo,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final int index;
  final int selectedIndex;
  final ValueChanged<int> onTap;

  const _NavItem({
    required this.icon,
    required this.label,
    required this.index,
    required this.selectedIndex,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isSelected = index == selectedIndex;
    return Expanded(
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () => onTap(index),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            AnimatedContainer(
              duration: const Duration(milliseconds: 220),
              curve: Curves.easeOutCubic,
              padding: EdgeInsets.symmetric(
                horizontal: isSelected ? 18 : 0,
                vertical: isSelected ? 10 : 0,
              ),
              decoration: BoxDecoration(
                color: isSelected ? AppTheme.redSoft : Colors.transparent,
                borderRadius: BorderRadius.circular(22),
              ),
              child: Icon(
                icon,
                size: 26,
                color: isSelected
                    ? AppTheme.primary
                    : AppTheme.onSurfaceMuted.withOpacity(0.75),
              ),
            ),
            const SizedBox(height: 6),
            Text(
              label,
              style: AppTheme.textTheme.labelSmall?.copyWith(
                color: isSelected
                    ? AppTheme.primary
                    : AppTheme.onSurfaceMuted.withOpacity(0.75),
                fontSize: 10,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
