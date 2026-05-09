import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static const Color primary = Color(0xFFD61F26);
  static const Color primaryDark = Color(0xFFB91319);
  static const Color primarySoft = Color(0xFFFFE7E7);
  static const Color blush = Color(0xFFFFF2F3);
  static const Color blushStrong = Color(0xFFF5E8FF);
  static const Color surface = Color(0xFFFCFAFB);
  static const Color card = Colors.white;
  static const Color onSurface = Color(0xFF18171C);
  static const Color onSurfaceMuted = Color(0xFF8F7B79);
  static const Color line = Color(0xFFF0E3E2);
  static const Color lavender = Color(0xFFA244D9);
  static const Color lavenderSoft = Color(0xFFF4E9FF);
  static const Color blue = Color(0xFF4B60C4);
  static const Color blueSoft = Color(0xFFEAEFFF);
  static const Color redSoft = Color(0xFFFFECEB);
  static const Color greenSoft = Color(0xFFEAF8F1);
  static const Color shadow = Color(0x14000000);

  static const double outerRadius = 34;
  static const double innerRadius = 20;

  static TextTheme get textTheme => TextTheme(
        displayLarge: GoogleFonts.manrope(
          fontSize: 48,
          fontWeight: FontWeight.w800,
          color: onSurface,
          letterSpacing: -2.2,
        ),
        displayMedium: GoogleFonts.manrope(
          fontSize: 38,
          fontWeight: FontWeight.w800,
          color: onSurface,
          letterSpacing: -1.8,
        ),
        headlineMedium: GoogleFonts.manrope(
          fontSize: 24,
          fontWeight: FontWeight.w800,
          color: onSurface,
          letterSpacing: -0.8,
        ),
        titleLarge: GoogleFonts.manrope(
          fontSize: 20,
          fontWeight: FontWeight.w700,
          color: onSurface,
          letterSpacing: -0.4,
        ),
        titleMedium: GoogleFonts.manrope(
          fontSize: 17,
          fontWeight: FontWeight.w700,
          color: onSurface,
        ),
        bodyLarge: GoogleFonts.poppins(
          fontSize: 16,
          fontWeight: FontWeight.w400,
          color: onSurface,
          height: 1.45,
        ),
        bodyMedium: GoogleFonts.poppins(
          fontSize: 14,
          fontWeight: FontWeight.w400,
          color: onSurfaceMuted,
          height: 1.55,
        ),
        labelLarge: GoogleFonts.poppins(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: onSurface,
        ),
        labelSmall: GoogleFonts.poppins(
          fontSize: 11,
          fontWeight: FontWeight.w600,
          color: onSurfaceMuted,
          letterSpacing: 1.5,
        ),
      );

  static LinearGradient get pageGradient => const LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          Color(0xFFFFF5F5),
          Color(0xFFFFFBFB),
          Color(0xFFFDFBFB),
        ],
      );

  static LinearGradient get heroGradient => const LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [
          Color(0xFFFDD8D6),
          Color(0xFFF1B7C6),
          Color(0xFFE64D52),
        ],
      );

  static LinearGradient get primaryGradient => const LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          Color(0xFFE13035),
          Color(0xFFD61F26),
        ],
      );

  static BoxDecoration get bentoDecoration => BoxDecoration(
        color: card,
        borderRadius: BorderRadius.circular(outerRadius),
        border: Border.all(color: const Color(0xFFF4ECEC)),
        boxShadow: const [
          BoxShadow(
            color: shadow,
            blurRadius: 28,
            offset: Offset(0, 12),
          ),
        ],
      );

  static BoxDecoration get primaryCardDecoration => BoxDecoration(
        gradient: primaryGradient,
        borderRadius: BorderRadius.circular(outerRadius),
        boxShadow: [
          BoxShadow(
            color: primary.withOpacity(0.22),
            blurRadius: 30,
            offset: const Offset(0, 14),
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
        ),
        textTheme: textTheme,
      );
}
