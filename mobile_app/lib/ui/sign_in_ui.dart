import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import '../theme/app_theme.dart';
import 'widgets/bento_widgets.dart';

class SignInUI extends ConsumerStatefulWidget {
  const SignInUI({super.key});

  @override
  ConsumerState<SignInUI> createState() => _SignInUIState();
}

class _SignInUIState extends ConsumerState<SignInUI> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

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
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFFFFEEF0), // Top: Gentle warm red-pink
              Color(0xFFFFFAFB), // Middle: Soft pale pink
              Color(0xFFF8F9FA), // Bottom: Base Canvas grey (very subtle)
            ],
            stops: [0.0, 0.6, 1.0],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.symmetric(horizontal: 40.0, vertical: 40.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 32),
                
                // ── Volumetric Organic Units ──
                const Center(
                  child: StitchHeart(
                    bpm: 68, 
                    size: 150, 
                    showBpm: false, 
                  ),
                ),
                const SizedBox(height: 12),
                Center(
                  child: Text(
                    'KEEPBEAT',
                    style: AppTheme.textTheme.labelSmall?.copyWith(
                      color: AppTheme.primary,
                      letterSpacing: 7.0,
                      fontWeight: FontWeight.w900,
                      fontSize: 11,
                    ),
                  ),
                ),
                
                const SizedBox(height: 60),

                // ── Hero Header ──
                Material(
                  color: Colors.transparent,
                  child: Text(
                    'Welcome Back',
                    style: AppTheme.textTheme.displayMedium?.copyWith(
                      fontSize: 38,
                      fontWeight: FontWeight.w900,
                      letterSpacing: -2.0,
                      color: AppTheme.onSurface,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  "Your heart's journey continues here.",
                  style: AppTheme.textTheme.bodyLarge?.copyWith(
                    color: AppTheme.onSurfaceMuted.withOpacity(0.55),
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                  ),
                  textAlign: TextAlign.center,
                ),

                const SizedBox(height: 56),

                // ── Authenticated Bento Case ──
                BentoTile(
                  title: 'Secure Clinical Access',
                  child: Column(
                    children: [
                      StitchInput(
                        controller: _emailController,
                        hintText: 'Clinical E-mail',
                        prefixIcon: Icons.email_outlined,
                      ),
                      const SizedBox(height: 20),
                      StitchInput(
                        controller: _passwordController,
                        hintText: 'Passcode Sequence',
                        prefixIcon: Icons.lock_outline_rounded,
                        isPassword: true,
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 16),
                
                Align(
                  alignment: Alignment.centerRight,
                  child: TextButton(
                    onPressed: () {},
                    child: Text(
                      'Forgot Passcode?',
                      style: AppTheme.textTheme.labelLarge?.copyWith(
                        color: AppTheme.primary,
                        fontWeight: FontWeight.w900,
                        fontSize: 13,
                        letterSpacing: -0.2,
                      ),
                    ),
                  ),
                ),

                const SizedBox(height: 48),

                // ── Tactile Dashboard Access ──
                StitchButton(
                  onTap: () => Navigator.of(context).pushReplacementNamed('/dashboard'),
                  text: 'DASHBOARD ACCESS',
                  icon: Icons.shield_rounded,
                ),

                const SizedBox(height: 48),

                // ── Connection Pivot ──
                Row(
                  children: [
                    const Expanded(child: Divider(color: Color(0xFFEDEFF3), thickness: 2)),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 24),
                      child: Text(
                        'OR CONNECT WITH',
                        style: AppTheme.textTheme.labelSmall?.copyWith(
                          color: AppTheme.onSurfaceMuted.withOpacity(0.35),
                          fontSize: 10,
                          letterSpacing: 2.0,
                        ),
                      ),
                    ),
                    const Expanded(child: Divider(color: Color(0xFFEDEFF3), thickness: 2)),
                  ],
                ),

                const SizedBox(height: 32),

                Row(
                  children: [
                    Expanded(
                      child: SocialAuthTile(
                        icon: FontAwesomeIcons.google,
                        label: 'Google',
                        onTap: () {},
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: SocialAuthTile(
                        icon: FontAwesomeIcons.apple,
                        label: 'Apple',
                        onTap: () {},
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 64),

                // ── Onboarding Pivot ──
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'New to the network? ',
                      style: AppTheme.textTheme.bodyMedium?.copyWith(
                        color: AppTheme.onSurfaceMuted,
                        fontSize: 15,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    GestureDetector(
                      onTap: () => Navigator.of(context).pushReplacementNamed('/signup'),
                      child: Text(
                        'Join Vital Pulse',
                        style: AppTheme.textTheme.labelLarge?.copyWith(
                          color: AppTheme.primary,
                          fontWeight: FontWeight.w900,
                          fontSize: 15,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 40),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
