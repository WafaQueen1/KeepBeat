import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // --- Stitch 'Vital Pulse' Palette ---
  static const Color primary = Color(0xFFB6171E); // Signature Deep Red
  static const Color primaryContainer = Color(0xFFDA3433); // High-volume Red
  static const Color primaryFixed = Color(0xFFFFDAD6); // Soft Glow Red
  
  static const Color secondary = Color(0xFF4C56AF); // Medical Indigo
  static const Color secondaryContainer = Color(0xFF959EFD); // Active Pulse Blue
  
  static const Color tertiary = Color(0xFF8A30B0); // AI / Electric Purple
  static const Color tertiaryContainer = Color(0xFFA54DCC); // AI Insight Highlight
  
  static const Color surface = Color(0xFFF8F9FA); // Base Canvas
  static const Color surfaceContainerLowest = Color(0xFFFFFFFF); // High-lift Card
  static const Color surfaceContainerLow = Color(0xFFF3F4F5); // Low-lift Segment
  static const Color surfaceContainerHigh = Color(0xFFE7E8E9); // Inset Well
  
  static const Color onSurface = Color(0xFF191C1D); // Primary Text
  static const Color onSurfaceMuted = Color(0xFF5B403F); // Secondary Text
  static const Color outlineVariant = Color(0xFFE4BEBC); // Ghost Border Base (15% opacity)

  // --- Heritage Compatibility & Accent Mapping ---
  static const Color accentBlue = secondaryContainer;
  static const Color accentPurple = tertiary;
  static const Color accentGreen = Color(0xFF34A853); // Positive / Mint Sage
  static const Color accentOrange = Color(0xFFFF9900); // Alert / Glucose

  static const Color background = surface;
  
  static Gradient get primaryGradient => const LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [primary, primaryContainer],
      );

  static BoxDecoration get primaryCardDecoration => BoxDecoration(
        gradient: primaryGradient,
        borderRadius: BorderRadius.circular(outerRadius),
        boxShadow: clayShadow,
      );

  static BoxDecoration get bentoBorderedDecoration => BoxDecoration(
        border: Border.all(color: outlineVariant.withOpacity(0.15)),
        borderRadius: BorderRadius.circular(innerRadius),
      );

  static const Color cardBorder = Color(0xFFE4BEBC); // outlineVariant base

  // --- Design System Tokens ---
  static const double outerRadius = 24.0; // xl radius
  static const double innerRadius = 12.0; // md radius

  // --- 3.5D Claymorphism Shadow Factory ---
  static List<BoxShadow> get clayShadow => [
        BoxShadow(
          color: primary.withOpacity(0.12),
          blurRadius: 40,
          offset: const Offset(0, 20),
        ),
      ];

  // --- Glassmorphism / Frosted Glass System ---
  static BoxDecoration glassDecoration({double opacity = 0.6}) => BoxDecoration(
        color: surfaceContainerLow.withOpacity(opacity),
        borderRadius: BorderRadius.circular(outerRadius),
      );

  // --- Bento Modular Grid Decoration ---
  static BoxDecoration get bentoDecoration => BoxDecoration(
        color: surfaceContainerLowest,
        borderRadius: BorderRadius.circular(outerRadius),
        boxShadow: [
          BoxShadow(
            color: onSurface.withOpacity(0.04),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      );

  // --- Typography: Medical Authority (Tri-Font System) ---
  static TextTheme get textTheme => TextTheme(
        // High-end, geometric, and authoritative
        displayLarge: GoogleFonts.manrope(
          fontSize: 54,
          fontWeight: FontWeight.w900,
          color: onSurface,
          letterSpacing: -2.0,
        ),
        displayMedium: GoogleFonts.manrope(
          fontSize: 42,
          fontWeight: FontWeight.w800,
          color: onSurface,
          letterSpacing: -1.5,
        ),
        headlineMedium: GoogleFonts.manrope(
          fontSize: 24,
          fontWeight: FontWeight.w800,
          color: onSurface,
          letterSpacing: -0.5,
        ),
        // Modern and approachable titles
        titleLarge: GoogleFonts.plusJakartaSans(
          fontSize: 20,
          fontWeight: FontWeight.w700,
          color: onSurface,
        ),
        titleMedium: GoogleFonts.plusJakartaSans(
          fontSize: 17,
          fontWeight: FontWeight.w600,
          color: onSurface,
        ),
        // Maximum legibility utility
        bodyLarge: GoogleFonts.inter(
          fontSize: 16,
          fontWeight: FontWeight.w400,
          color: onSurface,
          height: 1.5,
        ),
        bodyMedium: GoogleFonts.inter(
          fontSize: 14,
          fontWeight: FontWeight.w400,
          color: onSurfaceMuted,
          height: 1.6,
        ),
        labelLarge: GoogleFonts.inter(
          fontSize: 13,
          fontWeight: FontWeight.w700,
          color: onSurface,
          letterSpacing: 0.5,
        ),
        labelSmall: GoogleFonts.inter(
          fontSize: 11,
          fontWeight: FontWeight.w700,
          color: tertiary, // Defaulting labels for AI insights as per spec
          letterSpacing: 1.4,
        ),
      );

  static ThemeData get lightTheme => ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: surface,
        colorScheme: ColorScheme.fromSeed(
          seedColor: primary,
          primary: primary,
          secondary: secondary,
          tertiary: tertiary,
          surface: surface,
        ),
        textTheme: textTheme,
        // Global focus glow for StitchInput
        focusColor: primaryFixed.withOpacity(0.5),
      );
}
