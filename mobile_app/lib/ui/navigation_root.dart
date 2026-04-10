import 'dart:ui';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'patient_dashboard_ui.dart';
import 'alert_history_ui.dart';
import 'recovery_state_ui.dart';
import 'settings_ui.dart';
import '../services/hybrid_sensor_service.dart';

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
        onNavigateToAI: () => _navigateTo(2),
      ),
      const AlertHistoryUI(),
      const RecoveryStateUI(),
      const SettingsUI(),
    ];
  }

  void _navigateTo(int index) {
    if (mounted) setState(() => _selectedIndex = index);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      extendBody: true,
      body: IndexedStack(
        index: _selectedIndex,
        children: _screens,
      ),
      bottomNavigationBar: _buildNavBar(),
    );
  }

  Widget _buildNavBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 28),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(28),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
          child: Container(
            height: 72,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.90),
              borderRadius: BorderRadius.circular(28),
              border: Border.all(
                color: AppTheme.primary.withOpacity(0.1),
                width: 1.2,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.08),
                  blurRadius: 24,
                  offset: const Offset(0, 8),
                ),
              ],
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _NavItem(
                  icon: Icons.home_rounded,
                  outlinedIcon: Icons.home_outlined,
                  label: 'Home',
                  index: 0,
                  selectedIndex: _selectedIndex,
                  onTap: _navigateTo,
                ),
                _NavItem(
                  icon: Icons.notifications_rounded,
                  outlinedIcon: Icons.notifications_none_outlined,
                  label: 'Alerts',
                  index: 1,
                  selectedIndex: _selectedIndex,
                  onTap: _navigateTo,
                ),
                _NavItem(
                  icon: Icons.auto_awesome_rounded,
                  outlinedIcon: Icons.auto_awesome_outlined,
                  label: 'AI',
                  index: 2,
                  selectedIndex: _selectedIndex,
                  onTap: _navigateTo,
                ),
                _NavItem(
                  icon: Icons.settings_rounded,
                  outlinedIcon: Icons.settings_outlined,
                  label: 'Settings',
                  index: 3,
                  selectedIndex: _selectedIndex,
                  onTap: _navigateTo,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  final IconData icon;
  final IconData outlinedIcon;
  final String label;
  final int index;
  final int selectedIndex;
  final void Function(int) onTap;

  const _NavItem({
    required this.icon,
    required this.outlinedIcon,
    required this.label,
    required this.index,
    required this.selectedIndex,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final bool isSelected = index == selectedIndex;
    return Expanded(
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () => onTap(index),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeInOut,
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              AnimatedSwitcher(
                duration: const Duration(milliseconds: 200),
                child: isSelected
                    ? Container(
                        key: ValueKey('sel_$index'),
                        padding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 6),
                        decoration: BoxDecoration(
                          color: AppTheme.primary.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Icon(icon,
                            color: AppTheme.primary, size: 22),
                      )
                    : Icon(
                        key: ValueKey('unsel_$index'),
                        outlinedIcon,
                        color: AppTheme.onSurfaceMuted,
                        size: 22,
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
