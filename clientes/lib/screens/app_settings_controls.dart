import 'package:flutter/material.dart';

import '../language_controller.dart';
import '../services/bongusto_api.dart';
import '../theme_controller.dart';

class AppSettingsControls extends StatelessWidget {
  const AppSettingsControls({super.key, this.compact = true});

  final bool compact;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final borderColor = theme.colorScheme.outline.withValues(alpha: 0.22);
    final background = theme.colorScheme.surface.withValues(alpha: 0.92);

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        ValueListenableBuilder<bool>(
          valueListenable: ThemeController.isDark,
          builder: (context, isDark, _) {
            return _RoundAction(
              tooltip: isDark ? 'Modo claro' : 'Modo oscuro',
              background: background,
              borderColor: borderColor,
              onPressed: ThemeController.toggle,
              child: Icon(
                isDark ? Icons.light_mode_rounded : Icons.dark_mode_rounded,
                size: compact ? 19 : 21,
              ),
            );
          },
        ),
        const SizedBox(width: 8),
        ValueListenableBuilder<String>(
          valueListenable: LanguageController.language,
          builder: (context, language, _) {
            return _RoundAction(
              tooltip: language == 'en'
                  ? 'Cambiar a espanol'
                  : 'Switch to English',
              background: background,
              borderColor: borderColor,
              onPressed: () async {
                final next = await LanguageController.toggle();
                try {
                  await BongustoApi.cambiarIdioma(next);
                } catch (_) {}
              },
              child: Text(
                language == 'en' ? 'ES' : 'EN',
                style: TextStyle(
                  fontSize: compact ? 12 : 13,
                  fontWeight: FontWeight.w900,
                ),
              ),
            );
          },
        ),
      ],
    );
  }
}

class _RoundAction extends StatelessWidget {
  const _RoundAction({
    required this.tooltip,
    required this.background,
    required this.borderColor,
    required this.onPressed,
    required this.child,
  });

  final String tooltip;
  final Color background;
  final Color borderColor;
  final VoidCallback onPressed;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: tooltip,
      child: Material(
        color: background,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
          side: BorderSide(color: borderColor),
        ),
        child: InkWell(
          borderRadius: BorderRadius.circular(8),
          onTap: onPressed,
          child: SizedBox(width: 38, height: 38, child: Center(child: child)),
        ),
      ),
    );
  }
}
