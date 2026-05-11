// ===== Archivo principal `main.dart` | Aqui se arranca la app de meseros, se define el tema global y se registran las rutas principales. =====
import 'dart:async';

import 'package:flutter/material.dart';

import 'screens/confirm_code_screen.dart';
import 'screens/forgot_password_screen.dart';
import 'screens/gestion_mesas_screen.dart';
import 'screens/home_screen.dart';
import 'screens/interaccion_screen.dart';
import 'screens/login_screen.dart';
import 'screens/menu_screen.dart';
import 'screens/musica_screen.dart';
import 'screens/notificaciones_admin_screen.dart';
import 'screens/pedidos_screen.dart';
import 'screens/perfil_screen.dart';
import 'screens/reset_password_screen.dart';
import 'screens/success_screen.dart';
import 'screens/welcome_screen.dart';
import 'services/bongusto_api.dart';
import 'services/session_service.dart';
import 'language_controller.dart';
import 'theme_controller.dart';

// Punto de entrada de la app operativa para meseros.
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    await SessionService.init();
    await ThemeController.init();
    await LanguageController.init();
  } catch (_) {}
  runApp(const BonGustoApp());
  if (SessionService.estaAutenticado) {
    unawaited(_refrescarSesionEnSegundoPlano());
  }
}

Future<void> _refrescarSesionEnSegundoPlano() async {
  try {
    final usuario = await BongustoApi.refrescarSesionActual();
    await SessionService.actualizarSesion(usuario);
  } catch (_) {}
}

// Paleta base compartida por la experiencia visual de meseros.
const kBrandRed = Color(0xFFD90416);
const kFieldFill = Color(0xFFF8F8FA);
const kPageBg = Color(0xFFF2F1F4);
const kTextColor = Color(0xFF181818);
const kMutedText = Color(0xFF73727A);
const kLineColor = Color(0xFFE8E6EB);
const kDarkBg = Color(0xFF101218);
const kDarkSurface = Color(0xFF1A1D27);
const kDarkField = Color(0xFF232737);
const kDarkText = Color(0xFFF4F5F9);
const kDarkMuted = Color(0xFFA7ADBD);
const kDarkLine = Color(0xFF313544);

