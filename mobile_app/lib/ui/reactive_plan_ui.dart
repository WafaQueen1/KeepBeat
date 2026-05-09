import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';

class ReactivePlanUI extends StatelessWidget {
  const ReactivePlanUI({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.pageGradient),
        child: SafeArea(
          child: Column(
            children: [
              _buildHeader(context),
              Expanded(
                child: SingleChildScrollView(
                  physics: const BouncingScrollPhysics(),
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Column(
                    children: [
                      const _RecoveryHero(),
                      const SizedBox(height: 24),
                      const _ActionPlanSection(),
                      const SizedBox(height: 120), // Bottom padding
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
      padding: const EdgeInsets.fromLTRB(20, 10, 20, 20),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
            onPressed: () => Navigator.of(context).pop(),
          ),
          const AppLogoWordmark(
            assetPath: 'assets/images/logoKeepBeat.png',
            logoSize: 28,
            textSize: 16,
            redText: true,
          ),
          const CircleAvatar(
            radius: 18,
            backgroundImage: AssetImage('assets/images/avatar.png'),
          ),
        ],
      ),
    );
  }
}

class _RecoveryHero extends StatelessWidget {
  const _RecoveryHero();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(38),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 30,
            offset: const Offset(0, 15),
          ),
        ],
      ),
      child: Column(
        children: [
          const StatusBadge(label: 'RECOVERY PHASE', color: AppTheme.blue),
          const SizedBox(height: 28),
          Stack(
            alignment: Alignment.center,
            children: [
              Container(
                width: 160,
                height: 160,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      AppTheme.blue.withOpacity(0.12),
                      Colors.transparent,
                    ],
                  ),
                ),
              ),
              Image.asset(
                'assets/images/heart.png',
                width: 130,
                height: 130,
                fit: BoxFit.contain,
              ),
            ],
          ),
          const SizedBox(height: 24),
          Text(
            'Monitoring Stability',
            style: AppTheme.textTheme.displaySmall?.copyWith(fontSize: 26),
          ),
          const SizedBox(height: 8),
          Text(
            'Vital signs are returning to baseline.\nFollow the recovery plan below.',
            textAlign: TextAlign.center,
            style: AppTheme.textTheme.bodyMedium?.copyWith(
              color: AppTheme.onSurface.withOpacity(0.5),
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}

class _ActionPlanSection extends StatelessWidget {
  const _ActionPlanSection();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4, bottom: 16),
          child: Text(
            'RECOVERY ACTION PLAN',
            style: AppTheme.textTheme.titleSmall?.copyWith(
              letterSpacing: 1.5,
              fontWeight: FontWeight.w800,
              color: AppTheme.onSurface.withOpacity(0.4),
            ),
          ),
        ),
        _InstructionItem(
          icon: Icons.water_drop_rounded,
          color: AppTheme.blue,
          title: 'Check Glucose Level',
          subtitle: 'Verify if blood sugar is above 90 mg/dL.',
          isDone: true,
        ),
        const SizedBox(height: 14),
        _InstructionItem(
          icon: Icons.chair_rounded,
          color: AppTheme.lavender,
          title: 'Sit and Rest',
          subtitle: 'Keep activity minimal for the next 15 mins.',
          isDone: false,
        ),
        const SizedBox(height: 14),
        _InstructionItem(
          icon: Icons.medication_rounded,
          color: AppTheme.primary,
          title: 'Glucose Supplement',
          subtitle: 'Intake 15g of fast-acting carbohydrates.',
          isDone: false,
        ),
      ],
    );
  }
}

class _InstructionItem extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String title;
  final String subtitle;
  final bool isDone;

  const _InstructionItem({
    required this.icon,
    required this.color,
    required this.title,
    required this.subtitle,
    this.isDone = false,
  });

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(20),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTheme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w800,
                    decoration: isDone ? TextDecoration.lineThrough : null,
                  ),
                ),
                Text(
                  subtitle,
                  style: AppTheme.textTheme.bodySmall?.copyWith(
                    color: AppTheme.onSurface.withOpacity(0.5),
                  ),
                ),
              ],
            ),
          ),
          Icon(
            isDone ? Icons.check_circle_rounded : Icons.circle_outlined,
            color: isDone ? Colors.green : AppTheme.onSurface.withOpacity(0.2),
          ),
        ],
      ),
    );
  }
}
