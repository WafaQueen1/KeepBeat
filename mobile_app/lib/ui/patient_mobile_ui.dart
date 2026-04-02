import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/hybrid_sensor_service.dart';

class PatientMobileUI extends StatelessWidget {
  final HybridSensorService sensorService;

  const PatientMobileUI({super.key, required this.sensorService});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.surfaceContainerLowest,
      appBar: AppBar(
        title: Text(
          'My Heart',
          style: AppTheme.textTheme.headlineMedium,
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Big Pulse Animation Placeholder (Using Claymorphism block)
            Center(
              child: Container(
                width: 250,
                height: 250,
                decoration: AppTheme.clayBlockTheme.copyWith(
                  shape: BoxShape.circle,
                  borderRadius: null,
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.favorite, size: 64, color: AppTheme.primary),
                    const SizedBox(height: 16),
                    Text('72', style: AppTheme.textTheme.displayLarge),
                    Text('BPM', style: AppTheme.textTheme.labelSmall),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 64),
            // Status Chip
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              decoration: BoxDecoration(
                color: AppTheme.secondaryContainer,
                borderRadius: BorderRadius.circular(30),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.check_circle, color: AppTheme.onSecondaryContainer, size: 20),
                  const SizedBox(width: 8),
                  Text(
                    'Pacemaker functioning normally',
                    style: AppTheme.textTheme.labelSmall?.copyWith(
                      color: AppTheme.onSecondaryContainer,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
