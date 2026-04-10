import 'dart:ui';
import 'package:flutter/material.dart';
import '../../theme/app_theme.dart';

// ─────────────────────────────────────────────────────────────
//  BENTO TILE — Precision card wrapper (No-Line Rule)
// ─────────────────────────────────────────────────────────────
class BentoTile extends StatelessWidget {
  final String title;
  final Widget child;
  final EdgeInsetsGeometry padding;
  final Color? backgroundColor;

  const BentoTile({
    super.key,
    required this.title,
    required this.child,
    this.padding = const EdgeInsets.all(32.0), // Generous medical spacing
    this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: padding,
      decoration: BoxDecoration(
        color: backgroundColor ?? AppTheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppTheme.outerRadius),
        boxShadow: [
          // Multi-layer soft atmospheric shadows
          BoxShadow(
            color: Colors.black.withOpacity(0.02),
            blurRadius: 30,
            offset: const Offset(0, 15),
          ),
          BoxShadow(
            color: AppTheme.primary.withOpacity(0.015),
            blurRadius: 60,
            offset: const Offset(0, 25),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            title.toUpperCase(),
            style: AppTheme.textTheme.labelSmall?.copyWith(
              letterSpacing: 2.5,
              fontSize: 10,
              fontWeight: FontWeight.w900,
              color: AppTheme.onSurfaceMuted.withOpacity(0.3),
            ),
          ),
          const SizedBox(height: 20),
          child,
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────
//  STITCH BUTTON — 3.5D Hyper-Tactile Unit
// ─────────────────────────────────────────────────────────────
class StitchButton extends StatefulWidget {
  final VoidCallback onTap;
  final String text;
  final Color? backgroundColor;
  final Color textColor;
  final IconData? icon;

  const StitchButton({
    super.key,
    required this.onTap,
    required this.text,
    this.backgroundColor,
    this.textColor = Colors.white,
    this.icon,
  });

  @override
  State<StitchButton> createState() => _StitchButtonState();
}

class _StitchButtonState extends State<StitchButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scale;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 80), // Shorter, crisper feedback
    );
    _scale = Tween<double>(begin: 1.0, end: 0.935).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutCirc),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final baseColor = widget.backgroundColor ?? AppTheme.primary;
    return GestureDetector(
      onTapDown: (_) => _controller.forward(),
      onTapUp: (_) => _controller.reverse(),
      onTapCancel: () => _controller.reverse(),
      onTap: widget.onTap,
      child: ScaleTransition(
        scale: _scale,
        child: Container(
          height: 64,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                baseColor,
                baseColor.withAlpha(210), 
              ],
            ),
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              // Living drop shadow
              BoxShadow(
                color: baseColor.withOpacity(0.32),
                blurRadius: 28,
                offset: const Offset(0, 14),
              ),
              // Prominent top-left specular highlight
              BoxShadow(
                color: Colors.white.withOpacity(0.35),
                blurRadius: 8,
                offset: const Offset(-4, -4),
                spreadRadius: -2,
              ),
            ],
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (widget.icon != null) ...[
                Icon(widget.icon, color: widget.textColor, size: 20),
                const SizedBox(width: 12),
              ],
              Text(
                widget.text.toUpperCase(),
                style: AppTheme.textTheme.labelLarge?.copyWith(
                  color: widget.textColor,
                  fontSize: 14,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 2.2,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────
//  INSET WELL PAINTER — For recursive depth look
// ─────────────────────────────────────────────────────────────
class _InsetWellPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final rect = Rect.fromLTWH(0, 0, size.width, size.height);
    final rrect = RRect.fromRectAndRadius(rect, const Radius.circular(12));

    // 1. Base Fill
    canvas.drawRRect(rrect, Paint()..color = const Color(0xFFF1F2F4));

    // 2. Inner Dark Shadow (Top Left)
    final darkShadowPaint = Paint()
      ..color = Colors.black.withOpacity(0.08)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 6);
    
    canvas.save();
    canvas.clipRRect(rrect);
    canvas.translate(2, 2);
    canvas.drawRRect(rrect, darkShadowPaint);
    canvas.restore();

    // 3. Inner White Highlight (Bottom Right)
    final lightShadowPaint = Paint()
      ..color = Colors.white.withOpacity(0.9)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 4);
    
    canvas.save();
    canvas.clipRRect(rrect);
    canvas.translate(-2, -2);
    canvas.drawRRect(rrect, lightShadowPaint);
    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

// ─────────────────────────────────────────────────────────────
//  STITCH INPUT — Hyper-Refined Inset Well
// ─────────────────────────────────────────────────────────────
class StitchInput extends StatelessWidget {
  final String hintText;
  final IconData? prefixIcon;
  final bool isPassword;
  final TextEditingController? controller;

