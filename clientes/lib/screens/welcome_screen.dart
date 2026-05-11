// Pantalla de bienvenida mostrada al abrir la app por primera vez.
import 'package:flutter/material.dart';

import '../app_theme.dart';
import '../language_controller.dart';
import '../services/bongusto_api.dart';
import '../theme_controller.dart';

// Widget inicial que introduce la experiencia del cliente.
class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    final double imageHeight = size.height * 0.62; // alto de imagen

    return Scaffold(
      backgroundColor: AppThemeColors.bg,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  ValueListenableBuilder<bool>(
                    valueListenable: ThemeController.isDark,
                    builder: (context, isDark, _) {
                      return IconButton(
                        tooltip: isDark ? 'Modo claro' : 'Modo oscuro',
                        onPressed: ThemeController.toggle,
                        icon: Icon(
                          isDark
                              ? Icons.light_mode_rounded
                              : Icons.dark_mode_rounded,
                        ),
                      );
                    },
                  ),
                  const SizedBox(width: 8),
                  ValueListenableBuilder<String>(
                    valueListenable: LanguageController.language,
                    builder: (context, language, _) {
                      return OutlinedButton(
                        onPressed: () async {
                          final next = await LanguageController.toggle();
                          try {
                            await BongustoApi.cambiarIdioma(next);
                          } catch (_) {}
                        },
                        child: Text(language == 'en' ? 'ES' : 'EN'),
                      );
                    },
                  ),
                ],
              ),
              const SizedBox(height: 8),
              // Tarjeta
              Container(
                decoration: AppThemeColors.card(radius: 16, shadow: true),
                child: Column(
                  children: [
                    // Imagen
                    ClipRRect(
                      borderRadius: const BorderRadius.only(
                        topLeft: Radius.circular(16),
                        topRight: Radius.circular(16),
                      ),
                      child: Stack(
                        children: [
                          SizedBox(
                            height: imageHeight,
                            width: double.infinity,
                            child: Image.asset(
                              'assets/cocktail.png',
                              fit: BoxFit.cover,
                              alignment: Alignment.topCenter,
                            ),
                          ),
                          // Degradado
                          Positioned.fill(
                            child: DecoratedBox(
                              decoration: BoxDecoration(
                                gradient: LinearGradient(
                                  begin: Alignment.topCenter,
                                  end: Alignment.bottomCenter,
                                  colors: [
                                    Colors.transparent,
                                    AppThemeColors.surface.withValues(
                                      alpha: 0.98,
                                    ),
                                  ],
                                  stops: const [0.68, 1.0],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),

                    // Contenido inferior
                    Padding(
                      padding: const EdgeInsets.fromLTRB(20, 20, 20, 22),
                      child: Column(
                        children: [
                          Text(
                            'BonGusto',
                            style: TextStyle(
                              color: AppThemeColors.text,
                              fontSize: 22,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          const SizedBox(height: 12),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                LanguageController.tr('No tengo una cuenta, '),
                                style: TextStyle(color: AppThemeColors.muted),
                              ),
                              GestureDetector(
                                onTap: () =>
                                    Navigator.pushNamed(context, '/register'),
                                child: Text(
                                  LanguageController.tr('Regístrate'),
                                  style: const TextStyle(color: Colors.red),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 22),
                          // Botón grande
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton(
                              style: ElevatedButton.styleFrom(
                                shape: const StadiumBorder(),
                              ),
                              onPressed: () =>
                                  Navigator.pushNamed(context, '/login'),
                              child: Text(
                                LanguageController.tr('Iniciar sesión'),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}
