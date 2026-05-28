import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';

class AiTwinSidebar extends StatelessWidget {
  const AiTwinSidebar({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              AppTheme.lavenderSoft.withOpacity(0.9),
              Colors.white,
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              _buildHeader(context),
              Expanded(
                child: SingleChildScrollView(
                  physics: const BouncingScrollPhysics(),
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const _AiAvatarHero(),
                      const SizedBox(height: 32),
                      _buildNarrativeSection(),
                      const SizedBox(height: 32),
                      _buildRecommendationSection(),
                      const SizedBox(height: 40),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 24, 16),
      child: Row(
        children: [
          IconButton(
            icon: const Icon(Icons.close_rounded, size: 28),
            onPressed: () => Navigator.of(context).pop(),
          ),
          const Spacer(),
          const StatusBadge(
            label: 'AI ONLINE',
            color: AppTheme.lavender,
          ),
        ],
      ),
    );
  }

  Widget _buildNarrativeSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'DAILY TWIN SUMMARY',
          style: AppTheme.textTheme.labelSmall?.copyWith(
            letterSpacing: 2.0,
            color: AppTheme.lavender,
          ),
        ),
        const SizedBox(height: 16),
        Text(
          'Hello Wafa, your twin is synchronized.',
          style: AppTheme.textTheme.displaySmall?.copyWith(
            fontSize: 28,
            color: AppTheme.onSurface,
          ),
        ),
        const SizedBox(height: 12),
        Text(
          "I've analyzed your sleep, heart rhythm, and glucose patterns over the last 24 hours. You are currently in an 'Optimal Recovery' state, with your pacemaker performing at 98% efficiency.",
          style: AppTheme.textTheme.bodyLarge?.copyWith(
            color: AppTheme.onSurface.withOpacity(0.7),
            height: 1.6,
          ),
        ),
      ],
    );
  }

  Widget _buildRecommendationSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'PROACTIVE STEPS',
          style: AppTheme.textTheme.labelSmall?.copyWith(
            letterSpacing: 2.0,
            color: AppTheme.onSurface.withOpacity(0.4),
          ),
        ),
        const SizedBox(height: 16),
        const _InsightCard(
          icon: Icons.wb_sunny_rounded,
          title: 'Hydration Focus',
          description: 'Your heart rate variability indicates mild dehydration. Aim for 500ml of water in the next hour.',
          color: AppTheme.blue,
        ),
        const SizedBox(height: 16),
        const _InsightCard(
          icon: Icons.nightlight_round,
          title: 'Early Rest',
          description: 'Your glucose trend is slightly low this evening. Consider a light, high-protein snack before bed.',
          color: AppTheme.lavender,
        ),
        const SizedBox(height: 16),
        const _InsightCard(
          icon: Icons.check_circle_rounded,
          title: 'Pacemaker Check',
          description: 'The ECG leads are capturing high-fidelity data. No noise detected in the last 4 hours.',
          color: Colors.green,
        ),
      ],
    );
  }
}

class _AiAvatarHero extends StatelessWidget {
  const _AiAvatarHero();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Stack(
        alignment: Alignment.center,
        children: [
          Container(
            width: 140,
            height: 140,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  AppTheme.lavender.withOpacity(0.2),
                  Colors.transparent,
                ],
              ),
            ),
          ),
          Container(
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: AppTheme.lavender.withOpacity(0.15),
                  blurRadius: 20,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: const Icon(
              Icons.auto_awesome_rounded,
              color: AppTheme.lavender,
              size: 48,
            ),
          ),
          Positioned(
            bottom: 0,
            right: 0,
            child: Container(
              padding: const EdgeInsets.all(8),
              decoration: const BoxDecoration(
                color: Colors.green,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.bolt_rounded, color: Colors.white, size: 16),
            ),
          ),
        ],
      ),
    );
  }
}

class _InsightCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final Color color;

  const _InsightCard({
    required this.icon,
    required this.title,
    required this.description,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(20),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTheme.textTheme.titleMedium?.copyWith(
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: AppTheme.textTheme.bodyMedium?.copyWith(
                    color: AppTheme.onSurface.withOpacity(0.6),
                    height: 1.5,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
