import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';
import '../services/hybrid_sensor_service.dart';
import '../providers/vitals_provider.dart';

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
    with TickerProviderStateMixin {
  late AnimationController _pulseController;
  
  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final heartRate = ref.watch(heartRateProvider).value ?? 72;
    final glucose = ref.watch(glucoseProvider).value ?? 5.4;
    final batteryPct = ref.watch(batteryProvider).value ?? 82.0;
    final latestAlert = ref.watch(latestAlertProvider).value;

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: StitchBackdrop(
        child: SafeArea(
          child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.fromLTRB(24, 14, 24, 120),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _buildHeader(context),
                const SizedBox(height: 22),

                _buildHeartHero(heartRate),
                const SizedBox(height: 18),

                _buildHeartRateCard(heartRate),
                const SizedBox(height: 16),

                Row(
                  children: [
                    Expanded(
                      child: VitalBentoCard(
                        label: 'Glucose',
                        value: glucose.toStringAsFixed(1),
                        unit: 'g/L',
                        icon: Icons.water_drop_rounded,
                        accent: AppTheme.accentBlue,
                        status: (glucose < 0.70 || glucose > 2.50) ? 'CRITICAL' : 'STABLE',
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: VitalBentoCard(
                        label: 'Battery',
                        value: batteryPct.toStringAsFixed(0),
                        unit: '%',
                        icon: Icons.bolt_rounded,
                        accent: AppTheme.accentPurple,
                        trailing: CircularStatusIndicator(
                          value: (batteryPct.clamp(0, 100)) / 100.0,
                          color: AppTheme.accentPurple,
                        ),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 16),

                AiInsightBanner(
                  title: 'Digital Twin',
                  description:
                      'Synchronized — forecast + reactive plan ready. Tap to view twin prediction.',
                  icon: Icons.auto_awesome_rounded,
                  onTap: widget.onNavigateToAI,
                ),

                if (latestAlert != null) ...[
                  const SizedBox(height: 14),
                  BentoTile(
                    title: 'Clinical Alert',
                    padding: const EdgeInsets.all(18),
                    backgroundColor: const Color(0xFFFFF5F6),
                    child: Row(
                      children: [
                        Container(
                          width: 44,
                          height: 44,
                          decoration: BoxDecoration(
                            color: AppTheme.primary.withOpacity(0.12),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(Icons.warning_rounded, color: AppTheme.primary),
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Text(
                            latestAlert,
                            style: AppTheme.textTheme.bodyLarge?.copyWith(
                              fontWeight: FontWeight.w800,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  // --- Header Implementation ---
  Widget _buildHeader(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            // Premium SJ Avatar
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: AppTheme.primary.withOpacity(0.1),
                shape: BoxShape.circle,
                border: Border.all(color: AppTheme.primary.withOpacity(0.05), width: 1),
              ),
              child: Center(
                child: Text(
                  _getInitials('Sarah Jenkins'),
                  style: AppTheme.textTheme.labelLarge?.copyWith(
                    color: AppTheme.primary,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            RichText(
              text: TextSpan(
                children: [
                  TextSpan(
                    text: 'Keep',
                    style: AppTheme.textTheme.headlineMedium?.copyWith(
                      color: AppTheme.primary,
                      fontSize: 22,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  TextSpan(
                    text: 'Beat',
                    style: AppTheme.textTheme.headlineMedium?.copyWith(
                      color: AppTheme.primary,
                      fontSize: 22,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        Row(
          children: [
            GestureDetector(
              onTap: () => Navigator.of(context).pushNamed('/emergency'),
              child: GlassPill(
                tint: AppTheme.primaryFixed,
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                child: Row(
                  children: [
                    const Icon(Icons.sos_rounded, size: 18, color: AppTheme.primary),
                    const SizedBox(width: 8),
                    Text(
                      'SOS',
                      style: AppTheme.textTheme.labelLarge?.copyWith(
                        color: AppTheme.primary,
                        fontWeight: FontWeight.w900,
                        fontSize: 12,
                        letterSpacing: 1.2,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  // --- Antigravity Heart Hero ---
  Widget _buildHeartHero(int bpm) {
    return Center(
      child: Stack(
        alignment: Alignment.center,
        clipBehavior: Clip.none,
        children: [
          // Static Base Circle
          Container(
            width: 240,
            height: 240,
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              color: Color(0xFF3E464D), // Dark slate void
            ),
          ),

          // 🪐 Floating & Beating Heart
          AntiGravityWrapper(
            offset: 12,
            duration: const Duration(milliseconds: 3000),
            child: ScaleTransition(
              scale: Tween<double>(begin: 0.95, end: 1.05).animate(
                CurvedAnimation(parent: _pulseController, curve: Curves.elasticOut),
              ),
              child: StitchHeart(bpm: bpm, size: 170, showBpm: false),
            ),
          ),

          // 🌠 Parallax Status Badge
          Positioned(
            top: 20,
            right: -10,
            child: AntiGravityWrapper(
              offset: 6,
              duration: const Duration(milliseconds: 2400),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.06),
                      blurRadius: 20,
                      offset: const Offset(0, 10),
                    ),
                  ],
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'STATUS',
                      style: AppTheme.textTheme.labelSmall?.copyWith(
                        color: AppTheme.primary.withOpacity(0.6),
                        fontSize: 8,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 2.0,
                      ),
                    ),
                    Text(
                      'OPTIMAL',
                      style: AppTheme.textTheme.labelSmall?.copyWith(
                        color: const Color(0xFF1A1D20),
                        fontSize: 12,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // --- Heart Rate Card (Stitch Deep Red) ---
  Widget _buildHeartRateCard(int bpm) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: AppTheme.primaryCardDecoration,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'HEART RATE',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.8),
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.0,
                    ),
                  ),
                  Text(
                    '$bpm',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 80,
                      fontWeight: FontWeight.bold,
                      height: 1,
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(24),
                ),
                child: const Icon(Icons.favorite_rounded, color: Colors.white, size: 30),
              )
            ],
          ),
          const SizedBox(height: 24),
          // Animated Progress Bar
          Stack(
            children: [
              Container(
                height: 6,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
              FractionallySizedBox(
                widthFactor: 0.7,
                child: Container(
                  height: 6,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(10),
                    boxShadow: [
                      BoxShadow(color: Colors.white.withOpacity(0.4), blurRadius: 10),
                    ],
                  ),
                ),
              ),
            ],
          ),
          const Align(
            alignment: Alignment.centerRight,
            child: Padding(
              padding: EdgeInsets.only(top: 8),
              child: Text(
                'BPM',
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
              ),
            ),
          )
        ],
      ),
    );
  }

  String _getInitials(String name) {
    if (name.isEmpty) return '??';
    List<String> parts = name.trim().split(RegExp(r'\s+'));
    if (parts.length == 1) return parts[0].substring(0, parts[0].length >= 2 ? 2 : 1).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }
}

// 🪐 Antigravity Bobbing Animation
class AntiGravityWrapper extends StatefulWidget {
  final Widget child;
  final double offset;
  final Duration duration;

  const AntiGravityWrapper({
    super.key,
    required this.child,
    this.offset = 10.0,
    this.duration = const Duration(seconds: 2),
  });

  @override
  State<AntiGravityWrapper> createState() => _AntiGravityWrapperState();
}

class _AntiGravityWrapperState extends State<AntiGravityWrapper>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this, duration: widget.duration)
      ..repeat(reverse: true);
    
    _animation = Tween<double>(begin: 0, end: widget.offset).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOutSine),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Transform.translate(
          offset: Offset(0, -_animation.value),
          child: Container(
            decoration: BoxDecoration(
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.04 + (_animation.value * 0.001)),
                  blurRadius: 40 + _animation.value,
                  spreadRadius: -15,
                  offset: Offset(0, 30 + _animation.value),
                ),
              ],
            ),
            child: widget.child,
          ),
        );
      },
    );
  }
}
