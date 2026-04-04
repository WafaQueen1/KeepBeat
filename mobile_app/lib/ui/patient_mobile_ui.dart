import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/app_theme.dart';
import '../services/hybrid_sensor_service.dart';
import '../providers/patient_provider.dart';

class PatientMobileUI extends ConsumerStatefulWidget {
  final HybridSensorService sensorService;

  const PatientMobileUI({super.key, required this.sensorService});

  @override
  ConsumerState<PatientMobileUI> createState() => _PatientMobileUIState();
}

class _PatientMobileUIState extends ConsumerState<PatientMobileUI> {
  double _currentBPM = 72.0;
  String? _activeAlert;

  @override
  void initState() {
    super.initState();
    // Configure Fog-level callbacks for real-time reactivity
    widget.sensorService.onHeartRateUpdate = (bpm) {
      if (mounted) {
        setState(() {
          _currentBPM = bpm;
        });
      }
    };

    widget.sensorService.onAlert = (msg) {
      if (mounted) {
        setState(() {
          _activeAlert = msg;
        });
      }
    };
  }

  @override
  Widget build(BuildContext context) {
    final patient = ref.watch(patientContextProvider);
    widget.sensorService.currentPatientId = patient.patientId;

    return Scaffold(
      backgroundColor: AppTheme.surfaceContainerLowest,
      appBar: AppBar(
        title: Text(
          'Fog Node: ${patient.fullName}',
          style: AppTheme.textTheme.headlineMedium?.copyWith(fontSize: 18),
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Stack(
        children: [
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Heart Pulse Animation
                Center(
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 300),
                    width: _activeAlert != null ? 220 : 250,
                    height: _activeAlert != null ? 220 : 250,
                    decoration: AppTheme.clayBlockTheme.copyWith(
                      shape: BoxShape.circle,
                      borderRadius: null,
                      color: _activeAlert != null ? Colors.red.shade50 : null,
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.favorite,
                          size: 64,
                          color: _activeAlert != null ? Colors.red : AppTheme.primary,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          _currentBPM.toStringAsFixed(0),
                          style: AppTheme.textTheme.displayLarge?.copyWith(
                            color: _activeAlert != null ? Colors.red : null,
                          ),
                        ),
                        Text('BPM', style: AppTheme.textTheme.labelSmall),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 48),
                // Status Chip
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                  decoration: BoxDecoration(
                    color: _activeAlert != null ? Colors.red.shade100 : AppTheme.secondaryContainer,
                    borderRadius: BorderRadius.circular(30),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        _activeAlert != null ? Icons.warning_amber_rounded : Icons.check_circle,
                        color: _activeAlert != null ? Colors.red : AppTheme.onSecondaryContainer,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        _activeAlert ?? 'Pacemaker functioning normally',
                        style: AppTheme.textTheme.labelSmall?.copyWith(
                          color: _activeAlert != null ? Colors.red : AppTheme.onSecondaryContainer,
                          fontWeight: _activeAlert != null ? FontWeight.bold : null,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          if (_activeAlert != null)
            Positioned(
              top: 0,
              left: 24,
              right: 24,
              child: GestureDetector(
                onTap: () => setState(() => _activeAlert = null),
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.red,
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.red.withOpacity(0.3),
                        blurRadius: 20,
                        offset: const Offset(0, 10),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.emergency, color: Colors.white),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          'LOCAL ALERT: Critical threshold breach. Seek clinical attention.',
                          style: AppTheme.textTheme.labelSmall?.copyWith(color: Colors.white, fontWeight: FontWeight.bold),
                        ),
                      ),
                      const Icon(Icons.close, color: Colors.white, size: 16),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
