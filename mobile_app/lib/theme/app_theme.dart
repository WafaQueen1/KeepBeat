import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // Theme Colors
  static const Color primary = Color(0xFFb6171e);
  static const Color primaryContainer = Color(0xFFda3433);
  static const Color onPrimary = Colors.white;

  static const Color surface = Color(0xFFf8f9fa);
  static const Color surfaceContainerLow = Color(0xFFf3f4f5); // Frosted Glass Overlay base
  static const Color surfaceContainerHighest = Color(0xFFe1e3e4);
  static const Color surfaceContainerLowest = Color(0xFFffffff); // Base layer of cards
  static const Color onSurface = Color(0xFF191c1d);
  
  static const Color surfaceTint = Color(0xFFba1a20); // Used for shadows

  static const Color secondaryContainer = Color(0xFF959efd);
  static const Color onSecondaryContainer = Color(0xFF27308a); // Mint Sage text override

  static const Color tertiary = Color(0xFF8a30b0); // Electric Purple
  static const Color tertiaryContainer = Color(0xFFa54dcc);
  static const Color tertiaryFixed = Color(0xFFf8d8ff);

  static const Color outlineVariant = Color(0xFFe4bebc); // Ghost Border

  // Claymorphism BoxDecorations
  static BoxDecoration clayBlockTheme = BoxDecoration(
    color: surfaceContainerLowest,
    borderRadius: BorderRadius.circular(24), // xl (1.5rem / 24px)
    boxShadow: [
      BoxShadow(
        color: surfaceTint.withOpacity(0.12),
        offset: const Offset(0, 20),
        blurRadius: 40,
        spreadRadius: 0,
      )
    ],
  );

  static BoxDecoration innerHeroBlockTheme = BoxDecoration(
    gradient: const LinearGradient(
      colors: [primary, primaryContainer],
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
    ),
    borderRadius: BorderRadius.circular(12),
  );

  // Typography
  static TextTheme get textTheme {
    return TextTheme(
      displayLarge: GoogleFonts.manrope(
        fontSize: 57,
        fontWeight: FontWeight.bold,
        color: onSurface,
        letterSpacing: -0.25,
      ),
      headlineMedium: GoogleFonts.manrope(
        fontSize: 28,
        fontWeight: FontWeight.w600,
        color: onSurface,
      ),
      titleMedium: GoogleFonts.plusJakartaSans(
        fontSize: 16,
        fontWeight: FontWeight.w500,
        color: onSurface,
        letterSpacing: 0.15,
      ),
      labelSmall: GoogleFonts.inter(
        fontSize: 11,
        fontWeight: FontWeight.w600,
        color: onSurface,
        letterSpacing: 0.5,
      ),
    );
  }

  static ThemeData get lightTheme {
    return ThemeData(
      scaffoldBackgroundColor: surface,
      useMaterial3: true,
      textTheme: textTheme,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primary,
        primary: primary,
        primaryContainer: primaryContainer,
        onPrimary: onPrimary,
        surface: surface,
        onSurface: onSurface,
        secondaryContainer: secondaryContainer,
        onSecondaryContainer: onSecondaryContainer,
        tertiary: tertiary,
        tertiaryContainer: tertiaryContainer,
        outlineVariant: outlineVariant,
      ),
    );
  }
}