  const StitchInput({
    super.key,
    required this.hintText,
    this.prefixIcon,
    this.isPassword = false,
    this.controller,
  });

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: _InsetWellPainter(),
      child: Container(
        height: 64,
        padding: const EdgeInsets.symmetric(horizontal: 4),
        child: Center(
          child: TextField(
            controller: controller,
            obscureText: isPassword,
            cursorColor: AppTheme.primary,
            style: AppTheme.textTheme.bodyLarge?.copyWith(
              fontWeight: FontWeight.w700,
              color: AppTheme.onSurface,
              fontSize: 16,
            ),
            decoration: InputDecoration(
              hintText: hintText,
              hintStyle: AppTheme.textTheme.bodyMedium?.copyWith(
                color: AppTheme.onSurfaceMuted.withOpacity(0.3),
                fontWeight: FontWeight.w600,
              ),
              prefixIcon: prefixIcon != null
                  ? Icon(prefixIcon, color: AppTheme.onSurfaceMuted.withOpacity(0.5), size: 20)
                  : null,
              border: InputBorder.none,
              contentPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 18),
            ),
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────
//  VOLUMETRIC HEART PAINTER (Advanced Claymorphism)
// ─────────────────────────────────────────────────────────────
class _VolumetricHeartPainter extends CustomPainter {
  final double pulse; // 0.0 -> 1.0 animation progress

  _VolumetricHeartPainter({required this.pulse});

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;
    final path = _heartPath(w, h);

    // 1. Atmosphere Glow (Softer, broader outer glow)
    final glowPaint = Paint()
      ..color = AppTheme.primary.withOpacity(0.12 + (pulse * 0.05))
      ..maskFilter = MaskFilter.blur(BlurStyle.normal, 32 + (pulse * 10));
    canvas.drawPath(path, glowPaint);

    // 2. Primary 3D Body (Sophisticated Multi-Gradient)
    final bodyPaint = Paint()
      ..shader = RadialGradient(
        center: const Alignment(-0.25, -0.35),
        radius: 1.1,
        colors: [
          Color.lerp(const Color(0xFFFF5E7E), const Color(0xFFFF7E9E), pulse)!, // Interactive light source
          const Color(0xFFB6171E), // Signature Red
          const Color(0xFF4A0003), // Deep shadow base
        ],
        stops: const [0.0, 0.65, 1.0],
      ).createShader(Rect.fromLTWH(0, 0, w, h));
    canvas.drawPath(path, bodyPaint);

    // 3. Specular Highlight (The 'Wet' Gloss link)
    final specularPaint = Paint()
      ..color = Colors.white.withOpacity(0.38 + (pulse * 0.12))
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 12);
    canvas.drawOval(
      Rect.fromCenter(
        center: Offset(w * 0.32, h * 0.28),
        width: w * 0.28,
        height: h * 0.16,
      ),
      specularPaint,
    );

    // 4. Inner Depth Rim (Bottom Shadow)
    final rimPaint = Paint()
      ..color = Colors.black.withOpacity(0.18)
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 14);
    canvas.drawOval(
      Rect.fromCenter(
        center: Offset(w * 0.65, h * 0.72),
        width: w * 0.32,
        height: h * 0.20,
      ),
      rimPaint,
    );
  }

  Path _heartPath(double w, double h) {
    final p = Path();
    p.moveTo(w * 0.5, h * 0.90);
    p.cubicTo(w * 0.12, h * 0.68, w * -0.18, h * 0.35, w * 0.2, h * 0.14);
    p.cubicTo(w * 0.4, h * -0.02, w * 0.5, h * 0.2, w * 0.5, h * 0.2);
    p.cubicTo(w * 0.5, h * 0.2, w * 0.6, h * -0.02, w * 0.8, h * 0.14);
    p.cubicTo(w * 1.18, h * 0.35, w * 0.88, h * 0.68, w * 0.5, h * 0.90);
    p.close();
    return p;
  }

  @override
  bool shouldRepaint(_VolumetricHeartPainter old) => old.pulse != pulse;
}

// ─────────────────────────────────────────────────────────────
//  STITCH HEART — Hyper-Realistic Organic Unit
// ─────────────────────────────────────────────────────────────
class StitchHeart extends StatefulWidget {
  final int bpm;
  final double size;
  final bool showBpm;

  const StitchHeart({
    super.key, 
    required this.bpm, 
    this.size = 140,
    this.showBpm = true,
  });