// ===== Clase `BonGustoApp` | Representa la raiz del `MaterialApp` y la navegacion general del proyecto Flutter. =====
class BonGustoApp extends StatelessWidget {
  const BonGustoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<bool>(
      valueListenable: ThemeController.isDark,
      builder: (context, isDark, _) {
        return ValueListenableBuilder<String>(
          valueListenable: LanguageController.language,
          builder: (context, language, __) => MaterialApp(
            title: language == 'en' ? 'BonGusto Waiters' : 'BonGusto Meseros',
            debugShowCheckedModeBanner: false,
            themeMode: isDark ? ThemeMode.dark : ThemeMode.light,
            theme: _lightTheme(),
            darkTheme: _darkTheme(),
            builder: (context, child) => _ThemeToggleOverlay(child: child),
            // Mapa central de navegacion para el equipo de servicio.
            initialRoute: '/start',
            routes: {
              '/start': (_) => const WelcomeScreen(),
              '/login': (_) => const LoginScreen(),
              '/forgot': (_) => const ForgotPasswordScreen(),
              '/confirm': (_) => const ConfirmCodeScreen(),
              '/reset': (_) => const ResetPasswordScreen(),
              '/success': (_) => const SuccessScreen(),
              '/home': (_) => const HomeScreen(),
              '/notificaciones': (_) => const NotificacionesAdminScreen(),
              '/menu': (_) => const MenuScreen(),
              '/pedidos': (_) => const PedidosScreen(),
              '/mesas': (_) => const GestionMesasScreen(),
              '/interaccion': (_) => const InteraccionScreen(),
              '/musica': (_) => const MusicaScreen(),
              '/perfil': (_) => const PerfilScreen(),
            },
          ),
        );
      },
    );
  }

  ThemeData _lightTheme() {
    return ThemeData(
        useMaterial3: true,
        primaryColor: kBrandRed,
        scaffoldBackgroundColor: kPageBg,
        colorScheme: ColorScheme.fromSeed(
          seedColor: kBrandRed,
          primary: kBrandRed,
          surface: Colors.white,
        ),
        textTheme: ThemeData.light().textTheme.apply(
          bodyColor: kTextColor,
          displayColor: kTextColor,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: kFieldFill,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: kLineColor),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: kLineColor),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: const BorderSide(color: kBrandRed),
          ),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 14,
            vertical: 14,
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: kBrandRed,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            textStyle: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
        textButtonTheme: TextButtonThemeData(
          style: TextButton.styleFrom(foregroundColor: kBrandRed),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: kPageBg,
          foregroundColor: kTextColor,
          elevation: 0,
          scrolledUnderElevation: 0,
        ),
        bottomNavigationBarTheme: const BottomNavigationBarThemeData(
          backgroundColor: Colors.white,
          selectedItemColor: kBrandRed,
          unselectedItemColor: kMutedText,
          type: BottomNavigationBarType.fixed,
          showUnselectedLabels: true,
        ),
    );
  }

  ThemeData _darkTheme() {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      primaryColor: kBrandRed,
      scaffoldBackgroundColor: kDarkBg,
      colorScheme: ColorScheme.fromSeed(
        seedColor: kBrandRed,
        brightness: Brightness.dark,
        primary: kBrandRed,
        surface: kDarkSurface,
      ),
      textTheme: ThemeData.dark().textTheme.apply(
        bodyColor: kDarkText,
        displayColor: kDarkText,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: kDarkField,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: kDarkLine),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: kDarkLine),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: kBrandRed),
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 14,
          vertical: 14,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: kBrandRed,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(foregroundColor: kBrandRed),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: kDarkBg,
        foregroundColor: kDarkText,
        elevation: 0,
        scrolledUnderElevation: 0,
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: kDarkSurface,
        selectedItemColor: kBrandRed,
        unselectedItemColor: kDarkMuted,
        type: BottomNavigationBarType.fixed,
        showUnselectedLabels: true,
      ),
      cardColor: kDarkSurface,
      dividerColor: kDarkLine,
    );
  }
}

class _ThemeToggleOverlay extends StatelessWidget {
  final Widget? child;

  const _ThemeToggleOverlay({required this.child});

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        child ?? const SizedBox.shrink(),
        Positioned(
          right: 16,
          top: 16,
          child: SafeArea(
            child: ValueListenableBuilder<bool>(
              valueListenable: ThemeController.isDark,
              builder: (context, isDark, _) {
                return SizedBox(
                  width: 52,
                  height: 52,
                  child: FloatingActionButton.small(
                  heroTag: 'theme-toggle-mesero',
                  backgroundColor: isDark ? kDarkSurface : Colors.white,
                  foregroundColor: isDark ? kDarkText : kTextColor,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                    side: BorderSide(
                      color: isDark ? kDarkLine : kLineColor,
                    ),
                  ),
                  onPressed: ThemeController.toggle,
                  child: Icon(
                    isDark ? Icons.light_mode_rounded : Icons.dark_mode_rounded,
                  ),
                ),
                );
              },
            ),
          ),
        ),
        Positioned(
          right: 16,
          top: 76,
          child: SafeArea(
            child: ValueListenableBuilder<String>(
              valueListenable: LanguageController.language,
              builder: (context, language, _) {
                return SizedBox(
                  width: 52,
                  height: 52,
                  child: FloatingActionButton.small(
                  heroTag: 'language-toggle-mesero',
                  backgroundColor: kBrandRed,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                    side: const BorderSide(color: Colors.transparent),
                  ),
                  onPressed: () async {
                    final next = await LanguageController.toggle();
                    try {
                      await BongustoApi.cambiarIdioma(next);
                    } catch (_) {}
                  },
                  child: Text(
                    language == 'en' ? 'ES' : 'EN',
                    style: const TextStyle(fontWeight: FontWeight.w900),
                  ),
                ),
                );
              },
            ),
          ),
        ),
      ],
    );
  }
}
