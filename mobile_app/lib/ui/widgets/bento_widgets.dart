import 'dart:ui';

import 'package:flutter/material.dart';

import '../../theme/app_theme.dart';

class StitchBackdrop extends StatelessWidget {
  final Widget child;

  const StitchBackdrop({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(gradient: AppTheme.pageGradient),
      child: Stack(
        children: [
          Positioned(
            top: -90,
            left: -40,
            child: _GlowBlob(
              size: 240,
              color: AppTheme.primary.withOpacity(0.08),
            ),
          ),
          Positioned(
            right: -60,
            top: 180,
            child: _GlowBlob(
              size: 220,
              color: AppTheme.lavender.withOpacity(0.06),
            ),
          ),
          Positioned(
            left: -70,
            bottom: -40,
            child: _GlowBlob(
              size: 260,
              color: AppTheme.primaryFixed.withOpacity(0.40),
            ),
          ),
          child,
        ],
      ),
    );
  }
}

class _GlowBlob extends StatelessWidget {
  final double size;
  final Color color;

  const _GlowBlob({required this.size, required this.color});

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: color,
          boxShadow: [
            BoxShadow(
              color: color,
              blurRadius: size * 0.45,
              spreadRadius: size * 0.05,
            ),
          ],
        ),
      ),
    );
  }
}

class GlassPill extends StatelessWidget {
  final Widget child;
  final EdgeInsets padding;
  final Color? tint;

  const GlassPill({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
    this.tint,
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(999),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
        child: Container(
          padding: padding,
          decoration: BoxDecoration(
            color: (tint ?? Colors.white).withOpacity(0.78),
            borderRadius: BorderRadius.circular(999),
            border: Border.all(
              color: Colors.white.withOpacity(0.65),
            ),
            boxShadow: [
              BoxShadow(
                color: AppTheme.onSurface.withOpacity(0.06),
                blurRadius: 22,
                offset: const Offset(0, 10),
              ),
            ],
          ),
          child: child,
        ),
      ),
    );
  }
}

class BentoTile extends StatelessWidget {
  final String? title;
  final Widget child;
  final EdgeInsetsGeometry padding;
  final Color? backgroundColor;

  const BentoTile({
    super.key,
    this.title,
    required this.child,
    this.padding = const EdgeInsets.all(26),
    this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: padding,
      decoration: BoxDecoration(
        color: backgroundColor ?? Colors.white,
        borderRadius: BorderRadius.circular(AppTheme.outerRadius),
        boxShadow: const [
          BoxShadow(
            color: AppTheme.shadow,
            blurRadius: 28,
            offset: Offset(0, 12),
          ),
          BoxShadow(
            color: AppTheme.shadowTint,
            blurRadius: 42,
            offset: Offset(0, 22),
            spreadRadius: -20,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (title != null && title!.isNotEmpty) ...[
            Text(
              title!.toUpperCase(),
              style: AppTheme.textTheme.labelSmall?.copyWith(
                color: AppTheme.onSurfaceMuted.withOpacity(0.72),
                letterSpacing: 2.2,
              ),
            ),
            const SizedBox(height: 18),
          ],
          child,
        ],
      ),
    );
  }
}

class VitalBentoCard extends StatelessWidget {
  final String label;
  final String value;
  final String unit;
  final IconData icon;
  final Color accent;
  final Widget? trailing;
  final String? status;
  final bool showBar;

  const VitalBentoCard({
    super.key,
    required this.label,
    required this.value,
    required this.unit,
    required this.icon,
    required this.accent,
    this.trailing,
    this.status,
    this.showBar = false,
  });

