import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ThemeController {
  static const _storage = FlutterSecureStorage();
  static const _key = 'bongusto_theme_dark';
  static final ValueNotifier<bool> isDark = ValueNotifier<bool>(false);

  static Future<void> init() async {
    final value = await _storage.read(key: _key);
    isDark.value = value == 'true';
  }

  static Future<void> toggle() async {
    final next = !isDark.value;
    isDark.value = next;
    await _storage.write(key: _key, value: next ? 'true' : 'false');
  }
}
