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
        decoration: BoxDecoration(gradient: AppTheme.pageGradient),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(18, 10, 18, 24),
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.fromLTRB(10, 12, 10, 28),
                  decoration: BoxDecoration(
                    gradient: AppTheme.heroGradient,
                    borderRadius: const BorderRadius.only(
                      bottomLeft: Radius.circular(44),
                      bottomRight: Radius.circular(44),
                    ),
                  ),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          const AppLogoWordmark(
                            assetPath: 'assets/images/logoKeepBeat.png',
                            logoSize: 32,
                            textSize: 18,
                          ),
                          const Spacer(),
                          Text(
                            'Help',
                            style: AppTheme.textTheme.bodyMedium?.copyWith(
                              color: AppTheme.onSurface,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 18),
                      Text(
                        'Start Your Health\nJourney',
                        textAlign: TextAlign.center,
                        style: AppTheme.textTheme.displayMedium?.copyWith(
                          color: Colors.white,
                          fontSize: 34,
                          height: 1.05,
                        ),
                      ),
                      const SizedBox(height: 14),
                      Text(
                        "Your heart deserves the world's most\nadvanced digital guardian.",
                        textAlign: TextAlign.center,
                        style: AppTheme.textTheme.bodyLarge?.copyWith(
                          color: Colors.white.withOpacity(0.85),
                        ),
                      ),
                      const SizedBox(height: 26),
                      _featureCard(),
                    ],
                  ),
                ),
                Transform.translate(
                  offset: const Offset(0, -16),
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 18),
                    decoration: AppTheme.bentoDecoration,
                    child: Column(
                      children: [
                        Image.asset(
                          'assets/images/logoKeepBeat.png',
                          width: 120,
                          height: 120,
                        ),
                        const SizedBox(height: 18),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: const [
                            _PagerDot(active: true),
                            _PagerDot(active: false),
                            _PagerDot(active: false),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
                Transform.translate(
                  offset: const Offset(0, -2),
                  child: Container(
                    padding: const EdgeInsets.all(26),
                    decoration: AppTheme.bentoDecoration,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Create Your Account',
                          style: AppTheme.textTheme.headlineMedium?.copyWith(
                            fontSize: 24,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Join 12,000+ others tracking their vitality.',
                          style: AppTheme.textTheme.bodyLarge?.copyWith(
                            color: const Color(0xFF5B3B37),
                          ),
                        ),
                        const SizedBox(height: 26),
                        _fieldLabel('FULL NAME'),
                        const SizedBox(height: 8),
                        StitchInput(
                          controller: _nameController,
                          hintText: 'John Doe',
                          prefixIcon: Icons.person,
                        ),
                        const SizedBox(height: 18),
                        _fieldLabel('EMAIL ADDRESS'),
                        const SizedBox(height: 8),
                        StitchInput(
                          controller: _emailController,
                          hintText: 'john@example.com',
                          prefixIcon: Icons.email,
                        ),
                        const SizedBox(height: 18),
                        _fieldLabel('CREATE PASSWORD'),
                        const SizedBox(height: 8),
                        StitchInput(
                          controller: _passwordController,
                          hintText: '••••••••',
                          prefixIcon: Icons.lock,
                          isPassword: true,
                        ),
                        const SizedBox(height: 20),
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF1F1F4),
                            borderRadius: BorderRadius.circular(18),
                          ),
                          child: Row(
                            children: [
                              Container(
                                width: 42,
                                height: 42,
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(14),
                                ),
                                child: const Icon(Icons.verified_user, color: AppTheme.primary),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'Health Data Privacy Terms',
                                      style: AppTheme.textTheme.labelLarge,
                                    ),
                                    const SizedBox(height: 2),
                                    Text(
                                      'Learn more about our AI encryption',
                                      style: AppTheme.textTheme.bodyMedium?.copyWith(
                                        color: AppTheme.primary,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              Switch(
                                value: _acceptedPrivacy,
                                onChanged: (value) => setState(() => _acceptedPrivacy = value),
                                activeColor: Colors.white,
                                activeTrackColor: const Color(0xFFE8B7B6),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 20),
                        StitchButton(
                          onTap: () => Navigator.of(context).pushReplacementNamed('/dashboard'),
                          text: 'Create My Account',
                          icon: Icons.arrow_forward,
                        ),
                        const SizedBox(height: 24),
                        const Divider(color: AppTheme.line),
                        const SizedBox(height: 14),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              'Already have an account? ',
                              style: AppTheme.textTheme.bodyMedium,
                            ),
                            GestureDetector(
                              onTap: () => Navigator.of(context).pushReplacementNamed('/login'),
                              child: Text(
                                'Sign In',
                                style: AppTheme.textTheme.labelLarge?.copyWith(
                                  color: AppTheme.primary,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const CircleAvatar(radius: 12, backgroundImage: AssetImage('assets/images/avatar.png')),
                            const SizedBox(width: 4),
                            const CircleAvatar(radius: 12, backgroundImage: AssetImage('assets/images/avatar.png')),
                            const SizedBox(width: 4),
                            const CircleAvatar(radius: 12, backgroundImage: AssetImage('assets/images/avatar.png')),
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: AppTheme.redSoft,
                                borderRadius: BorderRadius.circular(999),
                              ),
                              child: Text(
                                '+12K',
                                style: AppTheme.textTheme.labelSmall?.copyWith(
                                  color: AppTheme.primary,
                                ),
                              ),
                            ),
                            const SizedBox(width: 10),
                            Text(
                              'ACTIVE COMMUNITY',
                              style: AppTheme.textTheme.labelSmall,
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 34),
                Text(
                  '© 2024 KEEPBEAT MEDICAL SYSTEMS. LOCALLY\nPROCESSED. FULLY ENCRYPTED.',
                  textAlign: TextAlign.center,
                  style: AppTheme.textTheme.labelSmall?.copyWith(
                    color: const Color(0xFFC8B2B2),
                    fontSize: 10,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _featureCard() {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 24, 20, 24),
      decoration: AppTheme.bentoDecoration,
      child: Column(
        children: [
          Container(
            width: 84,
            height: 84,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: AppTheme.lavender.withOpacity(0.16),
                  blurRadius: 18,
                  offset: const Offset(0, 8),
                ),
              ],
            ),
            child: Center(
              child: Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: AppTheme.lavender,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.settings, color: Colors.white),
              ),
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'AI FOG AGENT POWERED',
            style: AppTheme.textTheme.labelSmall?.copyWith(
              color: AppTheme.lavender,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Predictive Care',
            style: AppTheme.textTheme.titleLarge?.copyWith(fontSize: 18),
          ),
          const SizedBox(height: 8),
          Text(
            'Our AI Fog Agent monitors your heartbeat locally, ensuring maximum privacy and instant diagnostics.',
            textAlign: TextAlign.center,
            style: AppTheme.textTheme.bodyMedium?.copyWith(
              color: const Color(0xFF5D4A47),
            ),
          ),
        ],
      ),
    );
  }

  Widget _fieldLabel(String text) {
    return Text(
      text,
      style: AppTheme.textTheme.labelSmall?.copyWith(
        color: const Color(0xFF3D2421),
      ),
    );
  }
}

class _PagerDot extends StatelessWidget {
  final bool active;
  const _PagerDot({required this.active});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 8,
      height: 8,
      margin: const EdgeInsets.symmetric(horizontal: 3),
      decoration: BoxDecoration(
        color: active ? AppTheme.primary : const Color(0xFFE8C5C6),
        shape: BoxShape.circle,
      ),
    );
  }
}