  @override
  Widget build(BuildContext context) {
    return BentoTile(
      padding: const EdgeInsets.all(22),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: accent.withOpacity(0.14),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Icon(icon, color: accent, size: 22),
              ),
              const Spacer(),
              if (trailing != null)
                trailing!
              else if (status != null)
                GlassPill(
                  tint: accent.withOpacity(0.12),
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 7,
                  ),
                  child: Text(
                    status!,
                    style: AppTheme.textTheme.labelSmall?.copyWith(
                      color: accent,
                      fontSize: 10,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 20),
          Text(
            label.toUpperCase(),
            style: AppTheme.textTheme.labelSmall?.copyWith(
              color: accent == AppTheme.lavender
                  ? AppTheme.lavender
                  : AppTheme.onSurfaceMuted.withOpacity(0.86),
            ),
          ),
          const SizedBox(height: 10),
          RichText(
            text: TextSpan(
              children: [
                TextSpan(
                  text: value,
                  style: AppTheme.textTheme.displayMedium?.copyWith(
                    fontSize: 42,
                    letterSpacing: -2,
                  ),
                ),
                TextSpan(
                  text: ' $unit',
                  style: AppTheme.textTheme.titleMedium?.copyWith(
                    color: AppTheme.onSurfaceMuted.withOpacity(0.75),
                  ),
                ),
              ],
            ),
          ),
          if (showBar) ...[
            const SizedBox(height: 16),
            ClipRRect(
              borderRadius: BorderRadius.circular(999),
              child: LinearProgressIndicator(
                minHeight: 6,
                value: 0.68,
                backgroundColor: accent.withOpacity(0.12),
                valueColor: AlwaysStoppedAnimation<Color>(
                  accent.withOpacity(0.75),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class StitchButton extends StatefulWidget {
  final VoidCallback onTap;
  final String text;
  final Color? backgroundColor;
  final Color textColor;
  final IconData? icon;
  final bool iconTrailing;
  final double height;

  const StitchButton({
    super.key,
    required this.onTap,
    required this.text,
    this.backgroundColor,
    this.textColor = Colors.white,
    this.icon,
    this.iconTrailing = true,
    this.height = 64,
    this.border,
  });

  final BoxBorder? border;

  @override
  State<StitchButton> createState() => _StitchButtonState();
}

class _StitchButtonState extends State<StitchButton>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<double> _scale;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 90),
    );
    _scale = Tween<double>(begin: 1, end: 0.97).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic),
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
      onTapCancel: _controller.reverse,
      onTapUp: (_) => _controller.reverse(),
      onTap: widget.onTap,
      child: ScaleTransition(
        scale: _scale,
        child: Container(
          height: widget.height,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Color.lerp(baseColor, Colors.white, 0.15)!,
                baseColor,
                Color.lerp(baseColor, Colors.black, 0.05)!,
              ],
            ),
            borderRadius: BorderRadius.circular(22),
            boxShadow: [
              BoxShadow(
                color: baseColor.withOpacity(0.32),
                blurRadius: 28,
                offset: const Offset(0, 16),
                spreadRadius: -4,
              ),
              BoxShadow(
                color: Colors.white.withOpacity(0.12),
                blurRadius: 0,
                offset: const Offset(0, 2),
                spreadRadius: 0,
              ),
            ],
          ),
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(22),
              border: widget.border ?? Border.all(
                color: Colors.white.withOpacity(0.18),
                width: 1.5,
              ),
            ),
            child: Center(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (widget.icon != null && !widget.iconTrailing) ...[
                    Icon(widget.icon, size: 20, color: widget.textColor),
                    const SizedBox(width: 10),
                  ],
                  Text(
                    widget.text,
                    style: AppTheme.textTheme.titleLarge?.copyWith(
                      color: widget.textColor,
                      fontWeight: FontWeight.w800,
                      letterSpacing: -0.4,
                    ),
                  ),
                  if (widget.icon != null && widget.iconTrailing) ...[
                    const SizedBox(width: 10),
                    Icon(widget.icon, size: 20, color: widget.textColor),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class StitchInput extends StatefulWidget {
  final String hintText;
  final IconData? prefixIcon;
  final bool isPassword;
  final TextEditingController? controller;
  final TextInputType? keyboardType;

  const StitchInput({
    super.key,
    required this.hintText,
    this.prefixIcon,
    this.isPassword = false,
    this.controller,
    this.keyboardType,
  });

  @override
  State<StitchInput> createState() => _StitchInputState();
}

class _StitchInputState extends State<StitchInput> {
  late bool _obscureText;

  @override
  void initState() {
    super.initState();
    _obscureText = widget.isPassword;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 64,
      decoration: BoxDecoration(
        color: const Color(0xFFF1F3F5),
        borderRadius: BorderRadius.circular(22),
        boxShadow: [
          BoxShadow(
            color: Colors.white.withOpacity(0.95),
            blurRadius: 0,
            spreadRadius: 1,
            offset: const Offset(-1, -1),
          ),
          BoxShadow(
            color: AppTheme.primary.withOpacity(0.04),
            blurRadius: 16,
            offset: const Offset(6, 8),
            spreadRadius: -10,
          ),
        ],
      ),
      child: TextField(
        controller: widget.controller,
        obscureText: _obscureText,
        keyboardType: widget.keyboardType,
        style: AppTheme.textTheme.bodyLarge?.copyWith(
          color: AppTheme.onSurface,
          fontWeight: FontWeight.w600,
        ),
        decoration: InputDecoration(
          hintText: widget.hintText,
          hintStyle: AppTheme.textTheme.bodyLarge?.copyWith(
            color: AppTheme.onSurfaceMuted.withOpacity(0.45),
            fontWeight: FontWeight.w500,
          ),
          prefixIcon: widget.prefixIcon != null
              ? Icon(
                  widget.prefixIcon,
                  color: AppTheme.onSurfaceMuted.withOpacity(0.72),
                  size: 20,
                )
              : null,
          suffixIcon: widget.isPassword
              ? IconButton(
                  onPressed: () {
                    setState(() => _obscureText = !_obscureText);
                  },
                  icon: Icon(
                    _obscureText
                        ? Icons.visibility_off_rounded
                        : Icons.visibility_rounded,
                    color: AppTheme.onSurfaceMuted.withOpacity(0.64),
                  ),
                )
              : null,
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 22,
            vertical: 20,
          ),
        ),
      ),
    );
  }
}

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
        height: 78,
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.96),
          borderRadius: BorderRadius.circular(24),
          boxShadow: const [
            BoxShadow(
              color: AppTheme.shadow,
              blurRadius: 20,
              offset: Offset(0, 10),
            ),
          ],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 34,
              height: 34,
              decoration: BoxDecoration(
                color: const Color(0xFFF5F5F7),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, size: 16, color: AppTheme.onSurface),
            ),
            const SizedBox(width: 12),
            Text(
              label,
              style: AppTheme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class StatusBadge extends StatelessWidget {
  final String label;
  final Color color;
  final bool inverted;
  final EdgeInsetsGeometry? padding;

  const StatusBadge({
    super.key,
    required this.label,
    required this.color,
    this.inverted = false,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: padding ??
          const EdgeInsets.symmetric(
            horizontal: 14,
            vertical: 7,
          ),
      decoration: BoxDecoration(
        color: inverted ? Colors.white : color.withOpacity(0.10),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label.toUpperCase(),
        style: AppTheme.textTheme.labelSmall?.copyWith(
          color: color,
          fontSize: 10,
          letterSpacing: 1.5,
        ),
      ),
    );
  }
}

class CircularStatusIndicator extends StatelessWidget {
  final double value;
  final Color color;
  final double size;

  const CircularStatusIndicator({
    super.key,
    required this.value,
    required this.color,
    this.size = 40,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        fit: StackFit.expand,
        children: [
          CircularProgressIndicator(
            value: 1,
            strokeWidth: 4,
            valueColor: AlwaysStoppedAnimation<Color>(color.withOpacity(0.12)),
          ),
          CircularProgressIndicator(
            value: value,
            strokeCap: StrokeCap.round,
            strokeWidth: 4,
            valueColor: AlwaysStoppedAnimation<Color>(color),
          ),
        ],
      ),
    );
  }
}

class AiInsightBanner extends StatelessWidget {
  final String title;
  final String description;
  final IconData icon;
  final VoidCallback onTap;

