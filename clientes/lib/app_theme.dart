import 'package:flutter/material.dart';

import 'theme_controller.dart';

class AppThemeColors {
  static bool get _dark => ThemeController.isDark.value;

  static Color get bg =>
      _dark ? const Color(0xFF101218) : const Color(0xFFF2F1F4);
  static Color get surface =>
      _dark ? const Color(0xFF1A1D27) : const Color(0xFFFFFFFF);
  static Color get surfaceAlt =>
      _dark ? const Color(0xFF232737) : const Color(0xFFF8F8FA);
  static Color get text =>
      _dark ? const Color(0xFFF4F5F9) : const Color(0xFF181818);
  static Color get muted =>
      _dark ? const Color(0xFFA7ADBD) : const Color(0xFF73727A);
  static Color get line =>
      _dark ? const Color(0xFF313544) : const Color(0xFFE8E6EB);
  static Color get accent => const Color(0xFFD90416);
  static Color get accentSoft =>
      _dark ? const Color(0xFF3A1D24) : const Color(0xFFFFECEE);
  static Color get successSoft =>
      _dark ? const Color(0xFF193623) : const Color(0xFFE8F3EA);
  static Color get success =>
      _dark ? const Color(0xFF6EDB8A) : const Color(0xFF2F6E39);
  static Color get shadow => _dark
      ? Colors.black.withValues(alpha: 0.26)
      : Colors.black.withValues(alpha: 0.06);

  static BoxDecoration card({double radius = 24, bool shadow = false}) {
    return BoxDecoration(
      color: surface,
      borderRadius: BorderRadius.circular(radius),
      border: Border.all(color: line),
      boxShadow: shadow
          ? [
              BoxShadow(
                color: AppThemeColors.shadow,
                blurRadius: 18,
                offset: const Offset(0, 8),
              ),
            ]
          : null,
    );
  }

  static TextStyle title(double size) {
    return TextStyle(
      color: text,
      fontSize: size,
      fontWeight: FontWeight.w900,
      height: 1.1,
    );
  }

  static TextStyle body({
    double size = 14,
    FontWeight weight = FontWeight.w600,
  }) {
    return TextStyle(
      color: muted,
      fontSize: size,
      height: 1.45,
      fontWeight: weight,
    );
  }
}