  @override
  State<StitchHeart> createState() => _StitchHeartState();
}

class _StitchHeartState extends State<StitchHeart>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _pulseAnim;
  late Animation<double> _scaleAnim;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2), // Slower, more natural base
    )..repeat();

    _pulseAnim = CurvedAnimation(parent: _controller, curve: Curves.easeInOut);

    // Subtle natural scale animation (Lub-Dub feel)
    _scaleAnim = TweenSequence<double>([
      TweenSequenceItem(tween: Tween(begin: 1.0, end: 1.08).chain(CurveTween(curve: Curves.easeOutCubic)), weight: 20),
      TweenSequenceItem(tween: Tween(begin: 1.08, end: 1.02).chain(CurveTween(curve: Curves.easeInCubic)), weight: 15),
      TweenSequenceItem(tween: Tween(begin: 1.02, end: 1.05).chain(CurveTween(curve: Curves.easeOutCubic)), weight: 15),
      TweenSequenceItem(tween: Tween(begin: 1.05, end: 1.0).chain(CurveTween(curve: Curves.easeInOutCubic)), weight: 50),
    ]).animate(_controller);
  }

  @override
  void didUpdateWidget(StitchHeart old) {
    if (old.bpm != widget.bpm) {
      _controller.duration = Duration(milliseconds: (60000 / widget.bpm.clamp(40, 180)).round() * 2); 
    }
    super.didUpdateWidget(old);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, _) {
        return Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Transform.scale(
              scale: _scaleAnim.value,
              child: CustomPaint(
                size: Size(widget.size, widget.size * 0.9),
                painter: _VolumetricHeartPainter(pulse: _pulseAnim.value),
              ),
            ),
            if (widget.showBpm) ...[
              const SizedBox(height: 20),
              Text(
                widget.bpm.toString(),
                style: AppTheme.textTheme.displayLarge?.copyWith(
                  fontSize: 58,
                  fontWeight: FontWeight.w900,
                  letterSpacing: -3.0,
                ),
              ),
              Text(
                'VITAL BPM',
                style: AppTheme.textTheme.labelSmall?.copyWith(
                  color: AppTheme.onSurfaceMuted.withOpacity(0.35),
                  letterSpacing: 4.0,
                  fontSize: 10,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ],
          ],
        );
      },
    );
  }
}

// ─────────────────────────────────────────────────────────────
//  SOCIAL AUTH TILE — Stitch Medical Style
// ─────────────────────────────────────────────────────────────
class SocialAuthTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const SocialAuthTile({
    super.key,
    required this.icon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 64,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 20, color: AppTheme.onSurface),
            const SizedBox(width: 14),
            Text(
              label.toUpperCase(),
              style: AppTheme.textTheme.labelSmall?.copyWith(
                color: AppTheme.onSurface,
                fontSize: 12,
                letterSpacing: 1.5,
                fontWeight: FontWeight.w900,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────
//  STATUS BADGE — High-contrast clinical indicator
// ─────────────────────────────────────────────────────────────
class StatusBadge extends StatelessWidget {
  final String label;
  final Color color;
  final bool inverted;

  const StatusBadge({
    super.key,
    required this.label,
    required this.color,
    this.inverted = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: inverted ? Colors.white : color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: inverted ? Colors.white24 : color.withOpacity(0.2),
          width: 1,
        ),
      ),
      child: Text(
        label.toUpperCase(),
        style: AppTheme.textTheme.labelSmall?.copyWith(
          color: inverted ? color : color,
          fontSize: 10,
          fontWeight: FontWeight.w900,
          letterSpacing: 1.2,
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────
//  ECG PAINTER — Real-time cardiac rhythm strip
// ─────────────────────────────────────────────────────────────
class EcgPainter extends CustomPainter {
  final double progress;
  final Color color;

  EcgPainter({required this.progress, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color.withOpacity(0.6)
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final path = Path();
    final step = size.width / 100;
    
    path.moveTo(0, size.height / 2);

    for (var i = 0; i < 100; i++) {
      final x = i * step;
      // Synthetic ECG logic with peaks
      double y = size.height / 2;
      
      final normX = (i / 100 + progress) % 1.0;
      
      if (normX > 0.4 && normX < 0.45) {
        // P-Wave
        y -= 4;
      } else if (normX >= 0.45 && normX < 0.47) {
        // Q-Dip
        y += 4;
      } else if (normX >= 0.47 && normX < 0.50) {
        // R-Peak
        y -= 18;
      } else if (normX >= 0.50 && normX < 0.53) {
        // S-Dip
        y += 8;
      } else if (normX > 0.6 && normX < 0.7) {
        // T-Wave
        y -= 6;
      }

      path.lineTo(x, y);
    }

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant EcgPainter oldDelegate) => true;
}
