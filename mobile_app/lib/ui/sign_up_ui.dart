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
  final _confirmController = TextEditingController();
  final _clinicalIdController = TextEditingController();

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmController.dispose();
    _clinicalIdController.dispose();
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
              Color(0xFFF8F9FA), // Bottom: Base Canvas
            ],
            stops: [0.0, 0.6, 1.0],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.symmetric(horizontal: 32.0, vertical: 32.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // ── Volumetric Organic Units ──
                const Center(
                  child: StitchHeart(
                    bpm: 68, 
                    size: 110, 
                    showBpm: false, 
                  ),
                ),
                const SizedBox(height: 8),
                Center(
                  child: Text(
                    'KEEPBEAT',
                    style: AppTheme.textTheme.labelSmall?.copyWith(
                      color: AppTheme.primary,
                      letterSpacing: 7.0,
                      fontWeight: FontWeight.w900,
                      fontSize: 10,
                    ),
                  ),
                ),
                
                const SizedBox(height: 48),

                // ── Hero Header ──
                Material(
                  color: Colors.transparent,
                  child: Text(
                    'Join Vital Pulse',
                    style: AppTheme.textTheme.displayMedium?.copyWith(
                      fontSize: 34,
                      fontWeight: FontWeight.w900,
                      letterSpacing: -1.5,
                      color: AppTheme.onSurface,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  "Begin the standard of clinical heart care.",
                  style: AppTheme.textTheme.bodyLarge?.copyWith(
                    color: AppTheme.onSurfaceMuted.withOpacity(0.55),
                    fontSize: 15,
                    fontWeight: FontWeight.w500,
                  ),
                  textAlign: TextAlign.center,
                ),

                const SizedBox(height: 40),

                // ── Patient Identification Bento ──
                BentoTile(
                  title: 'Patient Identification',
                  child: Column(
                    children: [
                      StitchInput(
                        controller: _nameController,
                        hintText: 'Full Legal Identity',
                        prefixIcon: Icons.person_outline_rounded,
                      ),
                      const SizedBox(height: 16),
                      StitchInput(
                        controller: _emailController,
                        hintText: 'Verified Email Address',
                        prefixIcon: Icons.email_outlined,
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 16),

                // ── Clinical Security Bento ──
                BentoTile(
                  title: 'Clinical Security',
                  child: Column(
                    children: [
                      StitchInput(
                        controller: _passwordController,
                        hintText: 'Security Passcode',
                        prefixIcon: Icons.lock_outline_rounded,
                        isPassword: true,
                      ),
                      const SizedBox(height: 16),
                      StitchInput(
                        controller: _confirmController,
                        hintText: 'Confirm Sequence',
                        prefixIcon: Icons.shield_outlined,
                        isPassword: true,
                      ),
                      const SizedBox(height: 16),
                      StitchInput(
                        controller: _clinicalIdController,
                        hintText: 'Clinical Provider ID (Optional)',
                        prefixIcon: Icons.local_hospital_outlined,
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 40),

                // ── Sign Up Action ──
                StitchButton(
                  onTap: () => Navigator.of(context).pushReplacementNamed('/dashboard'),
                  text: 'START HEALTH JOURNEY',
                  icon: Icons.auto_awesome_rounded,
                ),

                const SizedBox(height: 48),

                // ── Footer Pivot ──
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'Member already? ',
                      style: AppTheme.textTheme.bodyMedium?.copyWith(
                        color: AppTheme.onSurfaceMuted,
                        fontSize: 15,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    GestureDetector(
                      onTap: () => Navigator.of(context).pushReplacementNamed('/login'),
                      child: Text(
                        'Access Account',
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
