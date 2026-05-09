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
  final _emailController = TextEditingController(text: 'sarah.jenkins@keepbeat.com');
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
        decoration: BoxDecoration(gradient: AppTheme.pageGradient),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(0, 0, 0, 24),
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(26, 18, 26, 14),
                  child: Row(
                    children: const [
                      AppLogoWordmark(
                        assetPath: 'assets/images/logoKeepBeat.png',
                        logoSize: 38,
                        textSize: 20,
                        redText: true,
                      ),
                    ],
                  ),
                ),
                Container(height: 1, color: AppTheme.line),
                const SizedBox(height: 60),
                Image.asset(
                  'assets/images/logoKeepBeat.png',
                  width: 110,
                  height: 110,
                ),
                const SizedBox(height: 26),
                Text(
                  'Welcome Back',
                  style: AppTheme.textTheme.displayMedium?.copyWith(fontSize: 42),
                ),
                const SizedBox(height: 8),
                Text(
                  "Your heart's journey continues here.",
                  style: AppTheme.textTheme.bodyLarge?.copyWith(
                    color: const Color(0xFF5B3434),
                    fontSize: 18,
                  ),
                ),
                const SizedBox(height: 28),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 22),
                  child: Container(
                    padding: const EdgeInsets.all(24),
                    decoration: AppTheme.bentoDecoration,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _fieldLabel('EMAIL ADDRESS'),
                        const SizedBox(height: 12),
                        StitchInput(
                          controller: _emailController,
                          hintText: 'heart@keepbeat.com',
                        ),
                        const SizedBox(height: 26),
                        Row(
                          children: [
                            _fieldLabel('PASSWORD'),
                            const Spacer(),
                            Text(
                              'Forgot Password?',
                              style: AppTheme.textTheme.labelLarge?.copyWith(
                                color: AppTheme.primary,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        StitchInput(
                          controller: _passwordController,
                          hintText: '••••••••',
                          isPassword: true,
                        ),
                        const SizedBox(height: 28),
                        StitchButton(
                          onTap: () => Navigator.of(context).pushReplacementNamed('/dashboard'),
                          text: 'Sign In',
                          icon: Icons.arrow_forward,
                        ),
                        const SizedBox(height: 28),
                        Row(
                          children: [
                            const Expanded(child: Divider(color: AppTheme.line)),
                            Padding(
                              padding: const EdgeInsets.symmetric(horizontal: 12),
                              child: Text(
                                'OR CONTINUE WITH',
                                style: AppTheme.textTheme.labelLarge?.copyWith(
                                  color: const Color(0xFF8D726F),
                                ),
                              ),
                            ),
                            const Expanded(child: Divider(color: AppTheme.line)),
                          ],
                        ),
                        const SizedBox(height: 24),
                        Row(
                          children: [
                            Expanded(
                              child: SocialAuthTile(
                                icon: FontAwesomeIcons.google,
                                label: 'Google',
                                onTap: () {},
                              ),
                            ),
                            const SizedBox(width: 14),
                            Expanded(
                              child: SocialAuthTile(
                                icon: FontAwesomeIcons.apple,
                                label: 'Apple',
                                onTap: () {},
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 32),
                RichText(
                  text: TextSpan(
                    style: AppTheme.textTheme.titleLarge?.copyWith(
                      color: const Color(0xFF5A3434),
                    ),
                    children: [
                      const TextSpan(text: 'New to KeepBeat? '),
                      TextSpan(
                        text: 'Create an account',
                        style: AppTheme.textTheme.titleLarge?.copyWith(
                          color: AppTheme.primary,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 48),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 22),
                  child: Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: AppTheme.lavenderSoft,
                      borderRadius: BorderRadius.circular(26),
                      border: Border.all(color: const Color(0xFFE8D6FB)),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          width: 56,
                          height: 56,
                          decoration: BoxDecoration(
                            color: AppTheme.lavender,
                            borderRadius: BorderRadius.circular(18),
                          ),
                          child: const Icon(Icons.auto_awesome, color: Colors.white),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'AI SECURITY TIP',
                                style: AppTheme.textTheme.labelLarge?.copyWith(
                                  letterSpacing: 1.3,
                                ),
                              ),
                              const SizedBox(height: 6),
                              Text(
                                'KeepBeat uses biometric-grade encryption to protect your vital statistics. Always use a unique password.',
                                style: AppTheme.textTheme.bodyLarge?.copyWith(
                                  color: const Color(0xFF7428B7),
                                ),
                              ),
                            ],
                          ),
                        ),
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

  Widget _fieldLabel(String text) {
    return Text(
      text,
      style: AppTheme.textTheme.labelSmall?.copyWith(
        color: const Color(0xFF53302B),
        fontSize: 12,
      ),
    );
  }
}
