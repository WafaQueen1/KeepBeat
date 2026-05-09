import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static const Color primary = Color(0xFFB6171E);
  static const Color primaryBright = Color(0xFFDA3433);
  static const Color primaryFixed = Color(0xFFFFDAD6);
  static const Color primarySoft = Color(0xFFFFECEB);
  static const Color blush = Color(0xFFFFF6F6);
  static const Color blushStrong = Color(0xFFFFEEF1);
  static const Color surface = Color(0xFFF8F9FA);
  static const Color background = surface;
  static const Color card = Colors.white;
  static const Color onSurface = Color(0xFF191C1D);
  static const Color onSurfaceMuted = Color(0xFF8F6F6E);
  static const Color line = Color(0xFFEFE3E2);
  static const Color lineSoft = Color(0xFFF5ECEB);
  static const Color lavender = Color(0xFF8A30B0);
  static const Color lavenderBright = Color(0xFFA54DCC);
  static const Color lavenderSoft = Color(0xFFF8E8FF);
  static const Color blue = Color(0xFF4C56AF);
  static const Color blueSoft = Color(0xFFE7EBFF);
  static const Color mint = Color(0xFFE0E0FF);
  static const Color redSoft = Color(0xFFFFE9E7);
  static const Color shadow = Color(0x14000000);
  static const Color shadowTint = Color(0x1FB6171E);

  static const double outerRadius = 32;
  static const double innerRadius = 20;

  static TextTheme get textTheme => TextTheme(
        displayLarge: GoogleFonts.manrope(
          fontSize: 50,
          fontWeight: FontWeight.w800,
          height: 1,
          letterSpacing: -2.4,
          color: onSurface,
        ),
        displayMedium: GoogleFonts.manrope(
          fontSize: 38,
          fontWeight: FontWeight.w800,
          height: 1.04,
          letterSpacing: -1.8,
          color: onSurface,
        ),
        headlineMedium: GoogleFonts.manrope(
          fontSize: 24,
          fontWeight: FontWeight.w800,
          height: 1.1,
          letterSpacing: -0.8,
          color: onSurface,
        ),
        titleLarge: GoogleFonts.plusJakartaSans(
          fontSize: 20,
          fontWeight: FontWeight.w700,
          height: 1.2,
          color: onSurface,
        ),
        titleMedium: GoogleFonts.plusJakartaSans(
          fontSize: 17,
          fontWeight: FontWeight.w700,
          height: 1.2,
          color: onSurface,
        ),
        bodyLarge: GoogleFonts.plusJakartaSans(
          fontSize: 16,
          fontWeight: FontWeight.w500,
          height: 1.5,
          color: onSurface,
        ),
        bodyMedium: GoogleFonts.plusJakartaSans(
          fontSize: 14,
          fontWeight: FontWeight.w500,
          height: 1.5,
          color: onSurfaceMuted,
        ),
        labelLarge: GoogleFonts.inter(
          fontSize: 14,
          fontWeight: FontWeight.w700,
          height: 1.2,
          color: onSurface,
        ),
        labelSmall: GoogleFonts.inter(
          fontSize: 11,
          fontWeight: FontWeight.w700,
          height: 1.2,
          letterSpacing: 1.4,
          color: onSurfaceMuted,
        ),
      );

  static const LinearGradient pageGradient = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          Color(0xFFFFFAFB),
          Color(0xFFFDF8F8),
          Color(0xFFF8F9FA),
        ],
      );

  static const LinearGradient heroGradient = LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [
          Color(0xFFFFDAD6),
          Color(0xFFF3BBC8),
          Color(0xFFDA3433),
        ],
      );

  static const LinearGradient primaryGradient = LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [
          primary,
          primaryBright,
        ],
      );

  static const LinearGradient emergencyGradient = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          Color(0xFF7A0D11),
          Color(0xFFB6171E),
          Color(0xFFDA3433),
        ],
      );

  static BoxDecoration get bentoDecoration => BoxDecoration(
        color: card,
        borderRadius: BorderRadius.circular(outerRadius),
        boxShadow: const [
          BoxShadow(
            color: shadow,
            blurRadius: 30,
            offset: Offset(0, 14),
          ),
          BoxShadow(
            color: shadowTint,
            blurRadius: 44,
            offset: Offset(0, 22),
            spreadRadius: -18,
          ),
        ],
      );

  static BoxDecoration get primaryCardDecoration => BoxDecoration(
        gradient: primaryGradient,
        borderRadius: BorderRadius.circular(outerRadius),
        boxShadow: [
          BoxShadow(
            color: primary.withOpacity(0.20),
            blurRadius: 34,
            offset: const Offset(0, 18),
          ),
        ],
      );

  static ThemeData get lightTheme => ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: surface,
        colorScheme: ColorScheme.fromSeed(
          seedColor: primary,
          primary: primary,
          secondary: blue,
          tertiary: lavender,
          surface: surface,
          brightness: Brightness.light,
        ),
        textTheme: textTheme,
      );
}