  const AiInsightBanner({
    super.key,
    required this.title,
    required this.description,
    required this.icon,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 18),
        decoration: BoxDecoration(
          color: AppTheme.lavenderSoft.withOpacity(0.72),
          borderRadius: BorderRadius.circular(28),
          boxShadow: const [
            BoxShadow(
              color: AppTheme.shadow,
              blurRadius: 20,
              offset: Offset(0, 10),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              width: 46,
              height: 46,
              decoration: BoxDecoration(
                color: AppTheme.lavender.withOpacity(0.12),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(icon, color: AppTheme.lavender, size: 22),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title.toUpperCase(),
                    style: AppTheme.textTheme.labelSmall?.copyWith(
                      color: AppTheme.lavender,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    description,
                    style: AppTheme.textTheme.bodyLarge?.copyWith(
                      fontSize: 13.5,
                      color: AppTheme.onSurface.withOpacity(0.82),
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.chevron_right_rounded,
              color: AppTheme.onSurfaceMuted.withOpacity(0.50),
              size: 24,
            ),
          ],
        ),
      ),
    );
  }
}

class AppLogoWordmark extends StatelessWidget {
  final String assetPath;
  final double logoSize;
  final double textSize;
  final bool redText;
  final FontStyle? fontStyle;

  const AppLogoWordmark({
    super.key,
    required this.assetPath,
    this.logoSize = 32,
    this.textSize = 20,
    this.redText = false,
    this.fontStyle,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Image.asset(
          assetPath,
          width: logoSize,
          height: logoSize,
          fit: BoxFit.contain,
        ),
        const SizedBox(width: 10),
        Text(
          'KeepBeat',
          style: AppTheme.textTheme.headlineMedium?.copyWith(
            fontSize: textSize,
            color: redText ? AppTheme.primary : AppTheme.onSurface,
            fontWeight: FontWeight.w800,
            fontStyle: fontStyle,
          ),
        ),
      ],
    );
  }
}

class GlassCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry padding;
  final double? minHeight;

  const GlassCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(24),
    this.minHeight,
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(28),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
        child: Container(
          width: double.infinity,
          constraints: BoxConstraints(minHeight: minHeight ?? 0),
          padding: padding,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.88),
            borderRadius: BorderRadius.circular(28),
            border: Border.all(color: Colors.white.withOpacity(0.70)),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.06),
                blurRadius: 26,
                offset: const Offset(0, 14),
              ),
              BoxShadow(
                color: AppTheme.primary.withOpacity(0.08),
                blurRadius: 48,
                offset: const Offset(0, 28),
                spreadRadius: -18,
              ),
            ],
          ),
          child: child,
        ),
      ),
    );
  }
}
