import 'dart:ui';

import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';

class SignUpUI extends StatefulWidget {
  const SignUpUI({super.key});

  @override
  State<SignUpUI> createState() => _SignUpUIState();
}

class _SignUpUIState extends State<SignUpUI> {
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _acceptedPrivacy = false;

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.pageGradient),
        child: SafeArea(
          bottom: false,
          child: LayoutBuilder(
            builder: (context, constraints) {
              final horizontalPadding = constraints.maxWidth < 380 ? 16.0 : 20.0;
              final maxContentWidth = constraints.maxWidth > 520 ? 430.0 : double.infinity;

              return SingleChildScrollView(
                physics: const BouncingScrollPhysics(),
                child: Center(
                  child: ConstrainedBox(
                    constraints: BoxConstraints(maxWidth: maxContentWidth),
                    child: Column(
                      children: [
                        _HeroSection(horizontalPadding: horizontalPadding),
                        Transform.translate(
                          offset: const Offset(0, -40),
                          child: Padding(
                            padding: EdgeInsets.symmetric(horizontal: horizontalPadding),
                            child: Column(
                              children: [
                                _CreateAccountCard(
                                  nameController: _nameController,
                                  emailController: _emailController,
                                  passwordController: _passwordController,
                                  acceptedPrivacy: _acceptedPrivacy,
                                  onPrivacyChanged: (value) {
                                    setState(() => _acceptedPrivacy = value);
                                  },
                                ),
                                const SizedBox(height: 54),
                                Text(
                                  '© 2024 KEEPBEAT MEDICAL SYSTEMS. LOCALLY\nPROCESSED. FULLY ENCRYPTED.',
                                  textAlign: TextAlign.center,
                                  style: AppTheme.textTheme.labelSmall?.copyWith(
                                    color: AppTheme.onSurfaceMuted.withOpacity(0.55),
                                    fontSize: 10,
                                    letterSpacing: 1.3,
                                    height: 1.45,
                                  ),
                                ),
                                const SizedBox(height: 28),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}

class _HeroSection extends StatelessWidget {
  final double horizontalPadding;

  const _HeroSection({required this.horizontalPadding});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 380,
      width: double.infinity,
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFFFFB6B8),
            Color(0xFFE53A40),
            Color(0xFFB6171E),
          ],
        ),
      ),
      child: Stack(
        children: [
          Positioned(
            top: -60,
            right: -40,
            child: _SoftOrb(
              size: 280,
              color: Colors.white.withOpacity(0.12),
            ),
          ),
          Positioned(
            left: -80,
            bottom: 40,
            child: _SoftOrb(
              size: 240,
              color: Colors.white.withOpacity(0.10),
            ),
          ),
          Padding(
            padding: EdgeInsets.fromLTRB(horizontalPadding + 6, 20, horizontalPadding + 6, 80),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Spacer(flex: 2),
                Center(
                  child: Container(
                    padding: const EdgeInsets.all(22),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.15),
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: Colors.white.withOpacity(0.25),
                        width: 1.5,
                      ),
                    ),
                    child: Image.asset(
                      'assets/images/logoKeepBeat.png',
                      width: 110,
                      height: 110,
                      fit: BoxFit.contain,
                    ),
                  ),
                ),
                const Spacer(flex: 3),
                Text(
                  'Start Your Health\nJourney',
                  textAlign: TextAlign.center,
                  style: AppTheme.textTheme.displayMedium?.copyWith(
                    color: Colors.white,
                    fontSize: 34,
                    height: 1.05,
                    letterSpacing: -1,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  "Join the next generation of cardiac care.",
                  textAlign: TextAlign.center,
                  style: AppTheme.textTheme.bodyLarge?.copyWith(
                    color: Colors.white.withOpacity(0.92),
                    fontSize: 16,
                    height: 1.35,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const Spacer(flex: 4),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// Removed unused _PredictiveCareCard and _LogoShowcaseCard

class _CreateAccountCard extends StatelessWidget {
  final TextEditingController nameController;
  final TextEditingController emailController;
  final TextEditingController passwordController;
  final bool acceptedPrivacy;
  final ValueChanged<bool> onPrivacyChanged;

  const _CreateAccountCard({
    required this.nameController,
    required this.emailController,
    required this.passwordController,
    required this.acceptedPrivacy,
    required this.onPrivacyChanged,
  });

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.fromLTRB(26, 27, 26, 26),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Create Your Account',
            style: AppTheme.textTheme.headlineMedium?.copyWith(
              fontSize: 21,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Join 12,000+ others tracking their\nvitality.',
            style: AppTheme.textTheme.bodyMedium?.copyWith(
              color: AppTheme.onSurface.withOpacity(0.72),
              fontSize: 14,
              height: 1.35,
            ),
          ),
          const SizedBox(height: 28),
          const _FieldLabel('FULL NAME'),
          const SizedBox(height: 9),
          StitchInput(
            controller: nameController,
            hintText: 'John Doe',
            prefixIcon: Icons.person_rounded,
          ),
          const SizedBox(height: 19),
          const _FieldLabel('EMAIL ADDRESS'),
          const SizedBox(height: 9),
          StitchInput(
            controller: emailController,
            hintText: 'john@example.com',
            keyboardType: TextInputType.emailAddress,
            prefixIcon: Icons.mail_rounded,
          ),
          const SizedBox(height: 19),
          const _FieldLabel('CREATE PASSWORD'),
          const SizedBox(height: 9),
          StitchInput(
            controller: passwordController,
            hintText: '••••••••',
            prefixIcon: Icons.lock_rounded,
            isPassword: true,
          ),
          const SizedBox(height: 20),
          _PrivacyTermsRow(
            value: acceptedPrivacy,
            onChanged: onPrivacyChanged,
          ),
          const SizedBox(height: 20),
          StitchButton(
            onTap: () => Navigator.of(context).pushReplacementNamed('/dashboard'),
            text: 'Create My Account',
            icon: Icons.arrow_forward_rounded,
            height: 62,
          ),
          const SizedBox(height: 24),
          Container(height: 1, color: AppTheme.lineSoft),
          const SizedBox(height: 17),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                'Already have an account? ',
                style: AppTheme.textTheme.bodyMedium?.copyWith(
                  color: AppTheme.onSurface.withOpacity(0.64),
                  fontSize: 12,
                ),
              ),
              GestureDetector(
                onTap: () => Navigator.of(context).pushReplacementNamed('/login'),
                child: Text(
                  'Sign In',
                  style: AppTheme.textTheme.labelLarge?.copyWith(
                    color: AppTheme.primary,
                    fontSize: 12,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          const _CommunityRow(),
        ],
      ),
    );
  }
}

class _PrivacyTermsRow extends StatelessWidget {
  final bool value;
  final ValueChanged<bool> onChanged;

  const _PrivacyTermsRow({
    required this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(13, 14, 12, 14),
      decoration: BoxDecoration(
        color: const Color(0xFFF0F1F3),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Row(
        children: [
          Container(
            width: 45,
            height: 45,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(13),
              boxShadow: [
                BoxShadow(
                  color: AppTheme.primary.withOpacity(0.08),
                  blurRadius: 18,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: const Icon(
              Icons.health_and_safety_rounded,
              color: AppTheme.primary,
              size: 22,
            ),
          ),
          const SizedBox(width: 13),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Health Data Privacy\nTerms',
                  style: AppTheme.textTheme.labelLarge?.copyWith(
                    color: AppTheme.onSurface,
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    height: 1.25,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  'Learn more about our AI\nencryption',
                  style: AppTheme.textTheme.bodyMedium?.copyWith(
                    color: AppTheme.primary,
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    height: 1.25,
                  ),
                ),
              ],
            ),
          ),
          Transform.scale(
            scale: 0.82,
            child: Switch(
              value: value,
              onChanged: onChanged,
              activeColor: Colors.white,
              activeTrackColor: AppTheme.primary,
              inactiveThumbColor: Colors.white,
              inactiveTrackColor: const Color(0xFFE8B9B8),
              materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
            ),
          ),
        ],
      ),
    );
  }
}

class _CommunityRow extends StatelessWidget {
  const _CommunityRow();

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        SizedBox(
          width: 74,
          height: 28,
          child: Stack(
            children: [
              for (var i = 0; i < 3; i++)
                Positioned(
                  left: i * 18,
                  child: Container(
                    width: 28,
                    height: 28,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.white, width: 2),
                      image: const DecorationImage(
                        image: AssetImage('assets/images/avatar.png'),
                        fit: BoxFit.cover,
                      ),
                    ),
                  ),
                ),
              Positioned(
                right: 0,
                child: Container(
                  width: 31,
                  height: 28,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color: AppTheme.primaryFixed,
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(color: Colors.white, width: 2),
                  ),
                  child: Text(
                    '+12K',
                    style: AppTheme.textTheme.labelSmall?.copyWith(
                      color: AppTheme.primary,
                      fontSize: 8,
                      letterSpacing: 0,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(width: 14),
        Text(
          'ACTIVE COMMUNITY',
          style: AppTheme.textTheme.labelSmall?.copyWith(
            color: AppTheme.onSurfaceMuted.withOpacity(0.86),
            fontSize: 9,
            letterSpacing: 1.7,
          ),
        ),
      ],
    );
  }
}

class _FieldLabel extends StatelessWidget {
  final String label;

  const _FieldLabel(this.label);

  @override
  Widget build(BuildContext context) {
    return Text(
      label,
      style: AppTheme.textTheme.labelSmall?.copyWith(
        color: AppTheme.onSurface.withOpacity(0.82),
        fontSize: 9,
        letterSpacing: 1.5,
      ),
    );
  }
}

// Private _GlassCard removed, using GlassCard from bento_widgets.dart

class _PagerDot extends StatelessWidget {
  final bool active;

  const _PagerDot({required this.active});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: active ? 7 : 8,
      height: active ? 7 : 8,
      margin: const EdgeInsets.symmetric(horizontal: 3),
      decoration: BoxDecoration(
        color: active ? AppTheme.primary : AppTheme.primary.withOpacity(0.25),
        shape: BoxShape.circle,
      ),
    );
  }
}

class _SoftOrb extends StatelessWidget {
  final double size;
  final Color color;

  const _SoftOrb({
    required this.size,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: color,
        ),
      ),
    );
  }
}
