import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

import '../theme/app_theme.dart';
import '../providers/patient_provider.dart';
import 'widgets/bento_widgets.dart';

class SignInUI extends ConsumerStatefulWidget {
  const SignInUI({super.key});

  @override
  ConsumerState<SignInUI> createState() => _SignInUIState();
}

class _SignInUIState extends ConsumerState<SignInUI> {
  final _emailController =
      TextEditingController(text: 'heart@keepbeat.com');
  final _passwordController = TextEditingController(text: 'patient123');

  @override
  void dispose() {
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
          child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            child: Column(
              children: [
                const _SignInHero(),
                Transform.translate(
                  offset: const Offset(0, -40),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: Column(
                      children: [
                        GlassCard(
                          padding: const EdgeInsets.fromLTRB(26, 28, 26, 26),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Sign In',
                                style: AppTheme.textTheme.headlineMedium?.copyWith(
                                  fontSize: 22,
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Access your health records securely.',
                                style: AppTheme.textTheme.bodyMedium?.copyWith(
                                  color: AppTheme.onSurface.withOpacity(0.72),
                                  fontSize: 14,
                                ),
                              ),
                              const SizedBox(height: 32),
                              _fieldLabel('EMAIL ADDRESS'),
                              const SizedBox(height: 10),
                              StitchInput(
                                controller: _emailController,
                                hintText: 'heart@keepbeat.com',
                                prefixIcon: Icons.mail_rounded,
                              ),
                              const SizedBox(height: 20),
                              Row(
                                children: [
                                  _fieldLabel('PASSWORD'),
                                  const Spacer(),
                                  Text(
                                    'Forgot?',
                                    style: AppTheme.textTheme.labelLarge?.copyWith(
                                      color: AppTheme.primary,
                                      fontSize: 12,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 10),
                              StitchInput(
                                controller: _passwordController,
                                hintText: '••••••••',
                                prefixIcon: Icons.lock_rounded,
                                isPassword: true,
                              ),
                              const SizedBox(height: 28),
                              StitchButton(
                                onTap: () {
                                  final email = _emailController.text;
                                  String name = 'Unknown User';
                                  if (email.contains('@')) {
                                    final parts = email.split('@')[0].replaceAll(RegExp(r'[^a-zA-Z0-9]'), ' ').trim().split(' ');
                                    name = parts.map((w) => w.isNotEmpty ? '${w[0].toUpperCase()}${w.substring(1).toLowerCase()}' : '').join(' ');
                                  }
                                  if (name.trim().isEmpty) name = 'User';
                                  ref.read(patientContextProvider.notifier).setActivePatient('PT_001', '#TP-8842', name);
                                  Navigator.of(context).pushReplacementNamed('/dashboard');
                                },
                                text: 'Sign In',
                                icon: Icons.arrow_forward_rounded,
                                height: 62,
                              ),
                              const SizedBox(height: 24),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Text(
                                    'New here? ',
                                    style: AppTheme.textTheme.bodyMedium?.copyWith(
                                      color: AppTheme.onSurface.withOpacity(0.64),
                                      fontSize: 12,
                                    ),
                                  ),
                                  GestureDetector(
                                    onTap: () => Navigator.of(context)
                                        .pushReplacementNamed('/signup'),
                                    child: Text(
                                      'Create Account',
                                      style: AppTheme.textTheme.labelLarge?.copyWith(
                                        color: AppTheme.primary,
                                        fontSize: 12,
                                        fontWeight: FontWeight.w800,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 60),
                        Text(
                          '© 2026 KEEPBEAT MEDICAL SYSTEMS',
                          style: AppTheme.textTheme.labelSmall?.copyWith(
                            color: AppTheme.onSurfaceMuted.withOpacity(0.50),
                            fontSize: 10,
                            letterSpacing: 1.2,
                          ),
                        ),
                        const SizedBox(height: 32),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _SignInHero extends StatelessWidget {
  const _SignInHero();

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 360,
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
            padding: const EdgeInsets.only(bottom: 80),
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
                  'Welcome Back',
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
                  "Continue your journey to better health.",
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

Widget _fieldLabel(String label) {
  return Text(
    label,
    style: AppTheme.textTheme.labelSmall?.copyWith(
      color: AppTheme.onSurface.withOpacity(0.78),
      fontSize: 11,
      letterSpacing: 1.4,
    ),
  );
}
